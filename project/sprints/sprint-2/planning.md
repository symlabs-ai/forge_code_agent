# Sprint 2 - Planning

**Project**: forgeCodeAgent
**Sprint Number**: 2
**Sprint Duration**: 2025-12-06 – 2025-12-20 (planejada)
**Planning Date**: 2025-12-06
**Team**: Agent Coders (forge_coder + tdd_coder)
**Stakeholder**: [Stakeholder Name]

---

## 📊 Sprint Overview

### Sprint Goals

**Primary Goal**: Entregar multi-provider real para o forgeCodeAgent (Codex + Claude + Gemini) com troca de engine via configuração simples, sem necessidade de refatorar scripts de automação.

**Secondary Goals**:
- Consolidar a API `CodeAgent.from_env()` como forma padrão de selecionar provider via configuração de ambiente.
- Documentar claramente uso multi-provider em docs de sprint e em script de demo (`examples/sprint2_demo.sh`).
- Incorporar recomendações R-001 e R-002 (cobertura de testes e capacidade/story points) ao fluxo de sprint.

**Success Criteria**:
- [ ] `CodeAgent.from_env()` funcionando para `codex`, `claude` e `gemini`, com testes cobrindo o comportamento.
- [ ] Script de demo da Sprint 2 (`examples/sprint2_demo.sh`) demonstrando troca de provider apenas via configuração (sem mudar código Python).
- [ ] Métrica de cobertura de testes medida pelo menos uma vez na sprint e registrada em `project/sprints/sprint-2/review.md`.

---

## 📈 Capacity Planning

### Velocity Baseline

A partir da Sprint 1:
- Features entregues: T4 (streaming via subprocess) e T7 (tool calling integrado ao runtime).
- Capacidade efetiva observada: ~2×M points / sprint.

### Capacity Calculation (Sprint 2)

**Sessions Available** (estimativa):
- Sessões: 1–2 sessões focadas em multi-provider.
- Duração: ~2–3h por sessão.

**Projected Capacity**:
- Foco em um ValueTrack bem definido (multi-provider), equivalente a ~2×M de esforço agregado, semelhante à Sprint 1.

---

## ✅ Features Selected (from BACKLOG / Recommendations)

Embora o `BACKLOG.md` atual (T1–T15) esteja marcado como concluído para o ciclo anterior, esta sprint nasce de recomendações e novos incrementos de valor:

### Committed Items

| Item | Origem                | Descrição                                                                 | Size | Status |
|------|-----------------------|---------------------------------------------------------------------------|------|--------|
| M1   | A2 (Sprint 1 Review)  | Suporte multi-provider real (Codex + Claude + Gemini) usando adapters.   | M    | TODO   |
| M2   | A2 (Sprint 1 Review)  | Seleção de provider via configuração (`CodeAgent.from_env`).             | S    | TODO   |
| M3   | R-001 (Recommendations) | Medir cobertura de testes e registrar na review da Sprint 2.           | XS   | TODO   |
| M4   | R-002 (Recommendations) | Ajustar planning/progress com capacidade/story points mais concretos. | XS   | TODO   |

**Total Committed**: ~2×M + 2×XS (alinhado à capacidade histórica).

### Stretch Goals (Optional)

| Item | Descrição                                                           | Size | Status |
|------|----------------------------------------------------------------------|------|--------|
| S1   | Explorar configuração futura via arquivo YAML (providers e comandos) | M    | TODO   |

Stretch só é considerado se M1–M4 estiverem concluídos com conforto.

---

## 🔗 Dependencies & Prerequisites

### Technical Dependencies

- [x] Runtime base implementado (`src/forge_code_agent/**`) com provider Codex-like.
- [x] Adapters de CLI estruturados (`adapters/cli/base.py`, `codex.py`).
- [x] BDD e testes gerais (`tests/**`) verdes.

### Process Dependencies

- [x] Ciclo anterior encerrado com feedback em `project/docs/feedback/cycle-01.md`.
- [x] Recomendações registradas em `project/recommendations.md` (R-001 e R-002).
- [ ] Atualização de `process/process_execution_state.md` para refletir Sprint 2 ao final da entrega.

---

## ⚠️ Risks & Mitigation

### Risk 1: Divergência de comportamento entre providers
- **Probability**: Média
- **Impact**: Médio
- **Mitigation**: manter contrato uniforme em `ExecutionResult` e nos eventos de stream; usar testes parametrizados por provider.

### Risk 2: Configuração pouco clara para usuários
- **Probability**: Média
- **Impact**: Alto
- **Mitigation**: documentar claramente `FORGE_CODE_AGENT_PROVIDER` e o uso de `CodeAgent.from_env()` na demo da sprint e nos artefatos de review.

### Risk 3: Cobertura de testes não medida de forma sistemática
- **Probability**: Baixa (dado o foco explícito)
- **Impact**: Médio
- **Mitigation**: incluir passo explícito no checklist da sprint para rodar `pytest --cov` e registrar o valor em `review.md`.

---

## 📋 Definition of Done (Sprint 2)

A Sprint 2 é considerada DONE quando:

- [ ] M1 e M2 estão implementados em `src/**` com testes passando (incluindo `tests/test_multi_provider_integration.py`).
- [ ] `examples/sprint2_demo.sh` demonstra multi-provider com troca via configuração (sem alterar código Python).
- [ ] Cobertura de testes foi medida pelo menos uma vez durante a sprint e o valor registrado em `project/sprints/sprint-2/review.md`.
- [ ] `project/sprints/sprint-2/progress.md` e `sessions/*.md` refletem o trabalho executado.
- [ ] `project/sprints/sprint-2/review.md` e `jorge-process-review.md` estão preenchidos e há aprovação em `stakeholder-approval.md`.
