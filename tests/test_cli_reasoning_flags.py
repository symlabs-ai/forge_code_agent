from __future__ import annotations

import json
from pathlib import Path

from forge_code_agent.cli import main as cli_main


class DummyAgent:
    """
    Agente mínimo usado para testar flags de reasoning da CLI.
    """

    def __init__(self, provider: str, workdir: Path, **_: object) -> None:
        self.provider = provider
        self.workdir = workdir

    @classmethod
    def from_env(cls, workdir: Path, **kwargs: object) -> DummyAgent:  # pragma: no cover - não usado nos testes
        return cls(provider="dummy", workdir=workdir, **kwargs)

    def run(self, prompt: str, timeout: float | None = None, **options: object):  # pragma: no cover
        raise NotImplementedError("DummyAgent.run not used in reasoning tests")

    def stream(self, prompt: str, timeout: float | None = None, **options: object):
        # Simula uma sequência de eventos JSONL similares aos retornados por providers reais.
        events: list[dict] = [
            {
                "item": {
                    "type": "reasoning",
                    "text": "step 1: analyze request",
                }
            },
            {
                "item": {
                    "type": "agent_message",
                    "text": "final answer for prompt",
                }
            },
            # Linha não JSON para testar fallback.
            "RAW LINE\n",
        ]
        for ev in events:
            if isinstance(ev, str):
                yield {"content": ev, "end": False}
            else:
                yield {"content": json.dumps(ev), "end": False}
        yield {"content": "", "end": True}


def _monkeypatch_dummy_agent(monkeypatch):
    # Substitui CodeAgent no módulo CLI por DummyAgent para isolar os testes.
    import forge_code_agent.cli as cli_module

    monkeypatch.setattr(cli_module, "CodeAgent", DummyAgent)


def test_stream_reasoning_only_filters_non_reasoning(monkeypatch, capsys, tmp_path: Path):
    _monkeypatch_dummy_agent(monkeypatch)

    argv = [
        "stream",
        "--provider",
        "dummy",
        "--workdir",
        str(tmp_path),
        "--prompt",
        "dummy prompt",
        "--reasoning-only",
    ]

    exit_code = cli_main(argv)
    assert exit_code == 0

    captured = capsys.readouterr()
    out = captured.out

    # Deve conter apenas o texto de reasoning, não o agent_message.
    assert "step 1: analyze request" in out
    assert "final answer for prompt" not in out
    # Linha bruta não JSON deve ser ignorada em modo reasoning-only.
    assert "RAW LINE" not in out


def test_stream_reasoning_with_output_marks_prefixes(monkeypatch, capsys, tmp_path: Path):
    _monkeypatch_dummy_agent(monkeypatch)

    argv = [
        "stream",
        "--provider",
        "dummy",
        "--workdir",
        str(tmp_path),
        "--prompt",
        "dummy prompt",
        "--reasoning-with-output",
    ]

    exit_code = cli_main(argv)
    assert exit_code == 0

    captured = capsys.readouterr()
    out = captured.out

    # Deve marcar reasoning e agent_message com prefixos.
    assert "[REASONING] step 1: analyze request" in out
    assert "[OUTPUT] final answer for prompt" in out
    # Linha não JSON deve aparecer bruta.
    assert "RAW LINE" in out
