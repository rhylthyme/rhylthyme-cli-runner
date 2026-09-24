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
