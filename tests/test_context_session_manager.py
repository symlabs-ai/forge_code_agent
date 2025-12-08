from __future__ import annotations

from pathlib import Path

from forge_code_agent.context.session_manager import ContextSessionManager
from forge_code_agent.domain.models import ExecutionResult


def _dummy_result(provider: str = "codex") -> ExecutionResult:
    return ExecutionResult(
        status="success",
        provider=provider,
        content="dummy content",
        raw_events=[
            {"kind": "reasoning", "text": "thinking..."},
            {"kind": "message", "text": "final answer"},
        ],
        metadata={"workdir": "/tmp/workdir"},
    )


def test_record_interaction_and_get_context(tmp_path: Path) -> None:
    mgr = ContextSessionManager(session_id="test-session", logs_dir=tmp_path)
    result = _dummy_result()

    mgr.record_interaction("What is 2+2?", result)

    ctx = mgr.get_context()
    # Esperamos ao menos: user + assistant content + reasoning + message
    assert len(ctx) >= 4
    roles = {item["role"] for item in ctx}
    assert "user" in roles
    assert "assistant" in roles or "system" in roles


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs" / "codeagent"
    mgr = ContextSessionManager(session_id="sess-123", logs_dir=logs_dir)
    result = _dummy_result(provider="codex")
    mgr.record_interaction("Qual é a capital do Brasil?", result)

    saved_path = mgr.save()
    assert saved_path.exists()

    loaded = ContextSessionManager.load(saved_path)
    assert loaded.session_id == "sess-123"
    assert len(loaded.events) == len(mgr.events)
    assert loaded.current_provider == mgr.current_provider
    assert (loaded.workdir is None) or isinstance(loaded.workdir, Path)


def test_summarize_if_needed_uses_summarizer_and_trims_events(tmp_path: Path) -> None:
    class DummySummarizer:
        def __init__(self) -> None:
            self.called = False

        def summarize(self, messages):  # type: ignore[override]
            self.called = True
            return "dummy summary"

    logs_dir = tmp_path / "logs" / "codeagent"
    mgr = ContextSessionManager(session_id="sess-sum", logs_dir=logs_dir, max_events=3)

    # Gerar mais eventos do que max_events para disparar o resumo.
    for i in range(5):
        result = _dummy_result()
        mgr.record_interaction(f"prompt {i}", result)

    summarizer = DummySummarizer()
    mgr.summarize_if_needed(summarizer)

    # Verifica que o summarizer foi invocado e que um resumo foi registrado.
    assert summarizer.called
    assert mgr.summaries, "expected at least one summary entry"

    # Após o resumo, a lista de eventos deve ter sido reduzida.
    assert len(mgr.events) <= 3
