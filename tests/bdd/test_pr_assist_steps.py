from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, scenarios, then, when

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.domain.models import ExecutionResult

scenarios("../../specs/bdd/42_pr_assist/42_pr_assist.feature")


class DummyPRAssistAgent:
    """
    Dummy agent used in BDD to simulate a PR-assist provider.

    It does not call real CLIs or MCP; instead, it reads changed files
    from the workspace and fabricates a summary + suggestion.
    """

    def __init__(self, provider: str, workdir: Path, **_: Any) -> None:
        self.provider = provider
        self.workdir = workdir

    @classmethod
    def from_env(cls, workdir: Path, **kwargs: Any) -> DummyPRAssistAgent:  # pragma: no cover
        return cls(provider="dummy-pr-assist", workdir=workdir, **kwargs)

    def run(
        self,
        prompt: str,
        timeout: float | None = None,
        **options: Any,
    ) -> ExecutionResult:  # pragma: no cover
        # Files considered "changed" for the PR are listed in pr_files.txt.
        pr_index = self.workdir / "pr_files.txt"
        changed_files: list[str] = []
        if pr_index.exists():
            for line in pr_index.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    changed_files.append(line)

        snippets: list[str] = []
        for rel in changed_files:
            target = self.workdir / rel
            if target.exists():
                snippets.append(f"{rel}: {target.read_text(encoding='utf-8')[:80]}")

        summary_lines: list[str] = [
            f"PR-assist summary for {len(changed_files)} changed files",
        ]
        if snippets:
            summary_lines.append("Changed files snippets:")
            summary_lines.extend(snippets)

        # Simple suggestion based on the prompt and presence of tests.
        suggestion = "suggestion: consider improving test coverage"
        tests_dir = self.workdir / "tests"
        if tests_dir.exists():
            suggestion = "suggestion: ensure new tests cover edge cases"

        content = "\n".join(summary_lines + [suggestion])
        return ExecutionResult(
            status="success",
            provider=self.provider,
            content=content,
            raw_events=[],
            metadata={"workdir": str(self.workdir), "prompt": prompt, "changed_files": changed_files},
        )


@pytest.fixture
def pr_workspace(tmp_path: Path) -> Path:
    """
    Workspace de repositório de exemplo para PR-assist.
    """
    workdir = tmp_path / "pr_assist_repo"
    workdir.mkdir(parents=True, exist_ok=True)

    src_dir = workdir / "src"
    tests_dir = workdir / "tests"
    src_dir.mkdir()
    tests_dir.mkdir()

    (src_dir / "module_a.py").write_text(
        "def foo():\n    return 1\n",
        encoding="utf-8",
    )
    (src_dir / "module_b.py").write_text(
        "def bar():\n    return 2\n",
        encoding="utf-8",
    )
    (tests_dir / "test_module_a.py").write_text(
        "def test_foo():\n    assert True\n",
        encoding="utf-8",
    )

    # Arquivo que lista os arquivos modificados no PR.
    (workdir / "pr_files.txt").write_text(
        "src/module_a.py\nsrc/module_b.py\n",
        encoding="utf-8",
    )

    return workdir


@pytest.fixture
def pr_code_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CodeManager:
    """
    CodeManager configurado para usar DummyPRAssistAgent nos testes BDD.
    """
    import forge_code_agent.context.manager as manager_module

    monkeypatch.setattr(manager_module, "CodeAgent", DummyPRAssistAgent)
    logs_dir = tmp_path / "logs" / "codeagent"
    return CodeManager(logs_dir=logs_dir)


@given("a repository workspace prepared for PR-assist demos", target_fixture="workdir")
def given_repository_workspace_prepared_for_pr_assist_demos(pr_workspace: Path) -> Path:
    return pr_workspace


@given("a diff or list of changed files for a pull request is available in the workspace")
def given_diff_or_list_of_changed_files_available(workdir: Path) -> None:
    pr_index = workdir / "pr_files.txt"
    assert pr_index.exists(), "pr_files.txt must exist in the workspace"


@given(
    'there is a CodeAgent configured with provider "codex" and MCP tools enabled for the workspace',
    target_fixture="session_id",
)
def given_codeagent_configured_with_provider_codex(pr_code_manager: CodeManager, workdir: Path) -> str:
    # For BDD we rely on DummyPRAssistAgent; the provider name is informational.
    session_id = "sess-pr-assist"
    pr_code_manager.run(
        "initial PR assist warmup",
        provider="codex",
        session_id=session_id,
        workdir=workdir,
    )
    return session_id


@when(
    "the developer runs the PR-assist CLI demo with that workspace",
    target_fixture="pr_result",
)
def when_developer_runs_pr_assist_cli_demo(
    pr_code_manager: CodeManager,
    workdir: Path,
    session_id: str,
) -> ExecutionResult:
    # In tests we call CodeManager directly; the CLI demo will be wired later by forge_coder.
    return pr_code_manager.run(
        "analyze this pull request and suggest improvements",
        session_id=session_id,
        workdir=workdir,
    )


@then("the agent reads the changed files via tools or MCP")
def then_agent_reads_changed_files(pr_result: ExecutionResult) -> None:
    changed = (pr_result.metadata or {}).get("changed_files") or []
    assert changed, "expected changed_files metadata to be populated"


@then("the final output includes a summary of the changes")
def then_final_output_includes_summary(pr_result: ExecutionResult) -> None:
    content = pr_result.content or ""
    assert "PR-assist summary" in content


@then("the final output includes at least one concrete suggestion for improvement")
def then_final_output_includes_suggestion(pr_result: ExecutionResult) -> None:
    content = pr_result.content or ""
    assert "suggestion:" in content


@given(
    "there is a PR-assist CLI demo script that uses the forge-code-agent CLI",
    target_fixture="multi_pr_workspace",
)
def given_pr_assist_cli_demo_script(workdir: Path) -> Path:
    # For BDD we only require that a workspace exists which could be used by a CLI script.
    return workdir


@given("this script is passing with provider \"codex\"")
def given_script_passing_with_codex() -> None:
    # The actual CLI script coverage will be provided by examples and separate tests;
    # here we only model the assumption in the feature.
    return None


@when(
    'the provider configuration is changed to "claude" or "gemini" for the same workspace',
    target_fixture="switched_session_id",
)
def when_provider_configuration_is_changed(
    pr_code_manager: CodeManager,
    session_id: str,
) -> str:
    pr_code_manager.switch_provider(session_id, "claude")
    return session_id


@then("the same PR-assist script still passes without modification")
def then_same_script_still_passes_without_modification(
    pr_code_manager: CodeManager,
    multi_pr_workspace: Path,
    switched_session_id: str,
) -> None:
    # Execute another run in the same session with the new provider.
    result = pr_code_manager.run(
        "reanalyze this pull request after provider switch",
        session_id=switched_session_id,
        workdir=multi_pr_workspace,
    )
    assert result.status == "success"


@then("the underlying provider used by the CLI reflects the new configuration")
def then_underlying_provider_reflects_new_configuration(
    pr_code_manager: CodeManager,
    switched_session_id: str,
) -> None:
    ctx = pr_code_manager.get_session_context(switched_session_id)
    providers = {ev.get("provider") for ev in ctx}
    assert "codex" in providers
    # In tests, DummyPRAssistAgent uses its own provider id; we rely on metadata
    # recorded by CodeManager to reflect the logical provider name.
    assert "claude" in providers
