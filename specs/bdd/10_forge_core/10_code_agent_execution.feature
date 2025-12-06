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

  @happy_path @provider_run
  @ci-int
  Scenario: Run code prompt with configured provider gemini
    Given there is a CodeAgent configured with provider "gemini" in the working directory
    When the developer sends a code prompt for execution
    Then the runtime executes the "gemini" provider CLI
    And the response object contains status "success"
    And the response object contains provider "gemini"
    And the response object contains non-empty code content

  @happy_path @streaming
  @ci-int
  Scenario: Consume streamed code response incrementally
    Given there is a CodeAgent configured with streaming support for provider "codex" in the working directory
    When the developer calls stream with a code prompt
    Then the runtime delivers response events incrementally
    And the developer can reconstruct the full response from the stream
    And the end of the stream is clearly indicated

  @happy_path @streaming
  @ci-int
  Scenario: Consume streamed code response incrementally with provider claude
    Given there is a CodeAgent configured with streaming support for provider "claude" in the working directory
    When the developer calls stream with a code prompt
    Then the runtime delivers response events incrementally
    And the developer can reconstruct the full response from the stream
    And the end of the stream is clearly indicated

  @happy_path @streaming
  @ci-int
  Scenario: Consume streamed code response incrementally with provider gemini
    Given there is a CodeAgent configured with streaming support for provider "gemini" in the working directory
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

  @provider @config @ci-int
  Scenario: Select provider from YAML configuration file without changing automation code
    Given there is a YAML configuration file that sets the provider to "codex" for the automation flow
    And there is an automation flow that creates a CodeAgent from that configuration file
    When the developer runs the automation flow
    Then the "codex" provider CLI is used to execute the code prompt
    And when the YAML configuration is changed to set the provider to "claude" without changing the automation code
    Then the same automation flow executes successfully using the "claude" provider CLI

  @cli @e2e
  Scenario: Run code prompt via forge-code-agent CLI
    Given the forge-code-agent CLI is installed and available in the environment
    And a working directory configured for the project
    When the developer runs "forge-code-agent run" with provider "codex" and a simple code prompt
    Then the CLI exits with status code 0
    And the CLI output contains generated code content for provider "codex"

  @cli @streaming @ci-int
  Scenario: Stream code prompt via forge-code-agent CLI
    Given the forge-code-agent CLI is installed and available in the environment
    And a working directory configured for the project
    When the developer runs "forge-code-agent stream" with provider "codex" and a simple code prompt
    Then the CLI exits with status code 0

  @observability @events @ci-int
  Scenario: Record canonical events for provider execution
    Given there is a CodeAgent configured with provider "codex" in the working directory
    When the developer sends a code prompt for execution
    Then the execution result contains canonical events for the provider
