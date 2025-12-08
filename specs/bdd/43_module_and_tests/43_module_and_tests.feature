@value @module_and_tests @e2e
Feature: Generate module and tests via CodeAgent and CLI
  As a developer starting a new service or module
  I want to use a CLI flow that generates a module and its tests into a workspace
  So that I can bootstrap functionality and tests consistently using the same provider abstraction

  Background:
    Given an empty or clean project workspace prepared for module-generation demos

  @happy_path @module_and_tests @codex
  Scenario: Generate a Python module and tests via CLI using Codex
    Given there is a CodeAgent configured with provider "codex" for the module-generation workspace
    When the developer runs the module-and-tests CLI demo with a prompt describing the desired module
    Then the demo creates a Python module file under the src directory
    And the demo creates a corresponding test file under the tests directory
    And the generated files are located inside the configured workspace

  @multi_provider @module_and_tests
  Scenario: Swap provider for module-and-tests generation without changing the automation script
    Given there is a CodeAgent configured with provider "codex" for the module-generation workspace
    And there is a module-and-tests CLI demo script that uses the forge-code-agent CLI
    And this script is passing with provider "codex"
    When the provider configuration is changed to "claude" or "gemini" for the same workspace
    Then the same module-and-tests script still passes without modification
    And the underlying provider used by the CLI reflects the new configuration
