@value @pr_assist @e2e
Feature: PR-assisted review via CLI and MCP
  As a developer working with pull requests
  I want to run a CLI flow that uses CodeAgent/CodeManager and MCP tools
  So that I can get AI-assisted review suggestions for a PR in a controlled workspace

  Background:
    Given a repository workspace prepared for PR-assist demos
    And a diff or list of changed files for a pull request is available in the workspace

  @happy_path @pr_assist @codex
  Scenario: Generate review suggestions for a PR using Codex + MCP
    Given there is a CodeAgent configured with provider "codex" and MCP tools enabled for the workspace
    When the developer runs the PR-assist CLI demo with that workspace
    Then the agent reads the changed files via tools or MCP
    And the final output includes a summary of the changes
    And the final output includes at least one concrete suggestion for improvement

  @multi_provider @pr_assist
  Scenario: Switch provider for PR-assist without changing the automation script
    Given there is a CodeAgent configured with provider "codex" and MCP tools enabled for the workspace
    And there is a PR-assist CLI demo script that uses the forge-code-agent CLI
    And this script is passing with provider "codex"
    When the provider configuration is changed to "claude" or "gemini" for the same workspace
    Then the same PR-assist script still passes without modification
    And the underlying provider used by the CLI reflects the new configuration
