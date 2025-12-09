# Sprint 6 - Progress

**Sprint**: 6
**Date**: 2025-12-08
**Owner**: sprint_coach

---

## 1. Overview

- Foco da sprint:
  - Hardening/modularização do MCP server.
  - Observabilidade e retenção de sessões (`logs/codeagent`).
  - UX da CLI para sessões e streaming.

---

## 2. Tasks Status (ligadas ao roadmap)

### MCP Server (T22, T26 - parte inicial)

- [x] Extrair framing/protocolo para módulo dedicado:
  - `src/forge_code_agent/mcp_server/protocol.py` criado com:
    - `MCPFramingState`,
    - `read_next_json_line(...)`,
    - `write_json_response(...)`.
- [x] Refatorar `run_stdio_server` para usar protocolo:
  - `src/forge_code_agent/mcp_server/__init__.py` agora delega framing/leitura/escrita a `protocol.py`.
- [x] Manter compatibilidade com testes e demos:
  - `tests/test_mcp_server_tools.py` verde (`ping`, `initialize`, `tools/list`, `tools/call`).

### Sessões e Retenção (T20/T24 - evolução)

- [x] Ajustar persistência de sessões:
  - `ContextSessionManager.save()` agora grava:
    - `session_<id>_current.json` como snapshot estável;
    - snapshots históricos `session_<id>_<timestamp>.json` para debug.
- [x] Implementar política simples de retenção:
  - manutenção de no máximo 5 snapshots históricos por sessão;
  - snapshots mais antigos são removidos de forma best-effort.
- [x] Garantir compatibilidade com load e testes:
  - `tests/test_context_session_manager.py` permanece verde.

### UX da CLI para Sessões/Streaming (T23/T25 - parte CLI)

- [x] Simplificar uso de CodeManager na CLI (`run`):
  - `--session-id` agora implica uso de `CodeManager` automaticamente;
  - `--use-code-manager` permanece como flag explícita, mas não é mais obrigatória quando há `--session-id`.
- [x] Manter comportamento de `--auto-summarize`:
  - integração com `AgentSummarizer` preservada quando CodeManager é usado;
  - testes `tests/test_cli_code_manager_summarize.py` verdes.
- [x] Preservar UX de streaming:
  - flags `--reasoning-only`, `--reasoning-with-output`, `--events-json` continuam mapeadas para `normalize_stream_line(...)`;
  - testes `tests/test_cli_reasoning_flags.py` verdes.

---

## 3. Tests Executed

- [x] `pytest -q tests/test_mcp_server_tools.py`
- [x] `pytest -q tests/test_context_session_manager.py`
- [x] `pytest -q tests/test_cli_code_manager_summarize.py tests/test_cli_reasoning_flags.py`

Todos passaram no ambiente local da sprint.

---

## 4. Pending / Next

- Hardening MCP adicional (T26) ainda planejado:
  - modularizar completamente dispatcher/tools;
  - limites adicionais (timeouts por tool, modos read-only configuráveis).
- Documentação:
  - atualizar `docs/product/sites/cli_sessions_and_context.md` com o novo formato de sessões/logs e fluxos de streaming;
  - referenciar o novo demo da sprint (abaixo).
