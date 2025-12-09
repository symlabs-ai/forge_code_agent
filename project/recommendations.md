# Project Recommendations — forgeCodeAgent

> Documento vivo mantido por **Jorge the Forge** com recomendações de processo e técnicas
> que devem ser consideradas nas próximas sprints.
> Deve ser lido pelo **Sprint Coach** no início de **cada sprint**.

---

## Estrutura

Cada recomendação deve ser registrada com:

- `id`: identificador curto (ex.: R-001).
- `source`: onde foi identificada (ex.: sprint-1/review.md, jorge-process-review, MDD review).
- `description`: descrição objetiva da recomendação.
- `owner_symbiota`: quem deve agir (ex.: sprint_coach, forge_coder, tdd_coder).
- `status`: `pending` | `done` | `cancelled`.
- `notes`: comentários curtos sobre decisões ou execução.

---

## Recomendações Atuais

### R-001 — Medir cobertura de testes por sprint

- `id`: R-001
- `source`: project/sprints/sprint-1/jorge-process-review.md
- `description`: Incluir medição e registro de cobertura de testes (pytest-cov ou similar) nas próximas sprints e registrar o valor em `review.md` e/ou `progress.md`.
- `owner_symbiota`: sprint_coach (coordena) + forge_coder (executa medição)
- `status`: done
- `notes`:
  - Estrutura implementada na Sprint 2:
    - `pytest-cov` adicionado em `dev-requirements.txt`;
    - `process/env/README.md` atualizado com instruções de cobertura;
    - Sprint 2 `planning.md`/`progress.md`/`review.md` orientam a medição via `pytest --cov`.
  - A execução do comando e registro do valor passa a ser parte do ritual de cada sprint.

### R-002 — Refinar datas reais e story points/capacity

- `id`: R-002
- `source`: project/sprints/sprint-1/jorge-process-review.md
- `description`: Ajustar datas reais, story points e capacidade/velocity nos artefatos de sprint (planning/progress) a partir da Sprint 2, para que deixem de ser placeholders e reflitam a cadência real.
- `owner_symbiota`: sprint_coach
- `status`: done
- `notes`:
  - Sprint 2 já incorpora datas/estimativas mais concretas em `planning.md` e `progress.md`.
  - Recomenda-se continuar refinando estes valores nas próximas sprints com base em histórico real.

### R-003 — Implementar CodeManager + ContextSessionManager

- `id`: R-003
- `source`: sprint-4/mcp-review (Jorge + bill_review)
- `description`: Implementar o `ContextSessionManager` e o `CodeManager` conforme `docs/product/CODE_MANAGER_PLAN.md`, centralizando o gerenciamento de contexto (histórico + resumo + sessões) e orquestração de providers/multi-sessão.
- `owner_symbiota`: sprint_coach (coordena), forge_coder (implementa), tdd_coder (testes)
- `status`: done
- `notes`:
  - Implementação concluída neste ciclo:
    - `ContextSessionManager` + `CodeManager` criados em `src/forge_code_agent/context/`.
    - Integração com CLI via `--use-code-manager` e `--auto-summarize`.
    - Persistência de sessões em `logs/codeagent/session_*.json`.
  - Coberto por testes unitários (`tests/test_context_session_manager.py`, `tests/test_code_manager.py`),
    testes de CLI (`tests/test_cli_code_manager_summarize.py`) e BDD (`specs/bdd/41_context/41_code_manager_sessions.feature`).

### R-004 — Centralizar MCP no CodeManager e estender para Claude/Gemini

- `id`: R-004
- `source`: sprint-4/mcp-review (Jorge + bill_review)
- `description`: Mover a responsabilidade de orquestração de MCP para o `CodeManager` (em vez do runtime), mantendo as idiossincrasias de cada provider nos adapters, e estender a integração MCP para Claude e Gemini além do Codex.
- `owner_symbiota`: sprint_coach (coordena), forge_coder (adapters/MCP), tdd_coder (BDD/tests)
- `status`: done
- `notes`:
  - CodeManager passou a ser o único ponto de orquestração MCP (`ensure_mcp_server` + metadata `"mcp"`),
    retirando essa responsabilidade do `CodeAgent`.
  - Demos MCP criados para os três providers principais em `examples/mcp/`:
    - Codex: `codex_register_mcp_server.sh`, `codex_read_file_demo.sh`;
    - Claude: `claude_tools_demo.sh`;
    - Gemini: `gemini_tools_demo.sh`.
  - Hardening inicial e fluxo MCP básico estão cobertos por testes (`tests/test_mcp_server_tools.py`)
    e pela feature BDD `specs/bdd/40_mcp/40_mcp_tools.feature`. Cenários adicionais `@mcp @e2e`
    por ValueTrack (ex.: PR assistido, módulo+testes) seguirão nos próximos ciclos.
