"""
``rhylthyme bridge --workcell lab.json`` with no program: wait for runs started
from rhylthyme.com (the web bridge, slice 3; design: rhylthyme-galago
docs/design/web-bridge.md).

The bridge stays listed as online on the Bridges page. A ``start_run`` command
names a program saved in the user's own library; this machine loads it,
checks it against the local workcell and refuses it unless it is safe to run
here, then runs it exactly as ``rhylthyme bridge PROGRAM`` would, and goes
back to waiting when the run completes or is aborted. Only simulated runs can
be started from the web for now.
"""

import json
import queue
import re
import sys
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from .instruments import INSTALL_HINT, InstrumentSetupError

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

Outcome = Dict[str, Any]


def _no(reason: str) -> Outcome:
    return {"accepted": False, "reason": reason}


def _has_code_blocks(program: Mapping[str, Any]) -> bool:
    for group in ("tracks", "trackTemplates"):
        for track in program.get(group) or []:
            for step in track.get("steps") or []:
                if isinstance(step, Mapping) and step.get("codeBlock"):
                    return True
    return False


def check_start(
    args: Mapping[str, Any],
    fetch_program: Callable[[str], Optional[Mapping[str, Any]]],
    workcell_source: Any,
    schema: Mapping[str, Any],
) -> Tuple[Outcome, Optional[Dict[str, Any]]]:
    """
    Decide whether a ``start_run`` may run here. Returns (outcome, program):
    the program when accepted, None otherwise.
    """
    from .validate_program import perform_additional_validations, validate_program

    mode = args.get("mode") or "simulated"
    if mode != "simulated":
        return _no("only simulated runs can be started from the web for now"), None
    program_id = str(args.get("program_id") or "")
    if not UUID_RE.match(program_id):
        return _no("program_id must be the id of a program in your library"), None
    row = fetch_program(program_id)
    if not row or not isinstance(row.get("program_json"), dict):
        return _no("no such program in your library"), None
    program = json.loads(json.dumps(row["program_json"]))
    if _has_code_blocks(program):
        return _no("programs with code blocks cannot be started from the web"), None
    is_valid, schema_errors = validate_program(program, dict(schema))
    errors = list(schema_errors) + perform_additional_validations(
        program, workcell=workcell_source
    )
    if not is_valid or errors:
        shown = "; ".join(str(e) for e in errors[:3])
        more = f" (+{len(errors) - 3} more)" if len(errors) > 3 else ""
        return _no(f"the program is not valid on this workcell: {shown}{more}"), None
    return {"accepted": True, "reason": ""}, program


def serve(
    workcell_source: Any,
    *,
    schema_file: str,
    time_scale: float = 1.0,
    record: bool = True,
    rest=None,
    token_fn: Optional[Callable[[], str]] = None,
    config_path=None,
    run: Optional[Callable[..., Any]] = None,
    max_runs: Optional[int] = None,
    out=None,
) -> int:
    """Wait for runs from the web until Ctrl-C (or ``max_runs``). Returns runs started."""
    out = out or sys.stdout
    try:
        import rhylthyme_galago as galago
        from rhylthyme_galago import bridge as B
    except ImportError:
        raise InstrumentSetupError(INSTALL_HINT) from None

    from .remote import auth
    from .validate_program import load_program_file

    if run is None:
        from .program_runner import run_program

        run = run_program
    run_fn: Callable[..., Any] = run

    try:
        workcell = galago.load_workcell(workcell_source)
    except galago.WorkcellError as e:
        raise InstrumentSetupError(str(e)) from None
    try:
        if rest is None or token_fn is None:
            creds = auth.load_credentials() or {}
            if not creds.get("supabase_url"):
                raise InstrumentSetupError(
                    "rhylthyme bridge needs you signed in: run `rhylthyme login`."
                )
            token_fn = token_fn or auth.access_token
            rest = rest or B.SupabaseRest(
                creds["supabase_url"], creds["supabase_anon_key"], token_fn
            )
        user_id = B.user_id_from_token(token_fn())
    except (auth.AuthError, B.BridgeError) as e:
        raise InstrumentSetupError(str(e)) from None

    bridge_id = B.bridge_id_for(
        workcell, config_path or (auth.config_dir() / "bridges.json")
    )
    schema = load_program_file(schema_file)
    tools: List[Dict[str, str]] = [
        {"name": t.name, "type": t.type, "status": "idle"}
        for t in workcell.tools.values()
    ]
    starts: "queue.Queue[Tuple[Dict[str, Any], str]]" = queue.Queue()

    def fetch_program(program_id: str) -> Optional[Mapping[str, Any]]:
        rows = rest.select(
            "programs",
            f"id=eq.{program_id}&user_id=eq.{user_id}&select=id,name,program_json",
        )
        return rows[0] if rows else None

    def submit(command: Dict[str, Any]) -> Outcome:
        if not starts.empty():
            return _no("a run is already starting")
        try:
            outcome, program = check_start(
                command.get("args") or {}, fetch_program, workcell_source, schema
            )
        except B.BridgeError as e:
            return _no(f"could not load the program: {e}")
        if outcome["accepted"] and program is not None:
            starts.put((program, command["args"]["program_id"]))
            print(
                f"Starting {program.get('name')!r} from the web (simulated).",
                file=out,
            )
        else:
            print(f"Refused a run from the web: {outcome['reason']}", file=out)
        return outcome

    runs = 0
    while max_runs is None or runs < max_runs:
        idle = B.Publisher(
            None,
            rest=rest,
            bridge_id=bridge_id,
            user_id=user_id,
            workcell=workcell,
            tools=tools,
            allows_live=False,
            version=getattr(galago, "__version__", ""),
            on_error=lambda message: print(f"Bridge: {message}", file=out),
            submit=submit,
        )
        try:
            idle.start()
        except B.BridgeError as e:
            raise InstrumentSetupError(
                f"Could not publish to rhylthyme.com: {e}"
            ) from None
        print(
            f"Bridge {workcell.name!r} is waiting for runs from rhylthyme.com "
            "(Bridges page). Ctrl-C stops it.",
            file=out,
        )
        try:
            while True:
                try:
                    program, program_id = starts.get(timeout=0.5)
                    break
                except queue.Empty:
                    continue
        finally:
            idle.stop()
        try:
            run_fn(
                None,
                schema_file,
                time_scale,
                False,  # validated in check_start
                # auto_start=False: the clock runs as soon as the runner opens.
                # (auto_start=True honours a program's manual start trigger and
                # would wait for someone to press 's' at the lab machine.)
                False,
                None,
                record=record,
                factor_prompt=False,
                workcell=workcell_source,
                bridge=True,
                program_data=program,
                program_id=program_id,
                exit_when_done=True,
            )
        except SystemExit:
            print("The run could not start; waiting for the next one.", file=out)
        runs += 1
    return runs
