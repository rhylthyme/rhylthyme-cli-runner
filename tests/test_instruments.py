"""Instrument steps (galago-tools via rhylthyme-galago) in the program runner."""

import copy
import json
import sys
import threading
import time
from typing import Any, Dict

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


# --- Validation (phase 2) --------------------------------------------------


def _write(tmp_path, name, data):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return str(path)


def _with_instrument(**changes):
    program = copy.deepcopy(PROGRAM)
    program["tracks"][0]["steps"][1]["instrument"].update(changes)
    return program


def _codes(findings):
    return [(f.code, f.severity) for f in findings]


def test_programs_without_instruments_need_no_package(monkeypatch):
    from rhylthyme_cli_runner.instruments import instrument_findings

    monkeypatch.setitem(sys.modules, "rhylthyme_galago", None)
    plain = copy.deepcopy(PROGRAM)
    del plain["tracks"][0]["steps"][1]["instrument"]
    assert instrument_findings(plain) == []


def test_missing_package_warns_without_workcell_and_fails_with_one(monkeypatch):
    from rhylthyme_cli_runner.instruments import instrument_findings

    monkeypatch.setitem(sys.modules, "rhylthyme_galago", None)
    [finding] = instrument_findings(PROGRAM)
    assert _codes([finding]) == [("instrument_unchecked", "warning")]
    assert "rhylthyme[galago]" in finding.fix
    [finding] = instrument_findings(PROGRAM, WORKCELL)
    assert _codes([finding]) == [("instrument_unchecked", "error")]


def test_findings_name_the_step_and_field():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.instruments import instrument_findings

    [finding] = instrument_findings(
        _with_instrument(toolType="bioshake", params={"speed": "fast"})
    )
    assert finding.code == "instrument_invalid_command"
    assert finding.where == "step:shake"
    assert finding.message == (
        "Step 'shake': shaker (bioshake) start_shake: "
        "param 'speed' must be an integer, got 'fast'"
    )
    assert _codes(instrument_findings(PROGRAM)) == [("instrument_unchecked", "warning")]
    assert instrument_findings(PROGRAM, WORKCELL) == []


def test_workcell_findings():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.instruments import instrument_findings

    assert _codes(instrument_findings(_with_instrument(tool="reader"), WORKCELL)) == [
        ("instrument_unknown_tool", "error")
    ]
    assert _codes(
        instrument_findings(_with_instrument(toolType="liconic"), WORKCELL)
    ) == [("instrument_tool_type_mismatch", "error")]
    [bad] = instrument_findings(PROGRAM, {"tools": [{"name": "shaker"}]})
    assert (bad.code, bad.where) == ("workcell_invalid", "workcell")
    assert "missing type, host, port" in bad.message


@pytest.mark.cli
def test_validate_cli_with_workcell(tmp_path):
    pytest.importorskip("rhylthyme_galago")
    from click.testing import CliRunner

    from rhylthyme_cli_runner.cli import cli

    good = _write(tmp_path, "good.json", PROGRAM)
    bad = _write(tmp_path, "bad.json", _with_instrument(command="spin"))
    workcell = _write(tmp_path, "lab.json", WORKCELL)

    ok = CliRunner().invoke(cli, ["validate", good, "--workcell", workcell])
    assert ok.exit_code == 0, ok.output
    assert "instrument_unchecked" not in ok.output

    offline = CliRunner().invoke(cli, ["validate", good])
    assert offline.exit_code == 0
    assert "instrument_unchecked" in offline.output

    failed = CliRunner().invoke(
        cli, ["validate", bad, "--workcell", workcell, "--json"]
    )
    assert failed.exit_code == 1
    result = json.loads(failed.output)
    [finding] = [f for f in result["findings"] if f["code"].startswith("instrument")]
    assert finding["where"] == "step:shake"
    assert "bioshake has no command 'spin'" in finding["message"]


def test_run_refuses_invalid_instrument_command(tmp_path, capsys):
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.cli import _default_schema_path

    path = _write(tmp_path, "p.json", _with_instrument(params={"rpm": 5}))
    workcell = _write(tmp_path, "lab.json", WORKCELL)
    with pytest.raises(SystemExit):
        run_program(path, _default_schema_path(), record=False, workcell=workcell)
    assert "unknown param 'rpm'" in capsys.readouterr().out


# --- Pre-flight and --live (phase 3) ---------------------------------------


@pytest.fixture
def fake_tools(monkeypatch):
    """Route run_program's tools to one FakeToolClient; never open curses."""
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    import rhylthyme_cli_runner.program_runner as pr

    tool = FakeToolClient()
    real_open = pr.open_instruments
    factory_calls = []

    def factory(binding):
        factory_calls.append(binding.name)
        return tool

    monkeypatch.setattr(
        pr,
        "open_instruments",
        lambda program, workcell, live=False: real_open(
            program, workcell, live=live, client_factory=factory
        ),
    )
    ran = []
    monkeypatch.setattr(pr.curses, "wrapper", lambda fn: ran.append(True))
    tool.ran = ran
    tool.factory_calls = factory_calls
    return tool


def _run(tmp_path, **kwargs):
    program = _write(tmp_path, "p.json", PROGRAM)
    workcell = _write(tmp_path, "lab.json", WORKCELL)
    return run_program(
        program, validate=False, record=False, workcell=workcell, **kwargs
    )


def test_open_instruments_contacts_no_tool():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.instruments import open_instruments

    made = []
    session = open_instruments(
        PROGRAM, WORKCELL, client_factory=lambda b: made.append(b) or None
    )
    assert session.tools == ["shaker"] and made == []
    assert not session.live


def test_live_summary_lists_tools_and_commands_without_configuring():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    from rhylthyme_cli_runner.instruments import open_instruments

    tool = FakeToolClient(status="READY")
    session = open_instruments(
        PROGRAM, WORKCELL, client_factory=lambda b: tool, live=True
    )
    text = "\n".join(session.summary(PROGRAM))
    assert "LIVE: real hardware will move" in text
    assert "shaker (bioshake) @ h:1: READY" in text
    assert "shake: shaker.start_shake(speed=1000, duration=5)" in text
    assert tool.configured == []


def test_default_run_configures_simulated(fake_tools, tmp_path, capsys):
    _run(tmp_path)
    assert [c.simulated for c in fake_tools.configured] == [True]
    assert fake_tools.ran
    assert "(simulated)" in capsys.readouterr().out


def test_live_without_a_terminal_needs_confirm_live(
    fake_tools, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    with pytest.raises(SystemExit):
        _run(tmp_path, live=True)
    out = capsys.readouterr().out
    assert "pass --confirm-live" in out and "nothing was sent" in out
    assert fake_tools.configured == [] and fake_tools.executed == []
    assert not fake_tools.ran


@pytest.mark.parametrize(
    "answer, proceeds", [("live", True), ("LIVE ", True), ("yes", False), ("", False)]
)
def test_live_asks_in_a_terminal(fake_tools, tmp_path, monkeypatch, answer, proceeds):
    import builtins

    fake_tools._status = "READY"
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(builtins, "input", lambda prompt="": answer)
    if proceeds:
        _run(tmp_path, live=True)
        assert [c.simulated for c in fake_tools.configured] == [False]
        assert fake_tools.ran
    else:
        with pytest.raises(SystemExit):
            _run(tmp_path, live=True)
        assert fake_tools.configured == [] and not fake_tools.ran


def test_confirm_live_skips_the_question(fake_tools, tmp_path, monkeypatch):
    fake_tools._status = "READY"
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    _run(tmp_path, live=True, confirm_live=True)
    assert [c.simulated for c in fake_tools.configured] == [False]


def test_live_refuses_tools_that_are_not_ready(fake_tools, tmp_path, capsys):
    fake_tools._status = "FAILED"
    with pytest.raises(SystemExit):
        _run(tmp_path, live=True, confirm_live=True)
    out = capsys.readouterr().out
    assert "shaker @ h:1: FAILED [NOT READY]" in out
    assert fake_tools.executed == [] and not fake_tools.ran


def test_run_record_holds_no_workcell_data(tmp_path):
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    from rhylthyme_cli_runner.history.recorder import RunRecorder

    workcell = copy.deepcopy(WORKCELL)
    workcell["tools"][0].update(host="10.20.30.40", port=50710)
    runner = ProgramRunner(copy.deepcopy(PROGRAM), time_scale=100.0)
    recorder = RunRecorder(
        runner, source_program=PROGRAM, runs_dir=str(tmp_path)
    ).attach()
    session = attach_instruments(
        runner, workcell, client_factory=lambda b: FakeToolClient()
    )
    try:
        runner.start()
        runner.command_queue.put("start_program")
        assert run_until(runner, lambda: not runner.is_running)
    finally:
        session.shutdown()
    written = recorder.finalize()
    text = open(written).read()
    assert "10.20.30.40" not in text and "50710" not in text
    from rhylthyme_cli_runner.history.store import validate_run

    record = json.loads(text)
    assert validate_run(record) == []
    assert {s["stepId"]: s.get("endedBy") for s in record["steps"]}[
        "shake"
    ] == "instrument"


# --- Failure handling (phase 4) ---------------------------------------------

# Bench: load -> shake (instrument) -> unload. Side: warm (100 s, running
# while the shake fails) -> after-warm (becomes ready during the failure).
TWO_TRACKS: Dict[str, Any] = copy.deepcopy(PROGRAM)
TWO_TRACKS["tracks"].append(
    {
        "trackId": "side",
        "name": "Side",
        "steps": [
            {
                "stepId": "warm",
                "name": "Warm media",
                "duration": {"type": "fixed", "seconds": 100},
                "startTrigger": {"type": "programStart"},
            },
            {
                "stepId": "after-warm",
                "name": "Use warm media",
                "duration": {"type": "fixed", "seconds": 1},
                "startTrigger": {"type": "afterStep", "stepId": "warm"},
            },
        ],
    }
)


def _failing(code="DRIVER_ERROR", message="lid open"):
    from rhylthyme_galago import FakeToolClient, ToolReply

    return FakeToolClient({"start_shake": ToolReply(code, message)})


@pytest.mark.parametrize(
    "code",
    [
        "DRIVER_ERROR",
        "ERROR_FROM_TOOL",
        "NOT_READY",
        "INVALID_ARGUMENTS",
        "UNREACHABLE",
    ],
)
def test_error_replies_fail_the_step(code):
    pytest.importorskip("rhylthyme_galago")
    runner, session, events = started_runner(_failing(code, "boom"))
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
    finally:
        session.shutdown()
    assert shake.failure == {
        "tool": "shaker",
        "command": "start_shake",
        "code": code,
        "errorMessage": "boom",
    }
    assert runner.failed_steps == ["shake"]
    assert f"FAILED shake: shaker.start_shake {code} (boom)" in runner.status_message
    assert "r: retry  x: skip  A: abort program" in runner.status_message
    failed = [d for k, d in events if k == "step_failed"]
    assert failed[0]["code"] == code


def test_timeout_fails_the_step():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    program = copy.deepcopy(PROGRAM)
    program["tracks"][0]["steps"][1]["instrument"]["timeoutSeconds"] = 0.2
    tool = FakeToolClient(gate=threading.Event())
    runner, session, _ = started_runner(tool, program)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
        assert shake.failure["code"] == "TIMEOUT"
    finally:
        tool.gate.set()
        session.shutdown()


def test_failure_holds_new_steps_but_running_ones_finish():
    pytest.importorskip("rhylthyme_galago")
    runner, session, _ = started_runner(_failing(), TWO_TRACKS)
    try:
        assert run_until(
            runner, lambda: runner.steps["shake"].status == StepStatus.FAILED
        )
        assert runner.steps["warm"].status == StepStatus.RUNNING
        assert run_until(
            runner, lambda: runner.steps["warm"].status == StepStatus.COMPLETED
        )
        run_until(runner, lambda: False, timeout=0.3)
        assert runner.steps["after-warm"].status == StepStatus.PENDING
        assert runner.steps["unload"].status == StepStatus.PENDING
        assert runner.is_running
    finally:
        session.shutdown()


def test_retry_resends_and_success_resumes():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import ToolReply

    tool = _failing()
    runner, session, events = started_runner(tool, TWO_TRACKS)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
        tool.replies["start_shake"] = ToolReply("SUCCESS")
        runner.command_queue.put("retry:shake")
        assert run_until(runner, lambda: shake.status == StepStatus.COMPLETED)
        assert run_until(
            runner, lambda: runner.steps["unload"].status != StepStatus.PENDING
        )
    finally:
        session.shutdown()
    assert [c["command"] for c in tool.executed] == ["start_shake", "start_shake"]
    assert shake.instrument_attempts == 2
    assert runner.failed_steps == []
    retries = [d for k, d in events if k == "step_retry"]
    assert retries[0]["attempt"] == 2


def test_retry_that_fails_again_stays_failed():
    pytest.importorskip("rhylthyme_galago")
    tool = _failing()
    runner, session, _ = started_runner(tool)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
        runner.command_queue.put("retry:")
        assert run_until(runner, lambda: len(tool.executed) == 2)
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
    finally:
        session.shutdown()


def test_skip_marks_done_and_releases_dependents():
    pytest.importorskip("rhylthyme_galago")
    runner, session, events = started_runner(_failing(), TWO_TRACKS)
    try:
        shake = runner.steps["shake"]
        assert run_until(runner, lambda: shake.status == StepStatus.FAILED)
        runner.command_queue.put("skip:shake")
        assert run_until(
            runner, lambda: runner.steps["unload"].status != StepStatus.PENDING
        )
    finally:
        session.shutdown()
    assert shake.status == StepStatus.COMPLETED
    ended = [d for k, d in events if k == "step_completed" and d["step_id"] == "shake"]
    assert ended[0]["ended_by"] == "skipped"


def test_abort_program_ends_the_run_with_a_reason(tmp_path):
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.history.recorder import RunRecorder

    runner = ProgramRunner(copy.deepcopy(TWO_TRACKS), time_scale=100.0)
    recorder = RunRecorder(
        runner, source_program=TWO_TRACKS, runs_dir=str(tmp_path)
    ).attach()
    session = attach_instruments(runner, WORKCELL, client_factory=lambda b: _failing())
    try:
        runner.start()
        runner.command_queue.put("start_program")
        assert run_until(
            runner, lambda: runner.steps["shake"].status == StepStatus.FAILED
        )
        runner.command_queue.put("abort_program:plate cracked")
        assert run_until(runner, lambda: not runner.is_running)
    finally:
        session.shutdown()
    assert runner.steps["shake"].status == StepStatus.ABORTED
    assert runner.steps["warm"].status == StepStatus.ABORTED
    assert runner.steps["unload"].status == StepStatus.PENDING
    assert runner.program_abort_reason == "plate cracked"
    record = json.loads(open(recorder.finalize()).read())
    assert record["outcome"] == "aborted"
    assert record["context"]["abortReason"] == "plate cracked"
    from rhylthyme_cli_runner.history.store import validate_run

    assert validate_run(record) == []


class _Keys:
    def __init__(self, *keys):
        self.keys = list(keys)

    def getkey(self):
        if not self.keys:
            raise Exception("no input")
        return self.keys.pop(0)


def test_keys_retry_skip_and_double_press_abort():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_cli_runner.program_runner import handle_input

    runner, session, _ = started_runner(_failing())
    try:
        assert run_until(runner, lambda: runner.failed_steps == ["shake"])
        handle_input(_Keys("r"), runner)
        assert runner.command_queue.get_nowait() == "retry:"
        handle_input(_Keys("x"), runner)
        assert runner.command_queue.get_nowait() == "skip:"
        handle_input(_Keys("A"), runner)
        assert runner.command_queue.empty()
        assert "Press A again" in runner.status_message
        handle_input(_Keys("A"), runner)
        assert runner.command_queue.get_nowait().startswith("abort_program:")
    finally:
        session.shutdown()


def test_ctrl_c_reports_in_flight_commands(fake_tools, tmp_path, capsys, monkeypatch):
    import rhylthyme_cli_runner.program_runner as pr

    fake_tools.gate = threading.Event()
    captured = {}
    real_runner = pr.ProgramRunner

    class Capturing(real_runner):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            captured["runner"] = self

    def wrapper(fn):
        # Run headlessly until the shake is in flight, then Ctrl-C
        r = captured["runner"]
        r.time_scale = 100.0
        r.start()
        r.command_queue.put("start_program")
        assert run_until(r, lambda: r.steps["shake"].status == StepStatus.RUNNING)
        raise KeyboardInterrupt

    monkeypatch.setattr(pr, "ProgramRunner", Capturing)
    monkeypatch.setattr(pr.curses, "wrapper", wrapper)
    started = time.time()
    _run(tmp_path)
    assert time.time() - started < 5
    out = capsys.readouterr().out
    assert "Program execution interrupted." in out
    assert "Instrument commands still running when the runner stopped: shake" in out
    fake_tools.gate.set()


# --- Tools as resources, mixed programs (phase 5) ----------------------------


def _shake_step(step_id):
    return {
        "stepId": step_id,
        "name": step_id,
        "instrument": {"tool": "shaker", "command": "start_shake"},
        "startTrigger": {"type": "programStart"},
    }


def _two_shakes(**program_fields):
    program = {
        "programId": "two-shakes",
        "name": "Two shakes",
        "startTrigger": {"type": "manual"},
        "tracks": [
            {"trackId": "a", "name": "A", "steps": [_shake_step("shake-a")]},
            {"trackId": "b", "name": "B", "steps": [_shake_step("shake-b")]},
        ],
        "resourceConstraints": [],
    }
    program.update(program_fields)
    return program


class _GatedPerCall:
    """FakeToolClient whose each execute waits for its own release."""

    def __new__(cls):
        from rhylthyme_galago import FakeToolClient

        class Tool(FakeToolClient):
            def __init__(self):
                super().__init__()
                self.releases = []

            def execute(self, command, timeout=None):
                gate = threading.Event()
                self.releases.append(gate)
                gate.wait(5)
                return super().execute(command, timeout)

        return Tool()


def test_each_tool_is_an_implicit_resource_of_one():
    pytest.importorskip("rhylthyme_galago")
    runner = ProgramRunner(_two_shakes())
    assert runner.resource_constraints["shaker"] == 1
    assert runner.implicit_tool_resources == {"shaker"}
    assert "shaker" in runner.steps["shake-a"].task_types


def test_two_steps_on_one_tool_take_turns():
    pytest.importorskip("rhylthyme_galago")
    tool = _GatedPerCall()
    runner, session, _ = started_runner(tool, _two_shakes())
    a, b = runner.steps["shake-a"], runner.steps["shake-b"]
    try:
        assert run_until(
            runner,
            lambda: a.status == StepStatus.RUNNING or b.status == StepStatus.RUNNING,
        )
        first, second = (a, b) if a.status == StepStatus.RUNNING else (b, a)
        run_until(runner, lambda: False, timeout=0.3)
        assert second.status == StepStatus.PENDING  # waiting on the tool, not failed
        assert second.trigger_fired_time is not None
        assert len(tool.releases) == 1
        tool.releases[0].set()
        assert run_until(runner, lambda: second.status == StepStatus.RUNNING)
        assert first.status == StepStatus.COMPLETED
        assert run_until(runner, lambda: len(tool.releases) == 2)
        tool.releases[1].set()
        assert run_until(runner, lambda: second.status == StepStatus.COMPLETED)
    finally:
        for gate in tool.releases:
            gate.set()
        session.shutdown()


def test_declared_constraint_overrides_the_capacity():
    pytest.importorskip("rhylthyme_galago")
    tool = _GatedPerCall()
    program = _two_shakes(
        resourceConstraints=[
            {"task": "shaker", "maxConcurrent": 2, "description": "two-deck shaker"}
        ]
    )
    runner, session, _ = started_runner(tool, program)
    try:
        assert run_until(
            runner,
            lambda: all(
                runner.steps[s].status == StepStatus.RUNNING
                for s in ("shake-a", "shake-b")
            ),
        )
        assert runner.implicit_tool_resources == set()
        assert runner.actor_requirements["shaker"] == 0.0
    finally:
        for gate in tool.releases:
            gate.set()
        session.shutdown()


def test_tool_steps_need_no_person():
    """With the only actor busy on a hand task, the shaker still starts."""
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    program = _two_shakes(
        actors=1,
        resourceConstraints=[
            {
                "task": "pipetting",
                "maxConcurrent": 1,
                "actorsRequired": 1,
                "description": "hands",
            }
        ],
    )
    program["tracks"][1]["steps"] = [
        {
            "stepId": "pipette",
            "name": "Pipette by hand",
            "task": "pipetting",
            "duration": {"type": "fixed", "seconds": 100},
            "startTrigger": {"type": "programStart"},
        }
    ]
    tool = FakeToolClient(gate=threading.Event())
    runner, session, _ = started_runner(tool, program)
    try:
        assert run_until(
            runner,
            lambda: runner.steps["pipette"].status == StepStatus.RUNNING
            and runner.steps["shake-a"].status == StepStatus.RUNNING,
        )
    finally:
        tool.gate.set()
        session.shutdown()


def test_hand_step_between_two_incubator_steps_runs_in_order():
    pytest.importorskip("rhylthyme_galago")
    from rhylthyme_galago import FakeToolClient

    program = {
        "programId": "mixed",
        "name": "Incubate, check, incubate",
        "startTrigger": {"type": "manual"},
        "tracks": [
            {
                "trackId": "culture",
                "name": "Culture",
                "steps": [
                    {
                        "stepId": "fetch",
                        "name": "Fetch plate",
                        "instrument": {
                            "tool": "incubator",
                            "command": "fetch_plate",
                            "params": {"cassette": 1, "level": 2},
                        },
                        "startTrigger": {"type": "programStart"},
                    },
                    {
                        "stepId": "check",
                        "name": "Check media colour",
                        "duration": {"type": "fixed", "seconds": 60},
                        "startTrigger": {"type": "afterStep", "stepId": "fetch"},
                    },
                    {
                        "stepId": "store",
                        "name": "Store plate",
                        "instrument": {
                            "tool": "incubator",
                            "command": "store_plate",
                            "params": {"cassette": 1, "level": 2},
                        },
                        "startTrigger": {"type": "afterStep", "stepId": "check"},
                    },
                ],
            }
        ],
        "resourceConstraints": [],
    }
    workcell = {
        "id": "bench",
        "tools": [{"name": "incubator", "type": "liconic", "host": "h", "port": 2}],
    }
    tool = FakeToolClient()
    runner = ProgramRunner(program, time_scale=100.0)
    order = []
    runner.add_event_listener(
        lambda kind, data: (
            order.append((kind, data["step_id"]))
            if kind in ("step_started", "step_completed")
            else None
        )
    )
    session = attach_instruments(runner, workcell, client_factory=lambda b: tool)
    try:
        runner.start()
        runner.command_queue.put("start_program")
        assert run_until(runner, lambda: not runner.is_running)
    finally:
        session.shutdown()
    assert order == [
        ("step_started", "fetch"),
        ("step_completed", "fetch"),
        ("step_started", "check"),
        ("step_completed", "check"),
        ("step_started", "store"),
        ("step_completed", "store"),
    ]
    assert [c["command"] for c in tool.executed] == ["fetch_plate", "store_plate"]
