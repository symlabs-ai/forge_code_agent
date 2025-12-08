@value @context @mcp @e2e
Feature: MCP tools and session context
  As a developer using forgeCodeAgent with MCP-enabled providers
  I want to use MCP tools through CodeManager and CodeAgent sessions
  So that I can read and write workspace files consistently across providers while keeping context

  Background:
    Given a working directory prepared for MCP demos
    And an MCP server configured for the project workspace

  @happy_path @mcp @codex @ci-int
  Scenario: Use MCP read_file tool via Codex in a CodeManager session
    Given there is a CodeManager configured with logs under "logs/codeagent"
    And there is a CodeAgent session "sess-mcp" using provider "codex" and the project workspace
    And the workspace contains a file "mcp_demo_file.txt" with example content
    When the developer executes a code prompt in session "sess-mcp" asking to read "mcp_demo_file.txt" via MCP
    Then the MCP server is used to read the file contents
    And the developer sees a summary that reflects the content of "mcp_demo_file.txt"
    And the session context persisted in logs includes events for the MCP tool call

  @multi_provider @mcp @ci-int
  Scenario: Switch provider while keeping MCP-enabled session context
    Given there is a CodeManager configured with logs under "logs/codeagent"
    And there is a CodeAgent session "sess-multi" using provider "codex" and the project workspace
    And the developer has executed at least one prompt in session "sess-multi" using MCP tools
    When the developer switches the session "sess-multi" provider to "claude"
    And executes a new prompt in the same session using the "claude" provider
    Then the new execution reuses the existing session context
    And the context includes events from both providers for the same session

  @observability @mcp @ci-int
  Scenario: Record canonical events for MCP tool calls
    Given there is a CodeManager session "sess-events" using provider "codex"
    And the developer executes a prompt that triggers at least one MCP tool call
    When the execution finishes
    Then the ExecutionResult contains canonical events for MCP tool calls
    And the persisted session context in logs/codeagent includes entries identifying the tool name and arguments
