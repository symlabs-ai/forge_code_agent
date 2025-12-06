from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from forge_code_agent.domain.errors import ProviderTimeoutError
from forge_code_agent.domain.models import ExecutionRequest, ExecutionResult


class ProviderAdapter(Protocol):
    """Abstração de provider de código baseado em CLI."""

    id: str

    def run(self, request: ExecutionRequest) -> ExecutionResult: ...

    def stream(self, request: ExecutionRequest) -> Iterable[dict]: ...


@dataclass
class CliExecutor:
    """
    Executor fino sobre subprocess, responsável por lidar com timeouts
    e mapeamento básico de erros de execução de CLI.
    """

    def run(
        self,
        cmd: list[str],
        timeout: float | None,
        cwd: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderTimeoutError("Provider execution exceeded configured timeout") from exc
