# Sprint 3 - Planning

**Project**: forgeCodeAgent
**Sprint Number**: 3
**Sprint Duration**: 2025-12-07 – 2025-12-14 (planejada)
**Planning Date**: 2025-12-07
**Team**: Agent Coders (forge_coder + tdd_coder)
**Stakeholder**: [Stakeholder Name]

---

## 📊 Sprint Overview

### Sprint Goals

**Primary Goal**: Entregar configuração avançada de provider via arquivo (YAML simples) para o forgeCodeAgent, permitindo trocar de engine sem alterar o código de automação.

**Secondary Goals**:
- Consolidar a API `CodeAgent.from_config(...)` como complemento da configuração via ambiente (`from_env`).
- Demonstrar o fluxo de troca de provider via YAML em um script de demo (`examples/sprint3_demo.sh`).

**Success Criteria**:
- [x] Cenário BDD “Select provider from YAML configuration file without changing automation code” implementado e verde.
- [x] Tarefa T16 registrada como DONE em `specs/roadmap/BACKLOG.md`.
- [x] Demo Sprint 3 executável pela stakeholder.

---

## 📈 Capacity Planning

### Velocity Baseline

Com base nas Sprints 1 e 2:
- Entregas anteriores: T4, T7 (Sprint 1), multi-provider + from_env (Sprint 2).
- Capacidade efetiva: ~2×M de esforço por sprint.

### Capacity Calculation (Sprint 3)

- Itens planejados:
  - T16 (M) — provider via config externa/YAML.
- Ajustado para caber em 1 sessão focada (~2–3h).

---

## ✅ Features Selected (from BACKLOG)

### Committed Items

| ID  | Track                                 | Size | Priority | Status |
|-----|---------------------------------------|------|----------|--------|
| T16 | value_forge_core_code_agent_execution | M    | Média    | TODO   |

**Rationale**:
- T16 complementa T5 (troca de provider sem refatorar) adicionando configuração via arquivo, em linha com o comportamento mapeado em BDD.

---

## 🔗 Dependencies & Prerequisites

### Technical Dependencies

- [x] Multi-provider já implementado (`codex`, `claude`, `gemini`).
- [x] `CodeAgent.from_env()` em produção.
- [x] Cenário BDD YAML descrito em `10_code_agent_execution.feature`.

### Process Dependencies

- [x] T16 definido em `specs/roadmap/estimates.yml` e `BACKLOG.md`.
- [x] TDD (tdd_coder) já criou os testes/steps BDD correspondentes (RED → GREEN após implementação).

---

## ⚠️ Risks & Mitigation

### Risk 1: Complexidade excessiva na configuração
- **Mitigation**: manter o formato de arquivo minimalista (chave `provider`), deixando extensões futuras para novos incrementos.

### Risk 2: Divergência entre env e arquivo
- **Mitigation**: definir regras claras de precedência (arquivo primeiro; se ausente, cair para env/default) e testá-las explicitamente.

---

## 📋 Definition of Done (Sprint 3)

A Sprint 3 é considerada DONE quando:

- [x] `CodeAgent.from_config(...)` está implementado em `src/**` e coberto por testes BDD.
- [x] T16 está marcado como DONE no backlog.
- [x] `examples/sprint3_demo.sh` demonstra a troca de provider via YAML sem mudar código.
- [x] `project/sprints/sprint-3/progress.md`, `session-1.md`, `review.md`, `jorge-process-review.md` e `stakeholder-approval.md` estão preenchidos.
