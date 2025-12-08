@value @context @ci-int
Feature: CodeManager sessions and context
  As a developer using CodeManager with multiple providers
  I want to reuse session context and summaries across runs
  So that I can keep history and switch providers without losing state

  Background:
    Given a temporary workspace for CodeManager sessions

  @happy_path @context
  Scenario: Reuse context across multiple runs in the same session
    Given there is a CodeManager configured for sessions
    And a session "sess-context" using provider "dummy" and the temporary workspace
    When the developer executes multiple prompts in the same session
    Then the session context contains events for all interactions
    And a snapshot file for the session is persisted under logs/codeagent

  @multi_provider @context
  Scenario: Switch provider in the same session and keep context
    Given there is a CodeManager configured for sessions
    And a session "sess-switch" using provider "dummy" and the temporary workspace
    And the developer has executed at least one prompt in session "sess-switch"
    When the developer switches the session "sess-switch" provider to "dummy-2"
    And executes a new prompt in the same session with provider "dummy-2"
    Then the session context includes events for both providers

  @summaries @context
  Scenario: Trigger summaries when context grows beyond limits
    Given there is a CodeManager configured for sessions
    And a session "sess-summary" using provider "dummy" and the temporary workspace with low context limits
    When the developer executes enough prompts to exceed the context limits
    Then at least one summary is recorded for the session
    And the number of stored events does not exceed the configured max_events
