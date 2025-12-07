from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MCPServerHandle:
    """
    Representa um servidor MCP associado a um workspace.

    Fase 1: não iniciamos processos automaticamente; o handle é usado apenas
    para reservar contrato e metadata. Na Fase 2, este módulo passa a cuidar
    do ciclo de vida real do servidor.
    """

    workdir: Path
    endpoint: str | None = None
    started: bool = False


def ensure_mcp_server(workdir: Path) -> MCPServerHandle:
    """
    Garantir a existência de um servidor MCP associado ao `workdir`.

    Fase 1:
        - Não inicia processos nem faz IPC real.
        - Apenas normaliza o caminho e devolve um handle estável que pode ser
          armazenado em metadata/logs.

    Fase 2:
        - Passará a iniciar (ou reaproveitar) um servidor real em background
          e preencher `endpoint`/`started` apropriadamente.
    """
    normalized = workdir.resolve()
    return MCPServerHandle(workdir=normalized, endpoint=None, started=False)
