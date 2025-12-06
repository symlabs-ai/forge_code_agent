# Sprint 1 - Planning

**Project**: forgeCodeAgent
**Sprint Number**: 1
**Sprint Duration**: [Start Date] - [End Date] (tipicamente 2 semanas)
**Planning Date**: 2025-12-05
**Team**: Agent Coders (forge_coder + tdd_coder)
**Stakeholder**: [Stakeholder Name]

---

## 📊 Sprint Overview

### Sprint Goals

**Primary Goal**: Consolidar o núcleo de execução do forgeCodeAgent com base no roadmap aprovado, iniciando a implementação de runtime real em `src/**` guiada pelos testes já consolidados.

**Secondary Goals** (se aplicável):
- Refinar a integração de streaming via CLI (T4) para o provider de referência.
- Preparar terreno para integração de tool calling com eventos CLI (T7) em sprint futura.

**Success Criteria**:
- [ ] Pelo menos 1 provider de referência com `run()` implementado via CLI real, mantendo BDD verde.
- [ ] Planejamento de streaming via CLI (T4) documentado e parcialmente explorado em código.
- [ ] Nenhum teste BDD existente quebrado ao final da sprint.

---

## 📈 Capacity Planning

### Velocity Baseline

Como esta é a primeira sprint do projeto, não há histórico de velocity; a capacidade será ajustada empiricamente.

### Capacity Calculation

**Sessions Available**: [N] sessões (estimado)
- Frequência: [X] sessões/semana × [2] semanas
- Duração: [2–3] horas por sessão (estimado)

**Projected Capacity**: conservadora, focada em poucas tarefas bem definidas.

---

## ✅ Features Selected (from BACKLOG.md)

### Committed Features

| Task ID | Track                                 | Story Points | Priority | Status |
|---------|---------------------------------------|-------------:|----------|--------|
| T4      | value_forge_core_code_agent_execution |            M | Alta     | TODO   |
| T7      | value_forge_core_tools_and_files      |            M | Média    | TODO   |

**Total Committed**: ~2×M (capacidade alvo inicial)

**Rationale**:
- T4 depende de T1–T3/T5, já marcadas como DONE no backlog e com testes cobrindo execução e streaming.
- T7 depende de T6, T8, T9 e T10–T15, já cobertos por testes; é um bom candidato para explorar em profundidade em sprint seguinte ou como preparação nesta sprint.

### Stretch Goals (Optional)

| Task ID | Track                                       | Story Points | Priority | Status |
|---------|---------------------------------------------|-------------:|----------|--------|
| —       | —                                           |            — | —        | —      |

**Stretch Conditions**:
- T4 avançou com segurança técnica e sem abrir dívidas.
- Há clareza suficiente para iniciar integração CLI ↔ tool calling (T7) sem reescrever a arquitetura definida.

---

## 🔗 Dependencies & Prerequisites

### Technical Dependencies

- [x] Roadmap aprovado (`specs/roadmap/ROADMAP.md`).
- [x] Backlog inicial definido (`specs/roadmap/BACKLOG.md`).
- [x] Testes BDD consolidados (`tests/bdd/**` verdes).

### Process Dependencies

- [x] Fase 5 (Execution) encerrada com handoff formal para Delivery.
- [ ] Ambiente de sprint/configuração de sessões (`project/sprints/sprint-1/progress.md`, `sessions/`) a ser criado pelo sprint_coach.

---

## ⚠️ Risks & Mitigation

### Risk 1: Complexidade de streaming via subprocess (T4)
- **Probability**: Média
- **Impact**: Alto
- **Mitigation**: começar com provider de referência único, preservar fallback já existente e manter BDD como contrato rígido.

### Risk 2: Acoplamento excessivo entre CLI e tool calling (T7)
- **Probability**: Média
- **Impact**: Médio
- **Mitigation**: seguir HLD/LLD e manter ToolCallingEngine isolado; introduzir integração em passos pequenos.

---

## 📋 Definition of Done (Sprint 1)

Esta sprint é considerada DONE quando:

- [ ] T4 tem implementação inicial em `src/**` via forge_coder, com BDD existente verde.
- [ ] Não há regressão nos cenários de tools/files e resiliência.
- [ ] `project/sprints/sprint-1/progress.md` registra sessões e resultados.
- [ ] `project/sprints/sprint-1/review.md` e `jorge-process-review.md` são preenchidos ao final da sprint.
