from __future__ import annotations

from pathlib import Path

from forge_code_agent.context.manager import CodeManager


def test_code_manager_run_creates_session_and_persists_context(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs" / "codeagent"
    workdir = tmp_path / "workdir"
    workdir.mkdir(parents=True, exist_ok=True)

    manager = CodeManager(logs_dir=logs_dir)

    result = manager.run(
        "What is 2+2?",
        provider="dummy",  # provider não registrado → fallback simulado (sem CLI real)
        session_id="sess-1",
        workdir=workdir,
    )

    # Execução deve ser bem-sucedida com o provider simulado.
    assert result.status == "success"
    assert result.provider == "dummy"

    # Sessão deve existir e conter eventos.
    ctx = manager.get_session_context("sess-1")
    assert len(ctx) >= 2

    # Pelo menos um arquivo de sessão deve ter sido gravado.
    assert logs_dir.exists()
    snapshot_files = list(logs_dir.glob("session_sess-1_*.json"))
    assert snapshot_files, "nenhum snapshot de sessão foi gravado"


def test_code_manager_switch_provider_keeps_context(tmp_path: Path) -> None:
    logs_dir = tmp_path / "logs" / "codeagent"
    workdir = tmp_path / "workdir"
    workdir.mkdir(parents=True, exist_ok=True)

    manager = CodeManager(logs_dir=logs_dir)

    # Primeira execução com provider "dummy".
    result1 = manager.run(
        "Primeira pergunta",
        provider="dummy",
        session_id="sess-ctx",
        workdir=workdir,
    )
    assert result1.provider == "dummy"

    ctx_after_first = manager.get_session_context("sess-ctx")
    len_first = len(ctx_after_first)
    assert len_first >= 1

    # Troca de provider.
    manager.switch_provider("sess-ctx", "dummy-2")

    # Segunda execução, sem especificar provider explicitamente.
    result2 = manager.run(
        "Segunda pergunta",
        session_id="sess-ctx",
        workdir=workdir,
    )

    # Provider efetivo deve ser o novo.
    assert result2.provider == "dummy-2"

    # Contexto deve conter eventos das duas interações.
    ctx_after_second = manager.get_session_context("sess-ctx")
    assert len(ctx_after_second) > len_first
