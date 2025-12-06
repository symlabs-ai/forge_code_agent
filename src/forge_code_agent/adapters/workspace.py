from __future__ import annotations

from pathlib import Path

from forge_code_agent.domain.errors import WorkspaceSecurityError


class FilesystemWorkspaceAdapter:
    """Filesystem-bound workspace adapter with path traversal protection."""

    def __init__(self, workdir: Path) -> None:
        # Normalizamos o diretório de trabalho uma vez; ele pode ainda não existir fisicamente.
        self.workdir = workdir.resolve()

    def ensure_within_workspace(self, target: Path) -> None:
        """
        Garantir que o caminho alvo esteja contido dentro do workspace.

        Levanta WorkspaceSecurityError em caso de path traversal ou acesso fora da raiz configurada.
        """
        target_resolved = target.resolve()

        try:
            target_resolved.relative_to(self.workdir)
        except ValueError as exc:
            raise WorkspaceSecurityError(
                f"Path traversal detected: '{target_resolved}' is outside workspace '{self.workdir}'"
            ) from exc

    def write_file(self, relative_path: str, content: str) -> Path:
        """
        Escrever um arquivo dentro do workspace, garantindo os limites de segurança.

        `relative_path` é sempre tratado como relativo ao diretório de trabalho configurado.
        """
        target = (self.workdir / relative_path).resolve()
        self.ensure_within_workspace(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target
