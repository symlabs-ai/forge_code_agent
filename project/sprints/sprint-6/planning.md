# Sprint 6 - Planning

**Sprint**: 6
**Date**: 2025-12-08
**Owner**: sprint_coach

---

## 1. Contexto

- Cycle 03 foi encerrado com:
  - `ContextSessionManager` + `CodeManager` implementados e exercitados em cenários reais.
  - MCP multi-provider (Codex, Claude, Gemini) integrado via CodeManager, com demos em `examples/mcp/`.
  - Fluxos E2E de **PR assistido** e **módulo + testes** implementados (Sprint 5).
- Próximo ciclo, conforme `docs/product/current_plan.md`, foca em:
  - hardening e modularização do servidor MCP;
  - observabilidade/retention de sessões (logs/codeagent);
  - UX da CLI para sessões e streaming;
  - aprofundar ValueTracks de PR assistido e módulo+testes.
- Referências:
  - `docs/product/current_plan.md`
  - `specs/roadmap/TECH_STACK.md`, `HLD.md`, `feature_breakdown.md`, `estimates.yml`, `BACKLOG.md`
  - `project/recommendations.md`
  - `project/docs/feedback/cycle-03.md`

---

## 2. Objetivos da Sprint

### Goal 1 — Hardening do MCP Server

- ValueTracks: `value_context_manager_codeagent` (MCP/tools) + `support_observability_code_agent_resilience`.
- Resultado esperado:
  - Servidor MCP modularizado (protocolo/dispatcher/tools) conforme plano em `docs/product/current_plan.md`.
  - Limites básicos implementados (timeouts, segurança de workspace consistentes para todas as tools).
  - Cenários BDD e testes cobrindo erros de protocolo e uso indevido de paths.

### Goal 2 — Observabilidade e Retenção de Sessões

- ValueTrack: `value_context_manager_codeagent`.
- Resultado esperado:
  - Formato de `logs/codeagent/session_*.json` estabilizado e documentado.
  - Política de retenção definida (e implementada) para sessões (ex.: N snapshots ou JSONL).
  - Métricas básicas de sessões (contagem por provider, resumos aplicados) acessíveis via logs/tests.

### Goal 3 — UX da CLI para Sessões e Streaming

- ValueTracks: `value_context_manager_codeagent`, `value_pr_assist_cli_mcp`, `value_module_and_tests_cli`.
- Resultado esperado:
  - Comportamento de `--session-id` simplificado (ativa CodeManager implicitamente, erros claros para combinações inválidas).
  - Streaming de reasoning + output funcionando de forma consistente para Codex, Claude e Gemini (especialmente visibilidade de código gerado).
  - Documentação CLI-first atualizada (`docs/product/sites/cli_sessions_and_context.md` ou equivalente) com exemplos completos.

---

## 3. Escopo e Tarefas (linkadas ao roadmap)

### 3.1 Hardening MCP (T26 + refinamentos T22)

- [ ] Refinar `specs/roadmap/HLD.md` e `LLD.md` com desenho modular do MCP server:
  - [ ] separar parsing de protocolo (headers/Content-Length), dispatcher e tools em seções/módulos distintos.
- [ ] Implementar refatoração incremental do MCP server:
  - [ ] manter comportamento atual para Codex (demos existentes verdes);
  - [ ] preparar ganchos para futura extensão de tools (sem quebrar API atual).
- [ ] Estender testes:
  - [ ] `tests/test_mcp_server_tools.py` cobrindo paths maliciosos, timeouts e erros de protocolo;
  - [ ] cenários BDD de MCP (`40_mcp_tools.feature`) ajustados para refletir hardening onde fizer sentido.

### 3.2 Observabilidade e Sessões (T20/T21/T24 — evolução)

- [ ] Definir formato estável para `session_*.json`:
  - [ ] documentar campos mínimos (identidade de sessão, provider, eventos, summaries, metadados) em `docs/product/` (seção de sessões/contexto).
- [ ] Implementar política de retenção:
  - [ ] opção de manter apenas últimos N snapshots por `session_id` ou
  - [ ] modo compacto (JSONL) opcional para ambientes de longa execução.
- [ ] Adicionar métricas mínimas:
  - [ ] contagem de execuções por provider/sessão;
  - [ ] contagem de summaries aplicados;
  - [ ] expor em logs de debug para futura integração com observabilidade ForgeBase.

### 3.3 UX de CLI para Sessões e Streaming (T23/T25 refinados)

- [ ] Ajustar `src/forge_code_agent/cli.py`:
  - [ ] fazer `--session-id` ativar implicitamente CodeManager (sem exigir `--use-code-manager`);
  - [ ] fornecer mensagens claras para combinações inválidas de flags.
- [ ] Revisar streaming:
  - [ ] garantir que flags `--reasoning-only`, `--reasoning-with-output`, `--events-json` tenham comportamento previsível para Codex, Claude e Gemini;
  - [ ] evitar filtragem excessiva de código (especialmente no caso de Claude).
- [ ] Atualizar e/ou criar documentação de sessões/streaming:
  - [ ] exemplos revisados em `docs/product/sites/cli_sessions_and_context.md`;
  - [ ] destacar uso de sessões nos fluxos de PR assistido e módulo+testes.
- [ ] Ajustar/dobrar demos em `examples/`:
  - [ ] garantir que `examples/run_codex.sh`, `run_claude.sh`, `run_gemini.sh` demonstrem claramente o comportamento de streaming e sessões;
  - [ ] adicionar notas ao final de `examples/sprint5_*` ou criar `sprint6_*` quando ajustes forem significativos.

---

## 4. Dependências e Riscos

- Depende da estabilidade das CLIs externas (Codex/Claude/Gemini) para validar certos cenários de streaming e MCP:
  - Em CI, usar smoke tests controlados e/ou providers simulados.
- Riscos:
  - Refatoração do MCP server deve ser incremental para não quebrar demos existentes;
  - Alterações na CLI precisam ser cuidadosas para manter compatibilidade com scripts `examples/` atuais (idealmente com warnings e deprecation, não breaking changes abruptas).

---

## 5. Definição de Pronto da Sprint

- Hardening MCP:
  - [ ] MCP server modularizado conforme LLD/HLD;
  - [ ] testes de segurança/limites passando;
  - [ ] docs de arquitetura atualizados.
- Observabilidade de sessões:
  - [ ] formato de `session_*.json` documentado e coberto por testes;
  - [ ] política de retenção implementada (pelo menos modo básico);
  - [ ] métricas de sessões rastreáveis via logs.
- UX CLI:
  - [ ] comportamento de `--session-id` e flags de streaming consolidado e documentado;
  - [ ] demos em `examples/` atualizados e executáveis para um stakeholder com ambiente configurado.
- Artefatos de sprint:
  - [ ] `project/sprints/sprint-6/progress.md` e `review.md` atualizados;
  - [ ] `project/sprints/sprint-6/stakeholder-approval.md` registrando a aprovação do incremento de hardening/UX.
