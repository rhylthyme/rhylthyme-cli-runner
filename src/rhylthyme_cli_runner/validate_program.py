#!/usr/bin/env python3
"""
Program Schema Validator

This script validates JSON and YAML program files against the program schema.
It ensures that programs conform to the specification for real-time schedules.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

import yaml
from jsonschema import SchemaError, ValidationError, validate

# Import environment loader for environment-based validation
try:
    from .environment_loader import get_default_loader, load_resource_constraints
except ImportError:
    # Fallback if running as standalone script
    def load_resource_constraints(program):
        return program.get("resourceConstraints", [])


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
        raise ValueError(f"Error parsing file {file_path}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise


def parse_time_string_to_seconds(time_value) -> int:
    """
    Parse a time value (string or int) to seconds.

    Args:
        time_value: Time string like "5m", "30s", "1h30m" or integer seconds

    Returns:
        Time in seconds
    """
    if not time_value:
        return 0

    # Handle integer format
    if isinstance(time_value, int):
        return time_value

    # Handle string format
    if not isinstance(time_value, str):
        return 0

    # Remove whitespace
    time_str = str(time_value).strip()

    # Handle pure numbers (assume seconds)
    if time_str.isdigit():
        return int(time_str)

    total_seconds = 0
    current_number = ""

    for char in time_str:
        if char.isdigit():
            current_number += char
        elif char in ["h", "m", "s"]:
            if current_number:
                value = int(current_number)
                if char == "h":
                    total_seconds += value * 3600
                elif char == "m":
                    total_seconds += value * 60
                elif char == "s":
                    total_seconds += value
                current_number = ""

    return total_seconds


def normalize_time_fields(data: Any) -> Any:
    """
    Recursively normalize time format strings to integers in the program data.
    This converts strings like '30s', '2m', '1h30m' to integer seconds.

    Args:
        data: Program data (dict, list, or primitive)

    Returns:
        Normalized data with time strings converted to integers
    """
    if isinstance(data, dict):
        normalized = {}
        for key, value in data.items():
            # Check if this is a time-related field
            if key in ['seconds', 'minSeconds', 'maxSeconds', 'defaultSeconds',
                      'optimalSeconds', 'offsetSeconds', 'bufferSeconds']:
                # Convert time string to integer
                if isinstance(value, str):
                    normalized[key] = parse_time_string_to_seconds(value)
                else:
                    normalized[key] = value
            else:
                # Recursively normalize nested structures
                normalized[key] = normalize_time_fields(value)
        return normalized
    elif isinstance(data, list):
        return [normalize_time_fields(item) for item in data]
    else:
        return data


def validate_program(
    program: Dict[str, Any], schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate a program against the schema.

    Returns:
        Tuple containing (is_valid, error_messages)
    """
    try:
        # Normalize time fields before validation
        normalized_program = normalize_time_fields(program)
        validate(instance=normalized_program, schema=schema)
        return True, []
    except ValidationError as e:
        # Extract the validation error path and message
        path = ".".join(str(p) for p in e.path) if e.path else "root"
        message = e.message
        return False, [f"Validation error at {path}: {message}"]
    except SchemaError as e:
        return False, [f"Schema error: {e}"]


def perform_additional_validations(
    program: Dict[str, Any], strict: bool = False
) -> List[str]:
    """
    Perform additional validations that go beyond basic schema validation.
    If strict is True, always require all tasks used in steps/buffers to be defined in resourceConstraints.
    Returns:
        List of error messages (empty if all validations pass)
    """
    errors = []

    # Check for duplicate step IDs
    step_id_count = {}
    step_ids = set()
    referenced_step_ids = set()

    # Collect all step IDs and check for duplicates
    for track in program.get("tracks", []):
        for step in track.get("steps", []):
            step_id = step.get("stepId")
            step_ids.add(step_id)

            # Count occurrences for duplicate detection
            if step_id in step_id_count:
                step_id_count[step_id] += 1
            else:
                step_id_count[step_id] = 1

            # Collect referenced step IDs
            start_trigger = step.get("startTrigger", {})
            if (
                start_trigger.get("type") in ["afterStep", "afterStepWithBuffer"]
                and "stepId" in start_trigger
            ):
                referenced_step_ids.add(start_trigger.get("stepId"))

    # Report duplicate step IDs
    for step_id, count in step_id_count.items():
        if count > 1:
            errors.append(f"Duplicate step ID '{step_id}' found {count} times")

    # Check for references to non-existent steps
    for ref_id in referenced_step_ids:
        if ref_id not in step_ids:
            errors.append(f"Referenced step ID '{ref_id}' does not exist in any track")

    # Check for resource constraints
    task_types_in_steps = set()
    task_types_in_constraints = set()

    # Collect task types used in steps and buffers
    for track in program.get("tracks", []):
        for step in track.get("steps", []):
            # Main step task
            if "task" in step:
                task_types_in_steps.add(step.get("task"))

            # Pre-buffer tasks
            pre_buffer = step.get("preBuffer", {})
            if "tasks" in pre_buffer:
                for task in pre_buffer.get("tasks", []):
                    task_types_in_steps.add(task)

            # Post-buffer tasks
            post_buffer = step.get("postBuffer", {})
            if "tasks" in post_buffer:
                for task in post_buffer.get("tasks", []):
                    task_types_in_steps.add(task)

            # Pre-buffer taskResources
            if "taskResources" in pre_buffer:
                for task_resource in pre_buffer.get("taskResources", []):
                    task_types_in_steps.add(task_resource.get("name"))

            # Post-buffer taskResources
            if "taskResources" in post_buffer:
                for task_resource in post_buffer.get("taskResources", []):
                    task_types_in_steps.add(task_resource.get("name"))

    # Try to load resource constraints (handles both embedded and environment-based)
    try:
        # Import here to avoid circular imports
        from .environment_loader import load_resource_constraints

        resource_constraints = load_resource_constraints(program)
    except:
        # Fallback to just embedded constraints
        resource_constraints = program.get("resourceConstraints", [])

    # Collect task types defined in constraints
    for constraint in resource_constraints:
        task_types_in_constraints.add(constraint.get("task"))

    # Check for task types used in steps but not defined in constraints
    # Only report errors if there's no actors property (which would provide default constraints)
    # and no environment reference (which would provide environment constraints)
    if strict or ("actors" not in program and "environment" not in program):
        for task_type in task_types_in_steps:
            if task_type not in task_types_in_constraints:
                errors.append(
                    f"Task '{task_type}' is used in steps but not defined in resourceConstraints"
                )

    # If environment is referenced, validate it exists
    if "environment" in program:
        environment_id = program["environment"]
        try:
            from .environment_loader import get_default_loader

            loader = get_default_loader()
            loader.load_environment(environment_id)
        except FileNotFoundError:
            errors.append(f"Referenced environment '{environment_id}' not found")
        except Exception as e:
            errors.append(f"Error loading environment '{environment_id}': {str(e)}")

    # Check template references
    template_ids = set()
    referenced_template_ids = set()

    # Collect all template IDs
    for template in program.get("trackTemplates", []):
        template_ids.add(template.get("templateId"))

    # Collect referenced template IDs
    for track in program.get("tracks", []):
        if "templateId" in track:
            referenced_template_ids.add(track.get("templateId"))

    # Check for references to non-existent templates
    for ref_id in referenced_template_ids:
        if ref_id not in template_ids:
            errors.append(
                f"Referenced template ID '{ref_id}' does not exist in trackTemplates"
            )

    # Check for overlapping steps within the same track
    track_overlap_errors = validate_track_step_overlaps(program)
    errors.extend(track_overlap_errors)

    return errors


def validate_track_step_overlaps(program: Dict[str, Any]) -> List[str]:
    """
    Validate that steps within the same track do not overlap in time.

    Args:
        program: The program dictionary to validate

    Returns:
        List of error messages for any overlapping steps found
    """
    errors = []

    # Calculate step timing for each track
    for track_idx, track in enumerate(program.get("tracks", [])):
        track_name = track.get("name", f"Track {track_idx + 1}")
        steps = track.get("steps", [])

        if len(steps) <= 1:
            continue  # No overlaps possible with 0 or 1 steps

        # Calculate actual start times for each step
        step_timings = []

        for step in steps:
            step_id = step.get("stepId")
            duration = parse_duration_to_seconds(step.get("duration", "0s"))

            # Calculate start time based on trigger
            start_time = calculate_step_start_time(step, steps, program)
            end_time = start_time + duration

            step_timings.append(
                {
                    "stepId": step_id,
                    "name": step.get("name", step_id),
                    "startTime": start_time,
                    "endTime": end_time,
                    "duration": duration,
                }
            )

        # Sort by start time
        step_timings.sort(key=lambda x: x["startTime"])

        # Check for overlaps
        for i in range(len(step_timings) - 1):
            current_step = step_timings[i]
            next_step = step_timings[i + 1]

            # Check if current step ends after next step starts
            if current_step["endTime"] > next_step["startTime"]:
                overlap_duration = current_step["endTime"] - next_step["startTime"]
                errors.append(
                    f"Track '{track_name}': Steps '{current_step['name']}' and '{next_step['name']}' "
                    f"overlap by {overlap_duration} seconds. "
                    f"Step '{current_step['name']}' ends at {current_step['endTime']}s, "
                    f"but step '{next_step['name']}' starts at {next_step['startTime']}s."
                )

    return errors


def parse_time_string_to_seconds(time_value) -> int:
    """
    Parse a time value (string or int) to seconds.

    Args:
        time_value: Time string like "5m", "30s", "1h30m" or integer seconds

    Returns:
        Time in seconds
    """
    if not time_value:
        return 0

    # Handle integer format
    if isinstance(time_value, int):
        return time_value

    # Handle string format
    if not isinstance(time_value, str):
        return 0

    # Remove whitespace
    time_str = str(time_value).strip()

    # Handle pure numbers (assume seconds)
    if time_str.isdigit():
        return int(time_str)

    total_seconds = 0
    current_number = ""

    for char in time_str:
        if char.isdigit():
            current_number += char
        elif char in ["h", "m", "s"]:
            if current_number:
                value = int(current_number)
                if char == "h":
                    total_seconds += value * 3600
                elif char == "m":
                    total_seconds += value * 60
                elif char == "s":
                    total_seconds += value
                current_number = ""

    return total_seconds


def parse_duration_to_seconds(duration) -> int:
    """
    Parse a duration (string or dict) to seconds.

    Args:
        duration: Duration string like "5m", "30s", "1h30m" or dict with type/seconds

    Returns:
        Duration in seconds
    """
    if not duration:
        return 0

    # Handle dict format (e.g., {"type": "fixed", "seconds": 180})
    if isinstance(duration, dict):
        if "seconds" in duration:
            seconds_value = duration["seconds"]
            return parse_time_string_to_seconds(seconds_value)
        elif "minutes" in duration:
            return int(duration["minutes"]) * 60
        elif "hours" in duration:
            return int(duration["hours"]) * 3600
        else:
            return 0

    # Handle string format
    return parse_time_string_to_seconds(duration)


def calculate_step_start_time(
    step: Dict[str, Any], track_steps: List[Dict[str, Any]], program: Dict[str, Any]
) -> int:
    """
    Calculate the start time of a step based on its trigger.

    Args:
        step: The step to calculate start time for
        track_steps: All steps in the same track
        program: The full program (for cross-track dependencies)

    Returns:
        Start time in seconds from program start
    """
    start_trigger = step.get("startTrigger", {})
    trigger_type = start_trigger.get("type", "programStart")

    if trigger_type == "programStart":
        offset_seconds = start_trigger.get("offsetSeconds", 0)
        return max(0, offset_seconds)

    elif trigger_type in ["afterStep", "afterStepWithBuffer"]:
        referenced_step_id = start_trigger.get("stepId")
        offset_seconds = start_trigger.get("offsetSeconds", 0)
        event = start_trigger.get("event", "end")  # Default to "end"

        if not referenced_step_id:
            return 0  # Invalid trigger, assume program start

        # Find the referenced step (could be in any track)
        referenced_step = None
        referenced_track_steps = None

        # First check current track
        for s in track_steps:
            if s.get("stepId") == referenced_step_id:
                referenced_step = s
                referenced_track_steps = track_steps
                break

        # If not found in current track, check all tracks
        if not referenced_step:
            for track in program.get("tracks", []):
                for s in track.get("steps", []):
                    if s.get("stepId") == referenced_step_id:
                        referenced_step = s
                        referenced_track_steps = track.get("steps", [])
                        break
                if referenced_step:
                    break

        if not referenced_step:
            return 0  # Referenced step not found, assume program start

        # Calculate referenced step's timing
        referenced_start_time = calculate_step_start_time(
            referenced_step, referenced_track_steps, program
        )
        referenced_duration = parse_duration_to_seconds(
            referenced_step.get("duration", "0s")
        )

        if event == "start":
            base_time = referenced_start_time
        else:  # event == "end"
            base_time = referenced_start_time + referenced_duration

        return max(0, base_time + offset_seconds)

    else:
        # Unknown trigger type, assume program start
        return 0


def validate_program_file_structured(
    program_file: str,
    schema_file: str = "program_schema.json",
    verbose: bool = False,
    strict: bool = False,
) -> dict:
    """
    Validate a program file and return a structured result for machine-readable output.
    Returns a dict with is_valid, schema_errors, logic_errors, and summary info.
    """
    schema = load_program_file(schema_file)
    program = load_program_file(program_file)
    is_valid, schema_errors = validate_program(program, schema)
    logic_errors = perform_additional_validations(program, strict=strict)
    summary = {
        "programId": program.get("programId"),
        "name": program.get("name"),
        "tracks": len(program.get("tracks", [])),
        "resourceConstraints": len(program.get("resourceConstraints", [])),
        "totalSteps": sum(
            len(track.get("steps", [])) for track in program.get("tracks", [])
        ),
    }
    return {
        "is_valid": is_valid and not logic_errors,
        "schema_errors": schema_errors,
        "logic_errors": logic_errors,
        "summary": summary,
    }


def validate_program_file(
    program_file: str,
    schema_file: str = "program_schema.json",
    verbose: bool = False,
    json_output: bool = False,
    strict: bool = False,
) -> bool:
    """
    Validate a program file against the schema.
    If json_output is True, print machine-readable JSON result.
    If strict is True, enforce all tasks must be defined in resourceConstraints.
    """
    result = validate_program_file_structured(
        program_file, schema_file, verbose, strict
    )
    if json_output:
        import json as _json

        print(_json.dumps(result, indent=2))
        return result["is_valid"]
    # Default: print human-readable output
    print(f"Validating {program_file}...")
    valid = result["is_valid"]
    if valid:
        print(f"✅ {program_file} is valid")
    else:
        print(f"❌ {program_file} has validation errors:")
        if result["schema_errors"]:
            print("\nSchema validation errors:")
            for error in result["schema_errors"]:
                print(f"  - {error}")
        if result["logic_errors"]:
            print("\nAdditional validation errors:")
            for error in result["logic_errors"]:
                print(f"  - {error}")
    if verbose:
        print("\nProgram details:")
        for k, v in result["summary"].items():
            print(f"  - {k}: {v}")
    return valid


def main():
    parser = argparse.ArgumentParser(
        description="Validate program files (JSON or YAML) against the schema"
    )
    parser.add_argument(
        "program_files", nargs="+", help="Program files (JSON or YAML) to validate"
    )
    parser.add_argument(
        "--schema",
        default="program_schema.json",
        help="Path to the schema file (default: program_schema.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed validation results"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Print machine-readable JSON result"
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Enforce all tasks must be defined in resourceConstraints",
    )

    args = parser.parse_args()

    all_valid = True

    for program_file in args.program_files:
        file_valid = validate_program_file(
            program_file, args.schema, args.verbose, args.json, args.strict
        )
        if not file_valid:
            all_valid = False

    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
