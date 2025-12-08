# MCP Demos — forgeCodeAgent

Este diretório contém demos de uso de MCP (Model Context Protocol) com o forgeCodeAgent
e CLIs de coding agents (Codex, Claude, Gemini).

## Pré-requisitos gerais

- Ambiente Python do projeto configurado (`.venv` + `PYTHONPATH=src`).
- CLIs instaladas e autenticadas, quando aplicável:
  - `codex`
  - `claude`
  - `gemini`
- MCP server local `forge-code-agent` registrado (via `codex mcp add`):
  - use `examples/mcp/codex_register_mcp_server.sh` para registrar.

## Demos disponíveis

- `codex_read_file_demo.sh`
  Demonstra `codex exec` usando a tool MCP `read_file` para ler um arquivo no workspace
  `project/demo_workdir`.

- `claude_tools_demo.sh`
  Pede explicitamente ao Claude para usar o servidor MCP `forge-code-agent` (se disponível)
  e ler o arquivo `mcp_demo_file_claude.txt` no workspace `project/demo_workdir_claude_mcp`.

- `gemini_tools_demo.sh`
  Pede ao Gemini Code para usar o servidor MCP `forge-code-agent` (se disponível) e ler o
  arquivo `mcp_demo_file_gemini.txt` no workspace `project/demo_workdir_gemini_mcp`.

> Observação: a configuração de MCP para Claude/Gemini depende do ambiente local das CLIs.
> Este repositório assume que a mesma configuração de MCP usada pelo Codex é compartilhada
> pelas outras CLIs. Caso contrário, ajuste a configuração MCP das CLIs conforme sua
> instalação local.
