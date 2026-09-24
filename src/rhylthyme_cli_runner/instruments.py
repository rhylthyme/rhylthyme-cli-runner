"""
Connect a ProgramRunner to galago-tools instruments (``rhylthyme run --workcell``).

Needs the optional ``rhylthyme-galago`` package (``pip install
rhylthyme[galago]``). When a step with an ``instrument`` starts, its command is
sent on a worker thread; the reply comes back through
``ProgramRunner.post_instrument_reply`` and ends (or fails) the step.
"""

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


def _instrument_steps(program: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [
        step
        for track in program.get("tracks", [])
        for step in track.get("steps", [])
        if step.get("instrument")
    ]


def _params_text(params: Optional[Mapping[str, Any]]) -> str:
    return ", ".join(f"{k}={v!r}" for k, v in (params or {}).items())


class InstrumentSession:
    """
    The workcell tools one run uses. Opening it touches no instrument;
    ``summary()`` only reads tool status; ``prepare()`` configures the tools
    (simulated unless the session is live); ``attach()`` wires the runner so
    each instrument step's command is sent when the step starts.
    """

    def __init__(self, executor: Any, tools: List[str]):
        self.executor = executor
        self.tools = tools
        self.checks: List[Any] = []

    @property
    def live(self) -> bool:
        return not self.executor.simulated

    def summary(self, program: Mapping[str, Any], limit: int = 12) -> List[str]:
        """What a run will do, for the --live confirmation. Status is read-only."""
        workcell = self.executor.workcell
        mode = "LIVE: real hardware will move" if self.live else "simulated"
        lines = [f"Workcell {workcell.id!r} ({mode})", "Tools:"]
        for name in self.tools:
            binding = workcell.tool(name)
            status = self.executor.client(name).status()
            lines.append(
                f"  {name} ({binding.type}) @ {binding.address}: {status.status}"
            )
        steps = _instrument_steps(program)
        lines.append(f"Instrument steps ({len(steps)}):")
        for step in steps[:limit]:
            inst = step["instrument"]
            lines.append(
                f"  {step['stepId']}: {inst['tool']}.{inst['command']}"
                f"({_params_text(inst.get('params'))})"
            )
        if len(steps) > limit:
            lines.append(f"  ... and {len(steps) - limit} more")
        return lines

    def prepare(self) -> None:
        """Configure every tool; raise InstrumentSetupError unless all are ready."""
        self.checks = self.executor.prepare(self.tools)
        if not all(check.ready for check in self.checks):
            raise InstrumentSetupError("\n".join(self.report()))

    def report(self) -> List[str]:
        mode = "simulated" if self.executor.simulated else "LIVE"
        lines = [f"Workcell {self.executor.workcell.id!r} ({mode}):"]
        for check in self.checks:
            mark = "ok" if check.ready else "NOT READY"
            detail = check.configure.error_message or check.status.error_message
            line = f"  {check.tool} @ {check.address}: {check.status.status} [{mark}]"
            lines.append(line + (f" {detail}" if detail and not check.ready else ""))
        return lines

    def attach(self, runner) -> None:
        executor = self.executor

        def on_reply(step_id: str, reply) -> None:
            runner.post_instrument_reply(step_id, _reply_dict(reply))

        def on_event(event_type: str, data: Dict[str, Any]) -> None:
            # A step's command goes out when it starts and again on each retry
            if event_type not in ("step_started", "step_retry"):
                return
            step = runner.steps.get(data["step_id"])
            if step is not None and step.instrument:
                step.instrument_attempts += 1
                executor.submit(step.step_id, step.instrument, on_reply)

        runner.add_event_listener(on_event)

    def shutdown(self) -> List[str]:
        """Stop the executor; return steps whose commands were still in flight."""
        return self.executor.shutdown()


def open_instruments(
    program: Mapping[str, Any],
    workcell_source,
    *,
    client_factory: Optional[Callable] = None,
    live: bool = False,
) -> InstrumentSession:
    """
    Load the workcell for ``program`` without contacting any tool.

    Tools run simulated unless ``live`` is true. Raises InstrumentSetupError
    when rhylthyme-galago is missing, the workcell is invalid, or a step
    names a tool the workcell lacks.
    """
    try:
        import rhylthyme_galago as galago
    except ImportError:
        raise InstrumentSetupError(INSTALL_HINT) from None

    try:
        workcell = galago.load_workcell(workcell_source)
    except galago.WorkcellError as e:
        raise InstrumentSetupError(str(e)) from None

    tools = galago.instrument_tools(program)
    unknown = [t for t in tools if t not in workcell.tools]
    if unknown:
        raise InstrumentSetupError(
            f"Workcell {workcell.id!r} has no tool named "
            + ", ".join(repr(t) for t in unknown)
            + f" (tools: {', '.join(sorted(workcell.tools))})"
        )

    kwargs: Dict[str, Any] = {"simulated": not live}
    if client_factory is not None:
        kwargs["client_factory"] = client_factory
    return InstrumentSession(galago.InstrumentExecutor(workcell, **kwargs), tools)


def attach_instruments(
    runner,
    workcell_source,
    *,
    client_factory: Optional[Callable] = None,
    live: bool = False,
) -> InstrumentSession:
    """
    Open, configure and attach in one go (no confirmation step): the tools
    are configured and ``runner`` sends each instrument step's command when
    the step starts.
    """
    session = open_instruments(
        runner.program, workcell_source, client_factory=client_factory, live=live
    )
    try:
        session.prepare()
    except InstrumentSetupError:
        session.shutdown()
        raise
    session.attach(runner)
    return session
