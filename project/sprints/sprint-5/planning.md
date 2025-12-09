# Sprint 5 - Planning

**Sprint**: 5
**Date**: 2025-12-08
**Owner**: sprint_coach

---

## 1. Contexto

- Ciclo anterior concluiu:
  - `ContextSessionManager` + `CodeManager` implementados e testados.
  - MCP centralizado no `CodeManager` com demos multi-provider (Codex, Claude, Gemini).
  - CLI-first para sessões (`--use-code-manager`, `--session-id`, `--auto-summarize`).
- Referências:
  - `docs/product/current_plan.md`
  - `specs/roadmap/feature_breakdown.md`
  - `specs/roadmap/BACKLOG.md`
  - `project/recommendations.md`

---

## 2. Objetivos da Sprint

### Goal 1 — PR assistido via CLI + MCP

- ValueTrack: **PR Assistido via CLI + MCP** (planejado em `docs/product/current_plan.md` e `specs/roadmap/feature_breakdown.md`).
- Resultado esperado:
  - Feature BDD `specs/bdd/42_pr_assist/42_pr_assist.feature` detalhada e com steps implementados.
  - Pelo menos um cenário `@pr_assist @cli @mcp @e2e` verde usando `CodeManager` + MCP (provider dummy ou codex, conforme ambiente de CI).
  - Script demo `examples/sprint5_pr_assist_demo.sh` mostrando o fluxo em workspace de exemplo.

### Goal 2 — Geração de módulo + testes via CLI

- ValueTrack: **Geração de módulo + testes**.
- Resultado esperado:
  - Feature BDD `specs/bdd/43_module_and_tests/43_module_and_tests.feature` detalhada e com steps implementados.
  - Pelo menos um cenário `@module_and_tests @cli @files @e2e` verde (pode usar provider dummy em testes).
  - Script demo `examples/sprint5_module_and_tests_demo.sh` que:
    - cria um workspace de exemplo;
    - chama a CLI oficial para gerar módulo + testes;
    - exibe arquivos gerados.

### Goal 3 — Integração com CodeManager e sessões

- Garantir que ambos os fluxos (PR assistido e módulo+testes):
  - possam ser executados via `CodeManager` com `session_id`;
  - registrem contexto em `logs/codeagent`;
  - possam reutilizar contexto entre chamadas (ex.: várias iterações sobre o mesmo PR).

---

## 3. Escopo e Tarefas (linkadas ao roadmap)

### 3.1 PR Assistido (T23)

- [ ] Refinar `specs/bdd/42_pr_assist/42_pr_assist.feature` com cenários:
  - [ ] Analisar um PR a partir de um conjunto de arquivos modificados em um workspace.
  - [ ] Gerar um resumo de mudanças.
  - [ ] Sugerir comentários de revisão em formato legível.
- [ ] Implementar steps em `tests/bdd/test_pr_assist_steps.py` (novo arquivo):
  - [ ] Preparar workspace de PR fake (ex.: `tmp_path / "repo"` com arquivos modificados).
  - [ ] Executar `CodeManager.run` ou CLI oficial (`python -m forge_code_agent.cli run`) apontando para esse workspace.
  - [ ] Asserções sobre arquivos/resultados gerados (ex.: arquivo de review, stdout).
- [ ] Criar `examples/sprint5_pr_assist_demo.sh`:
  - [ ] Script CLI-first que:
    - prepara um workspace `project/pr_assist_demo_workdir`;
    - executa a CLI oficial com provider configurado;
    - imprime um mini-relatório de revisão.

### 3.2 Módulo + Testes (T25)

- [ ] Refinar `specs/bdd/43_module_and_tests/43_module_and_tests.feature`:
  - [ ] Cenário de geração de módulo em `src/` e testes em `tests/`.
  - [ ] Cenário de reexecução com o mesmo `session_id` refinando o módulo/testes.
- [ ] Implementar steps em `tests/bdd/test_module_and_tests_steps.py`:
  - [ ] Preparar workspace com estrutura mínima `src/` + `tests/`.
  - [ ] Chamar `CodeManager.run` ou CLI (`run --write-to-file`) para gerar arquivos.
  - [ ] Verificar a existência e conteúdo mínimo dos arquivos gerados.
- [ ] Criar `examples/sprint5_module_and_tests_demo.sh`:
  - [ ] Script CLI-first que:
    - prepara workspace `project/module_tests_demo_workdir`;
    - executa CLI para gerar módulo + testes;
    - lista arquivos gerados.

### 3.3 Integração com sessões/contexto (T20, T21, T24)

- [ ] Garantir que os steps BDD de T23/T25:
  - [ ] usem `CodeManager` com `session_id` explícito;
  - [ ] validem que `logs/codeagent/session_*.json` é criado durante os testes.
- [ ] Atualizar `docs/product/sites/cli_sessions_and_context.md` com exemplos:
  - [ ] PR assistido com `--use-code-manager --session-id`;
  - [ ] módulo+testes com reuso de sessão.

---

## 4. Dependências e Riscos

- Dependência de CLIs reais (Codex/Claude/Gemini) é opcional para testes:
  - Em CI, usar providers dummies/simulados.
  - Demos em `examples/` podem exigir ambiente configurado, como já ocorre nas sprints anteriores.
- Riscos:
  - Complexidade de BDD de PR assistido (cuidado para manter cenários enxutos e determinísticos).
  - Tempo necessário para scripts de demo E2E com múltiplos providers.

---

## 5. Definição de Pronto da Sprint

- Todas as tarefas das seções 3.1–3.3 concluídas.
- Todos os testes (`pytest -q`) verdes.
- Demos `examples/sprint5_pr_assist_demo.sh` e `examples/sprint5_module_and_tests_demo.sh` executáveis com ambiente local preparado.
- `project/sprints/sprint-5/progress.md` e `project/sprints/sprint-5/review.md` atualizados ao longo da sprint.
