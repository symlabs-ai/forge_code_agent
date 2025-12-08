from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, scenarios, then, when

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.domain.models import ExecutionResult

scenarios("../../specs/bdd/43_module_and_tests/43_module_and_tests.feature")


class DummyModuleAndTestsAgent:
    """
    Dummy agent used in BDD to simulate generation of a module and tests.

    It writes simple Python files under src/ and tests/ in the workspace.
    """

    def __init__(self, provider: str, workdir: Path, **_: Any) -> None:
        self.provider = provider
        self.workdir = workdir

    @classmethod
    def from_env(cls, workdir: Path, **kwargs: Any) -> DummyModuleAndTestsAgent:  # pragma: no cover
        return cls(provider="dummy-module-tests", workdir=workdir, **kwargs)

    def run(
        self,
        prompt: str,
        timeout: float | None = None,
        **options: Any,
    ) -> ExecutionResult:  # pragma: no cover
        src_dir = self.workdir / "src"
        tests_dir = self.workdir / "tests"
        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        module_path = src_dir / "generated_service.py"
        test_path = tests_dir / "test_generated_service.py"

        module_path.write_text(
            "def generated_function(x: int) -> int:\n"
            "    return x + 1\n",
            encoding="utf-8",
        )
        test_path.write_text(
            "from generated_service import generated_function\n\n"
            "def test_generated_function():\n"
            "    assert generated_function(1) == 2\n",
            encoding="utf-8",
        )

        return ExecutionResult(
            status="success",
            provider=self.provider,
            content="module and tests generated",
            raw_events=[],
            metadata={
                "workdir": str(self.workdir),
                "module_path": str(module_path.relative_to(self.workdir)),
                "test_path": str(test_path.relative_to(self.workdir)),
            },
        )


@pytest.fixture
def module_workspace(tmp_path: Path) -> Path:
    """
    Workspace limpo para geração de módulo + testes.
    """
    workdir = tmp_path / "module_tests_workspace"
    workdir.mkdir(parents=True, exist_ok=True)
    return workdir


@pytest.fixture
def module_code_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CodeManager:
    """
    CodeManager configurado para usar DummyModuleAndTestsAgent nos testes BDD.
    """
    import forge_code_agent.context.manager as manager_module

    monkeypatch.setattr(manager_module, "CodeAgent", DummyModuleAndTestsAgent)
    logs_dir = tmp_path / "logs" / "codeagent"
    return CodeManager(logs_dir=logs_dir)


@given("an empty or clean project workspace prepared for module-generation demos", target_fixture="workdir")
def given_empty_or_clean_workspace_for_module_generation(module_workspace: Path) -> Path:
    return module_workspace


@given(
    'there is a CodeAgent configured with provider "codex" for the module-generation workspace',
    target_fixture="session_id",
)
def given_codeagent_configured_for_module_generation(
    module_code_manager: CodeManager,
    workdir: Path,
) -> str:
    session_id = "sess-module-tests"
    module_code_manager.run(
        "initial module-generation warmup",
        provider="codex",
        session_id=session_id,
        workdir=workdir,
    )
    return session_id


@when(
    "the developer runs the module-and-tests CLI demo with a prompt describing the desired module",
    target_fixture="module_result",
)
def when_developer_runs_module_and_tests_demo(
    module_code_manager: CodeManager,
    workdir: Path,
    session_id: str,
) -> ExecutionResult:
    return module_code_manager.run(
        "create a simple service module with tests",
        session_id=session_id,
        workdir=workdir,
    )


@then("the demo creates a Python module file under the src directory")
def then_demo_creates_module_under_src(workdir: Path, module_result: ExecutionResult) -> None:
    meta = module_result.metadata or {}
    module_rel = meta.get("module_path") or "src/generated_service.py"
    module_path = workdir / module_rel
    assert module_path.exists(), f"expected module at {module_path}"


@then("the demo creates a corresponding test file under the tests directory")
def then_demo_creates_test_under_tests(workdir: Path, module_result: ExecutionResult) -> None:
    meta = module_result.metadata or {}
    test_rel = meta.get("test_path") or "tests/test_generated_service.py"
    test_path = workdir / test_rel
    assert test_path.exists(), f"expected test file at {test_path}"


@then("the generated files are located inside the configured workspace")
def then_generated_files_are_inside_workspace(workdir: Path, module_result: ExecutionResult) -> None:
    meta = module_result.metadata or {}
    module_rel = Path(meta.get("module_path") or "src/generated_service.py")
    test_rel = Path(meta.get("test_path") or "tests/test_generated_service.py")
    assert not module_rel.is_absolute()
    assert not test_rel.is_absolute()
    assert (workdir / module_rel).exists()
    assert (workdir / test_rel).exists()


@given(
    "there is a module-and-tests CLI demo script that uses the forge-code-agent CLI",
    target_fixture="multi_module_workspace",
)
def given_module_and_tests_cli_demo_script(workdir: Path) -> Path:
    return workdir


@given("this script is passing with provider \"codex\"")
def given_module_and_tests_script_passing_with_codex() -> None:
    return None


@when(
    'the provider configuration is changed to "claude" or "gemini" for the same workspace',
    target_fixture="switched_session_id",
)
def when_module_provider_configuration_is_changed(
    module_code_manager: CodeManager,
    session_id: str,
) -> str:
    module_code_manager.switch_provider(session_id, "gemini")
    return session_id


@then("the same module-and-tests script still passes without modification")
def then_same_module_and_tests_script_still_passes(
    module_code_manager: CodeManager,
    multi_module_workspace: Path,
    switched_session_id: str,
) -> None:
    result = module_code_manager.run(
        "regenerate module and tests after provider switch",
        session_id=switched_session_id,
        workdir=multi_module_workspace,
    )
    assert result.status == "success"


@then("the underlying provider used by the CLI reflects the new configuration")
def then_underlying_provider_for_module_reflects_configuration(
    module_code_manager: CodeManager,
    switched_session_id: str,
) -> None:
    ctx = module_code_manager.get_session_context(switched_session_id)
    providers = {ev.get("provider") for ev in ctx}
    assert "codex" in providers
    assert "gemini" in providers
