@support @observability @resilience
Feature: CodeAgent reliability and resilience
  As a team relying on forgeCodeAgent
  I want clear and differentiated error handling around providers and CLI execution
  So that I can diagnose failures quickly and keep automations stable

  Background:
    Given a working directory configured for the project

  @config_error @provider
  @ci-int
  Scenario: Fail to configure unsupported provider
    Given a developer tries to create a CodeAgent with provider "unknown"
    When the agent is initialized
    Then the runtime fails with a clear error indicating the provider is not supported
    And no provider CLI is executed

  @cli_error @provider
  @ci-int
  Scenario: Handle failure while executing provider CLI
    Given the CLI for provider "codex" is not available in the environment
    When the runtime tries to execute a code prompt
    Then the runtime returns a provider execution error
    And the error message allows identifying that the CLI command could not be found

  @streaming @interruption
  @ci-int
  Scenario: Indicate that streamed response was interrupted
    Given a CodeAgent is executing a prompt in streaming mode
    And the provider CLI is interrupted before completion
    When the runtime delivers the events to the caller
    Then the developer receives the chunks that were already generated
    And the developer is informed that the response was interrupted before completion

  @parsing @json
  @ci-int
  Scenario: Handle malformed JSON output from CLI
    Given a provider CLI returns malformed JSON in its output
    When the runtime tries to parse the CLI response
    Then the runtime raises a clear parsing error
    And the error contains enough information to debug the malformed output

  @timeout @cli_error
  @ci-int
  Scenario: Timeout when provider execution exceeds configured limit
    Given a CodeAgent is configured with a timeout of 5 seconds for provider "codex"
    And the provider CLI takes longer than 5 seconds to respond
    When the runtime executes a code prompt
    Then the runtime fails with a timeout error
    And the error indicates that the provider execution exceeded the configured time limit

  @stderr @diagnostics
  @ci-int
  Scenario: Capture provider stderr output safely for diagnostics
    Given the CLI for provider "codex" writes an error message to stderr
    When the runtime executes a code prompt
    Then the runtime captures the stderr output for diagnostics
    And the stderr content is exposed in a safe, structured error object
