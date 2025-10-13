#!/usr/bin/env python3
"""
Real-Time Program Runner

This script executes real-time program files according to the program schema.
It provides a command-line interface to visualize program execution and
allows manual triggering of steps with variable durations.
"""

import argparse
import curses
import datetime
import json
import logging
import os
import queue
import re  # Add import for regular expressions
import signal
import subprocess
import sys
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml  # Add import for YAML support
from colorama import Fore, Style


# Define sort modes for the display
class SortMode(Enum):
    """Enum representing the sort mode for the display."""

    DEFAULT = "default"  # Sort by step ID/definition order
    REMAINING = "remaining"  # Sort by remaining time
    STATUS = "status"  # Sort by status (running first, then pending, then completed)


# Define duration types
class DurationType(Enum):
    """Enum representing the duration type of a step."""

    FIXED = "fixed"  # Fixed duration
    VARIABLE = "variable"  # Variable duration with min/max
    INDEFINITE = "indefinite"  # Indefinite duration (manual end)


# Try to import the validator to reuse its functions
try:
    from .environment_loader import EnvironmentLoader, load_resource_constraints
    from .validate_program import (
        load_program_file,
        perform_additional_validations,
        validate_program,
    )
except ImportError:
    # Define our own load_program_file function if the validator is not available
    def load_program_file(file_path: str) -> Dict[str, Any]:
        """Load and parse a program file (JSON or YAML)."""
        try:
            with open(file_path, "r") as file:
                # Determine file type based on extension
                _, ext = os.path.splitext(file_path)
                if ext.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(file)
                else:  # Default to JSON
                    return json.load(file)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print(f"Error parsing file {file_path}: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            sys.exit(1)

    # Stub functions for validation if the validator is not available
    def validate_program(
        program: Dict[str, Any], schema: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        return True, []

    def perform_additional_validations(program: Dict[str, Any]) -> List[str]:
        return []


class StepStatus(Enum):
    """Enum representing the status of a step."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    WAITING_FOR_MANUAL = "WAITING_FOR_MANUAL"
    ABORTED = "ABORTED"


class StepVariables:
    """Class to hold step variables for code execution."""

    def __init__(self, step: "Step"):
        """Initialize step variables from a Step object."""
        self.stepId = step.step_id
        self.name = step.name
        self.trackId = step.track_id
        self.description = step.description
        self.status = step.status.value

        # Add task types and fractions
        self.taskTypes = step.task_types
        self.taskFractions = step.task_fractions

        # Add duration information if available
        if step.duration_type:
            self.durationType = step.duration_type.value
            if step.duration_seconds is not None:
                self.durationSeconds = step.duration_seconds
            if step.min_seconds is not None:
                self.minSeconds = step.min_seconds
            if step.max_seconds is not None:
                self.maxSeconds = step.max_seconds
            if step.default_seconds is not None:
                self.defaultSeconds = step.default_seconds


class Step:
    """Class representing a step in a program."""

    def __init__(self, step_data, track_id, batch_index=0):
        self.step_id = step_data["stepId"]
        self.name = step_data["name"]
        self.description = step_data.get("description", "")
        self.track_id = track_id
        self.batch_index = batch_index
        self.priority = step_data.get("priority", 100)
        self.expected_end_time = None
        self.manual_trigger_name = None

        # Debug logging for cook-bacon step
        if self.step_id == "cook-bacon":
            print(f"DEBUG: cook-bacon step data: {step_data}")
            print(f"DEBUG: cook-bacon duration: {step_data.get('duration', {})}")

        # Extract duration information
        self.duration_type = None
        self.duration_seconds = None
        self.min_seconds = None
        self.max_seconds = None
        self.default_seconds = None

        if "duration" in step_data:
            duration = step_data["duration"]
            if isinstance(duration, (int, float)):
                # Handle simple numeric duration (fixed duration in seconds)
                self.duration_type = DurationType.FIXED
                self.duration_seconds = float(duration)
            elif isinstance(duration, dict):
                duration_type = duration.get("type", "fixed")
                if duration_type == "fixed":
                    self.duration_type = DurationType.FIXED
                    self.duration_seconds = float(duration["seconds"])
                elif duration_type == "variable":
                    self.duration_type = DurationType.VARIABLE
                    self.min_seconds = float(duration.get("minSeconds", 0))
                    self.max_seconds = float(duration.get("maxSeconds", float("inf")))
                    self.default_seconds = float(
                        duration.get(
                            "defaultSeconds",
                            (
                                (self.min_seconds + self.max_seconds) / 2
                                if self.max_seconds < float("inf")
                                else self.min_seconds + 60
                            ),
                        )
                    )
                    # Debug logging for cook-bacon step
                    if self.step_id == "cook-bacon":
                        print(
                            f"DEBUG: cook-bacon variable duration: type={self.duration_type}, min={self.min_seconds}, max={self.max_seconds}, default={self.default_seconds}"
                        )
                        print(
                            f"DEBUG: cook-bacon triggerName: {duration.get('triggerName')}"
                        )
                    self.manual_trigger_name = duration.get("triggerName")
                elif duration_type == "indefinite" or duration_type == "manual":
                    self.duration_type = DurationType.INDEFINITE
                    self.min_seconds = float(duration.get("minSeconds", 0))
                    self.default_seconds = float(
                        duration.get("defaultSeconds", self.min_seconds + 60)
                    )
                    self.manual_trigger_name = duration.get("triggerName")

        # Extract start trigger information
        start_trigger_data = step_data["startTrigger"]

        # Check if it's multiple triggers with logic
        if "logic" in start_trigger_data and "triggers" in start_trigger_data:
            self.start_trigger_logic = start_trigger_data["logic"]  # "all" or "any"
            self.start_triggers = start_trigger_data[
                "triggers"
            ]  # List of trigger objects
            self.start_trigger = None  # Legacy field - set to None for multi-trigger
        else:
            # Single trigger (backward compatibility)
            self.start_trigger_logic = None
            self.start_triggers = None
            self.start_trigger = start_trigger_data

        # Extract task types
        self.task_types = []
        self.task_fractions = {}  # Dictionary mapping task name to fraction

        # Handle backward compatibility with single task
        if "task" in step_data and step_data["task"]:
            self.task_types.append(step_data["task"])
            self.task_fractions[step_data["task"]] = 1.0

        # Handle multiple tasks
        if "tasks" in step_data and step_data["tasks"]:
            for task in step_data["tasks"]:
                if task not in self.task_types:
                    self.task_types.append(task)
                    self.task_fractions[task] = 1.0

        # Handle fractional task resources
        if "taskResources" in step_data and step_data["taskResources"]:
            for task_resource in step_data["taskResources"]:
                task_name = task_resource["name"]
                fraction = task_resource["fraction"]
                if task_name not in self.task_types:
                    self.task_types.append(task_name)
                self.task_fractions[task_name] = fraction

        # Check for code execution
        self.has_code = "codeBlock" in step_data
        self.code_type = None
        self.code_block = None
        if self.has_code:
            self.code_type = step_data["codeBlock"]["type"]
            self.code_block = step_data["codeBlock"]["code"]

        # Initialize status
        self.status = StepStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.progress = 0.0
        self.abort_reason = None

    def to_dict(self):
        return {
            "stepId": self.step_id,
            "name": self.name,
            "description": self.description,
            "trackId": self.track_id,
            "batchIndex": self.batch_index,
            "priority": self.priority,
            "status": self.status.value,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "expectedEndTime": (
                self.expected_end_time.isoformat() if self.expected_end_time else None
            ),
            "progress": self.progress,
            "abortReason": self.abort_reason,
            "taskTypes": self.task_types,
            "taskFractions": self.task_fractions,
            "manualTriggerName": self.manual_trigger_name,
        }

    def start(self, current_time: float) -> None:
        """Start the step."""
        self.status = StepStatus.RUNNING
        self.start_time = current_time

        if self.duration_type == "fixed":
            self.expected_end_time = current_time + self.duration_seconds
        elif self.duration_type == "variable":
            self.expected_end_time = current_time + self.default_seconds
        else:
            self.expected_end_time = None

        # Execute code block if present
        if self.code_type and self.code_block:
            self.execute_code_block()

    def execute_code_block(self) -> None:
        """Execute the code block associated with this step."""
        if not self.code_type or not self.code_block:
            return

        try:
            # Create step variables for substitution
            step_vars = StepVariables(self)

            # Replace variables in the code
            code_with_vars = self._substitute_variables(self.code_block, step_vars)

            if self.code_type == "python":
                # Execute Python code
                local_vars = {}
                # Add step variables to local_vars
                local_vars["rhyl"] = step_vars
                exec(code_with_vars, globals(), local_vars)
                self.code_result = local_vars
            elif self.code_type == "shell":
                # Execute shell command with variable substitution
                result = subprocess.run(
                    code_with_vars, shell=True, capture_output=True, text=True
                )
                self.code_result = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            self.code_executed = True
        except Exception as e:
            self.code_error = str(e)
            self.code_executed = True

    def _substitute_variables(self, code: str, step_vars: StepVariables) -> str:
        """
        Substitute variables in the code with their values.

        Args:
            code: The code to substitute variables in
            step_vars: The step variables object

        Returns:
            The code with variables substituted
        """
        # Find all {rhyl.variable} patterns
        pattern = r"\{rhyl\.([a-zA-Z0-9_]+)\}"

        def replace_var(match):
            var_name = match.group(1)
            if hasattr(step_vars, var_name):
                return str(getattr(step_vars, var_name))
            return match.group(0)  # Return the original if not found

        # Replace all matches
        return re.sub(pattern, replace_var, code)

    def complete(self, current_time: float) -> None:
        """Complete the step."""
        self.status = StepStatus.COMPLETED
        self.end_time = current_time

    def abort(self, current_time: float) -> None:
        """Abort the step."""
        if self.status != StepStatus.RUNNING:
            return

        self.status = StepStatus.ABORTED
        self.end_time = current_time

    def can_be_aborted(self) -> bool:
        """Check if the step can be aborted."""
        return self.status == StepStatus.RUNNING

    def is_ready_to_start(
        self,
        completed_steps: Set[str],
        program_start_time: float,
        current_time: float,
        aborted_steps: Set[str] = None,
    ) -> bool:
        """Check if the step is ready to start based on its start trigger(s)."""
        if aborted_steps is None:
            aborted_steps = set()

        if (
            self.status != StepStatus.PENDING
            and self.status != StepStatus.WAITING_FOR_MANUAL
        ):
            return False

        if self.status == StepStatus.WAITING_FOR_MANUAL:
            return True

        # Handle multiple triggers
        if self.start_triggers is not None and self.start_trigger_logic is not None:
            trigger_results = []

            for trigger in self.start_triggers:
                trigger_ready = self._evaluate_single_trigger(
                    trigger,
                    completed_steps,
                    program_start_time,
                    current_time,
                    aborted_steps,
                )
                trigger_results.append(trigger_ready)

            if self.start_trigger_logic == "all":
                return all(trigger_results)  # ALL triggers must be satisfied
            elif self.start_trigger_logic == "any":
                return any(trigger_results)  # ANY trigger can start the step
            else:
                return False  # Unknown logic

        # Handle single trigger (backward compatibility)
        elif self.start_trigger is not None:
            return self._evaluate_single_trigger(
                self.start_trigger,
                completed_steps,
                program_start_time,
                current_time,
                aborted_steps,
            )

        return False

    def _evaluate_single_trigger(
        self,
        trigger: Dict[str, Any],
        completed_steps: Set[str],
        program_start_time: float,
        current_time: float,
        aborted_steps: Set[str],
    ) -> bool:
        """Evaluate a single trigger condition."""
        start_trigger_type = trigger.get("type")

        if start_trigger_type == "programStart":
            return True
        elif start_trigger_type == "programStartOffset":
            # Parse offset with flexible time format
            offset_value = trigger.get("offsetSeconds", 0)
            offset_seconds = parse_time_string(offset_value)
            return (current_time - program_start_time) >= offset_seconds
        elif start_trigger_type == "afterStep":
            ref_step_id = trigger.get("stepId")
            return ref_step_id in completed_steps
        elif start_trigger_type == "afterStepWithBuffer":
            ref_step_id = trigger.get("stepId")
            # Parse buffer with flexible time format
            buffer_value = trigger.get("bufferSeconds", 0)
            buffer_seconds = parse_time_string(buffer_value)

            # Check if the referenced step is completed and the buffer time has passed
            if ref_step_id in completed_steps:
                # We need to find the end time of the referenced step
                return True  # This is simplified; in a real implementation, we'd check the buffer time
        elif start_trigger_type == "manual":
            return False
        elif start_trigger_type == "onAbort":
            ref_step_id = trigger.get("stepId")
            return ref_step_id in aborted_steps

        return False

    def is_ready_to_complete(self, current_time: float) -> bool:
        """Check if the step is ready to complete based on its duration."""
        if self.status != StepStatus.RUNNING:
            return False

        if self.duration_type == "fixed":
            if self.expected_end_time is None:
                return False
            # Add small epsilon for floating point precision
            # If we're within 0.05 seconds of completion, complete it
            return current_time >= (self.expected_end_time - 0.05)
        elif self.duration_type == "variable":
            # For variable duration, we check if we've reached the minimum duration
            if self.start_time is None or self.min_seconds is None:
                return False
            return current_time >= (self.start_time + self.min_seconds)
        elif self.duration_type == "indefinite":
            # Indefinite steps are never automatically completed
            return False

        return False

    def must_complete(self, current_time: float) -> bool:
        """Check if the step must be completed (reached max duration)."""
        if self.status != StepStatus.RUNNING:
            return False

        if self.duration_type == "variable":
            return current_time >= (self.start_time + self.max_seconds)

        return False

    def get_progress(self, current_time: float) -> float:
        """Get the progress of the step as a percentage (0-100)."""
        if self.status == StepStatus.PENDING:
            return 0.0
        elif self.status == StepStatus.COMPLETED:
            return 100.0
        elif self.status == StepStatus.RUNNING:
            if self.duration_type == "indefinite":
                # For indefinite steps, we don't show progress
                return -1.0

            # Defensive checks
            if self.start_time is None:
                logging.warning(
                    f"Step {self.step_id} is RUNNING but start_time is None!"
                )
                return 0.0

            elapsed = current_time - self.start_time
            if self.duration_type == "fixed":
                if self.duration_seconds is None or self.duration_seconds == 0:
                    logging.warning(
                        f"Step {self.step_id} has invalid duration_seconds: {self.duration_seconds}"
                    )
                    return 0.0
                progress = (elapsed / self.duration_seconds) * 100.0
                # Debug: Store values for display
                self._debug_elapsed = elapsed
                self._debug_duration = self.duration_seconds
                self._debug_progress = progress
                return min(100.0, progress)
            elif self.duration_type == "variable":
                if self.default_seconds is None or self.default_seconds == 0:
                    logging.warning(
                        f"Step {self.step_id} has invalid default_seconds: {self.default_seconds}"
                    )
                    return 0.0
                return min(100.0, (elapsed / self.default_seconds) * 100.0)

        return 0.0

    def get_remaining_time(self, current_time: float) -> Optional[float]:
        """Get the remaining time in seconds."""
        if self.status != StepStatus.RUNNING:
            return None

        if self.expected_end_time is None:
            logging.warning(
                f"Step {self.step_id} is RUNNING but expected_end_time is None!"
            )
            return None

        return max(0, self.expected_end_time - current_time)

    def set_waiting_for_manual(self) -> None:
        """Set the step as waiting for manual trigger."""
        self.status = StepStatus.WAITING_FOR_MANUAL

    def has_manual_trigger(self) -> bool:
        """Check if this step has any manual triggers."""
        # Handle multiple triggers
        if self.start_triggers is not None:
            return any(
                trigger.get("type") == "manual" for trigger in self.start_triggers
            )
        # Handle single trigger
        elif self.start_trigger is not None:
            return self.start_trigger.get("type") == "manual"
        return False


def parse_time_string(time_str: str) -> float:
    """
    Parse a time string with optional units (s, m, h) into seconds.

    Examples:
        "60" -> 60 (seconds)
        "60s" -> 60 (seconds)
        "5m" -> 300 (seconds)
        "1h" -> 3600 (seconds)
        "1h30m" -> 5400 (seconds)
        "1h30m10s" -> 5410 (seconds)

    Args:
        time_str: The time string to parse

    Returns:
        The time in seconds
    """
    if isinstance(time_str, (int, float)):
        return float(time_str)

    # If it's just a number, assume seconds
    if str(time_str).isdigit():
        return float(time_str)

    # Parse complex time strings like "1h20m30s"
    total_seconds = 0

    # Find all hour, minute, and second components
    hour_match = re.search(r"(\d+)h", str(time_str))
    if hour_match:
        total_seconds += int(hour_match.group(1)) * 3600

    minute_match = re.search(r"(\d+)m", str(time_str))
    if minute_match:
        total_seconds += int(minute_match.group(1)) * 60

    second_match = re.search(r"(\d+)s", str(time_str))
    if second_match:
        total_seconds += int(second_match.group(1))

    # If no units were found but it's not a pure digit, try to convert directly
    if total_seconds == 0 and not str(time_str).isdigit():
        try:
            return float(time_str)
        except ValueError:
            # If we can't parse it, return 0
            return 0

    return total_seconds


class ProgramRunner:
    """Class for running a program."""

    def __init__(
        self, program: Dict[str, Any], time_scale: float = 1.0, auto_start: bool = False
    ):
        """
        Initialize the program runner.

        Args:
            program: The program to run
            time_scale: The time scale factor (1.0 = real-time, 2.0 = 2x speed, etc.)
            auto_start: Whether to start the program automatically
        """
        self.program = program
        self.time_scale = time_scale
        self.auto_start = auto_start

        # Initialize resource constraints using environment loader
        self.resource_constraints = {}
        self.resource_usage = {}
        self.actor_requirements = {}  # Track how many actors each task requires
        self.qualified_actor_types = {}  # Track which actor types can perform each task
        self.actor_types = {}  # Available actor types and their counts
        self.actor_usage_by_type = {}  # Track usage by actor type

        # Load resource constraints (handles both embedded and environment-based)
        resource_constraints = load_resource_constraints(program)
        for constraint in resource_constraints:
            task = constraint.get("task")
            max_concurrent = constraint.get("maxConcurrent", 1)
            actors_required = constraint.get(
                "actorsRequired", 1.0
            )  # Default to 1 actor if not specified
            qualified_types = constraint.get(
                "qualifiedActorTypes", []
            )  # Actor types that can perform this task
            if task:
                self.resource_constraints[task] = max_concurrent
                self.resource_usage[task] = 0.0
                self.actor_requirements[task] = actors_required
                self.qualified_actor_types[task] = qualified_types

        # Load actor types from environment if available
        environment_id = program.get("environment")
        if environment_id:
            from .environment_loader import EnvironmentLoader

            loader = EnvironmentLoader()
            environment = loader.get_environment(environment_id)
            if environment:
                # Handle new actorTypes format
                if "actorTypes" in environment:
                    for actor_type_id, actor_info in environment["actorTypes"].items():
                        self.actor_types[actor_type_id] = {
                            "name": actor_info.get("name", actor_type_id),
                            "count": actor_info.get("count", 1),
                            "description": actor_info.get("description", ""),
                        }
                        self.actor_usage_by_type[actor_type_id] = 0.0
                # Handle legacy actors field for backward compatibility
                elif "actors" in environment:
                    self.actor_types["generic"] = {
                        "name": "Generic Actor",
                        "count": environment["actors"],
                        "description": "Generic actor type for backward compatibility",
                    }
                    self.actor_usage_by_type["generic"] = 0.0
                    # Update qualified actor types to use generic if empty
                    for task in self.qualified_actor_types:
                        if not self.qualified_actor_types[task]:
                            self.qualified_actor_types[task] = ["generic"]
        else:
            # Fall back to program-level actors if no environment
            actor_count = program.get("actors", 1)
            self.actor_types["generic"] = {
                "name": "Generic Actor",
                "count": actor_count,
                "description": "Generic actor type from program definition",
            }
            self.actor_usage_by_type["generic"] = 0.0
            # Update qualified actor types to use generic if empty
            for task in self.qualified_actor_types:
                if not self.qualified_actor_types[task]:
                    self.qualified_actor_types[task] = ["generic"]

        # Calculate total actors available (for display purposes)
        self.actors_available = sum(info["count"] for info in self.actor_types.values())
        self.actor_usage = 0.0  # Track total actor usage for display

        self.is_running = False
        self.program_start_time = None
        self.current_time = 0
        self.status_message = "Program waiting for manual start. Press 's' to start."

        self.steps = {}
        self.tracks = {}
        self.manual_triggers = {}
        self.completed_steps = set()
        self.aborted_steps = set()
        self.resource_usage = {}
        self.sort_mode = SortMode.DEFAULT
        self.selected_step_index = 0
        self.running_steps = []  # Initialize running_steps as an empty list
        self.manually_triggered_steps = (
            set()
        )  # Initialize manually_triggered_steps as an empty set
        self.event_listeners = []  # Add event listeners list

        self.command_queue = queue.Queue()

        # Parse tracks and steps
        tracks = program.get("tracks", [])
        for track_data in tracks:
            track_id = track_data.get("trackId")
            if not track_id:
                continue

            track_name = track_data.get("name", track_id)
            self.tracks[track_id] = {"name": track_name, "steps": []}

            steps = track_data.get("steps", [])
            for step_data in steps:
                step_id = step_data.get("stepId")
                if not step_id:
                    continue

                step_name = step_data.get("name", step_id)
                step = Step(step_data, track_id)
                self.steps[step_id] = step
                self.tracks[track_id]["steps"].append(step_id)

                # Register manual triggers
                if step.manual_trigger_name:
                    if step.manual_trigger_name not in self.manual_triggers:
                        self.manual_triggers[step.manual_trigger_name] = []
                    self.manual_triggers[step.manual_trigger_name].append(step)

        # Get the actors count (default to 1 if not specified)
        self.actors = max(1, program.get("actors", 1))

        # Collect all task types used in the program
        used_task_types = set()
        for track in program.get("tracks", []):
            for step_data in track.get("steps", []):
                task_type = step_data.get("task")
                if task_type:
                    used_task_types.add(task_type)

        # Initialize resource constraints
        for constraint in program.get("resourceConstraints", []):
            task_type = constraint.get("task")
            max_concurrent = constraint.get("maxConcurrent", 1)
            self.resource_constraints[task_type] = max_concurrent
            self.resource_usage[task_type] = 0

        # Add default constraints for tasks that don't have explicit constraints
        # These will be limited by the actors count
        for task_type in used_task_types:
            if task_type not in self.resource_constraints:
                self.resource_constraints[task_type] = self.actors
                self.resource_usage[task_type] = 0

        # Initialize steps
        for track in program.get("tracks", []):
            track_id = track.get("trackId")
            batch_size = track.get("batch_size", 1)

            # Get stagger value and parse it if it's a string with units
            stagger_value = track.get("stagger", track.get("stagger_seconds", 0))
            stagger_seconds = parse_time_string(stagger_value)

            track_steps = []

            # Create multiple instances of steps for tracks with batch_size > 1
            for batch_index in range(batch_size):
                batch_suffix = f"_{batch_index + 1}" if batch_size > 1 else ""

                for step_data in track.get("steps", []):
                    step_id = step_data.get("stepId") + batch_suffix
                    step_name = step_data.get("name")

                    # Add batch number to step name if batch_size > 1
                    if batch_size > 1:
                        step_name = f"{step_name} #{batch_index + 1}"

                    # Create a copy of step_data to avoid modifying the original
                    step_data_copy = step_data.copy()

                    # Apply stagger to programStart and programStartOffset triggers
                    if batch_size > 1 and batch_index > 0 and stagger_seconds > 0:
                        start_trigger = step_data_copy.get("startTrigger", {})
                        trigger_type = start_trigger.get("type")

                        if trigger_type == "programStart":
                            # Convert programStart to programStartOffset for staggered batches
                            step_data_copy["startTrigger"] = {
                                "type": "programStartOffset",
                                "offsetSeconds": stagger_seconds * batch_index,
                            }
                        elif trigger_type == "programStartOffset":
                            # Add stagger time to existing offset
                            current_offset = start_trigger.get("offsetSeconds", 0)
                            step_data_copy["startTrigger"]["offsetSeconds"] = (
                                current_offset + (stagger_seconds * batch_index)
                            )

                    # Update step ID references in start triggers for batched steps
                    start_trigger = step_data_copy.get("startTrigger", {})
                    if start_trigger.get("type") == "afterStep" and batch_size > 1:
                        ref_step_id = start_trigger.get("stepId")
                        # Only update references to steps in the same track
                        if any(
                            s.get("stepId") == ref_step_id
                            for s in track.get("steps", [])
                        ):
                            start_trigger["stepId"] = ref_step_id + batch_suffix

                    step = Step(step_data_copy, track_id, batch_index)
                    self.steps[step_id] = step
                    track_steps.append(step)

                    # Register manual triggers
                    if step.manual_trigger_name:
                        if batch_size > 1:
                            # Create unique trigger names for each batch
                            batch_trigger_name = (
                                f"{step.manual_trigger_name}{batch_suffix}"
                            )
                            step.manual_trigger_name = batch_trigger_name

                        if step.manual_trigger_name not in self.manual_triggers:
                            self.manual_triggers[step.manual_trigger_name] = []
                        self.manual_triggers[step.manual_trigger_name].append(step)

            self.tracks[track_id] = track_steps

    def start(self) -> None:
        """Start the program execution."""
        self.program_start_time = time.time()
        self.current_time = self.program_start_time
        self.is_running = True

        # If auto_start is False, set the program to wait for manual start
        if not self.auto_start:
            self.status_message = (
                "Program waiting for manual start. Press 's' to start."
            )
            return

        # Process the program start trigger
        start_trigger = self.program.get("startTrigger", {})
        trigger_type = start_trigger.get("type", "manual")

        if trigger_type == "absolute":
            # For absolute time, we would wait until the specified time
            # For simplicity, we'll just start immediately in this example
            self.status_message = "Program started with absolute time trigger."
        elif trigger_type == "offset":
            # For offset, we would wait for the specified offset
            # For simplicity, we'll just start immediately in this example
            self.status_message = "Program started with offset trigger."
        elif trigger_type == "manual":
            # For manual, we wait for user input
            self.status_message = (
                "Program waiting for manual start. Press 's' to start."
            )
            self.is_running = False

    def update(self) -> None:
        """Update the program state."""
        # Always process commands first, even if not running
        # (this allows starting the program via 's' key)
        self.process_commands()

        if not self.is_running:
            return

        # Update current time
        real_elapsed = time.time() - self.program_start_time
        self.current_time = self.program_start_time + (real_elapsed * self.time_scale)

        # Start steps that are ready
        self.start_ready_steps(self.current_time)

        # Complete steps that are finished
        self.complete_finished_steps()

        # Check if all steps are completed
        if all(step.status == StepStatus.COMPLETED for step in self.steps.values()):
            self.is_running = False
            self.status_message = "Program execution completed."

    def process_commands(self) -> None:
        """Process commands from the command queue."""
        while not self.command_queue.empty():
            try:
                command = self.command_queue.get_nowait()
                if command == "start_program":
                    self.is_running = True
                    # Initialize program start time if not already set
                    if self.program_start_time is None:
                        self.program_start_time = time.time()
                        self.current_time = self.program_start_time
                    self.status_message = "Program started manually."
                elif command.startswith("trigger:"):
                    parts = command.split(":", 2)
                    if len(parts) == 3:
                        trigger_name, step_id = parts[1], parts[2]
                        self.trigger_manual_step(trigger_name, step_id)
                    else:
                        trigger_name = parts[1]
                        self.trigger_manual_step(trigger_name)
                elif command.startswith("abort:"):
                    step_id = command.split(":", 1)[1]
                    if step_id in self.steps and self.steps[step_id].can_be_aborted():
                        self.abort_step(self.steps[step_id], self.current_time)
            except queue.Empty:
                break

    def start_ready_steps(self, current_time: float) -> None:
        """Start steps that are ready to start."""
        # Sort steps by priority (lower number = higher priority)
        pending_steps = [
            step for step in self.steps.values() if step.status == StepStatus.PENDING
        ]
        pending_steps.sort(key=lambda s: s.priority)

        for step in pending_steps:
            if self.is_step_ready_to_start(step, current_time):
                # Check resource constraints and actor availability for each task type
                can_start = True
                required_actors_by_type = (
                    {}
                )  # Track how many actors of each type are needed

                for task_type in step.task_types:
                    if task_type in self.resource_constraints:
                        max_concurrent = self.resource_constraints[task_type]
                        fraction = step.task_fractions.get(task_type, 1.0)
                        current_usage = self.resource_usage.get(task_type, 0.0)

                        # Check if adding this step's fractional usage would exceed the constraint
                        if current_usage + fraction > max_concurrent:
                            can_start = False
                            break

                        # Check actor constraints
                        actors_required = (
                            self.actor_requirements.get(task_type, 1.0) * fraction
                        )
                        qualified_types = self.qualified_actor_types.get(task_type, [])

                        if not qualified_types:
                            # If no qualified types specified, can't run the task
                            can_start = False
                            break

                        # Find the best actor type to assign (one with lowest current usage)
                        best_actor_type = None
                        best_available_capacity = 0

                        for actor_type in qualified_types:
                            if actor_type not in self.actor_types:
                                continue

                            total_capacity = self.actor_types[actor_type]["count"]
                            current_usage = self.actor_usage_by_type.get(
                                actor_type, 0.0
                            )
                            pending_usage = required_actors_by_type.get(actor_type, 0.0)
                            available_capacity = (
                                total_capacity - current_usage - pending_usage
                            )

                            if (
                                available_capacity >= actors_required
                                and available_capacity > best_available_capacity
                            ):
                                best_actor_type = actor_type
                                best_available_capacity = available_capacity

                        if best_actor_type is None:
                            # No qualified actor type has enough capacity
                            can_start = False
                            break

                        # Reserve the actors
                        if best_actor_type not in required_actors_by_type:
                            required_actors_by_type[best_actor_type] = 0.0
                        required_actors_by_type[best_actor_type] += actors_required

                if can_start:
                    # Update resource usage for each task type
                    for task_type in step.task_types:
                        if task_type in self.resource_constraints:
                            fraction = step.task_fractions.get(task_type, 1.0)
                            self.resource_usage[task_type] = (
                                self.resource_usage.get(task_type, 0.0) + fraction
                            )

                    # Update actor usage by type
                    total_actor_usage = 0.0
                    for actor_type, usage in required_actors_by_type.items():
                        self.actor_usage_by_type[actor_type] = (
                            self.actor_usage_by_type.get(actor_type, 0.0) + usage
                        )
                        total_actor_usage += usage

                    # Update total actor usage for display
                    self.actor_usage += total_actor_usage

                    step.start(current_time)

                    # Set expected end time for fixed duration steps
                    if (
                        step.duration_type == DurationType.FIXED
                        and step.duration_seconds is not None
                    ):
                        step.expected_end_time = current_time + step.duration_seconds
                    elif (
                        step.duration_type == DurationType.VARIABLE
                        and step.default_seconds is not None
                    ):
                        step.expected_end_time = current_time + step.default_seconds
                    elif (
                        step.duration_type == DurationType.INDEFINITE
                        and step.default_seconds is not None
                    ):
                        step.expected_end_time = current_time + step.default_seconds

                    # Execute code block if present
                    if step.has_code:
                        self.execute_code_block(step)

                    # Add to running steps
                    self.running_steps.append(step.step_id)

                    # Log the step start
                    logging.info(f"Started step {step.step_id}: {step.name}")

                    # Emit event
                    self.emit_event(
                        "step_started", {"step_id": step.step_id, "time": current_time}
                    )

    def complete_finished_steps(self) -> None:
        """Complete steps that are finished."""
        for step in self.steps.values():
            if step.is_ready_to_complete(self.current_time):
                self.complete_step(step, self.current_time)
            # Aggressive completion: if remaining time displays as "< 0.1s", force complete
            elif step.status == StepStatus.RUNNING:
                remaining = step.get_remaining_time(self.current_time)
                if remaining is not None and remaining < 0.1:
                    logging.info(
                        f"Force completing step {step.step_id} with {remaining:.3f}s remaining (< 0.1s threshold)"
                    )
                    self.complete_step(step, self.current_time)

    def complete_step(self, step: Step, current_time: float) -> None:
        """Complete a step."""
        step.status = StepStatus.COMPLETED
        step.end_time = current_time
        step.progress = 1.0

        # Calculate actor usage to free by type
        freed_actors_by_type = {}

        # Decrement resource usage for each task type
        for task_type in step.task_types:
            if task_type in self.resource_constraints:
                fraction = step.task_fractions.get(task_type, 1.0)
                current_usage = self.resource_usage.get(task_type, 0.0)
                # Ensure we don't go below zero due to rounding errors
                self.resource_usage[task_type] = max(0.0, current_usage - fraction)

                # Calculate actor usage for this task
                actors_required = self.actor_requirements.get(task_type, 1.0) * fraction
                qualified_types = self.qualified_actor_types.get(task_type, [])

                # Find which actor type was actually used (choose the one with highest usage)
                best_actor_type = None
                best_usage = 0

                for actor_type in qualified_types:
                    if actor_type in self.actor_usage_by_type:
                        current_usage = self.actor_usage_by_type[actor_type]
                        if current_usage > best_usage:
                            best_actor_type = actor_type
                            best_usage = current_usage

                if best_actor_type:
                    if best_actor_type not in freed_actors_by_type:
                        freed_actors_by_type[best_actor_type] = 0.0
                    freed_actors_by_type[best_actor_type] += actors_required

        # Free actor usage by type
        total_freed = 0.0
        for actor_type, usage in freed_actors_by_type.items():
            current_usage = self.actor_usage_by_type.get(actor_type, 0.0)
            self.actor_usage_by_type[actor_type] = max(0.0, current_usage - usage)
            total_freed += usage

        # Update total actor usage for display
        self.actor_usage = max(0.0, self.actor_usage - total_freed)

        # Remove from running steps
        if step.step_id in self.running_steps:
            self.running_steps.remove(step.step_id)

        # Log the step completion
        logging.info(f"Completed step {step.step_id}: {step.name}")

        # Emit event
        self.emit_event(
            "step_completed", {"step_id": step.step_id, "time": current_time}
        )

    def trigger_manual_step(
        self, trigger_name: str, step_id: Optional[str] = None
    ) -> None:
        """
        Trigger a manual step.

        Args:
            trigger_name: The name of the trigger
            step_id: Optional specific step ID to trigger (if multiple steps have the same trigger name)
        """
        if trigger_name == "start_program":
            self.is_running = True
            self.program_start_time = self.current_time
            self.status_message = "Program started."
            return

        if trigger_name not in self.manual_triggers:
            self.status_message = f"Unknown trigger: {trigger_name}"
            return

        # If a specific step_id is provided, only trigger that step
        if step_id:
            for step in self.manual_triggers[trigger_name]:
                if step.step_id == step_id:
                    self._trigger_step(step)
                    return
            self.status_message = (
                f"Step with ID {step_id} not found for trigger {trigger_name}"
            )
            return

        # Otherwise, trigger all steps with this trigger name
        for step in self.manual_triggers[trigger_name]:
            self._trigger_step(step)

    def _trigger_step(self, step: Step) -> None:
        """
        Trigger a specific step.

        Args:
            step: The step to trigger
        """
        if step.status == StepStatus.PENDING and step.has_manual_trigger():
            step.set_waiting_for_manual()
            self.status_message = f"Step {step.name} is now waiting to start."
        elif step.status == StepStatus.RUNNING:
            if step.can_be_aborted():
                self.abort_step(step, self.current_time)
                self.status_message = f"Aborted step: {step.name}"
            elif step.duration_type == "variable" or step.duration_type == "indefinite":
                self.complete_step(step, self.current_time)
                self.status_message = f"Manually completed step: {step.name}"

    def abort_step(
        self, step: Step, current_time: float, reason: str = "Aborted"
    ) -> None:
        """
        Abort a step.

        Args:
            step: The step to abort
            current_time: The current time
            reason: The reason for aborting the step
        """
        step.status = StepStatus.ABORTED
        step.end_time = current_time
        step.abort_reason = reason

        # Calculate actor usage to free by type
        freed_actors_by_type = {}

        # Decrement resource usage for each task type
        for task_type in step.task_types:
            if task_type in self.resource_constraints:
                fraction = step.task_fractions.get(task_type, 1.0)
                current_usage = self.resource_usage.get(task_type, 0.0)
                # Ensure we don't go below zero due to rounding errors
                self.resource_usage[task_type] = max(0.0, current_usage - fraction)

                # Calculate actor usage for this task
                actors_required = self.actor_requirements.get(task_type, 1.0) * fraction
                qualified_types = self.qualified_actor_types.get(task_type, [])

                # Find which actor type was actually used (choose the one with highest usage)
                best_actor_type = None
                best_usage = 0

                for actor_type in qualified_types:
                    if actor_type in self.actor_usage_by_type:
                        current_usage = self.actor_usage_by_type[actor_type]
                        if current_usage > best_usage:
                            best_actor_type = actor_type
                            best_usage = current_usage

                if best_actor_type:
                    if best_actor_type not in freed_actors_by_type:
                        freed_actors_by_type[best_actor_type] = 0.0
                    freed_actors_by_type[best_actor_type] += actors_required

        # Free actor usage by type
        total_freed = 0.0
        for actor_type, usage in freed_actors_by_type.items():
            current_usage = self.actor_usage_by_type.get(actor_type, 0.0)
            self.actor_usage_by_type[actor_type] = max(0.0, current_usage - usage)
            total_freed += usage

        # Update total actor usage for display
        self.actor_usage = max(0.0, self.actor_usage - total_freed)

        # Remove from running steps
        if step.step_id in self.running_steps:
            self.running_steps.remove(step.step_id)

        # Add to aborted steps
        self.aborted_steps.add(step.step_id)

        # Log the step abortion
        logging.info(f"Aborted step {step.step_id}: {step.name} - Reason: {reason}")

        # Emit event
        self.emit_event(
            "step_aborted",
            {"step_id": step.step_id, "time": current_time, "reason": reason},
        )

    def get_available_triggers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available manual triggers.

        Returns:
            List of dictionaries containing trigger information:
            {
                "id": Trigger ID (for selection),
                "name": Display name,
                "type": Trigger type (program, start, end),
                "step_id": Step ID (if applicable),
                "step_name": Step name (if applicable),
                "track_id": Track ID (if applicable)
            }
        """
        available_triggers = []

        # Check for program start trigger
        if (
            not self.is_running
            and self.program.get("startTrigger", {}).get("type") == "manual"
        ):
            available_triggers.append(
                {"id": "start_program", "name": "Start Program", "type": "program"}
            )

        # Check for step triggers
        for trigger_name, steps in self.manual_triggers.items():
            for step in steps:
                if step.status == StepStatus.PENDING and step.has_manual_trigger():
                    available_triggers.append(
                        {
                            "id": f"start:{trigger_name}:{step.step_id}",
                            "name": f"Start: {step.name}",
                            "type": "start",
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "track_id": step.track_id,
                        }
                    )
                elif step.status == StepStatus.RUNNING and (
                    step.duration_type == "variable"
                    or step.duration_type == "indefinite"
                ):
                    if (
                        step.duration_type == "variable"
                        and step.get_progress(self.current_time)
                        < (step.min_seconds / step.default_seconds) * 100
                    ):
                        continue  # Can't end yet if we haven't reached minimum duration
                    available_triggers.append(
                        {
                            "id": f"end:{trigger_name}:{step.step_id}",
                            "name": f"End: {step.name}",
                            "type": "end",
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "track_id": step.track_id,
                        }
                    )

        # Check for steps that can be aborted
        for step_id, step in self.steps.items():
            if step.can_be_aborted():
                track_id = step.track_id
                track_name = self.program.get("tracks", [{}])[0].get("name", "Unknown")
                for track in self.program.get("tracks", []):
                    if track.get("trackId") == track_id:
                        track_name = track.get("name", "Unknown")
                        break

                available_triggers.append(
                    {
                        "id": f"abort:{step_id}",
                        "name": f"Abort: {step.name}",
                        "type": "abort",
                        "step_id": step_id,
                        "step_name": step.name,
                        "track_id": track_id,
                        "track_name": track_name,
                    }
                )

        return available_triggers

    def format_time(self, seconds: float) -> str:
        """Format time in seconds to a human-readable string."""
        if seconds == float("inf"):
            return "∞"

        # For times less than 10 seconds, show decimal precision
        if seconds < 10.0:
            if seconds < 0.05:
                return "< 0.1s"
            return f"{seconds:.1f}s"

        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{int(seconds)}s"

    def get_step_display_info(self, step: Step) -> Dict[str, Any]:
        """Get display information for a step."""
        progress = step.get_progress(self.current_time)
        remaining = step.get_remaining_time(self.current_time)

        # Debug: Add timing info to status for selected step
        debug_info = ""
        if hasattr(step, "_debug_elapsed") and step.status == StepStatus.RUNNING:
            debug_info = f" [DBG: e={step._debug_elapsed:.1f}s d={step._debug_duration:.1f}s p={step._debug_progress:.1f}%]"

        return {
            "id": step.step_id,
            "name": step.name + debug_info,
            "track": step.track_id,
            "status": step.status.value,
            "progress": progress,
            "remaining": (
                self.format_time(remaining) if remaining is not None else "N/A"
            ),
            "task_type": (
                step.task_types[0] if step.task_types else "N/A"
            ),  # Keep for backward compatibility
            "task_types": step.task_types,  # Add all task types
            "trigger": step.manual_trigger_name or "N/A",
        }

    def select_next_step(self) -> None:
        """Select the next step in the list."""
        steps_info = [self.get_step_display_info(step) for step in self.steps.values()]
        sorted_steps = self.sort_steps(steps_info)
        if sorted_steps:
            self.selected_step_index = (self.selected_step_index + 1) % len(
                sorted_steps
            )
            self.status_message = (
                f"Selected step: {sorted_steps[self.selected_step_index]['name']}"
            )

    def select_previous_step(self) -> None:
        """Select the previous step in the list."""
        steps_info = [self.get_step_display_info(step) for step in self.steps.values()]
        sorted_steps = self.sort_steps(steps_info)
        if sorted_steps:
            self.selected_step_index = (self.selected_step_index - 1) % len(
                sorted_steps
            )
            self.status_message = (
                f"Selected step: {sorted_steps[self.selected_step_index]['name']}"
            )

    def get_selected_step_id(self) -> Optional[str]:
        """Get the ID of the currently selected step."""
        steps_info = [self.get_step_display_info(step) for step in self.steps.values()]
        sorted_steps = self.sort_steps(steps_info)
        if not sorted_steps:
            return None
        if self.selected_step_index >= len(sorted_steps):
            self.selected_step_index = 0
        return sorted_steps[self.selected_step_index]["id"]

    def get_all_steps_display_info(self) -> List[Dict[str, Any]]:
        """Get display information for all steps."""
        steps_info = [self.get_step_display_info(step) for step in self.steps.values()]
        sorted_steps = self.sort_steps(steps_info)

        # Add selection indicator
        selected_id = self.get_selected_step_id()
        for step_info in sorted_steps:
            step_info["selected"] = step_info["id"] == selected_id

        return sorted_steps

    def get_resource_usage_display(self) -> List[Dict[str, Any]]:
        """Get display information for resource usage."""
        result = []

        # Make sure we have resource constraints defined
        if not hasattr(self, "resource_constraints") or not self.resource_constraints:
            # Check if resourceConstraints is defined in the program
            resource_constraints = self.program.get("resourceConstraints", [])
            if resource_constraints:
                # Convert to the format we need
                for constraint in resource_constraints:
                    name = constraint.get("name")
                    max_concurrent = constraint.get("maxConcurrent", 1)
                    if name:
                        current_usage = self.resource_usage.get(name, 0)
                        result.append(
                            {
                                "task_type": name,
                                "usage": f"{current_usage}/{max_concurrent}",
                                "percentage": (
                                    (current_usage / max_concurrent) * 100
                                    if max_concurrent > 0
                                    else 0
                                ),
                            }
                        )
            else:
                # No resource constraints defined
                result.append({"task_type": "None", "usage": "0/1", "percentage": 0})
        else:
            # Use the resource constraints we have
            for task_type, max_concurrent in self.resource_constraints.items():
                # Skip null task types
                if task_type is None:
                    continue

                current_usage = self.resource_usage.get(task_type, 0)
                result.append(
                    {
                        "task_type": task_type,
                        "usage": f"{current_usage}/{max_concurrent}",
                        "percentage": (
                            (current_usage / max_concurrent) * 100
                            if max_concurrent > 0
                            else 0
                        ),
                    }
                )

        return result

    def get_actor_types_display(self) -> List[Dict[str, Any]]:
        """Get display information for actor types usage."""
        result = []

        for actor_type_id, actor_info in self.actor_types.items():
            total_capacity = actor_info["count"]
            current_usage = self.actor_usage_by_type.get(actor_type_id, 0.0)
            percentage = (
                (current_usage / total_capacity * 100) if total_capacity > 0 else 0
            )

            result.append(
                {
                    "actor_type": actor_info["name"],
                    "usage": f"{current_usage:.1f}/{total_capacity}",
                    "percentage": percentage,
                }
            )

        return result

    def sort_steps(self, steps_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort steps based on the current sort mode."""
        if self.sort_mode == SortMode.DEFAULT:
            # Default order (as defined in the program)
            return steps_info
        elif self.sort_mode == SortMode.REMAINING:
            # Sort by remaining time (running steps with shortest time first, then pending, then completed)
            def remaining_time_key(step_info):
                if step_info["status"] == "COMPLETED":
                    return (2, 0)  # Completed steps last
                elif step_info["status"] == "PENDING":
                    return (1, 0)  # Pending steps in the middle
                else:
                    # For running steps, convert remaining time to seconds for sorting
                    remaining = step_info["remaining"]
                    if remaining == "N/A":
                        return (0, float("inf"))  # Indefinite duration at the end

                    # Parse the time string (e.g., "1h 30m 15s", "45m 10s", "20s")
                    seconds = 0
                    if "h" in remaining:
                        hours, remaining = remaining.split("h", 1)
                        seconds += int(hours.strip()) * 3600
                    if "m" in remaining:
                        minutes, remaining = remaining.split("m", 1)
                        seconds += int(minutes.strip()) * 60
                    if "s" in remaining:
                        s, _ = remaining.split("s", 1)
                        seconds += int(s.strip())

                    return (0, seconds)

            return sorted(steps_info, key=remaining_time_key)
        elif self.sort_mode == SortMode.STATUS:
            # Sort by status (running first, then pending, then completed)
            def status_key(step_info):
                if step_info["status"] == "RUNNING":
                    return 0
                elif step_info["status"] == "WAITING_FOR_MANUAL":
                    return 1
                elif step_info["status"] == "PENDING":
                    return 2
                else:  # COMPLETED
                    return 3

            return sorted(steps_info, key=status_key)

        return steps_info

    def display_step(self, step: Step, is_selected: bool = False) -> None:
        """Display a step with its status and progress."""
        info = self.get_step_display_info(step)

        # Determine color based on status
        color = self.get_status_color(step.status)

        # Add selection indicator
        prefix = "→ " if is_selected else "  "

        # Format the step display
        step_display = f"{prefix}{color}{info['name']} ({info['id']}){Style.RESET_ALL}"

        # Add status and progress
        status_display = (
            f"{color}[{self.get_status_display(step.status)}]{Style.RESET_ALL}"
        )
        progress_display = f"{self.get_progress_bar(info['progress'])}"
        time_display = f"{info['remaining']}"

        # Add code execution status if applicable
        code_display = ""
        if info.get("has_code", False):
            code_type = info.get("code_type", "")
            if info.get("code_executed", False):
                if info.get("code_error"):
                    code_display = f" {Fore.RED}[{code_type} error]{Style.RESET_ALL}"
                else:
                    code_display = (
                        f" {Fore.GREEN}[{code_type} executed]{Style.RESET_ALL}"
                    )
            else:
                code_display = f" {Fore.BLUE}[{code_type} pending]{Style.RESET_ALL}"

        # Print the formatted step information
        print(
            f"{step_display} {status_display} {progress_display} {time_display}{code_display}"
        )

    def display_help(self) -> None:
        """Display help information."""
        print("\nRhylthyme Program Runner Help:")
        print("------------------------------")
        print("Controls:")
        print("  q, Ctrl+C: Quit the program")
        print("  p: Pause/resume the program")
        print("  h: Display this help message")
        print("  t: Trigger the selected step (if it's waiting for manual trigger)")
        print("  e: End the selected step (if it has variable duration)")
        print("  s: Sort steps (cycles through different sort modes)")
        print("  ↑/↓: Navigate between steps")
        print("  Enter: Trigger or end the selected step")
        print("\nStep Status Colors:")
        print("  Green: Running")
        print("  Yellow: Waiting for manual trigger or end")
        print("  Red: Blocked by resource constraints")
        print("  Blue: Pending")
        print("  Gray: Completed")
        print("\nCode Execution:")
        print(
            "  Steps can include Python or shell code blocks that execute when the step starts"
        )
        print("  Code execution status is shown next to the step:")
        print("    Blue [python/shell pending]: Code has not been executed yet")
        print("    Green [python/shell executed]: Code executed successfully")
        print("    Red [python/shell error]: Code execution failed with an error")
        print("\nPress any key to continue...")

    def get_step_by_id(self, step_id: str) -> Optional[Step]:
        """Get a step by its ID."""
        return self.steps.get(step_id)

    def execute_code_block(self, step: Step) -> None:
        """Execute a code block in a step."""
        if not step.code_type or not step.code_block:
            return

        try:
            # Create step variables for substitution
            step_vars = StepVariables(step)

            # Replace variables in the code
            code_with_vars = self._substitute_variables(step.code_block, step_vars)

            if step.code_type == "python":
                # Execute Python code
                local_vars = {}
                # Add step variables to local_vars
                local_vars["rhyl"] = step_vars
                exec(code_with_vars, globals(), local_vars)
                step.code_result = local_vars
            elif step.code_type == "shell":
                # Execute shell command with variable substitution
                result = subprocess.run(
                    code_with_vars, shell=True, capture_output=True, text=True
                )
                step.code_result = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            step.code_executed = True
        except Exception as e:
            step.code_error = str(e)
            step.code_executed = True

    def _substitute_variables(self, code: str, step_vars: StepVariables) -> str:
        """
        Substitute variables in the code with their values.

        Args:
            code: The code to substitute variables in
            step_vars: The step variables object

        Returns:
            The code with variables substituted
        """
        # Find all {rhyl.variable} patterns
        pattern = r"\{rhyl\.([a-zA-Z0-9_]+)\}"

        def replace_var(match):
            var_name = match.group(1)
            if hasattr(step_vars, var_name):
                return str(getattr(step_vars, var_name))
            return match.group(0)  # Return the original if not found

        # Replace all matches
        return re.sub(pattern, replace_var, code)

    def get_status_color(self, status: StepStatus) -> int:
        """Get the color for a step status."""
        if status == StepStatus.PENDING:
            return curses.COLOR_WHITE
        elif status == StepStatus.RUNNING:
            return curses.COLOR_GREEN
        elif status == StepStatus.COMPLETED:
            return curses.COLOR_BLUE
        elif status == StepStatus.WAITING_FOR_MANUAL:
            return curses.COLOR_YELLOW
        elif status == StepStatus.ABORTED:
            return curses.COLOR_RED
        return curses.COLOR_WHITE

    def get_status_display(self, status: Union[StepStatus, str]) -> str:
        """
        Get the display string for a step status.

        Args:
            status: The step status (either StepStatus enum or string)

        Returns:
            The display string for the status
        """
        # Convert string status to enum if needed
        if isinstance(status, str):
            try:
                # Try to match the string to an enum value
                for enum_status in StepStatus:
                    if enum_status.value == status:
                        status = enum_status
                        break
            except:
                # If conversion fails, return the string as is
                return status

        if status == StepStatus.PENDING:
            return "PENDING"
        elif status == StepStatus.RUNNING:
            return "RUNNING"
        elif status == StepStatus.COMPLETED:
            return "COMPLETED"
        elif status == StepStatus.WAITING_FOR_MANUAL:
            return "WAITING"
        elif status == StepStatus.ABORTED:
            return "ABORTED"
        return "UNKNOWN"  # Default for unhandled status values

    def is_step_ready_to_start(self, step: Step, current_time: float) -> bool:
        """
        Check if a step is ready to start.

        Args:
            step: The step to check
            current_time: The current time

        Returns:
            True if the step is ready to start, False otherwise
        """
        # Only pending steps can be started
        if step.status != StepStatus.PENDING:
            return False

        start_trigger = step.start_trigger
        trigger_type = start_trigger.get("type")

        # Program start trigger
        if trigger_type == "programStart":
            return self.is_running

        # Absolute time trigger
        elif trigger_type == "absolute":
            trigger_time = datetime.fromisoformat(start_trigger["time"]).timestamp()
            return current_time >= trigger_time

        # Offset time trigger
        elif trigger_type == "offset":
            offset_seconds = float(start_trigger["offsetSeconds"])
            reference_time = self.program_start_time
            return current_time >= reference_time + offset_seconds
        
        # Program start with offset trigger
        elif trigger_type == "programStartOffset":
            offset_seconds = float(start_trigger["offsetSeconds"])
            if self.program_start_time is None:
                return False
            return current_time >= self.program_start_time + offset_seconds

        # After step trigger
        elif trigger_type == "afterStep":
            ref_step_id = start_trigger["stepId"]
            # Check if the referenced step is completed
            if ref_step_id in self.steps:
                ref_step = self.steps[ref_step_id]
                return ref_step.status == StepStatus.COMPLETED
            return False

        # Manual trigger
        elif trigger_type == "manual":
            trigger_name = start_trigger.get("triggerName", "")
            # Check if this step has been manually triggered
            return step.step_id in self.manually_triggered_steps

        # Unknown trigger type
        else:
            return False

    def emit_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Emit an event to all registered listeners.

        Args:
            event_type: The type of event
            event_data: The event data
        """
        # Log the event
        logging.debug(f"Event: {event_type} - {event_data}")

        # Call any registered event listeners
        for listener in self.event_listeners:
            try:
                listener(event_type, event_data)
            except Exception as e:
                logging.error(f"Error in event listener: {e}")

    def add_event_listener(self, listener):
        """
        Add an event listener.

        Args:
            listener: A function that takes event_type and event_data as arguments
        """
        self.event_listeners.append(listener)

    def get_upcoming_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the next upcoming events (step starts or ends).

        Args:
            limit: Maximum number of events to return

        Returns:
            List of upcoming events, each with event_type, step_id, name, time, and time_str
        """
        events = []

        # Add potential start events for pending steps
        for step in self.steps.values():
            if step.status == StepStatus.PENDING:
                # Try to estimate when this step will start
                estimated_start_time = self._estimate_step_start_time(step)
                if (
                    estimated_start_time is not None
                    and estimated_start_time >= self.current_time
                ):
                    events.append(
                        {
                            "event_type": "start",
                            "step_id": step.step_id,
                            "name": step.name,
                            "time": estimated_start_time,
                            "time_str": self.format_time(
                                estimated_start_time - self.current_time
                            ),
                        }
                    )

        # Add end events for running steps
        for step in self.steps.values():
            if step.status == StepStatus.RUNNING and step.expected_end_time is not None:
                events.append(
                    {
                        "event_type": "end",
                        "step_id": step.step_id,
                        "name": step.name,
                        "time": step.expected_end_time,
                        "time_str": self.format_time(
                            step.expected_end_time - self.current_time
                        ),
                    }
                )

        # Sort by time and limit
        events.sort(key=lambda e: e["time"])
        return events[:limit]

    def _estimate_step_start_time(self, step: Step) -> Optional[float]:
        """
        Estimate when a pending step will start.

        Args:
            step: The step to estimate

        Returns:
            Estimated start time or None if it can't be determined
        """
        if not self.is_running or self.program_start_time is None:
            return None

        trigger = step.start_trigger
        trigger_type = trigger.get("type")

        if trigger_type == "programStart":
            return self.program_start_time

        elif trigger_type == "programStartOffset":
            offset_seconds = trigger.get("offsetSeconds", 0)
            if isinstance(offset_seconds, str):
                offset_seconds = parse_time_string(offset_seconds)
            return self.program_start_time + offset_seconds

        elif trigger_type == "afterStep" or trigger_type == "afterStepWithBuffer":
            ref_step_id = trigger.get("stepId")
            if ref_step_id not in self.steps:
                return None

            ref_step = self.steps[ref_step_id]
            event = trigger.get("event", "end")

            # If reference step is completed, use its actual end time
            if (
                ref_step.status == StepStatus.COMPLETED
                and ref_step.end_time is not None
            ):
                base_time = ref_step.end_time if event == "end" else ref_step.start_time
            # If reference step is running and has expected end time
            elif (
                ref_step.status == StepStatus.RUNNING
                and ref_step.expected_end_time is not None
            ):
                if event == "end":
                    base_time = ref_step.expected_end_time
                else:
                    base_time = ref_step.start_time
            # If reference step is still pending, recursively estimate its start/end time
            elif ref_step.status == StepStatus.PENDING:
                ref_start_time = self._estimate_step_start_time(ref_step)
                if ref_start_time is None:
                    return None

                if event == "start":
                    base_time = ref_start_time
                else:
                    # Estimate end time based on duration
                    if (
                        ref_step.duration_type == DurationType.FIXED
                        and ref_step.duration_seconds is not None
                    ):
                        base_time = ref_start_time + ref_step.duration_seconds
                    elif (
                        ref_step.duration_type == DurationType.VARIABLE
                        and ref_step.default_seconds is not None
                    ):
                        base_time = ref_start_time + ref_step.default_seconds
                    elif (
                        ref_step.duration_type == DurationType.INDEFINITE
                        and ref_step.default_seconds is not None
                    ):
                        base_time = ref_start_time + ref_step.default_seconds
                    else:
                        return None
            else:
                return None

            # Add buffer if needed
            if trigger_type == "afterStepWithBuffer":
                buffer_seconds = trigger.get("bufferSeconds", 0)
                if isinstance(buffer_seconds, str):
                    buffer_seconds = parse_time_string(buffer_seconds)
                base_time += buffer_seconds

            return base_time

        elif trigger_type == "manual" or trigger_type == "onAbort":
            # Can't estimate manual triggers or abort triggers
            return None

        return None


def draw_ui(stdscr, runner: ProgramRunner) -> None:
    """Draw the user interface."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # Running
    curses.init_pair(2, curses.COLOR_BLUE, -1)  # Completed
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Waiting
    curses.init_pair(4, curses.COLOR_RED, -1)  # Aborted
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Upcoming events

    # Helper function to safely add strings to the screen
    def safe_addstr(y, x, text, attr=curses.A_NORMAL):
        # Ensure we don't write beyond the screen width
        if x >= width:
            return
        # Truncate the string if it would go beyond the screen width
        max_len = width - x - 1
        if max_len <= 0:
            return
        text = str(text)[:max_len]
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            # Catch any curses errors (like writing to the bottom-right corner)
            pass

    # Draw header
    program_name = runner.program.get("name", "Unnamed Program")
    header = f" {program_name} "
    safe_addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)

    # Draw status
    status = f" Status: {'Running' if runner.is_running else 'Stopped'} | Time Scale: {runner.time_scale}x | Actors: {runner.actors_available} "
    safe_addstr(1, (width - len(status)) // 2, status)

    # Draw actor usage
    actor_percentage = (
        (runner.actor_usage / runner.actors_available * 100)
        if runner.actors_available > 0
        else 0
    )
    actor_str = f" Actor Usage: {runner.actor_usage:.1f}/{runner.actors_available} ({actor_percentage:.0f}%) "
    safe_addstr(
        2,
        (width - len(actor_str)) // 2,
        actor_str,
        curses.color_pair(1) if actor_percentage > 80 else curses.A_NORMAL,
    )

    # Draw sort mode
    sort_mode_text = f" Sort: {runner.sort_mode.value.capitalize()} "
    safe_addstr(1, max(0, width - len(sort_mode_text) - 2), sort_mode_text)

    # Draw time
    if runner.program_start_time:
        elapsed = runner.current_time - runner.program_start_time
        time_str = f" Elapsed: {runner.format_time(elapsed)} "
        safe_addstr(3, (width - len(time_str)) // 2, time_str)

    # Draw steps table
    steps_info = runner.get_all_steps_display_info()

    # Table header
    header_y = 5
    safe_addstr(header_y, 2, "Step ID", curses.A_BOLD)
    safe_addstr(header_y, 20, "Name", curses.A_BOLD)
    safe_addstr(header_y, 40, "Track", curses.A_BOLD)

    # Add sort indicator to the status header if sorting by status
    if runner.sort_mode == SortMode.STATUS:
        safe_addstr(header_y, 55, "Status ↑", curses.A_BOLD)
    else:
        safe_addstr(header_y, 55, "Status", curses.A_BOLD)

    safe_addstr(header_y, 65, "Progress", curses.A_BOLD)

    # Add sort indicator to the remaining header if sorting by remaining time
    if runner.sort_mode == SortMode.REMAINING:
        safe_addstr(header_y, 80, "Remaining ↑", curses.A_BOLD)
    else:
        safe_addstr(header_y, 80, "Remaining", curses.A_BOLD)

    # Table rows
    last_row_y = header_y  # Track the last row we drew
    for i, step_info in enumerate(steps_info):
        row_y = header_y + 1 + i
        if (
            row_y >= height - 13
        ):  # Leave space for resources, upcoming events, and triggers
            break
        last_row_y = row_y

        # Get status color
        status_color = 0
        if step_info["status"] == "RUNNING":
            status_color = 1
        elif step_info["status"] == "COMPLETED":
            status_color = 2
        elif step_info["status"] == "WAITING_FOR_MANUAL":
            status_color = 3
        elif step_info["status"] == "ABORTED":
            status_color = 4

        # Get status display
        status_display = runner.get_status_display(step_info["status"])

        # Highlight running steps
        attr = curses.A_NORMAL
        if step_info["status"] == "RUNNING":
            attr = curses.A_BOLD

        # Draw selection indicator
        if step_info.get("selected", False):
            safe_addstr(row_y, 0, ">", curses.A_BOLD)

        safe_addstr(row_y, 2, step_info["id"][:15], attr)
        safe_addstr(row_y, 20, step_info["name"][:18], attr)
        safe_addstr(row_y, 40, step_info["track"][:13], attr)
        safe_addstr(row_y, 55, status_display[:8], attr)

        # Draw progress bar for running steps
        if step_info["status"] == "RUNNING" and step_info["progress"] >= 0:
            progress_width = 10
            filled = int((step_info["progress"] / 100) * progress_width)
            # Show at least 1 symbol if progress > 0 but < 10%
            if step_info["progress"] > 0 and filled == 0:
                progress_bar = "[>" + " " * (progress_width - 1) + "]"
            elif filled == progress_width:
                progress_bar = "[" + "#" * filled + "]"
            else:
                progress_bar = (
                    "[" + "#" * filled + ">" + " " * (progress_width - filled - 1) + "]"
                )
            safe_addstr(row_y, 65, progress_bar, attr)
        else:
            safe_addstr(row_y, 65, "N/A", attr)

        safe_addstr(row_y, 80, step_info["remaining"], attr)

    # Draw resource usage (left column in bottom section)
    resource_y = height - 12  # Move up to make room for actor types
    safe_addstr(resource_y, 2, "Resource Usage:", curses.A_BOLD)

    resource_info = runner.get_resource_usage_display()
    for i, resource in enumerate(resource_info):
        row_y = resource_y + 1 + i
        if row_y >= height - 8:  # Leave space for actor types, triggers and status
            break

        safe_addstr(row_y, 4, f"{resource['task_type']}: {resource['usage']}")

        # Draw usage bar
        bar_width = 20
        filled = int((resource["percentage"] / 100) * bar_width)
        bar = "[" + "#" * filled + " " * (bar_width - filled) + "]"
        safe_addstr(row_y, 25, bar)

    # Draw actor types usage
    actor_types_y = height - 8
    safe_addstr(actor_types_y, 2, "Actor Types:", curses.A_BOLD)

    actor_types_info = runner.get_actor_types_display()
    for i, actor_type in enumerate(actor_types_info):
        row_y = actor_types_y + 1 + i
        if row_y >= height - 4:  # Leave space for triggers and status
            break

        safe_addstr(row_y, 4, f"{actor_type['actor_type']}: {actor_type['usage']}")

        # Draw usage bar
        bar_width = 20
        filled = int((actor_type["percentage"] / 100) * bar_width)
        bar = "[" + "#" * filled + " " * (bar_width - filled) + "]"
        color_attr = (
            curses.color_pair(1) if actor_type["percentage"] > 80 else curses.A_NORMAL
        )
        safe_addstr(row_y, 25, bar, color_attr)

    # Draw upcoming events (right column in bottom section)
    events_col_x = 55  # Start column for events (right of resource usage)
    events_y = resource_y  # Same Y position as resource usage

    safe_addstr(
        events_y, events_col_x, "Upcoming Events:", curses.A_BOLD | curses.color_pair(5)
    )

    # Get upcoming events
    upcoming_events = runner.get_upcoming_events(8)  # Show up to 8 events

    if upcoming_events:
        # Draw event header
        safe_addstr(
            events_y + 1,
            events_col_x + 2,
            "Event",
            curses.A_BOLD | curses.color_pair(5),
        )
        safe_addstr(
            events_y + 1,
            events_col_x + 10,
            "Step",
            curses.A_BOLD | curses.color_pair(5),
        )
        safe_addstr(
            events_y + 1, events_col_x + 30, "In", curses.A_BOLD | curses.color_pair(5)
        )

        # Draw events
        for i, event in enumerate(upcoming_events):
            row_y = events_y + 2 + i
            if row_y >= height - 4:  # Stop before triggers section
                break

            event_type = event["event_type"].capitalize()
            step_name = event["name"]
            time_str = event["time_str"]

            # Ensure we don't exceed terminal width
            if events_col_x + 35 < width:
                safe_addstr(
                    row_y, events_col_x + 2, event_type[:5], curses.color_pair(5)
                )
                safe_addstr(
                    row_y, events_col_x + 10, step_name[:18], curses.color_pair(5)
                )
                safe_addstr(
                    row_y, events_col_x + 30, time_str[:10], curses.color_pair(5)
                )
    else:
        safe_addstr(
            events_y + 1, events_col_x + 2, "No upcoming events", curses.color_pair(5)
        )

    # Draw available triggers
    triggers_y = height - 4
    available_triggers = runner.get_available_triggers()
    if available_triggers:
        safe_addstr(triggers_y, 2, "Available Triggers:", curses.A_BOLD)
        trigger_names = [trigger["name"] for trigger in available_triggers]
        triggers_str = ", ".join(trigger_names)
        safe_addstr(triggers_y + 1, 4, triggers_str[: width - 8])

    # Draw status message
    status_y = height - 2
    if runner.status_message:
        safe_addstr(status_y, 2, runner.status_message[: width - 4])

    # Draw help
    help_text = " q: Quit | s: Start | ↑↓: Select | t: Trigger | a: Abort | c: Complete | T: Menu | +/-: Speed | o: Sort "
    # Ensure help text fits on screen
    if len(help_text) > width - 2:
        help_text = help_text[: width - 5] + "..."
    safe_addstr(height - 1, max(0, (width - len(help_text)) // 2), help_text)

    stdscr.refresh()


def handle_input(stdscr, runner: ProgramRunner) -> bool:
    """Handle user input."""
    try:
        key = stdscr.getkey()
    except:
        return True

    if key == "q":
        return False
    elif key == "s" and not runner.is_running:
        runner.command_queue.put("start_program")
    elif key == "KEY_UP" or key == "k":
        # Select previous step
        runner.select_previous_step()
    elif key == "KEY_DOWN" or key == "j":
        # Select next step
        runner.select_next_step()
    elif key == "t":
        # Get the selected step
        selected_step_id = runner.get_selected_step_id()
        if not selected_step_id or selected_step_id not in runner.steps:
            runner.status_message = "No step selected."
            return True

        selected_step = runner.steps[selected_step_id]

        # Check if the step has a manual trigger or can be aborted
        if not selected_step.manual_trigger_name:
            if selected_step.can_be_aborted():
                runner.status_message = f"Step '{selected_step.name}' has no manual trigger. Press 'a' to abort or 'T' for menu."
            else:
                runner.status_message = (
                    f"Step '{selected_step.name}' has no manual trigger."
                )
            return True

        # Check if the step can be triggered
        if (
            selected_step.status == StepStatus.PENDING
            and selected_step.has_manual_trigger()
        ):
            # Trigger the step to start
            runner.command_queue.put(
                f"trigger:{selected_step.manual_trigger_name}:{selected_step_id}"
            )
        elif selected_step.status == StepStatus.RUNNING and (
            selected_step.duration_type == "variable"
            or selected_step.duration_type == "indefinite"
        ):
            # Check if we've reached minimum duration for variable steps
            if selected_step.duration_type == "variable":
                progress = selected_step.get_progress(runner.current_time)
                min_progress = (
                    selected_step.min_seconds / selected_step.default_seconds
                ) * 100
                if progress < min_progress:
                    runner.status_message = f"Step '{selected_step.name}' hasn't reached minimum duration yet."
                    return True

            # Trigger the step to end
            runner.command_queue.put(
                f"trigger:{selected_step.manual_trigger_name}:{selected_step_id}"
            )
        else:
            runner.status_message = (
                f"Step '{selected_step.name}' cannot be triggered in its current state."
            )
            return True
    elif key == "a":
        # Abort the selected step
        selected_step_id = runner.get_selected_step_id()
        if not selected_step_id or selected_step_id not in runner.steps:
            runner.status_message = "No step selected."
            return True

        selected_step = runner.steps[selected_step_id]

        # Check if the step can be aborted
        if selected_step.can_be_aborted():
            runner.command_queue.put(f"abort:{selected_step_id}")
            runner.status_message = f"Aborting step '{selected_step.name}'..."
        else:
            runner.status_message = (
                f"Step '{selected_step.name}' cannot be aborted (not running)."
            )
        return True
    elif key == "c":
        # Force complete the selected running step (debug feature)
        selected_step_id = runner.get_selected_step_id()
        if not selected_step_id or selected_step_id not in runner.steps:
            runner.status_message = "No step selected."
            return True

        selected_step = runner.steps[selected_step_id]

        if selected_step.status == StepStatus.RUNNING:
            runner.complete_step(selected_step, runner.current_time)
            runner.status_message = f"Force completed step '{selected_step.name}'"
        else:
            runner.status_message = f"Step '{selected_step.name}' is not running (status: {selected_step.status.value})"
        return True
    elif key == "T":
        # Show trigger selection menu (original behavior)
        available_triggers = runner.get_available_triggers()
        if not available_triggers:
            runner.status_message = "No triggers available."
            return True

        # Create a submenu for trigger selection
        height, width = stdscr.getmaxyx()
        menu_height = min(len(available_triggers) + 4, height - 4)
        menu_width = min(60, width - 4)  # Wider menu to accommodate more information
        menu_y = (height - menu_height) // 2
        menu_x = (width - menu_width) // 2

        menu_win = curses.newwin(menu_height, menu_width, menu_y, menu_x)
        menu_win.box()
        menu_win.addstr(1, 2, "Select a trigger:", curses.A_BOLD)

        for i, trigger in enumerate(available_triggers):
            if i < menu_height - 4:
                if trigger["type"] == "program":
                    menu_win.addstr(i + 2, 2, f"{i+1}. {trigger['name']}")
                else:
                    # Show more details for step triggers
                    menu_win.addstr(
                        i + 2,
                        2,
                        f"{i+1}. {trigger['name']} (Track: {trigger['track_id']})",
                    )

        menu_win.addstr(menu_height - 1, 2, "Enter number or ESC to cancel")
        menu_win.refresh()

        # Get user selection
        curses.echo()
        selection = ""
        while True:
            try:
                ch = menu_win.getkey()
                if ch == "\x1b":  # ESC
                    break
                elif ch == "\n":  # Enter
                    if selection and selection.isdigit():
                        idx = int(selection) - 1
                        if 0 <= idx < len(available_triggers):
                            trigger = available_triggers[idx]
                            if trigger["id"] == "start_program":
                                runner.command_queue.put("start_program")
                            else:
                                trigger_type, trigger_name, step_id = trigger[
                                    "id"
                                ].split(":", 2)
                                runner.command_queue.put(
                                    f"trigger:{trigger_name}:{step_id}"
                                )
                    break
                elif ch.isdigit():
                    selection += ch
            except:
                break

        curses.noecho()
        stdscr.clear()
    elif key == "+" or key == "=":
        runner.time_scale = min(100.0, runner.time_scale * 2)
    elif key == "-" or key == "_":
        runner.time_scale = max(0.1, runner.time_scale / 2)
    elif key == "o" or key == "O":
        # Toggle sort mode
        if runner.sort_mode == SortMode.DEFAULT:
            runner.sort_mode = SortMode.REMAINING
            runner.status_message = "Sorted by remaining time"
        elif runner.sort_mode == SortMode.REMAINING:
            runner.sort_mode = SortMode.STATUS
            runner.status_message = "Sorted by status"
        else:
            runner.sort_mode = SortMode.DEFAULT
            runner.status_message = "Default sort order"

    return True


def main_loop(stdscr, runner: ProgramRunner) -> None:
    """Main loop for the program runner."""
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Set non-blocking input timeout

    # Start the program
    runner.start()

    # Main loop
    running = True
    while running:
        # Update program state
        runner.update()

        # Draw UI
        draw_ui(stdscr, runner)

        # Handle input
        running = handle_input(stdscr, runner)

        # Sleep to limit CPU usage
        time.sleep(0.05)


def run_program(
    program_file: str,
    schema_file: str = "program_schema.json",
    time_scale: float = 1.0,
    validate: bool = True,
    auto_start: bool = False,
    environment: str = None,
) -> None:
    """
    Run a program file with the interactive UI.

    Args:
        program_file: Path to the program file (JSON or YAML)
        schema_file: Path to the schema file (JSON or YAML)
        time_scale: Time scale factor
        validate: Whether to validate the program before running
        auto_start: Whether to automatically start the program
        environment: Environment ID to use (overrides program environment setting)
    """
    # Load the program
    program = load_program_file(program_file)

    # Handle environment resolution using the CLI's environment loader
    try:
        from .cli import get_environment_loader

        loader = get_environment_loader()
    except ImportError:
        # Fallback to default loader if CLI module not available
        from .environment_loader import EnvironmentLoader

        loader = EnvironmentLoader()

    if environment:
        # Override environment if specified via command line
        program["environment"] = environment
    elif "environmentType" in program and "environment" not in program:
        # Try to resolve environment type to a specific environment
        environment_type = program["environmentType"]
        default_env = loader.get_default_environment_for_type(environment_type)
        if default_env:
            program["environment"] = default_env
            print(
                f"Using default environment '{default_env}' for type '{environment_type}'"
            )
        else:
            available_envs = loader.list_environments_by_type(environment_type)
            if available_envs:
                print(f"Available environments for type '{environment_type}':")
                for env in available_envs:
                    print(f"  - {env['id']}: {env['name']}")
                print(f"\nUse -e/--environment to specify which environment to use.")
                print(f"Running without environment (unlimited resources)...")
            else:
                print(f"No environments found for type '{environment_type}'")
                print(f"Running without environment (unlimited resources)...")
            # Don't exit - allow program to run without environment constraints

    # Validate if requested
    if validate:
        try:
            schema = load_program_file(schema_file)
            is_valid, schema_errors = validate_program(program, schema)
            additional_errors = perform_additional_validations(program)

            if not is_valid or additional_errors:
                print(f"Program validation failed for {program_file}:")

                if schema_errors:
                    print("\nSchema validation errors:")
                    for error in schema_errors:
                        print(f"  - {error}")

                if additional_errors:
                    print("\nAdditional validation errors:")
                    for error in additional_errors:
                        print(f"  - {error}")

                sys.exit(1)

            print(f"Program {program_file} is valid.")
        except Exception as e:
            print(f"Error validating program: {e}")
            sys.exit(1)

    # Create the program runner
    runner = ProgramRunner(program, time_scale=time_scale, auto_start=auto_start)

    # Run the program with curses UI
    try:
        curses.wrapper(lambda stdscr: main_loop(stdscr, runner))
    except KeyboardInterrupt:
        print("Program execution interrupted.")


def main():
    parser = argparse.ArgumentParser(description="Run a real-time program file")
    parser.add_argument("program_file", help="Program JSON file to run")
    parser.add_argument(
        "--schema",
        default="program_schema.json",
        help="Path to the schema file (default: program_schema.json)",
    )
    parser.add_argument(
        "--time-scale", type=float, default=1.0, help="Time scale factor (default: 1.0)"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate the program before running"
    )
    parser.add_argument(
        "--auto-start", action="store_true", help="Automatically start the program"
    )

    args = parser.parse_args()

    run_program(
        args.program_file, args.schema, args.time_scale, args.validate, args.auto_start
    )


if __name__ == "__main__":
    main()
