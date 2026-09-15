"""Model clients for the live evaluation harness.

Three things live here:

* :class:`Client` -- the protocol the harness talks to. One method,
  :meth:`Client.complete`, taking a message list and returning a
  :class:`Completion` (text plus token counts).
* :class:`AnthropicClient` -- the real thing, wrapping the Anthropic SDK's
  Messages API. The SDK is imported lazily so the scorer and the tests
  never need it installed.
* :class:`FakeClient` -- canned responses for tests, keyed either by a
  substring of the last user message or served in sequence.

Plus a small price table so runs can log an estimated cost.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Union

Message = Dict[str, Any]

# Prices in USD per million tokens (input, output) for the first-party
# Anthropic API, as listed by the claude-api skill on 2026-06-24. Lookup
# strips any date suffix ("claude-haiku-4-5-20251001" -> "claude-haiku-4-5")
# and then falls back to the longest matching prefix, so a new snapshot of
# a known family still gets a price.
PRICE_TABLE_DATE = "2026-06-24"
PRICES_PER_MTOK: Dict[str, tuple] = {
    "claude-fable-5-1": (10.00, 50.00),
    "claude-fable-5": (10.00, 50.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}


def price_for(model: str) -> Optional[tuple]:
    """``(input, output)`` USD per million tokens, or ``None`` if unknown."""
    if model in PRICES_PER_MTOK:
        return PRICES_PER_MTOK[model]
    best = None
    for key in PRICES_PER_MTOK:
        if model.startswith(key) and (best is None or len(key) > len(best)):
            best = key
    return PRICES_PER_MTOK[best] if best else None


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """Estimated USD for one call; ``None`` when the model is not priced."""
    price = price_for(model)
    if price is None:
        return None
    return (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000


@dataclass
class Completion:
    """What a model call returns, reduced to what the harness needs."""

    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    stop_reason: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "raw": self.raw,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Completion":
        return cls(
            text=str(data.get("text", "")),
            input_tokens=int(data.get("input_tokens", 0) or 0),
            output_tokens=int(data.get("output_tokens", 0) or 0),
            model=str(data.get("model", "")),
            stop_reason=data.get("stop_reason"),
            raw=dict(data.get("raw") or {}),
        )


class Client(Protocol):
    """Anything that can turn a message list into a :class:`Completion`."""

    def complete(
        self,
        messages: Sequence[Message],
        *,
        system: Optional[str] = None,
        model: str,
        max_tokens: int,
    ) -> Completion:  # pragma: no cover - protocol
        ...


class AnthropicClient:
    """Messages API client. Imports the SDK on first use."""

    def __init__(self, api_key: Optional[str] = None, **client_kwargs: Any):
        self._api_key = api_key
        self._client_kwargs = client_kwargs
        self._client = None
        self._lock = threading.Lock()

    def _get(self):
        with self._lock:
            if self._client is None:
                try:
                    import anthropic
                except ImportError as exc:  # pragma: no cover - environment
                    raise RuntimeError(
                        "The anthropic package is required for live eval runs: "
                        "pip install anthropic"
                    ) from exc
                kwargs = dict(self._client_kwargs)
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = anthropic.Anthropic(**kwargs)
            return self._client

    def complete(
        self,
        messages: Sequence[Message],
        *,
        system: Optional[str] = None,
        model: str,
        max_tokens: int,
    ) -> Completion:
        client = self._get()
        kwargs: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": list(messages),
        }
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        text = "".join(block.text for block in response.content if block.type == "text")
        usage = getattr(response, "usage", None)
        try:
            raw = response.to_dict()
        except Exception:  # noqa: BLE001 - raw is best-effort
            raw = {}
        return Completion(
            text=text,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
            model=str(getattr(response, "model", model)),
            stop_reason=getattr(response, "stop_reason", None),
            raw=raw,
        )


CannedResponse = Union[str, Completion]


@dataclass
class FakeCall:
    messages: List[Message]
    system: Optional[str]
    model: str
    max_tokens: int


class FakeClient:
    """Canned responses for tests.

    ``responses`` is either a sequence (served in order, the last one
    repeating) or a mapping from a substring to a response; the first key
    found in the last user message wins, with ``"*"`` as the fallback.
    Every call is recorded in :attr:`calls`.
    """

    def __init__(
        self,
        responses: Union[Sequence[CannedResponse], Mapping[str, CannedResponse]],
        *,
        input_tokens: int = 100,
        output_tokens: int = 50,
    ):
        self._responses = responses
        self._input_tokens = input_tokens
        self._output_tokens = output_tokens
        self.calls: List[FakeCall] = []
        self._lock = threading.Lock()

    @staticmethod
    def last_user_text(messages: Sequence[Message]) -> str:
        for message in reversed(list(messages)):
            if message.get("role") == "user":
                content = message.get("content")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    return "\n".join(
                        str(block.get("text", ""))
                        for block in content
                        if isinstance(block, dict)
                    )
        return ""

    def _pick(self, messages: Sequence[Message], index: int) -> CannedResponse:
        if isinstance(self._responses, Mapping):
            text = self.last_user_text(messages)
            for key, value in self._responses.items():
                if key != "*" and key in text:
                    return value
            if "*" in self._responses:
                return self._responses["*"]
            raise KeyError(
                "FakeClient has no canned response for message: " + text[:120]
            )
        sequence = list(self._responses)
        if not sequence:
            raise IndexError("FakeClient has no canned responses")
        return sequence[min(index, len(sequence) - 1)]

    def complete(
        self,
        messages: Sequence[Message],
        *,
        system: Optional[str] = None,
        model: str,
        max_tokens: int,
    ) -> Completion:
        with self._lock:
            index = len(self.calls)
            self.calls.append(FakeCall(list(messages), system, model, max_tokens))
        chosen = self._pick(messages, index)
        if isinstance(chosen, Completion):
            return chosen
        return Completion(
            text=str(chosen),
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
            model=model,
            stop_reason="end_turn",
        )


def make_client(fake_responses: Optional[Any] = None) -> Client:
    """Build the client the CLI uses: a fake when canned responses are given."""
    if fake_responses is not None:
        return FakeClient(fake_responses)
    return AnthropicClient()
