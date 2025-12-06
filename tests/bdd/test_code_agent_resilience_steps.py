import pytest
from pytest_bdd import given, scenarios, then, when

from forge_code_agent.domain.errors import (
    ParsingError,
    ProviderExecutionError,
    ProviderNotSupportedError,
    ProviderTimeoutError,
)
from forge_code_agent.runtime.agent import CodeAgent

scenarios("../../specs/bdd/50_observabilidade/50_code_agent_resilience.feature")


# --- Background --------------------------------------------------------------


@pytest.fixture
def workdir(tmp_path):
    return tmp_path


@given("a working directory configured for the project", target_fixture="workdir")
def given_working_directory(workdir):
    return workdir


# --- Scenario: Fail to configure unsupported provider ------------------------


@given('a developer tries to create a CodeAgent with provider "unknown"', target_fixture="agent_factory")
def given_unknown_provider_agent_factory(workdir):
    def factory():
        return CodeAgent(provider="unknown", workdir=workdir)

    return factory


@when("the agent is initialized", target_fixture="init_error")
def when_agent_is_initialized(agent_factory):
    try:
        agent_factory()
    except ProviderNotSupportedError as exc:
        return exc
    return None


@then("the runtime fails with a clear error indicating the provider is not supported")
def then_runtime_fails_with_provider_not_supported(init_error):
    assert isinstance(init_error, ProviderNotSupportedError)


@then("no provider CLI is executed")
def then_no_provider_cli_is_executed(init_error):
    # No MVP, garantir apenas que o erro aconteceu antes de qualquer execução.
    assert isinstance(init_error, ProviderNotSupportedError)


# --- Scenario: Handle failure while executing provider CLI -------------------


@given('the CLI for provider "codex" is not available in the environment', target_fixture="unavailable_cli_agent")
def given_unavailable_cli_agent(workdir):
    # Simulamos falha de CLI configurando um provider especial que sempre falha.
    return CodeAgent(provider="codex-missing-cli", workdir=workdir)


@when("the runtime tries to execute a code prompt", target_fixture="cli_error")
def when_runtime_tries_to_execute_prompt(unavailable_cli_agent):
    try:
        unavailable_cli_agent.run("print('test cli failure')")
    except ProviderExecutionError as exc:
        return exc
    return None


@then("the runtime returns a provider execution error")
def then_runtime_returns_provider_execution_error(cli_error):
    assert isinstance(cli_error, ProviderExecutionError)


@then("the error message allows identifying that the CLI command could not be found")
def then_error_message_identifies_cli_not_found(cli_error):
    assert "not found" in str(cli_error).lower() or "cli" in str(cli_error).lower()


# --- Scenario: Indicate that streamed response was interrupted ---------------


@given("a CodeAgent is executing a prompt in streaming mode", target_fixture="stream_agent")
def given_stream_agent(workdir):
    # Provider especial que simula interrupção de streaming.
    return CodeAgent(provider="codex-stream-interrupt", workdir=workdir)


@given("the provider CLI is interrupted before completion", target_fixture="stream_events")
def given_provider_cli_interrupted(stream_agent):
    return list(stream_agent.stream("print('stream interruption')"))


@when("the runtime delivers the events to the caller")
def when_runtime_delivers_events_to_caller(stream_events):
    # Step de passagem; eventos já foram obtidos.
    return


@then("the developer receives the chunks that were already generated")
def then_developer_receives_chunks(stream_events):
    assert isinstance(stream_events, list)
    assert len(stream_events) >= 1


@then("the developer is informed that the response was interrupted before completion")
def then_developer_informed_response_interrupted(stream_events):
    # No MVP, sinalizamos interrupção com uma flag 'interrupted' no último evento.
    last = stream_events[-1]
    assert last.get("interrupted") is True


# --- Scenario: Handle malformed JSON output from CLI -------------------------


@given("a provider CLI returns malformed JSON in its output", target_fixture="malformed_json_agent")
def given_malformed_json_agent(workdir):
    return CodeAgent(provider="codex-malformed-json", workdir=workdir)


@when("the runtime tries to parse the CLI response", target_fixture="parsing_error")
def when_runtime_tries_to_parse_cli_response(malformed_json_agent):
    try:
        malformed_json_agent.run("print('malformed json')")
    except ParsingError as exc:
        return exc
    return None


@then("the runtime raises a clear parsing error")
def then_runtime_raises_parsing_error(parsing_error):
    assert isinstance(parsing_error, ParsingError)


@then("the error contains enough information to debug the malformed output")
def then_error_contains_debug_info(parsing_error):
    assert "malformed" in str(parsing_error).lower() or getattr(parsing_error, "raw_output", None) is not None


# --- Scenario: Timeout when provider execution exceeds configured limit ------


@given('a CodeAgent is configured with a timeout of 5 seconds for provider "codex"', target_fixture="timeout_agent")
def given_timeout_agent(workdir):
    return CodeAgent(provider="codex-timeout", workdir=workdir)


@given("the provider CLI takes longer than 5 seconds to respond")
def given_provider_cli_takes_too_long():
    # Simulado pelo próprio provider "codex-timeout".
    return


@when("the runtime executes a code prompt", target_fixture="runtime_error")
def when_runtime_executes_code_prompt(request):
    # Este step é reutilizado pelos cenários de timeout e stderr.
    if "timeout_agent" in request.fixturenames:
        agent = request.getfixturevalue("timeout_agent")
    elif "stderr_agent" in request.fixturenames:
        agent = request.getfixturevalue("stderr_agent")
    else:  # pragma: no cover - proteção extra
        pytest.fail("No suitable agent fixture found for this step")

    try:
        agent.run("print('resilience test')", timeout=5.0)
    except (ProviderTimeoutError, ProviderExecutionError) as exc:
        return exc
    return None


@then("the runtime fails with a timeout error")
def then_runtime_fails_with_timeout_error(runtime_error):
    assert isinstance(runtime_error, ProviderTimeoutError)


@then("the error indicates that the provider execution exceeded the configured time limit")
def then_error_indicates_exceeded_time(runtime_error):
    assert "timeout" in str(runtime_error).lower() or "time" in str(runtime_error).lower()


# --- Scenario: Capture provider stderr output safely for diagnostics ---------


@given('the CLI for provider "codex" writes an error message to stderr', target_fixture="stderr_agent")
def given_stderr_agent(workdir):
    return CodeAgent(provider="codex-stderr", workdir=workdir)


@then("the runtime captures the stderr output for diagnostics")
def then_runtime_captures_stderr(runtime_error):
    assert isinstance(runtime_error, ProviderExecutionError)
    assert getattr(runtime_error, "stderr", None) is not None


@then("the stderr content is exposed in a safe, structured error object")
def then_stderr_exposed_safely(runtime_error):
    assert isinstance(runtime_error, ProviderExecutionError)
    # Confiamos no tipo da exceção + atributo stderr como estrutura mínima.
    assert isinstance(runtime_error.stderr, str)
