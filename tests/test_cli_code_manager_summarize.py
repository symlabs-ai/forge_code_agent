from __future__ import annotations

from pathlib import Path

from forge_code_agent.cli import main as cli_main
from forge_code_agent.domain.models import ExecutionResult


class DummyManager:
    """
    Manager mínimo para verificar a passagem de summarizer_factory a partir da CLI.
    """

    last_kwargs: dict | None = None

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        DummyManager.last_kwargs = kwargs

    def run(self, prompt: str, **_: object) -> ExecutionResult:  # type: ignore[override]
        return ExecutionResult(
            status="success",
            provider="dummy-manager",
            content=f"ok: {prompt}",
            raw_events=[],
            metadata={},
        )


def _monkeypatch_dummy_manager(monkeypatch):
    import forge_code_agent.cli as cli_module

    monkeypatch.setattr(cli_module, "CodeManager", DummyManager)


def test_run_with_code_manager_without_auto_summarize(monkeypatch, capsys, tmp_path: Path) -> None:
    _monkeypatch_dummy_manager(monkeypatch)

    argv = [
        "run",
        "--provider",
        "dummy",
        "--workdir",
        str(tmp_path),
        "--prompt",
        "hello",
        "--use-code-manager",
    ]

    exit_code = cli_main(argv)
    assert exit_code == 0

    # Quando auto-summarize não é usado, summarizer_factory não deve ser passado.
    assert DummyManager.last_kwargs is not None
    assert "summarizer_factory" not in DummyManager.last_kwargs

    out = capsys.readouterr().out
    assert "provider=dummy-manager" in out


def test_run_with_code_manager_and_auto_summarize(monkeypatch, capsys, tmp_path: Path) -> None:
    _monkeypatch_dummy_manager(monkeypatch)

    argv = [
        "run",
        "--provider",
        "dummy",
        "--workdir",
        str(tmp_path),
        "--prompt",
        "hello",
        "--use-code-manager",
        "--auto-summarize",
    ]

    exit_code = cli_main(argv)
    assert exit_code == 0

    # Com auto-summarize, esperamos que summarizer_factory seja passado ao manager.
    assert DummyManager.last_kwargs is not None
    assert "summarizer_factory" in DummyManager.last_kwargs
    assert callable(DummyManager.last_kwargs["summarizer_factory"])

    out = capsys.readouterr().out
    assert "provider=dummy-manager" in out
