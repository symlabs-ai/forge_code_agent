from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:
    # Integração explícita com ForgeBase quando disponível
    from forgebase.domain import EntityBase  # type: ignore
except Exception:  # pragma: no cover - fallback para ambientes sem forgebase
    class EntityBase:  # type: ignore
        """Fallback mínimo quando forgebase não está instalado."""

        pass


ProviderStatus = Literal["success", "error", "partial"]


@dataclass
class ExecutionRequest(EntityBase):
    provider: str
    prompt: str
    mode: Literal["run", "stream"]
    timeout: float | None = None
    workdir: Path | None = None
    options: dict[str, Any] = field(default_factory=dict)

    # Hook exigido por EntityBase do ForgeBase; para o MVP
    # utilizamos uma validação mínima/no-op.
    def validate(self) -> None:  # type: ignore[override]
        return None


@dataclass
class ExecutionResult(EntityBase):
    status: ProviderStatus
    provider: str
    content: str | None = None
    raw_events: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:  # type: ignore[override]
        return None
