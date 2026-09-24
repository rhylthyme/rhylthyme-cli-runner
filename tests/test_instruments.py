"""Instrument steps (galago-tools via rhylthyme-galago) in the program runner."""

import copy
import json
import sys
import threading
import time

import pytest

from rhylthyme_cli_runner.instruments import (
    INSTALL_HINT,
    InstrumentSetupError,
    attach_instruments,
    program_uses_instruments,
)
from rhylthyme_cli_runner.program_runner import ProgramRunner, StepStatus, run_program

pytestmark = pytest.mark.unit

PROGRAM = {
    "programId": "shake-plate",
    "name": "Shake a plate",
    "startTrigger": {"type": "manual"},
    "tracks": [
        {
            "trackId": "bench",
            "name": "Bench",
            "steps": [
                {
                    "stepId": "load",
                    "name": "Load plate",
                    "duration": {"type": "fixed", "seconds": 1},
                    "startTrigger": {"type": "programStart"},
                },
                {
                    "stepId": "shake",
                    "name": "Shake",
                    "instrument": {
                        "tool": "shaker",
                        "command": "start_shake",
                        "params": {"speed": 1000, "duration": 5},
                    },
                    "startTrigger": {"type": "afterStep", "stepId": "load"},
                },
                {
                    "stepId": "unload",
                    "name": "Unload plate",
                    "duration": {"type": "fixed", "seconds": 1},
                    "startTrigger": {"type": "afterStep", "stepId": "shake"},
                },
            ],
        }
    ],
    "resourceConstraints": [],
}
WORKCELL = {
    "id": "bench",
    "tools": [{"name": "shaker", "type": "bioshake", "host": "h", "port": 1}],
}


def run_until(runner, predicate, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        runner.update()
        if predicate():
            return True
        time.sleep(0.01)
    return False


def started_runner(client, program=PROGRAM):
    pytest.importorskip("rhylthyme_galago")
    runner = ProgramRunner(copy.deepcopy(program), time_scale=100.0)
    events = []
    runner.add_event_listener(lambda kind, data: events.append((kind, data)))
    session = attach_instruments(runner, WORKCELL, client_factory=lambda b: client)
    runner.start()
    runner.command_queue.put("start_program")
    return runner, session, events


def test_program_uses_instruments():
    assert program_uses_instruments(PROGRAM)
    plain = copy.deepcopy(PROGRAM)
    del plain["tracks"][0]["steps"][1]["instrument"]
    assert not program_uses_instruments(plain)


def test_instrument_step_ends_on_the_reply_not_a_timer():
    from rhylthyme_galago import FakeToolClient

    shaker = FakeToolClient(gate=threading.Event())
    runner, session, events = started_runner(shaker)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.RUNNING)
        # At 100x the planned 60 s placeholder would long have passed; the
        # step still waits for the instrument.
        run_until(runner, lambda: False, timeout=0.8)
        assert shake.status == StepStatus.RUNNING
        assert runner.steps["unload"].status == StepStatus.PENDING
        assert shaker.executed[0]["command"] == "start_shake"
        assert shaker.configured[0].simulated is True

        shaker.gate.set()
        assert run_until(runner, lambda: shake.status == StepStatus.COMPLETED)
        assert run_until(
            runner, lambda: runner.steps["unload"].status != StepStatus.PENDING
        )
    finally:
        session.shutdown()

    completed = [
        d for k, d in events if k == "step_completed" and d["step_id"] == "shake"
    ]
    assert completed[0]["ended_by"] == "instrument"
    replies = [d for k, d in events if k == "instrument_reply"]
    assert replies[0]["ok"] and replies[0]["code"] == "SUCCESS"


def test_failed_command_aborts_the_step_with_the_reason():
    from rhylthyme_galago import FakeToolClient, ToolReply

    shaker = FakeToolClient({"start_shake": ToolReply("DRIVER_ERROR", "lid open")})
    runner, session, _ = started_runner(shaker)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.ABORTED)
    finally:
        session.shutdown()
    assert shake.abort_reason == "shaker.start_shake failed: DRIVER_ERROR (lid open)"
    assert runner.steps["unload"].status == StepStatus.PENDING


def test_late_reply_for_an_aborted_step_is_ignored():
    from rhylthyme_galago import FakeToolClient

    shaker = FakeToolClient(gate=threading.Event())
    runner, session, _ = started_runner(shaker)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.RUNNING)
        runner.abort_step(shake, runner.current_time, reason="operator")
        shaker.gate.set()
        run_until(runner, lambda: False, timeout=0.3)
    finally:
        session.shutdown()
    assert shake.status == StepStatus.ABORTED
    assert shake.abort_reason == "operator"


def test_unknown_tool_is_refused_before_the_run():
    pytest.importorskip("rhylthyme_galago")
    program = copy.deepcopy(PROGRAM)
    program["tracks"][0]["steps"][1]["instrument"]["tool"] = "reader"
    runner = ProgramRunner(program)
    with pytest.raises(InstrumentSetupError, match="no tool named 'reader'"):
        attach_instruments(runner, WORKCELL)


def test_tool_not_ready_is_refused_with_a_report():
    from rhylthyme_galago import FakeToolClient, ToolReply

    class OfflineTool(FakeToolClient):
        def configure(self, config):
            return ToolReply("UNREACHABLE", "connection refused")

    runner = ProgramRunner(copy.deepcopy(PROGRAM))
    offline = OfflineTool(status="OFFLINE")
    with pytest.raises(
        InstrumentSetupError, match="shaker @ h:1: OFFLINE \\[NOT READY\\]"
    ):
        attach_instruments(runner, WORKCELL, client_factory=lambda b: offline)


def test_missing_package_gives_the_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "rhylthyme_galago", None)
    runner = ProgramRunner(copy.deepcopy(PROGRAM))
    with pytest.raises(InstrumentSetupError, match="rhylthyme\\[galago\\]"):
        attach_instruments(runner, WORKCELL)
    assert "pip install" in INSTALL_HINT


def test_run_refuses_instrument_program_without_workcell(tmp_path, capsys):
    path = tmp_path / "p.json"
    path.write_text(json.dumps(PROGRAM))
    with pytest.raises(SystemExit):
        run_program(str(path), validate=False, record=False)
    assert "pass --workcell" in capsys.readouterr().out
