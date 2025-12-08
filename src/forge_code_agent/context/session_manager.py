from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from forge_code_agent.context.summarizer import Summarizer
from forge_code_agent.domain.models import ExecutionResult


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class ContextEvent:
    role: str
    text: str
    provider: str
    timestamp: str
    meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "text": self.text,
            "provider": self.provider,
            "timestamp": self.timestamp,
            "meta": self.meta,
        }


@dataclass
class ContextSummary:
    at_index: int
    text: str
    provider: str
    timestamp: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "at_index": self.at_index,
            "text": self.text,
            "provider": self.provider,
            "timestamp": self.timestamp,
        }


@dataclass
class ContextSessionManager:
    """
    Gerencia o contexto de uma sessão de CodeAgent.

    Responsável por armazenar o histórico de interações (prompts, respostas,
    eventos canônicos) e por persistir esse contexto em disco para reuso.

    Nesta fase, o summarizer ainda não é aplicado; apenas preparamos a
    estrutura de eventos/summaries e a persistência básica em JSON.
    """

    session_id: str
    logs_dir: Path
    max_events: int = 200
    # Limite aproximado de caracteres para o contexto antes de resumir.
    # Em vez de tokens, usamos chars como proxy simples da janela de contexto
    # dos modelos (tipicamente 128k–256k tokens).
    max_summary_chars: int = 128_000
    current_provider: str | None = None
    workdir: Path | None = None
    created_at: str = field(default_factory=_utc_now_iso)
    events: list[ContextEvent] = field(default_factory=list)
    summaries: list[ContextSummary] = field(default_factory=list)

    def _base_dir(self) -> Path:
        path = self.logs_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def record_interaction(self, prompt: str, result: ExecutionResult) -> None:
        """
        Registrar uma interação completa no contexto.

        - prompt do usuário;
        - resposta final do provider;
        - eventos canônicos (quando disponíveis).
        """
        provider = result.provider
        timestamp = _utc_now_iso()

        user_event = ContextEvent(
            role="user",
            text=prompt,
            provider=provider,
            timestamp=timestamp,
            meta={},
        )
        self.events.append(user_event)

        if result.content is not None:
            assistant_event = ContextEvent(
                role="assistant",
                text=result.content,
                provider=provider,
                timestamp=_utc_now_iso(),
                meta={"status": result.status},
            )
            self.events.append(assistant_event)

        # Eventos canônicos (reasoning/messages/logs) são anexados como meta.
        for raw in result.raw_events:
            kind = raw.get("kind", "log")
            text = raw.get("text") or ""
            if not text:
                continue
            event = ContextEvent(
                role="assistant" if kind in {"reasoning", "message"} else "system",
                text=text,
                provider=provider,
                timestamp=_utc_now_iso(),
                meta={"kind": kind, "raw": raw},
            )
            self.events.append(event)

        # Atualiza provider/workdir correntes se ainda não definidos.
        if self.current_provider is None:
            self.current_provider = provider
        if self.workdir is None and isinstance(result.metadata.get("workdir"), str):
            self.workdir = Path(result.metadata["workdir"])

    def get_context(self) -> list[dict[str, Any]]:
        """
        Exportar o contexto atual como lista de dicts simples.
        """
        return [ev.as_dict() for ev in self.events]

    def summarize_if_needed(self, summarizer: Summarizer | None = None) -> None:
        """
        Aplicar resumo do contexto quando limites forem excedidos.

        Regras atuais (simples, podem evoluir):
        - se não houver summarizer, nada é feito;
        - se o número de eventos for menor ou igual a max_events, nada é feito;
        - caso contrário, gera um resumo dos eventos atuais, registra em
          `summaries` e mantém apenas a metade mais recente dos eventos.

        O objetivo desta fase é apenas preparar o fluxo de resumo de forma
        segura; políticas mais sofisticadas podem ser adicionadas em sprints
        futuras.
        """
        if summarizer is None:
            return

        total_events = len(self.events)
        total_chars = sum(len(ev.text) for ev in self.events)

        # Apenas aplica resumo se ultrapassar pelo menos um dos limites:
        # - número de eventos, ou
        # - tamanho aproximado em caracteres.
        if total_events <= self.max_events and total_chars <= self.max_summary_chars:
            return

        # Converte eventos para dicts simples e delega ao summarizer.
        messages = [ev.as_dict() for ev in self.events]
        summary_text = summarizer.summarize(messages)

        if not summary_text:
            return

        total_events = len(self.events)
        summary = ContextSummary(
            at_index=total_events,
            text=summary_text,
            provider=self.current_provider or "unknown",
            timestamp=_utc_now_iso(),
        )
        self.summaries.append(summary)

        # Estratégia simples: manter apenas os últimos max_events eventos.
        if total_events > self.max_events:
            self.events = self.events[-self.max_events :]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_provider": self.current_provider,
            "workdir": str(self.workdir) if self.workdir is not None else None,
            "created_at": self.created_at,
            "events": [ev.as_dict() for ev in self.events],
            "summaries": [s.as_dict() for s in self.summaries],
            "max_events": self.max_events,
            "max_summary_chars": self.max_summary_chars,
        }

    def save(self) -> Path:
        """
        Persistir o snapshot da sessão em logs/codeagent.
        """
        import json

        base = self._base_dir()
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"session_{self.session_id}_{timestamp}.json"
        path = base / filename
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> ContextSessionManager:
        """
        Recarregar uma sessão previamente salva.
        """
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        session_id = data.get("session_id") or path.stem
        logs_dir = path.parent
        mgr = cls(
            session_id=session_id,
            logs_dir=logs_dir,
            max_events=data.get("max_events", 200),
            max_summary_chars=data.get("max_summary_chars", 8000),
            current_provider=data.get("current_provider"),
            workdir=Path(data["workdir"]) if data.get("workdir") else None,
            created_at=data.get("created_at", _utc_now_iso()),
        )

        for ev_data in data.get("events", []):
            mgr.events.append(
                ContextEvent(
                    role=ev_data.get("role", "assistant"),
                    text=ev_data.get("text", ""),
                    provider=ev_data.get("provider", ""),
                    timestamp=ev_data.get("timestamp", _utc_now_iso()),
                    meta=ev_data.get("meta") or {},
                )
            )

        for s_data in data.get("summaries", []):
            mgr.summaries.append(
                ContextSummary(
                    at_index=int(s_data.get("at_index", 0)),
                    text=s_data.get("text", ""),
                    provider=s_data.get("provider", ""),
                    timestamp=s_data.get("timestamp", _utc_now_iso()),
                )
            )

        return mgr
