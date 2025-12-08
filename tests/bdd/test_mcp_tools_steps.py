from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, scenarios, then, when

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.domain.models import ExecutionResult

scenarios("../../specs/bdd/40_mcp/40_mcp_tools.feature")


class DummyMCPAgent:
    """
    Agente de teste que simula um provider com suporte a MCP tools.

    Não chama CLIs reais; apenas produz um ExecutionResult contendo
    conteúdo derivado do arquivo e eventos canônicos de tool.
    """

    def __init__(self, provider: str, workdir: Path, **_: Any) -> None:
        self.provider = provider
        self.workdir = workdir

    @classmethod
    def from_env(cls, workdir: Path, **kwargs: Any) -> DummyMCPAgent:  # pragma: no cover
        return cls(provider="dummy", workdir=workdir, **kwargs)

    def run(self, prompt: str, timeout: float | None = None, **options: Any) -> ExecutionResult:  # pragma: no cover
        # Nome do arquivo a ser lido é derivado do próprio prompt.
        filename = "mcp_demo_file.txt"
        target = self.workdir / filename
        content = target.read_text(encoding="utf-8") if target.exists() else ""

        tool_event = {
            "kind": "tool",
            "text": f"read_file({filename})",
            "name": "read_file",
            "args": {"path": filename},
        }

        message_event = {
            "kind": "message",
            "text": f"file summary: {content[:60]}",
        }

        return ExecutionResult(
            status="success",
            provider=self.provider,
            content=f"summary for {filename}: {content}",
            raw_events=[tool_event, message_event],
            metadata={"workdir": str(self.workdir)},
        )


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    workdir = tmp_path / "workspace"
    workdir.mkdir(parents=True, exist_ok=True)
    return workdir


@pytest.fixture
def code_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CodeManager:
    # Garante que CodeManager use DummyMCPAgent em vez de CodeAgent real.
    import forge_code_agent.context.manager as manager_module

    monkeypatch.setattr(manager_module, "CodeAgent", DummyMCPAgent)
    logs_dir = tmp_path / "logs" / "codeagent"
    return CodeManager(logs_dir=logs_dir)


@given("a working directory prepared for MCP demos", target_fixture="workdir")
def given_working_directory_prepared_for_mcp_demos(tmp_workspace: Path) -> Path:
    return tmp_workspace


@given("an MCP server configured for the project workspace")
def given_mcp_server_configured_for_workspace() -> None:
    # Para fins de teste BDD, assumimos que o servidor MCP está configurado.
    # A integração real é exercitada pelos demos e testes unitários de mcp_server.
    return None


@given('there is a CodeManager configured with logs under "logs/codeagent"')
def given_code_manager_with_logs(code_manager: CodeManager) -> None:
    # A simples presença do fixture code_manager já garante logs configurados;
    # o step existe apenas para expressar a intenção na feature.
    return None


@given(
    'there is a CodeAgent session "sess-mcp" using provider "codex" and the project workspace',
    target_fixture="session_id",
)
def given_codeagent_session_sess_mcp(code_manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-mcp"
    # Criar sessão inicial com uma interação neutra.
    code_manager.run(
        "initial prompt",
        provider="codex",
        session_id=session_id,
        workdir=workdir,
    )
    return session_id


@given('the workspace contains a file "mcp_demo_file.txt" with example content')
def given_workspace_contains_demo_file(workdir: Path) -> None:
    target = workdir / "mcp_demo_file.txt"
    target.write_text(
        "Este é um arquivo de exemplo para o demo MCP.\nLinha 2.\n",
        encoding="utf-8",
    )


@when(
    'the developer executes a code prompt in session "sess-mcp" asking to read "mcp_demo_file.txt" via MCP',
    target_fixture="mcp_result",
)
def when_developer_executes_prompt_reading_file_via_mcp(
    code_manager: CodeManager,
    workdir: Path,
    session_id: str,
) -> ExecutionResult:
    return code_manager.run(
        "Use MCP read_file to inspect mcp_demo_file.txt",
        session_id=session_id,
        workdir=workdir,
    )


@then("the MCP server is used to read the file contents")
def then_mcp_server_used_to_read_file(mcp_result: ExecutionResult) -> None:
    # No teste, DummyMCPAgent lê o arquivo diretamente e inclui o conteúdo na resposta.
    assert "mcp_demo_file.txt" in (mcp_result.content or "")


@then('the developer sees a summary that reflects the content of "mcp_demo_file.txt"')
def then_developer_sees_summary(mcp_result: ExecutionResult) -> None:
    assert "arquivo de exemplo" in (mcp_result.content or "")


@then("the session context persisted in logs includes events for the MCP tool call")
def then_session_context_includes_tool_events(code_manager: CodeManager, session_id: str) -> None:
    ctx: list[dict[str, Any]] = code_manager.get_session_context(session_id)
    tool_events = [
        ev for ev in ctx if ev.get("meta", {}).get("kind") == "tool"
    ]
    assert tool_events, "no tool events found in session context"
    names = {ev["meta"]["raw"].get("name") for ev in tool_events}
    assert "read_file" in names


@given(
    'there is a CodeAgent session "sess-multi" using provider "codex" and the project workspace',
    target_fixture="session_multi_id",
)
def given_codeagent_session_sess_multi(code_manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-multi"
    code_manager.run("primeira interação MCP", provider="codex", session_id=session_id, workdir=workdir)
    return session_id


@given('the developer has executed at least one prompt in session "sess-multi" using MCP tools')
def given_developer_has_executed_prompt_in_sess_multi(
    code_manager: CodeManager, workdir: Path, session_multi_id: str
) -> None:
    code_manager.run("segunda interação MCP", session_id=session_multi_id, workdir=workdir)


@when(
    'the developer switches the session "sess-multi" provider to "claude"',
    target_fixture="switched_session_id",
)
def when_developer_switches_provider(code_manager: CodeManager, session_multi_id: str) -> str:
    code_manager.switch_provider(session_multi_id, "claude")
    return session_multi_id


@when(
    'executes a new prompt in the same session using the "claude" provider',
    target_fixture="multi_result",
)
def when_executes_new_prompt_with_claude(
    code_manager: CodeManager,
    workdir: Path,
    switched_session_id: str,
) -> ExecutionResult:
    return code_manager.run(
        "interação com provider claude",
        session_id=switched_session_id,
        workdir=workdir,
    )


@then("the new execution reuses the existing session context")
def then_new_execution_reuses_context(code_manager: CodeManager, session_multi_id: str) -> None:
    ctx = code_manager.get_session_context(session_multi_id)
    assert len(ctx) >= 3


@then("the context includes events from both providers for the same session")
def then_context_includes_events_from_both_providers(code_manager: CodeManager, session_multi_id: str) -> None:
    ctx = code_manager.get_session_context(session_multi_id)
    providers = {ev.get("provider") for ev in ctx}
    # "codex" e "claude" devem estar presentes em algum momento.
    assert "codex" in providers
    assert "claude" in providers


@given('there is a CodeManager session "sess-events" using provider "codex"', target_fixture="session_events_id")
def given_code_manager_session_sess_events(code_manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-events"
    code_manager.run("primeira interação para eventos", provider="codex", session_id=session_id, workdir=workdir)
    return session_id


@given("the developer executes a prompt that triggers at least one MCP tool call", target_fixture="events_result")
def given_developer_executes_prompt_with_tool_call(
    code_manager: CodeManager,
    workdir: Path,
    session_events_id: str,
) -> ExecutionResult:
    return code_manager.run(
        "interação que aciona MCP tool",
        session_id=session_events_id,
        workdir=workdir,
    )


@when("the execution finishes")
def when_the_execution_finishes() -> None:
    # A execução já ocorreu nos steps anteriores; este step existe apenas
    # para deixar o fluxo Gherkin mais legível.
    return None


@then("the ExecutionResult contains canonical events for MCP tool calls")
def then_execution_result_contains_mcp_tool_events(events_result: ExecutionResult) -> None:
    tool_events = [ev for ev in events_result.raw_events if ev.get("kind") == "tool"]
    assert tool_events, "ExecutionResult.raw_events missing tool events"


@then("the persisted session context in logs/codeagent includes entries identifying the tool name and arguments")
def then_persisted_context_includes_tool_name_and_args(
    code_manager: CodeManager,
    session_events_id: str,
) -> None:
    ctx = code_manager.get_session_context(session_events_id)
    tool_events = [ev for ev in ctx if ev.get("meta", {}).get("kind") == "tool"]
    assert tool_events
    raw = tool_events[0]["meta"]["raw"]
    assert raw.get("name") == "read_file"
    assert raw.get("args", {}).get("path") == "mcp_demo_file.txt"
