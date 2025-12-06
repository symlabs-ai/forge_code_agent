from pathlib import Path

from forge_code_agent.runtime.agent import CodeAgent


def test_run_triggers_before_and_after_handlers(tmp_path: Path) -> None:
    agent = CodeAgent(provider="codex", workdir=tmp_path)

    seen_before = []
    seen_after = []

    def before_hook(request) -> None:
        seen_before.append((request.provider, request.prompt))

    def after_hook(request, result) -> None:
        seen_after.append((request.provider, result.status))

    agent.add_before_run_handler(before_hook)
    agent.add_after_run_handler(after_hook)

    result = agent.run("dummy prompt")

    assert result.status == "success"
    assert seen_before == [("codex", "dummy prompt")]
    assert seen_after == [("codex", "success")]
