from __future__ import annotations

from typing import Any


class ForgeCodeAgentError(Exception):
    """Base exception for forgeCodeAgent domain errors."""


class ProviderNotSupportedError(ForgeCodeAgentError):
    """Raised when a provider id is not registered or supported."""


class ProviderExecutionError(ForgeCodeAgentError):
    """Raised when the underlying provider CLI fails to execute correctly."""

    def __init__(self, message: str, *, returncode: int | None = None, stderr: str | None = None) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class ProviderTimeoutError(ForgeCodeAgentError):
    """Raised when provider execution exceeds the configured timeout."""


class ParsingError(ForgeCodeAgentError):
    """Raised when provider output cannot be parsed into the expected format."""

    def __init__(self, message: str, *, raw_output: Any | None = None) -> None:
        super().__init__(message)
        self.raw_output = raw_output


class WorkspaceSecurityError(ForgeCodeAgentError):
    """Raised when a workspace boundary or path traversal rule is violated."""


class ToolExecutionError(ForgeCodeAgentError):
    """Raised when a registered tool fails during execution."""
