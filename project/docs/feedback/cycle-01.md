# Feedback — Cycle 01 — forgeCodeAgent

**Cycle**: 01
**From**: MDD → BDD → Execution → Delivery (Sprint 1)
**To**: Feedback
**Date**: 2025-12-05
**Reviewer**: Jorge the Forge (process) + Stakeholder

---

## 1. Resumo do Ciclo

- Visão/MDD, BDD e Execution concluídos com roadmap/backlog aprovados.
- Delivery/Sprint 1 implementou o primeiro incremento de runtime:
  - T4 — Execução `stream()` via subprocess (Codex-like).
  - T7 — Integração inicial de tool calling na execução (`tool_calls` em `CodeAgent.run`).
- Stakeholder aprovou a Sprint 1 (`project/sprints/sprint-1/stakeholder-approval.md`).

---

## 2. Métricas e Sinais

- Features do ciclo:
  - Núcleo de execução via CLI com provider de referência:
    - `run()` via `subprocess.run` (já consolidado em Execution).
    - `stream()` via `subprocess.Popen` (T4).
  - Tool calling:
    - `ToolCallingEngine` (Execution).
    - Integração `tool_calls` em `CodeAgent.run` (T7).
- Testes:
  - `pytest` completo passando (BDD + teste de integração de tool calling).
- Backlog:
  - T1–T7, T8–T15: T4 e T7 concluídas nesta sprint; demais já preparados em Execution (tests) ou planejados para sprints futuras.

---

## 3. O que funcionou bem

- Uso consistente de BDD/TDD como contrato para evolução do runtime.
- Separação clara de papéis:
  - `tdd_coder` focado em testes/BDD.
  - `forge_coder` cuidando de `src/**` apenas em Delivery.
- Adição do mecanismo `project/recommendations.md` para garantir reciclagem de recomendações entre sprints.
- Scripts de demo (`examples/sprint1_demo.sh`) ajudam stakeholders a ver valor rapidamente.

---

## 4. O que pode melhorar

- Medir e registrar cobertura de testes por sprint (não foi feito neste ciclo).
- Preencher datas reais e story points/capacity em `planning.md`/`progress.md` com mais precisão.
- Planejar com antecedência a evolução para segundo provider (Claude/Gemini) e integração CLI ↔ tool calling via JSON real.

---

## 5. Recomendações para Próximos Ciclos

Recomendações consolidadas em `project/recommendations.md`:

- **R-001** — Medir cobertura de testes por sprint (owner: sprint_coach + forge_coder; status: `pending`).
- **R-002** — Refinar datas reais e story points/capacity em artefatos de sprint (owner: sprint_coach; status: `pending`).

Estas recomendações devem ser consideradas no planejamento da Sprint 2.

---

## 6. Revisão Geral do Ciclo (Processo)

Além da análise de valor e métricas técnicas, este ciclo passou por uma revisão geral de processo conduzida por `jorge_the_forge`, com foco em:

- clarear os papéis de `tdd_coder` vs `forge_coder` (tests vs `src/**`);
- reforçar o uso de artefatos de sprint (`planning`, `progress`, `sessions`, `review`, `stakeholder-approval`);
- introduzir `project/recommendations.md` como registro vivo de melhorias a serem lidas pelo `sprint_coach` no início de cada sprint.

As principais melhorias de processo identificadas foram registradas como recomendações (R-001, R-002). A validação com stakeholders acontece nas revisões de sprint e neste documento de feedback, e o acompanhamento da execução fica a cargo do `sprint_coach` nas sprints subsequentes.

---

## 7. Decisão de Próximo Ciclo

- [x] Manter visão atual (não há necessidade de reabrir MDD).
- [x] Continuar expandindo ValueTracks existentes:
  - Evolução de providers (multi-provider).
  - Integração de tool calling via saída CLI real.
- [ ] Iniciar novos ValueTracks (a definir em roadmap futuro).
