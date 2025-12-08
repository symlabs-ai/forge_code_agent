from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, scenarios, then, when

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.context.session_manager import ContextSessionManager
from forge_code_agent.domain.models import ExecutionResult

scenarios("../../specs/bdd/41_context/41_code_manager_sessions.feature")


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    workdir = tmp_path / "workspace"
    workdir.mkdir(parents=True, exist_ok=True)
    return workdir


@pytest.fixture
def manager(tmp_workspace: Path) -> CodeManager:
    logs_dir = tmp_workspace.parent / "logs" / "codeagent"
    return CodeManager(logs_dir=logs_dir)


@given("a temporary workspace for CodeManager sessions", target_fixture="workdir")
def given_temporary_workspace_for_sessions(tmp_workspace: Path) -> Path:
    return tmp_workspace


@given("there is a CodeManager configured for sessions")
def given_code_manager_for_sessions(manager: CodeManager) -> None:
    # A presença do fixture `manager` já configura logs e estrutura básica.
    return None


@given(
    'a session "sess-context" using provider "dummy" and the temporary workspace',
    target_fixture="session_context_id",
)
def given_session_sess_context(manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-context"
    manager.run(
        "Primeira interação na sessão de contexto",
        provider="dummy",
        session_id=session_id,
        workdir=workdir,
    )
    return session_id


@when("the developer executes multiple prompts in the same session")
def when_developer_executes_multiple_prompts(manager: CodeManager, workdir: Path, session_context_id: str) -> None:
    for i in range(3):
        manager.run(
            f"Interação adicional {i} na sessão de contexto",
            session_id=session_context_id,
            workdir=workdir,
        )


@then("the session context contains events for all interactions")
def then_session_context_contains_events(manager: CodeManager, session_context_id: str) -> None:
    ctx: list[dict[str, Any]] = manager.get_session_context(session_context_id)
    # Esperamos pelo menos uma sequência de eventos equivalente a múltiplas interações.
    assert len(ctx) >= 4


@then("a snapshot file for the session is persisted under logs/codeagent")
def then_snapshot_file_persisted(manager: CodeManager, tmp_workspace: Path, session_context_id: str) -> None:
    logs_dir = tmp_workspace.parent / "logs" / "codeagent"
    assert logs_dir.exists()
    snapshots = list(logs_dir.glob(f"session_{session_context_id}_*.json"))
    assert snapshots, "no session snapshot files found"


@given(
    'a session "sess-switch" using provider "dummy" and the temporary workspace',
    target_fixture="session_switch_id",
)
def given_session_sess_switch(manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-switch"
    manager.run(
        "Primeira interação na sessão de troca de provider",
        provider="dummy",
        session_id=session_id,
        workdir=workdir,
    )
    return session_id


@given('the developer has executed at least one prompt in session "sess-switch"')
def given_has_executed_prompt_in_sess_switch(manager: CodeManager, workdir: Path, session_switch_id: str) -> None:
    manager.run(
        "Segunda interação antes da troca de provider",
        session_id=session_switch_id,
        workdir=workdir,
    )


@when(
    'the developer switches the session "sess-switch" provider to "dummy-2"',
    target_fixture="switched_session_id",
)
def when_switches_session_provider(manager: CodeManager, session_switch_id: str) -> str:
    manager.switch_provider(session_switch_id, "dummy-2")
    return session_switch_id


@when(
    'executes a new prompt in the same session with provider "dummy-2"',
    target_fixture="switch_result",
)
def when_executes_new_prompt_with_new_provider(
    manager: CodeManager,
    workdir: Path,
    switched_session_id: str,
) -> ExecutionResult:
    return manager.run(
        "Interação após troca de provider",
        session_id=switched_session_id,
        workdir=workdir,
    )


@then("the session context includes events for both providers")
def then_session_context_has_events_for_both_providers(manager: CodeManager, session_switch_id: str) -> None:
    ctx = manager.get_session_context(session_switch_id)
    providers = {ev.get("provider") for ev in ctx}
    assert "dummy" in providers
    assert "dummy-2" in providers


@given(
    'a session "sess-summary" using provider "dummy" and the temporary workspace with low context limits',
    target_fixture="session_summary_id",
)
def given_session_with_low_limits(manager: CodeManager, workdir: Path) -> str:
    session_id = "sess-summary"
    # Cria a sessão inicialmente.
    manager.run(
        "Interação inicial para sessão de resumo",
        provider="dummy",
        session_id=session_id,
        workdir=workdir,
    )
    # Força limites baixos para disparar summarize_if_needed rapidamente.
    session = manager._get_or_create_session(session_id, workdir, provider="dummy")  # type: ignore[attr-defined]
    session.max_events = 6
    session.max_summary_chars = 200
    return session_id


@when("the developer executes enough prompts to exceed the context limits")
def when_executes_enough_prompts_for_summary(manager: CodeManager, workdir: Path, session_summary_id: str) -> None:
    # Para disparar summarize_if_needed(), precisamos de um Summarizer configurado.
    # Neste teste, criamos uma nova instância de CodeManager com summarizer_factory
    # simplificada e copiamos o estado da sessão existente.
    from forge_code_agent.context.summarizer import AgentSummarizer as _AgentSummarizer
    from forge_code_agent.context.summarizer import Summarizer as _Summarizer
    from forge_code_agent.runtime.agent import CodeAgent as _CodeAgent

    def summarizer_factory(agent: _CodeAgent, _session) -> _Summarizer:  # type: ignore[override]
        # Para fins de teste, usamos AgentSummarizer, mas poderíamos substituir
        # por um summarizer fake se necessário.
        return _AgentSummarizer(agent=agent)

    # Recria o manager com summarizer_factory e reaproveita a sessão existente.
    logs_dir = manager.logs_dir  # type: ignore[attr-defined]
    new_manager = CodeManager(logs_dir=logs_dir, summarizer_factory=summarizer_factory)
    # Reusa internamente a mesma sessão/sessões em _sessions.
    new_manager._sessions = manager._sessions  # type: ignore[attr-defined]
    new_manager._agents = manager._agents  # type: ignore[attr-defined]

    for i in range(8):
        new_manager.run(
            f"Interação extra {i} para forçar resumo",
            session_id=session_summary_id,
            workdir=workdir,
        )


@then("at least one summary is recorded for the session")
def then_at_least_one_summary_recorded(manager: CodeManager, session_summary_id: str) -> None:
    # Carregamos o último snapshot e verificamos summaries.
    # Como o diretório de logs é derivado do fixture, inspecionamos diretamente
    # via ContextSessionManager.load.
    # Obtemos logs_dir a partir de uma sessão existente.
    # Atenção: usamos o atributo interno `_sessions` apenas para fins de teste.
    session: ContextSessionManager = manager._sessions[session_summary_id]  # type: ignore[attr-defined]
    logs_dir = session.logs_dir
    snapshots = sorted(logs_dir.glob(f"session_{session_summary_id}_*.json"))
    assert snapshots, "no snapshot files found for summary session"

    loaded = ContextSessionManager.load(snapshots[-1])
    assert loaded.summaries, "expected at least one summary"


@then("the number of stored events does not exceed the configured max_events")
def then_number_of_events_does_not_exceed_limit(manager: CodeManager, session_summary_id: str) -> None:
    session: ContextSessionManager = manager._sessions[session_summary_id]  # type: ignore[attr-defined]
    assert len(session.events) <= session.max_events
