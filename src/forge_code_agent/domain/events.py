from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentEvent:
    """
    Canonical representation of a single event emitted by a provider.

    - kind: semantic category (reasoning, message, tool, log, raw).
    - role: conversational role when aplicable (assistant, user, tool, system).
    - text: human-readable text associated with the event, when available.
    - provider: provider identifier (codex, claude, gemini, dummy, etc.).
    - raw: raw payload (JSON/dict/string) used for debug/auditoria.
    """

    kind: str
    role: str
    text: str
    provider: str
    raw: Any

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "role": self.role,
            "text": self.text,
            "provider": self.provider,
            "raw": self.raw,
        }


def _event(
    *,
    kind: str,
    role: str,
    text: str,
    provider: str,
    raw: Any,
) -> AgentEvent:
    return AgentEvent(kind=kind, role=role, text=text, provider=provider, raw=raw)


def normalize_stream_line(provider: str, line: str) -> list[dict[str, Any]]:
    """
    Map a single stdout line from a provider CLI into one or more canonical AgentEvents.

    The function is intentionally conservative: whenever it cannot confidently
    classify the payload, it produces a single `raw` event preserving the
    original content so nothing é perdido para debug.
    """
    stripped = line.rstrip("\n")
    if not stripped:
        return []

    # Best-effort JSON parse; se falhar, tratamos como texto cru.
    try:
        data = json.loads(stripped)
    except Exception:
        ev = _event(
            kind="raw",
            role="assistant",
            text=stripped,
            provider=provider,
            raw=stripped,
        )
        return [ev.as_dict()]

    # Provider-agnostic fallback: estrutura com item {type, text}.
    def _from_item_dict(item: dict[str, Any]) -> list[dict[str, Any]]:
        item_type = item.get("type")
        text = item.get("text")
        if not isinstance(text, str):
            raw_ev = _event(
                kind="raw",
                role="assistant",
                text="",
                provider=provider,
                raw=data,
            )
            return [raw_ev.as_dict()]

        if item_type == "reasoning":
            kind = "reasoning"
        elif item_type in {"agent_message", "message"}:
            kind = "message"
        else:
            kind = "log"

        ev = _event(kind=kind, role="assistant", text=text, provider=provider, raw=data)
        return [ev.as_dict()]

    # Provider-specific mapeamentos.
    if provider in {"codex", "dummy"}:
        # Codex (e Dummy nos testes) usam um envelope com "item".
        item = data.get("item") or data.get("payload")
        if isinstance(item, dict):
            return _from_item_dict(item)

        # Eventos de alto nível (thread.started, turn.started, etc.) caem como logs.
        ev = _event(
            kind="log",
            role="system",
            text=str(data.get("type", "")),
            provider=provider,
            raw=data,
        )
        return [ev.as_dict()]

    if provider == "claude":
        ev_type = data.get("type")
        if ev_type == "assistant":
            msg = data.get("message") or {}
            role = msg.get("role") or "assistant"
            content_blocks = msg.get("content") or []
            texts: list[str] = []
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    txt = block.get("text")
                    if isinstance(txt, str):
                        texts.append(txt)
            if texts:
                ev = _event(
                    kind="message",
                    role=role,
                    text="\n".join(texts),
                    provider=provider,
                    raw=data,
                )
                return [ev.as_dict()]

        # Outros tipos (system, user, result, tool_use, etc.) ficam como logs/raw.
        ev = _event(
            kind="log",
            role="system",
            text=str(data.get("type", "")),
            provider=provider,
            raw=data,
        )
        return [ev.as_dict()]

    if provider == "gemini":
        ev_type = data.get("type")
        if ev_type == "message":
            role = data.get("role") or "assistant"
            text = data.get("content")
            if isinstance(text, str):
                ev = _event(
                    kind="message",
                    role=role,
                    text=text,
                    provider=provider,
                    raw=data,
                )
                return [ev.as_dict()]

        # tool_use, tool_result, init, result etc. → log/raw.
        ev = _event(
            kind="log",
            role="system",
            text=str(data.get("type", "")),
            provider=provider,
            raw=data,
        )
        return [ev.as_dict()]

    # Fallback para providers desconhecidos: apenas encapsula o JSON como raw.
    ev = _event(
        kind="raw",
        role="assistant",
        text="",
        provider=provider,
        raw=data,
    )
    return [ev.as_dict()]
