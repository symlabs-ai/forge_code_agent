import os
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../../specs/bdd/10_forge_core/10_code_agent_execution.feature")


@pytest.fixture
def working_directory(tmp_path: Path) -> Path:
    """Working directory for CodeAgent executions."""
    return tmp_path


@given("a working directory configured for the project", target_fixture="workdir")
def given_working_directory(working_directory: Path) -> Path:
    return working_directory


@given('there is a CodeAgent configured with provider "codex" in the working directory', target_fixture="code_agent")
def given_code_agent_codex(workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    return CodeAgent(provider="codex", workdir=workdir)


@given('there is a CodeAgent configured with provider "gemini" in the working directory', target_fixture="code_agent")
def given_code_agent_gemini(workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    return CodeAgent(provider="gemini", workdir=workdir)


@when("the developer sends a code prompt for execution", target_fixture="execution_result")
def when_developer_sends_prompt(code_agent):
    prompt = "print('hello from forgeCodeAgent')"
    return code_agent.run(prompt)


@then('the runtime executes the "codex" provider CLI')
def then_runtime_executes_codex_cli(execution_result):
    # For o nível de BDD, interpretamos "executar CLI" como
    # usar o provider correto para processar o prompt.
    assert execution_result.provider == "codex"


@then('the runtime executes the "gemini" provider CLI')
def then_runtime_executes_gemini_cli(execution_result):
    assert execution_result.provider == "gemini"


@then('the response object contains status "success"')
def then_response_contains_status_success(execution_result):
    assert execution_result.status == "success"


@then('the response object contains provider "codex"')
def then_response_contains_provider_codex(execution_result):
    assert execution_result.provider == "codex"


@then('the response object contains provider "gemini"')
def then_response_contains_provider_gemini(execution_result):
    assert execution_result.provider == "gemini"


@then("the response object contains non-empty code content")
def then_response_contains_non_empty_content(execution_result):
    assert isinstance(execution_result.content, str)
    assert execution_result.content.strip() != ""


@then("the execution result contains canonical events for the provider")
def then_execution_result_contains_canonical_events(execution_result):
    # O adapter deve ter preenchido raw_events com eventos normalizados.
    events = execution_result.raw_events
    assert isinstance(events, list)
    assert len(events) >= 1
    # Pelo menos um evento deve estar associado ao provider correto.
    assert any(ev.get("provider") == execution_result.provider for ev in events)


@given(
    'there is a CodeAgent configured with streaming support for provider "codex" in the working directory',
    target_fixture="code_agent",
)
def given_streaming_code_agent_codex(workdir: Path, monkeypatch: pytest.MonkeyPatch):
    """
    CodeAgent com provider "codex" preparado para streaming.

    Aqui instrumentamos o adapter de provider para detectar se o caminho de
    streaming passou, de fato, pelo ProviderAdapter registrado, e não apenas
    por um fallback em memória.
    """
    import forge_code_agent.adapters.cli.registry as registry
    from forge_code_agent.adapters.cli.codex import CodexProviderAdapter
    from forge_code_agent.runtime.agent import CodeAgent

    class SpyCodexProviderAdapter(CodexProviderAdapter):
        def __init__(self):
            super().__init__()
            self.stream_called = False

        def stream(self, request):
            self.stream_called = True
            return super().stream(request)

    spy_adapter = SpyCodexProviderAdapter()
    # Substitui o adapter "codex" no registry apenas para este cenário.
    new_registry = dict(registry._REGISTRY)
    new_registry["codex"] = spy_adapter
    monkeypatch.setattr(registry, "_REGISTRY", new_registry)

    return CodeAgent(provider="codex", workdir=workdir)


@given(
    'there is a CodeAgent configured with streaming support for provider "claude" in the working directory',
    target_fixture="code_agent",
)
def given_streaming_code_agent_claude(workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    return CodeAgent(provider="claude", workdir=workdir)


@given(
    'there is a CodeAgent configured with streaming support for provider "gemini" in the working directory',
    target_fixture="code_agent",
)
def given_streaming_code_agent_gemini(workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    return CodeAgent(provider="gemini", workdir=workdir)


@when("the developer calls stream with a code prompt", target_fixture="stream_events")
def when_developer_calls_stream(code_agent):
    prompt = "print('streamed hello from forgeCodeAgent')"
    return list(code_agent.stream(prompt))


@then("the runtime delivers response events incrementally")
def then_runtime_delivers_events_incrementally(stream_events):
    # Para este nível de BDD, considerar "incremental" como ter mais de um evento.
    assert isinstance(stream_events, list)
    assert len(stream_events) > 1

    # Além disso, para provider "codex", garantir que o streaming passou pelo
    # ProviderAdapter registrado (caminho de CLI/adapters, não fallback genérico).
    from forge_code_agent.adapters.cli import get_provider_adapter

    adapter = get_provider_adapter("codex")
    if adapter is not None and hasattr(adapter, "stream_called"):
        assert adapter.stream_called is True


@then("the developer can reconstruct the full response from the stream")
def then_developer_can_reconstruct_response(stream_events):
    contents = [e["content"] for e in stream_events]
    full = "".join(contents)
    assert isinstance(full, str)
    assert "streamed hello from forgeCodeAgent" in full


@then("the end of the stream is clearly indicated")
def then_end_of_stream_clearly_indicated(stream_events):
    # Último evento deve marcar explicitamente o fim do stream.
    last = stream_events[-1]
    assert last.get("end") is True


@given(
    'there is an automation flow that uses a CodeAgent with provider "codex" and is passing',
    target_fixture="automation_flow",
)
def given_passing_automation_flow(workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    agent = CodeAgent(provider="codex", workdir=workdir)

    def flow(prompt: str):
        return agent.run(prompt)

    # Verifica que o fluxo está passando com o provider inicial.
    initial_result = flow("print('initial')")
    assert initial_result.status == "success"
    assert initial_result.provider == "codex"

    return {"agent": agent, "flow": flow}


@when('the provider is changed to "claude" only in configuration', target_fixture="automation_flow")
def when_provider_is_changed_to_claude(automation_flow, workdir: Path):
    from forge_code_agent.runtime.agent import CodeAgent

    # Atualiza apenas a configuração do provider na automação.
    new_agent = CodeAgent(provider="claude", workdir=workdir)

    def flow(prompt: str):
        return new_agent.run(prompt)

    return {"agent": new_agent, "flow": flow}


@then("the flow continues to execute successfully")
def then_flow_continues_to_execute_successfully(automation_flow):
    flow = automation_flow["flow"]
    result = flow("print('still ok')")
    assert result.status == "success"


@then('the CLI invoked becomes the "claude" provider CLI')
def then_cli_invoked_becomes_claude(automation_flow):
    flow = automation_flow["flow"]
    result = flow("print('provider changed')")
    assert result.provider == "claude"


@given(
    'there is a YAML configuration file that sets the provider to "codex" for the automation flow',
    target_fixture="config_file",
)
def given_yaml_config_codex(workdir: Path) -> Path:
    """
    Cria um arquivo de configuração YAML simples para o CodeAgent.

    O detalhamento de como esse arquivo será carregado fica para o forge_coder
    na fase de Delivery; aqui apenas estabelecemos o contrato mínimo esperado.
    """
    config_path = workdir / "forge_code_agent.yml"
    config_path.write_text("provider: codex\n", encoding="utf-8")
    return config_path


@given(
    "there is an automation flow that creates a CodeAgent from that configuration file",
    target_fixture="yaml_configured_flow",
)
def given_automation_flow_from_yaml_config(workdir: Path, config_file: Path):
    """
    Define a assinatura esperada para criação de CodeAgent a partir de config.

    A função concreta `CodeAgent.from_config` será implementada pelo forge_coder;
    aqui descrevemos o uso esperado no nível de teste.
    """
    from forge_code_agent.runtime.agent import CodeAgent

    def create_agent_from_config() -> CodeAgent:
        # Interface esperada (a ser implementada):
        # CodeAgent.from_config(config_path: Path, workdir: Path) -> CodeAgent
        return CodeAgent.from_config(config_path=config_file, workdir=workdir)  # type: ignore[attr-defined]

    def flow(prompt: str):
        agent = create_agent_from_config()
        return agent.run(prompt)

    return {"create_agent": create_agent_from_config, "flow": flow, "config_path": config_file}


@when("the developer runs the automation flow", target_fixture="yaml_flow_result")
def when_developer_runs_yaml_flow(yaml_configured_flow):
    flow = yaml_configured_flow["flow"]
    return flow("print('from yaml config')")


@then('the "codex" provider CLI is used to execute the code prompt')
def then_codex_provider_used_from_yaml(yaml_flow_result):
    assert yaml_flow_result.status == "success"
    assert yaml_flow_result.provider == "codex"


@then(
    'when the YAML configuration is changed to set the provider to "claude" without changing the automation code',
    target_fixture="yaml_flow_after_change",
)
def when_yaml_config_is_changed_to_claude(yaml_configured_flow):
    config_path: Path = yaml_configured_flow["config_path"]
    # Atualiza apenas o arquivo YAML; o código da automação permanece igual.
    config_path.write_text("provider: claude\n", encoding="utf-8")
    flow = yaml_configured_flow["flow"]
    return flow("print('after yaml change')")


@then('the same automation flow executes successfully using the "claude" provider CLI')
def then_same_flow_uses_claude_from_yaml(yaml_flow_after_change):
    assert yaml_flow_after_change.status == "success"
    assert yaml_flow_after_change.provider == "claude"


@given("the forge-code-agent CLI is installed and available in the environment")
def given_cli_installed():
    """
    Para o MVP, consideramos a CLI disponível via `python -m forge_code_agent.cli`.

    Em ambientes onde um entrypoint `forge-code-agent` estiver configurado,
    este step pode ser adaptado para usá-lo diretamente.
    """
    # Nada a fazer aqui; a existência da CLI é garantida pelo layout do pacote.
    return


@when(
    'the developer runs "forge-code-agent run" with provider "codex" and a simple code prompt',
    target_fixture="cli_run_result",
)
def when_developer_runs_cli_run(workdir: Path):
    """
    Executa a CLI oficial (via módulo) em modo run, usando o provider "codex".
    """
    import subprocess
    import sys

    # Em ambiente de testes, usamos a CLI via módulo garantindo o PYTHONPATH.
    repo_root = Path(__file__).resolve().parents[2]
    env = dict(**os.environ)
    env["PYTHONPATH"] = f"{repo_root / 'src'}" + (f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else "")

    cmd = [
        sys.executable,
        "-m",
        "forge_code_agent.cli",
        "run",
        "--provider",
        "codex",
        "--workdir",
        str(workdir),
        "--prompt",
        "Qual é a capital do Brasil?",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return {"completed": completed}


@then("the CLI exits with status code 0")
def then_cli_exits_with_zero(cli_run_result):
    completed = cli_run_result["completed"]
    assert completed.returncode == 0


@then('the CLI output contains generated code content for provider "codex"')
def then_cli_output_contains_generated_code(cli_run_result):
    completed = cli_run_result["completed"]
    stdout = completed.stdout or ""
    assert "codex" in stdout
    assert "Qual é a capital do Brasil?" in stdout or stdout.strip() != ""


@when(
    'the developer runs "forge-code-agent stream" with provider "codex" and a simple code prompt',
    target_fixture="cli_run_result",
)
def when_developer_runs_cli_stream(workdir: Path):
    """
    Executa a CLI oficial (via módulo) em modo stream, usando o provider "codex".
    """
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parents[2]
    env = dict(**os.environ)
    env["PYTHONPATH"] = f"{repo_root / 'src'}" + (f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else "")

    cmd = [
        sys.executable,
        "-m",
        "forge_code_agent.cli",
        "stream",
        "--provider",
        "codex",
        "--workdir",
        str(workdir),
        "--prompt",
        "Qual é a capital do Brasil?",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return {"completed": completed}
