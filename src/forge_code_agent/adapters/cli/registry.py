from __future__ import annotations

from forge_code_agent.adapters.cli.base import ProviderAdapter
from forge_code_agent.adapters.cli.claude import ClaudeProviderAdapter
from forge_code_agent.adapters.cli.codex import CodexProviderAdapter
from forge_code_agent.adapters.cli.gemini import GeminiProviderAdapter

_REGISTRY: dict[str, ProviderAdapter] = {
    "codex": CodexProviderAdapter(),
    "claude": ClaudeProviderAdapter(),
    "gemini": GeminiProviderAdapter(),
}


def get_provider_adapter(provider_id: str) -> ProviderAdapter | None:
    """Obter adapter de provider registrado, se existir."""
    return _REGISTRY.get(provider_id)
