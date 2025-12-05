@value @forge_core @critical
Feature: CodeAgent execution via CLI
  As a developer using forgeCodeAgent
  I want to run code prompts through different providers via CLI
  So that I can automate code generation with a single Python API

  Background:
    Given a working directory configured for the project

  @happy_path @provider_run
  @ci-int
  Scenario: Run code prompt with configured provider
    Given there is a CodeAgent configured with provider "codex" in the working directory
    When the developer sends a code prompt for execution
    Then the runtime executes the "codex" provider CLI
    And the response object contains status "success"
    And the response object contains provider "codex"
    And the response object contains non-empty code content

  @happy_path @streaming
  @ci-int
  Scenario: Consume streamed code response incrementally
    Given there is a CodeAgent configured with streaming support for provider "codex" in the working directory
    When the developer calls stream with a code prompt
    Then the runtime delivers response events incrementally
    And the developer can reconstruct the full response from the stream
    And the end of the stream is clearly indicated

  @ci-int
  Scenario: Switch provider while keeping the same automation flow
    Given there is an automation flow that uses a CodeAgent with provider "codex" and is passing
    When the provider is changed to "claude" only in configuration
    Then the flow continues to execute successfully
    And the CLI invoked becomes the "claude" provider CLI
