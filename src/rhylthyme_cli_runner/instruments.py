"""
Connect a ProgramRunner to galago-tools instruments (``rhylthyme run --workcell``).

Needs the optional ``rhylthyme-galago`` package (``pip install
rhylthyme[galago]``). When a step with an ``instrument`` starts, its command is
sent on a worker thread; the reply comes back through
``ProgramRunner.post_instrument_reply`` and ends (or fails) the step.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional

from .instance_checks import Finding

INSTALL_HINT = "Instrument steps need rhylthyme-galago: pip install 'rhylthyme[galago]'"


class InstrumentSetupError(RuntimeError):
    """The workcell cannot run this program's instrument steps."""


def program_uses_instruments(program: Mapping[str, Any]) -> bool:
    return any(
        step.get("instrument")
        for track in program.get("tracks", [])
        for step in track.get("steps", [])
    )


def instrument_findings(
    program: Mapping[str, Any], workcell_source=None
) -> List[Finding]:
    """
    Validation findings for a program's instrument steps: galago commands and
    params checked against each step's toolType, or against the workcell's
    tools when ``workcell_source`` (a path or dict) is given.
    """
    if workcell_source is None and not program_uses_instruments(program):
        return []
    try:
        import rhylthyme_galago as galago
    except ImportError:
        return [
            Finding(
                code="instrument_unchecked",
                message="Instrument steps were not checked",
                where="program",
                fix=INSTALL_HINT,
                severity="error" if workcell_source is not None else "warning",
            )
        ]
    workcell = None
    if workcell_source is not None:
        try:
            workcell = galago.load_workcell(workcell_source)
        except galago.WorkcellError as e:
            return [Finding(code="workcell_invalid", message=str(e), where="workcell")]
    return [
        Finding(
            code=issue.code,
            message=issue.message,
            where=f"step:{issue.step_id}",
            severity=issue.severity,
        )
        for issue in galago.check_program(program, workcell)
    ]


def _reply_dict(reply) -> Dict[str, Any]:
    return {
        "ok": reply.ok,
        "code": reply.code,
        "errorMessage": reply.error_message,
        "metadata": dict(reply.metadata),
    }


@dataclass
class InstrumentSession:
    executor: Any
    checks: List[Any]

    def report(self) -> List[str]:
        mode = "simulated" if self.executor.simulated else "LIVE"
        lines = [f"Workcell {self.executor.workcell.id!r} ({mode}):"]
        for check in self.checks:
            mark = "ok" if check.ready else "NOT READY"
            detail = check.configure.error_message or check.status.error_message
            line = f"  {check.tool} @ {check.address}: {check.status.status} [{mark}]"
            lines.append(line + (f" {detail}" if detail and not check.ready else ""))
        return lines

    def shutdown(self) -> List[str]:
        """Stop the executor; return steps whose commands were still in flight."""
        return self.executor.shutdown()


def attach_instruments(
    runner,
    workcell_source,
    *,
    client_factory: Optional[Callable] = None,
    simulated: bool = True,
) -> InstrumentSession:
    """
    Configure the workcell's tools for ``runner.program`` and wire the runner
    so each instrument step's command is sent when the step starts.

    Raises InstrumentSetupError when rhylthyme-galago is missing, the workcell
    is invalid, a step names a tool the workcell lacks, or a tool is not ready.
    """
    try:
        import rhylthyme_galago as galago
    except ImportError:
        raise InstrumentSetupError(INSTALL_HINT) from None

    try:
        workcell = galago.load_workcell(workcell_source)
    except galago.WorkcellError as e:
        raise InstrumentSetupError(str(e)) from None

    tools = galago.instrument_tools(runner.program)
    unknown = [t for t in tools if t not in workcell.tools]
    if unknown:
        raise InstrumentSetupError(
            f"Workcell {workcell.id!r} has no tool named "
            + ", ".join(repr(t) for t in unknown)
            + f" (tools: {', '.join(sorted(workcell.tools))})"
        )

    kwargs: Dict[str, Any] = {"simulated": simulated}
    if client_factory is not None:
        kwargs["client_factory"] = client_factory
    executor = galago.InstrumentExecutor(workcell, **kwargs)
    session = InstrumentSession(executor, executor.prepare(tools))
    if not all(check.ready for check in session.checks):
        executor.shutdown()
        raise InstrumentSetupError("\n".join(session.report()))

    def on_reply(step_id: str, reply) -> None:
        runner.post_instrument_reply(step_id, _reply_dict(reply))

    def on_event(event_type: str, data: Dict[str, Any]) -> None:
        if event_type != "step_started":
            return
        step = runner.steps.get(data["step_id"])
        if step is not None and step.instrument:
            executor.submit(step.step_id, step.instrument, on_reply)

    runner.add_event_listener(on_event)
    return session
