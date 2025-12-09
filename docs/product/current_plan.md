# Current Plan — Próximo Ciclo (Hardening + Observabilidade + UX de Sessões)

> Este plano descreve o **próximo ciclo** do ForgeProcess para o forgeCodeAgent
> após o encerramento do Cycle 03, no qual:
> - `ContextSessionManager` e `CodeManager` já estão implementados e exercitados;
> - MCP multi‑provider (Codex, Claude, Gemini) está integrado ao CodeManager;
> - fluxos de **PR assistido** e **módulo + testes** existem com demos CLI e BDD.

O foco agora é:

- endurecer a implementação (hardening) do servidor MCP e do runtime;
- melhorar observabilidade e retenção de sessões/contexto;
- simplificar e tornar mais previsível a UX da CLI com sessões;
- aprofundar os ValueTracks de PR assistido e módulo+testes com mais cenários.

---

## 1. Hardening do MCP Server e Protocolo

- [ ] Modularizar o MCP server (`src/forge_code_agent/mcp_server`) em componentes menores:
  - [ ] extrair parsing de protocolo (headers + Content-Length) para um módulo `protocol.py`;
  - [ ] extrair dispatch/registry de tools para um `dispatcher.py`;
  - [ ] manter as tools em módulo dedicado (`tools.py`), mantendo regras de workspace.
- [ ] Revisar modos de operação:
  - [ ] avaliar remover ou isolar o modo “JSON puro” do loop principal, mantendo apenas o protocolo MCP padrão em produção;
  - [ ] se mantido para testes, documentar claramente que é apenas para uso interno.
- [ ] Hardening de erros:
  - [ ] eliminar `except Exception: pass` em integração MCP/CodeManager;
  - [ ] garantir logging estruturado de falhas MCP e propagação adequada até `ExecutionResult.errors`.
- [ ] Atualizar documentação:
  - [ ] alinhar `docs/product/TOOL_CALLING_MCP_PLAN.md` e `docs/product/TOOL_CALLING_MCP_PROPOSAL.md` ao estado real do MCP (sem “tool calling mágico”, focado em MCP/tools externos).

---

## 2. Observabilidade e Retenção de Sessões

- [ ] Melhorar o modelo de logs de sessão em `logs/codeagent/`:
  - [ ] definir formato estável para `session_*.json` (campos mínimos obrigatórios, versão);
  - [ ] garantir que eventos redundantes não inflam demais o arquivo (ex.: `raw` só quando necessário).
- [ ] Introduzir política de retenção:
  - [ ] opção de manter apenas os N últimos snapshots por `session_id`;
  - [ ] ou modo “compacto” (um arquivo JSONL por sessão, com eventos append‑only).
- [ ] Métricas básicas:
  - [ ] contar execuções por provider e por sessão;
  - [ ] registrar número de resumos (`summaries`) aplicados por sessão;
  - [ ] expor esses dados via logs (para futura integração com métricas externas).

---

## 3. UX da CLI para Sessões e Streaming

- [ ] Simplificar o uso de sessões na CLI (`src/forge_code_agent/cli.py`):
  - [ ] fazer `--session-id` ativar implicitamente o `CodeManager` (evitando combinações confusas com `--use-code-manager`);
  - [ ] emitir warning ou erro claro quando flags forem usadas em combinação inválida.
- [ ] Revisar flags de streaming:
  - [ ] garantir que `--reasoning-only`, `--reasoning-with-output` e `--events-json` funcionem de forma consistente entre Codex, Claude e Gemini;
  - [ ] evitar filtragem excessiva de eventos (especialmente para Claude), para que o usuário veja código e reasoning em tempo hábil.
- [ ] Atualizar documentação CLI-first:
  - [ ] revisar e expandir `docs/product/sites/cli_sessions_and_context.md` (ou equivalente) com exemplos atualizados de:
    - sessões com troca de provider mantendo contexto;
    - uso de streaming com reasoning + output;
    - leitura de contexto a partir de `logs/codeagent/session_*.json`.

---

## 4. Aprofundar ValueTrack — PR Assistido via CLI + MCP

- [ ] Estender BDD de PR assistido (`specs/bdd/42_pr_assist/42_pr_assist.feature`):
  - [ ] adicionar cenários com múltiplos arquivos no PR, incluindo mudanças em testes;
  - [ ] cobrir casos onde há falhas de testes e o agente precisa apontar riscos;
  - [ ] marcar cenários representativos com `@e2e @mcp`.
- [ ] Evoluir demos em `examples/`:
  - [ ] enriquecer `examples/sprint5_pr_assist_demo.sh` ou criar `sprint6_pr_assist_demo.sh` com:
    - leitura de `pr_files.txt` via MCP sempre que possível;
    - pelo menos um fluxo em que dois providers analisam o mesmo PR na mesma sessão e produzem insights complementares.
- [ ] Preparar terreno para tools adicionais de PR no MCP (planejamento apenas neste ciclo):
  - [ ] especificar no `TOOL_CALLING_MCP_PROPOSAL.md` possíveis tools MCP futuras para PR (ex.: `run_tests`, `format_diff_summary`), sem implementá‑las ainda.

---

## 5. Aprofundar ValueTrack — Módulo + Testes via CLI

- [ ] Estender BDD de módulo+testes (`specs/bdd/43_module_and_tests/43_module_and_tests.feature`):
  - [ ] cobrir geração de módulos com dependências internas (ex.: serviço + repositório);
  - [ ] cobrir múltiplos arquivos de teste e casos parametrizados;
  - [ ] garantir cenários `@e2e` com providers diferentes na mesma sessão.
- [ ] Evoluir demo `examples/sprint5_module_and_tests_demo.sh`:
  - [ ] demonstrar pelo menos um fluxo em que:
    - Codex gera módulo+testes;
    - Gemini (ou Claude) refina testes e estrutura do módulo na mesma sessão;
    - `pytest` é executado ao final, com saída clara na CLI.
- [ ] Considerar integração futura com MCP para rodar testes:
  - [ ] planejar (em docs) uma tool MCP `run_tests` que possa ser ligada a esse fluxo em ciclos posteriores.

---

## 6. Critérios de Encerramento deste Ciclo

- [ ] MCP server modularizado (protocol/dispatcher/tools) com testes cobrindo o novo desenho.
- [ ] Política de retenção de sessões definida e implementada (documentada em `docs/product/` e comprovada por testes automatizados).
- [ ] CLI com UX de sessões simplificada:
  - [ ] `--session-id` + comportamento CodeManager bem definidos e documentados;
  - [ ] demos de streaming mostrando claramente reasoning + código para Codex, Claude e Gemini.
- [ ] BDD de PR assistido e módulo+testes estendidos com novos cenários `@e2e`, passando em ambiente real.
- [ ] Demos CLI atualizados (`examples/`) cobrindo os fluxos refinados, referenciados em:
  - [ ] `project/sprints/sprint-N/review.md`;
  - [ ] `project/docs/feedback/cycle-0X.md` correspondente ao ciclo.

---

## 7. Estado e Próximos Passos

- O Cycle 03 está encerrado (ver `project/docs/feedback/cycle-03.md`).
- Este documento passa a ser a referência para o **próximo ciclo**:
  - BDD (etapa 01) deve considerar estas prioridades ao revisar `specs/bdd/drafts/behavior_mapping.md` e `tracks.yml`;
  - o Sprint Coach deve usar este plano como insumo para `project/sprints/sprint-6/planning.md` (ou equivalente).
