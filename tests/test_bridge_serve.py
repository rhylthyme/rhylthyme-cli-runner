"""rhylthyme bridge with no program: runs started from the web (slice 3)."""

import copy
import datetime
import io
import json

import pytest

pytestmark = pytest.mark.unit

pytest.importorskip("rhylthyme_galago")

from rhylthyme_cli_runner.bridge_serve import check_start, serve  # noqa: E402
from rhylthyme_cli_runner.cli import _default_schema_path  # noqa: E402
from rhylthyme_cli_runner.validate_program import load_program_file  # noqa: E402

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
            ],
        }
    ],
    "resourceConstraints": [],
}
WORKCELL = {
    "id": "bench",
    "tools": [{"name": "shaker", "type": "bioshake", "host": "h", "port": 1}],
}


def _jwt(sub):
    import base64

    body = (
        base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).decode().rstrip("=")
    )
    return f"h.{body}.s"


PID = "11111111-2222-3333-4444-555555555555"
SCHEMA = load_program_file(_default_schema_path())


def fetch(program):
    return lambda pid: {"id": pid, "program_json": program} if pid == PID else None


def test_a_valid_saved_program_is_accepted():
    outcome, program = check_start(
        {"program_id": PID}, fetch(PROGRAM), WORKCELL, SCHEMA
    )
    assert outcome == {"accepted": True, "reason": ""}
    assert program == PROGRAM and program is not PROGRAM


@pytest.mark.parametrize(
    "args, program, reason",
    [
        (
            {"program_id": PID, "mode": "live"},
            PROGRAM,
            "only simulated runs can be started from the web for now",
        ),
        (
            {"program_id": "../etc"},
            PROGRAM,
            "program_id must be the id of a program in your library",
        ),
        (
            {"program_id": "99999999-2222-3333-4444-555555555555"},
            PROGRAM,
            "no such program in your library",
        ),
    ],
)
def test_refusals(args, program, reason):
    outcome, got = check_start(args, fetch(program), WORKCELL, SCHEMA)
    assert (outcome["accepted"], outcome["reason"], got) == (False, reason, None)


def test_code_blocks_are_never_started_from_the_web():
    program = copy.deepcopy(PROGRAM)
    program["tracks"][0]["steps"][0]["codeBlock"] = {
        "type": "shell",
        "code": "rm -rf ~",
    }
    outcome, _ = check_start({"program_id": PID}, fetch(program), WORKCELL, SCHEMA)
    assert (
        outcome["reason"] == "programs with code blocks cannot be started from the web"
    )


def test_a_program_that_does_not_fit_the_workcell_is_refused():
    program = copy.deepcopy(PROGRAM)
    program["tracks"][0]["steps"][1]["instrument"]["tool"] = "reader"
    outcome, _ = check_start({"program_id": PID}, fetch(program), WORKCELL, SCHEMA)
    assert outcome["reason"].startswith("the program is not valid on this workcell:")
    assert "no tool 'reader'" in outcome["reason"]


class Rest:
    def __init__(self, commands):
        self.commands = commands
        self.rows = []

    def select(self, table, query):
        if table == "bridge_commands":
            rows, self.commands = self.commands, []
            return rows
        if table == "programs":
            assert f"id=eq.{PID}" in query and "user_id=eq.user-9" in query
            return [{"id": PID, "name": PROGRAM["name"], "program_json": PROGRAM}]
        return []

    def upsert(self, table, row, on_conflict):
        self.rows.append((table, json.loads(json.dumps(row))))

    def patch(self, table, match, row):
        self.rows.append((table, dict(row, match=match)))


def test_serve_waits_starts_the_run_and_answers(tmp_path):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rest = Rest(
        [
            {
                "id": "c1",
                "bridge_id": None,
                "user_id": "user-9",
                "kind": "start_run",
                "args": {"program_id": PID, "mode": "simulated"},
                "status": "pending",
                "created_at": now,
            }
        ]
    )
    runs = []
    out = io.StringIO()
    started = serve(
        WORKCELL,
        schema_file=_default_schema_path(),
        rest=rest,
        token_fn=lambda: _jwt("user-9"),
        config_path=tmp_path / "b.json",
        run=lambda *a, **k: runs.append((a, k)),
        max_runs=1,
        out=out,
    )
    assert started == 1
    [(args, kw)] = runs
    # Positional (file, schema, time_scale, validate, auto_start, environment):
    # a web-started run must not wait for someone to press 's'.
    assert args[4] is False
    assert kw["program_data"] == PROGRAM and kw["program_id"] == PID
    assert kw["bridge"] and kw["exit_when_done"] and kw["workcell"] == WORKCELL
    tables = [t for t, _ in rest.rows]
    assert (
        tables[0] == "bridges" and "bridge_state" not in tables
    )  # idle: heartbeat only
    answered = [row for t, row in rest.rows if t == "bridge_commands"]
    assert (
        answered[0]["status"] == "done"
        and answered[0]["match"] == "id=eq.c1&status=eq.pending"
    )
    assert "Starting 'Shake a plate' from the web (simulated)." in out.getvalue()
