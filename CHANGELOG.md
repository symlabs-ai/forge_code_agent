Changelog
=========

Todas as mudanças relevantes deste projeto são documentadas aqui.

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/), com versionamento semântico simplificado.

## [0.3.1]

### Changed

- Bump de versão para `0.3.1` em `forge_code_agent.__version__` sem mudanças funcionais.
- Documentação atualizada para refletir:
  - novo nome do repositório GitHub `symlabs-ai/forge_code_agent`
  - pacote Python `forge_code_agent`
  - entrada oficial de CLI `python -m forge_code_agent.cli`.

## [0.3.0] – Cycle 04 / Sprint 6

### Added

- `CodeManager` + `ContextSessionManager` para sessões de contexto, com:
  - snapshots em `logs/codeagent/session_<id>_current.json`
  - retenção limitada de snapshots históricos por sessão.
- Servidor MCP modularizado:
  - framing/protocolo extraído para `src/forge_code_agent/mcp_server/protocol.py`
  - tools de filesystem (`read_file`, `list_dir`, modo opcional `write_file`)
  - modo read-only configurável.
- UX de CLI para sessões e streaming:
  - `--session-id` ativa automaticamente o CodeManager
  - flags `--reasoning-only`, `--reasoning-with-output`, `--events-json` normalizadas para Codex/Claude/Gemini.
- Demos novas:
  - `examples/sprint5_pr_assist_demo.sh` e `sprint5_pr_assist_streaming_demo.sh`
  - `examples/sprint5_module_and_tests_demo.sh`
  - `examples/sprint6_demo.sh`
  - `examples/mcp/*` para Codex/Claude/Gemini.
- Documentação de produto reestruturada em `docs/product/`, incluindo:
  - `current_plan.md`, `CODE_MANAGER_PLAN.md`, `TOOL_CALLING_MCP_PLAN.md`
  - feedbacks de ciclo em `project/docs/feedback/cycle-03.md` e `cycle-04.md`.

### Changed

- CLI `run` passa a resolver o uso de CodeManager baseado em `--session-id`, reduzindo necessidade de múltiplas flags.
- Persistência de sessões atualizada para formato estável e compacto.
- Hardening do MCP server, com limites de workspace e política de tools.

### Fixed

- Vários ajustes de estilo e lint (ruff/pre-commit) em scripts de publicação MDD (`process/symbiotes/mdd_publisher/scripts/*.py`).
- Correções em testes de MCP (`tests/test_mcp_server_tools.py`) e de contexto.

## [0.2.1]

### Added

- Execução multi-provider real:
  - suporte inicial para Codex, Claude Code e Gemini Code via adapters CLI específicos.
- CLI-first consolidada:
  - `python -m forge_code_agent.cli run/stream` com parâmetro `--provider`.
- Scripts de exemplo em `/examples` para demonstrar:
  - troca de provider via configuração YAML
  - ValueTrack de execução e de tools+files.

### Notes

- Tag criada após os primeiros fluxos E2E com múltiplos providers funcionando e testes passando.

## [0.1.1]

### Added

- MVP inicial do forgeCodeAgent:
  - `CodeAgent` com execução básica via CLI (foco em Codex).
  - Especificações BDD iniciais em `specs/bdd/` para execução, tools+files e resiliência.
  - Primeiras integrações com ForgeProcess (MDD/BDD/TDD) em `process/`.

### Notes

- Primeira versão tagueada do repositório, usada como base para evolução posterior (multi-provider, MCP, sessões).
