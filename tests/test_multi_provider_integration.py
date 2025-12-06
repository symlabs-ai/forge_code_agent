import os
from pathlib import Path

import pytest

from forge_code_agent.runtime.agent import CodeAgent


@pytest.fixture
def workdir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.mark.parametrize("provider", ["codex", "claude", "gemini"])
def test_code_agent_from_env_uses_configured_provider(monkeypatch: pytest.MonkeyPatch, workdir: Path, provider: str):
    monkeypatch.setenv("FORGE_CODE_AGENT_PROVIDER", provider)

    agent = CodeAgent.from_env(workdir=workdir)
    result = agent.run(f"print('hello from {provider}')")

    assert result.provider == provider
    assert isinstance(result.content, str)
    assert provider in result.content
