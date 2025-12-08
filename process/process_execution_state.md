# ForgeProcess — Roteiro Operacional & Estado de Execução

> Documento de referência para **symbiotas** e humanos seguirem o fluxo
> completo do ForgeProcess (MDD → BDD → Execution → Delivery → Feedback),
> com **checklists por etapa** e **arquivos obrigatórios**.
>
> Objetivo: evitar “atalhos” (ex.: pular Roadmap Planning e ir direto para TDD)
> e manter um ponto único de verdade sobre o estado atual da execução.
>
> **Regra operacional para symbiotas:** no início de **cada fase** (MDD, BDD,
> Execution, Delivery, Feedback), o symbiota responsável por aquela fase deve
> ser carregado/ativado para conduzir a execução junto ao usuário, atuando como
> facilitador e executor das tarefas daquela fase. A cada etapa concluída,
> esse symbiota (ou o orquestrador que o invocou) deve **atualizar o progresso**
> neste arquivo (`process/process_execution_state.md`), marcando os checkboxes
> relevantes e ajustando `current_phase`, `last_completed_step` e
> `next_recommended_step`.

---

## 0. Convenções gerais

- Sempre seguir a ordem macro (não inverter):
  - Intenção de valor → **MDD** → **BDD** → **Execution (Roadmap → TDD)** → **Delivery (Sprint + Review)** → **Feedback**.
- Arquitetura e backlog **NUNCA** são definidos dentro do TDD:
  - TDD implementa o que já está definido em `specs/roadmap/` (principalmente `BACKLOG.md`).
  - Roadmap Planning é o lugar para validar arquitetura, dependências e priorização.
- Persistência:
  - Artefatos em Markdown/YAML, versionados em Git.
  - Commits preferencialmente por etapa/fase, com mensagem clara.
- CLI-first (para produtos CLI, como forgeCodeAgent):
  - A interface primária de validação deve ser uma **CLI oficial** (ex.: `forge-code-agent ...`), não apenas a API Python.
  - Para cada funcionalidade exposta em `src/**` que faça parte de um ValueTrack, deve existir um comando correspondente na CLI oficial.
  - Scripts em `examples/` existem para **exercitar fluxos end-to-end via CLI oficial** (por sprint e por ValueTrack), não para testar apenas funções/mocks diretamente em Python.
- Symbiotas relevantes:
  - `mdd_coach`, `mdd_publisher`
  - `bdd_coach`
  - `roadmap_coach`, `execution_coach`, `mark_arc`
  - `tdd_coder`, `forge_coder`
  - `sprint_coach`, `delivery_coach`
  - `bill_review`, `jorge_the_forge`

---

## 1. Estado atual do ForgeProcess (preencher e manter)

> Campo de **estado vivo** para ser atualizado pelos agentes/symbiotas.
> Pode ser usado pelo orquestrador para saber onde o projeto está.

- [x] `current_phase`: `delivery.sprint`
- [x] `current_cycle`: `cycle-03`
- [x] `current_sprint`: `sprint-05`
- [x] `last_completed_step`: `execution.tdd.phase_3_minimal_implementation`
- [x] `next_recommended_step`: `delivery.sprint.sprint_planning`

> Convenção sugerida: atualizar este bloco ao final de cada etapa significativa
> (pelo menos por fase) para facilitar handoffs entre agentes.

---

## 2. Bootstrap do projeto

- [x] Verificar estrutura mínima:
  - [x] Diretórios: `process/`, `specs/`, `project/`, `src/`, `tests/`
  - [x] Arquivos: `process/PROCESS.yml`, `process/README.md`
- [x] Criar hipótese inicial (se não existir):
  - [x] `docs/hipotese.md` (template: `process/mdd/templates/template_hipotese.md`)
- [x] Atualizar estado:
  - [x] `current_phase = mdd`
  - [x] `last_completed_step = mdd.etapa_01_concepcao`
  - [x] `next_recommended_step = mdd.etapa_02_sintese`

---

## 3. Fase MDD — Market Driven Development

Referência: `process/mdd/PROCESS.yml`

> Symbiota responsável pela fase (etapas 3.1 a 3.6): `mdd_coach`.
> Revisor de processo ao final da fase: `jorge_the_forge` (audita se o MDD seguiu o ForgeProcess).

### 3.1 Etapa 01 — Concepção da Visão

- Entradas:
  - [x] `docs/hipotese.md`
- Saídas (criar/preencher):
  - [x] `docs/visao.md` (template: `process/mdd/templates/template_visao.md`)
- Critério de conclusão:
  - [x] Visão aprovada pelo stakeholder (decisão `validar_visao = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = mdd.etapa_01_concepcao`
    - [x] `next_recommended_step = mdd.etapa_02_sintese`

### 3.2 Etapa 02 — Síntese Executiva

- Entradas:
  - [x] `docs/visao.md`
- Saídas:
  - [x] `docs/sumario_executivo.md` (template: `process/mdd/templates/template_sumario_executivo.md`)
  - [ ] (opcional) `output/docs/sumario_executivo.pdf` — gerado por `mdd_publisher`
- Critério de conclusão:
  - [x] Síntese aprovada (`validar_sintese = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = mdd.etapa_02_sintese`
    - [x] `next_recommended_step = mdd.etapa_03_pitch`

### 3.3 Etapa 03 — Pitch de Valor

- Entradas:
  - [x] `docs/visao.md`
  - [x] `docs/sumario_executivo.md`
- Saídas:
  - [x] `docs/pitch_deck.md` (template: `process/mdd/templates/template_pitch_deck.md`)
  - [ ] (opcional) `output/docs/pitch_deck.pptx` — gerado por `mdd_publisher`
- Critério de conclusão:
  - [x] Pitch aprovado (`validar_pitch = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = mdd.etapa_03_pitch`
    - [x] `next_recommended_step = mdd.etapa_04_validacao`

### 3.4 Etapa 04 — Validação Pública Inicial

- Entradas:
  - [x] `docs/visao.md`
  - [x] `docs/sumario_executivo.md`
  - [x] `docs/pitch_deck.md`
- Saídas:
  - [x] `docs/sites/site_A.md` (template: `process/mdd/templates/template_site.md`)
  - [x] `docs/sites/site_B.md` (template: `process/mdd/templates/template_site.md`)
  - [x] `docs/sites/site_C.md` (template: `process/mdd/templates/template_site.md`)
  - [ ] (opcionais) `output/docs/sites/site_*.html` — por `mdd_publisher`
  - [x] `docs/resultados_validacao.md` (template: `process/mdd/templates/template_resultados_validacao.md`)
  - [ ] (opcional) `output/docs/resultados_validacao.html`
- Critério de conclusão:
  - [x] Stakeholder confirma que dados de validação estão prontos (`validar_landing_pages = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = mdd.etapa_04_validacao`
    - [x] `next_recommended_step = mdd.etapa_05_avaliacao`

### 3.5 Etapa 05 — Avaliação Estratégica

- Entradas:
  - [x] `docs/resultados_validacao.md`
- Saídas (uma ou mais, dependendo da decisão):
  - [x] `docs/aprovacao_mvp.md` (template: `process/mdd/templates/template_aprovacao_mvp.md`)
  - [ ] `docs/revisao_estrategica.md` (template: `process/mdd/templates/template_revisao_estrategica.md`)
  - [ ] `docs/rejeicao_projeto.md` (template: `process/mdd/templates/template_rejeicao_projeto.md`)
- Critério de conclusão:
  - [x] Decisão do stakeholder (`decisao_mvp` = `approved` | `needs_revision` | `rejected`)
  - Se `needs_revision`: voltar para Etapa 01 e atualizar estado.
  - Se `rejected`: macro-processo termina (`end_projeto_rejeitado`).
  - Se `approved`:
    - [x] `next_recommended_step = mdd.etapa_06_handoff`

### 3.6 Etapa 06 — Handoff para BDD

- Entradas:
  - [x] `docs/aprovacao_mvp.md`
- Saídas:
  - [x] `docs/handoff_bdd.md` (template: `process/mdd/templates/template_handoff_bdd.md`)
- Critério de conclusão:
  - [x] Handoff concluído (`return_approved`)
  - Atualizar estado:
    - [x] `current_phase = bdd`
    - [x] `last_completed_step = mdd.etapa_06_handoff`
    - [x] `next_recommended_step = bdd.etapa_01_mapeamento`

---

## 4. Fase BDD — Behavior Driven Development

Referência: `process/bdd/PROCESS.yml`

> Symbiota responsável pela fase (etapas 4.1 a 4.6): `bdd_coach`.
> Revisor de processo ao final da fase: `jorge_the_forge` (audita se o BDD seguiu o ForgeProcess).

### 4.1 Etapa 01 — Mapeamento de Comportamentos

- Entradas:
  - [x] `docs/visao.md`
  - [x] `docs/aprovacao_mvp.md`
- Saídas:
  - [x] `specs/bdd/drafts/behavior_mapping.md`
- Critério de conclusão:
  - [x] Mapeamento aprovado (`validar_mapeamento = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = bdd.etapa_01_mapeamento`
    - [x] `next_recommended_step = bdd.etapa_02_features`

### 4.2 Etapa 02 — Escrita de Features Gherkin

- Entradas:
  - [x] `specs/bdd/drafts/behavior_mapping.md`
- Saídas:
  - [x] `specs/bdd/**/*.feature` (cenários Given/When/Then, linguagem de negócio)
- Critério de conclusão:
  - [x] Features aprovadas (`validar_features = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = bdd.etapa_02_features`
    - [x] `next_recommended_step = bdd.etapa_03_organizacao`

### 4.3 Etapa 03 — Organização e Tagging

- Entradas:
  - [x] `specs/bdd/**/*.feature`
- Saídas:
  - [x] Estrutura de pastas organizada (10_, 20_, 30_, etc.) em `specs/bdd/`
  - [x] Tags aplicadas (@ci-fast, @ci-int, @e2e) em todas as features
  - [x] `specs/bdd/README.md` atualizado
- Critério de conclusão:
  - [x] Organização e tags aprovadas (`validar_organizacao = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = bdd.etapa_03_organizacao`
    - [x] `next_recommended_step = bdd.etapa_04_tracks`

### 4.4 Etapa 04 — Criação de tracks.yml

- Entradas:
  - [x] `specs/bdd/**/*.feature`
  - [x] `docs/visao.md`
- Saídas:
  - [x] `specs/bdd/tracks.yml`
- Critério de conclusão:
  - [x] tracks.yml aprovado (`validar_tracks = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = bdd.etapa_04_tracks`
    - [x] `next_recommended_step = bdd.etapa_05_skeleton`

### 4.5 Etapa 05 — Skeleton de Automação

- Entradas:
  - [x] `specs/bdd/**/*.feature`
- Saídas:
  - [x] `tests/bdd/test_*_steps.py`
  - [x] `tests/bdd/conftest.py`
  - [x] `pytest.ini`
- Critério de conclusão:
  - [x] Skeleton aprovado (`validar_skeleton = approved`)
  - Atualizar estado:
    - [x] `last_completed_step = bdd.etapa_05_skeleton`
    - [x] `next_recommended_step = bdd.etapa_06_handoff`

### 4.6 Etapa 06 — Handoff para Roadmap Planning

- Entradas:
  - [x] `specs/bdd/**/*.feature`
  - [x] `specs/bdd/tracks.yml`
  - [x] `tests/bdd/`
- Saídas:
  - [x] `specs/bdd/HANDOFF_BDD.md`
- Critério de conclusão:
  - [x] Tech lead confirma completude (`decisao_completude = complete`)
  - Atualizar estado:
    - [x] `current_phase = execution.roadmap_planning`
    - [x] `last_completed_step = bdd.etapa_06_handoff`
    - [x] `next_recommended_step = execution.roadmap_planning.etapa_00_validacao_stakeholder`

---

## 5. Fase Execution — Roadmap Planning + TDD

Referência: `process/execution/PROCESS.yml`

### IMPORTANTE — Ordem obrigatória dentro de Execution

- [ ] **NUNCA** chamar `tdd_coder` direto logo após BDD.
- [ ] Sempre seguir:
  - [ ] `execution.roadmap_planning` → gerar `specs/roadmap/*`
  - [ ] **só depois** `execution.tdd` (TDD Workflow)
- TDD só começa se:
  - [ ] `specs/roadmap/ROADMAP.md` existir
  - [ ] `specs/roadmap/BACKLOG.md` existir
  - [ ] O núcleo do ForgeBase estiver instalado e importável no ambiente (ver `docs/guides/forgebase_guides/forgebase_install.md`)
  - [ ] Ambiente de testes e hooks de pre-commit estiverem configurados (virtualenv, pytest/pytest-bdd, pre-commit + ruff conforme `temp/setup-git.txt`)

### 5.1 Roadmap Planning (execution.roadmap_planning)

Referência: `process/execution/roadmap_planning/PROCESS.yml`

> Symbiotas por intervalo de etapas desta fase:
> - Etapas 5.1.1–5.1.2 (validação arquitetural + stack/ADRs): `mark_arc` (análise arquitetural ForgeBase).
> - Etapas 5.1.3–5.1.6 (dependências, quebra, estimativa, backlog): `roadmap_coach`.

#### 5.1.1 Etapa 00 — Validação Arquitetural com Stakeholders

- Entradas:
  - [x] `docs/visao.md`
  - [x] `specs/bdd/*.feature`
  - [x] `specs/bdd/tracks.yml`
- Saídas:
  - [x] `specs/roadmap/ARCHITECTURAL_QUESTIONNAIRE.md`
  - [x] `specs/roadmap/ARCHITECTURAL_DECISIONS_APPROVED.md`
- Critério de conclusão:
  - [x] Stakeholder aprova propostas (`decisao_aprovacao_arquitetura = approved`)

#### 5.1.2 Etapa 01 — Definição Arquitetural e Stack (ADR)

- Entradas:
  - [x] `specs/roadmap/ARCHITECTURAL_DECISIONS_APPROVED.md`
- Saídas:
  - [x] `specs/roadmap/TECH_STACK.md`
  - [x] `specs/roadmap/ADR.md`
  - [x] `specs/roadmap/adr/*.md`
  - [x] `specs/roadmap/HLD.md`
  - [x] `specs/roadmap/LLD.md`

#### 5.1.3 Etapa 02 — Análise de Dependências

- Entradas:
  - [x] `specs/bdd/tracks.yml`
  - [x] `specs/bdd/**/*.feature`
- Saídas:
  - [x] `specs/roadmap/dependency_graph.md`

#### 5.1.4 Etapa 03 — Quebra de Features

- Entradas:
  - [x] `specs/bdd/**/*.feature`
  - [x] `specs/roadmap/dependency_graph.md`
- Saídas:
  - [x] `specs/roadmap/feature_breakdown.md`

#### 5.1.5 Etapa 04 — Estimativa e Priorização

- Entradas:
  - [x] `specs/roadmap/feature_breakdown.md`
  - [x] `specs/roadmap/dependency_graph.md`
- Saídas:
  - [x] `specs/roadmap/estimates.yml`

#### 5.1.6 Etapa 05 — Criação do Roadmap e Backlog

- Entradas:
  - [x] `specs/roadmap/estimates.yml`
  - [x] `specs/roadmap/dependency_graph.md`
- Saídas:
  - [x] `specs/roadmap/ROADMAP.md`
  - [x] `specs/roadmap/BACKLOG.md`
- Critério de conclusão:
  - [x] Tech lead aprova roadmap (`decisao_aprovacao_roadmap = approved`) — aprovador: _stakeholder/tech lead deste projeto_
  - Atualizar estado:
    - [x] `current_phase = execution.tdd`
    - [x] `last_completed_step = execution.roadmap_planning.etapa_05_roadmap_backlog`
    - [x] `next_recommended_step = execution.tdd.phase_1_selecao`

### 5.2 TDD Workflow (execution.tdd)

Referência: `process/execution/tdd/PROCESS.yml`

> Symbiota responsável por esta fase: `tdd_coder` (seleciona tarefa, escreve e consolida testes/steps BDD, sem alterar `src/**`).
> Regra: **TDD SEMPRE parte de um item do `BACKLOG.md` e entrega uma suíte de testes pronta para o forge_coder usar em Delivery.**

#### 5.2.1 Phase 1 — Seleção da Tarefa e BDD Scenarios

- Entradas:
  - [ ] `specs/roadmap/BACKLOG.md`
  - [ ] `specs/bdd/**/*.feature`
- Saídas:
  - [ ] `tests/bdd/test_*_steps.py` (arquivo de teste preparado/focado na tarefa)

#### 5.2.2 Phase 2 — Test Setup (RED)

- Entradas:
  - [ ] `specs/bdd/**/*.feature`
- Saídas:
  - [ ] `tests/bdd/test_*.py` com teste falhando (RED)

#### 5.2.3 Phase 3 — Minimal Implementation (GREEN - Testes)

- Entradas:
  - [ ] `tests/bdd/test_*.py`
- Saídas:
  - [ ] `tests/**/*.py` verdes para a tarefa selecionada (cobertura comportamental garantida pelo `tdd_coder`).
  - Observação: qualquer implementação de código em `src/**` decorrente desses testes deve ser realizada pelo `forge_coder` na Fase 6 (Delivery/Sprint).

> Revisor de processo ao final da fase 5 (Execution): `jorge_the_forge` (audita se Roadmap Planning + TDD seguiram o ForgeProcess, incluindo relação com BDD, backlog e limites de escopo entre tdd_coder e forge_coder).

### Handoff Execution → Delivery

- Critério para encerrar a Fase 5 (Execution) em um ciclo:
  - [ ] `specs/roadmap/ROADMAP.md` e `specs/roadmap/BACKLOG.md` existentes e aprovados (5.1 concluída).
  - [ ] Tarefas selecionadas do backlog cobertas por testes BDD/pytest verdes (`tests/bdd/**`) para o escopo deste ciclo (5.2.3 concluída para essas tarefas).
  - [ ] Revisão de processo da Fase 5 realizada por `jorge_the_forge`, confirmando aderência ao ForgeProcess e limites de escopo entre `tdd_coder` e `forge_coder`.
- Ao concluir Execution para o ciclo atual:
  - Atualizar estado neste arquivo:
    - [ ] `current_phase = delivery.sprint`
    - [ ] `last_completed_step = execution.tdd.phase_3_minimal_implementation`
    - [ ] `next_recommended_step = delivery.sprint.sprint_planning`
  - Orquestração:
    - [ ] Carregar/ativar `sprint_coach` e `forge_coder` para iniciar a Fase 6 (Sprint Planning e Session Implementation).

---

## 6. Fase Delivery — Sprint + Review

Referência: `process/delivery/PROCESS.yml`

### 6.1 Sprint (delivery.sprint)

Referência: `process/delivery/sprint/PROCESS.yml`

> Symbiota responsável por facilitar a fase (etapas 6.1.1–6.1.5): `sprint_coach`.
> Symbiota executor de código nas etapas de implementação/commit (6.1.3 e 6.1.5): `forge_coder`.

#### 6.1.1 Sprint Planning

- Entradas:
  - [ ] `specs/roadmap/BACKLOG.md`
- Saídas:
  - [ ] `project/sprints/sprint-N/planning.md`

#### 6.1.2 Session Mini-Planning

- Entradas:
  - [ ] `project/sprints/sprint-N/planning.md`
- Saídas:
  - [ ] `project/sprints/sprint-N/sessions/session-M.md`

#### 6.1.3 Session Implementation

> Symbiota executor de código na sessão: `forge_coder` (implementa features usando TDD, seguindo arquitetura ForgeBase).

- Entradas:
  - [ ] `project/sprints/sprint-N/sessions/session-M.md`
- Saídas:
  - [ ] `src/**/*.py`
  - [ ] `tests/**/*.py`

#### 6.1.4 Session Review

- Entradas:
  - [ ] `src/**/*.py`
  - [ ] `tests/**/*.py`
- Saídas:
  - [ ] `project/sprints/sprint-N/sessions/session-M.md` atualizado com resultado

#### 6.1.5 Session Commit

- Saídas:
  - [ ] `project/sprints/sprint-N/progress.md`
- Critério:
  - [ ] Se `sprint.has_remaining_sessions()` → repetir mini-planning/implementation/review/commit.
  - [ ] Senão → `session_complete` e Delivery chama Review.

### 6.2 Review (delivery.review)

Referência: `process/delivery/review/PROCESS.yml`

#### 6.2.1 Day 1 — bill-review (Technical)

- Entradas:
  - [ ] `src/**/*.py`
  - [ ] `tests/**/*.py`
  - [ ] `specs/bdd/**/*.feature`
- Saídas:
  - [ ] `project/sprints/sprint-N/review.md`

#### 6.2.2 Day 2 — Jorge the Forge (Process)

- Entradas:
  - [ ] `project/sprints/sprint-N/review.md`
  - [ ] `project/sprints/sprint-N/planning.md`
  - [ ] `project/sprints/sprint-N/progress.md`
- Saídas:
  - [ ] `project/sprints/sprint-N/jorge-process-review.md`

#### 6.2.3 Day 3 — Stakeholder Review & Deploy

- Entradas:
  - [ ] `project/sprints/sprint-N/review.md`
  - [ ] `project/sprints/sprint-N/jorge-process-review.md`
- Saídas:
  - [ ] `project/sprints/sprint-N/stakeholder-approval.md`
- Decisão:
  - [ ] Se `approved` e `!backlog.has_pending_items()` → `deployed`.
  - [ ] Se `needs_fixes` → volta a Sprint.
  - [ ] Se `needs_revision`/`rollback` → Execution precisa revisar (típico).
- Atualizar estado:
  - [ ] `current_phase = feedback` (quando `return_deployed`)
  - [ ] `last_completed_step = delivery.review.stakeholder_review`
  - [ ] `next_recommended_step = feedback.feedback_collect`

> Revisores ao final da fase 6 (Delivery):
> - `bill_review` — revisão técnica da sprint e do incremento entregue;
> - `jorge_the_forge` — revisão de processo da sprint (compliance com ForgeProcess).

#### 6.2.4 Demo Script por Sprint (focado em E2E)

- Antes ou durante a etapa de Review/Stakeholder Validation, o `forge_coder` deve:
  - [ ] Criar (ou atualizar) um script de demo específico da sprint em `examples/` (ex.: `examples/sprint1_demo.sh`, `examples/sprint2_demo.sh`),
        **apenas quando houver algo a demonstrar em termos de fluxo end-to-end** (por exemplo, integração com provider real, MCP, gateway externo).
  - [ ] Garantir que o script:
        - explique no início, via `echo`, o que será demonstrado;
        - use o runtime atual do projeto (via instalação local ou `PYTHONPATH`) **para chamar a CLI oficial do produto** (ex.: `forge-code-agent run ...`, `forge-code-agent stream ...`), em vez de invocar diretamente funções Python internas;
        - execute um cenário equivalente a pelo menos um teste `@e2e` (ou, na ausência de marcação explícita, um fluxo que dependa de integrações externas reais);
        - seja simples de rodar para o stakeholder (`./examples/sprintN_demo.sh`).
  - [ ] Em sprints que só entregam lógica interna/mocks (sem integrações externas), o uso de `examples/` é opcional; a validação pode ser feita exclusivamente via testes automatizados (`pytest`, BDD, etc.).
  - [ ] Referenciar o script de demo em `project/sprints/sprint-N/review.md` e em `project/sprints/sprint-N/stakeholder-approval.md` como parte das demos executadas, quando aplicável.

#### 6.2.5 Scripts de ValueTrack por Ciclo (CLI-first)

- Ao concluir um ValueTrack em nível de ciclo (por exemplo, execução via CLI, tools/files, observabilidade), o time deve:
  - [ ] Criar um script agregador em `examples/` (ex.: `examples/valuetrack_code_agent_execution.sh`) que:
        - utilize **somente a CLI oficial** para demonstrar, em sequência, todas as funcionalidades cobertas por aquele ValueTrack;
        - possa ser rodado pelo stakeholder como demo de “fechamento de ciclo” para aquele ValueTrack.
  - [ ] Atualizar o feedback de ciclo correspondente (`project/docs/feedback/cycle-XX.md`) mencionando esse script como referência principal de demo E2E do ValueTrack.

### Handoff Delivery → Feedback

- Critério para encerrar a Fase 6 (Delivery) em um ciclo:
  - [ ] `project/sprints/sprint-N/review.md` consolidado (bill-review técnico concluído).
  - [ ] `project/sprints/sprint-N/jorge-process-review.md` consolidado (review de processo concluído).
  - [ ] `project/sprints/sprint-N/stakeholder-approval.md` com decisão `approved`.
  - [ ] `!backlog.has_pending_items()` para o escopo definido do ciclo/sprint.
- Ao atingir esses critérios:
  - Confirmar as checkboxes de “Atualizar estado” na seção 6.2.3:
    - [ ] `current_phase = feedback`
    - [ ] `last_completed_step = delivery.review.stakeholder_review`
    - [ ] `next_recommended_step = feedback.feedback_collect`
  - Orquestração:
    - [ ] Encerrar a sprint corrente.
    - [ ] Carregar/ativar `jorge_the_forge` (ou agente equivalente) para conduzir a Fase 7 (Feedback), registrando métricas, aprendizados e decisões de próximo ciclo.

---

## 7. Fase Feedback — Reflexão e Próximos Ciclos

Referência: macro em `process/PROCESS.yml` (phases.feedback)

### 7.1 Coletar Feedback

- Entradas (exemplos):
  - [x] Métricas operacionais (logs, observabilidade) — neste ciclo, centradas em testes/verdes e entregas de sprint.
  - [x] KPIs de valor definidos na visão / tracks — para o MVP atual (execução básica via CLI + tools/files + resiliência).
- Saídas:
  - [x] Registro de métricas e observações (`project/docs/feedback/cycle-01.md`)

### 7.2 Analisar Feedback

- Atividades:
  - [x] Analisar dados, comparar com KPIs
  - [x] Sugerir ajustes de visão, novos ValueTracks ou encerrar ciclo
  - [x] Conduzir uma **revisão geral de ciclo** (liderada por `jorge_the_forge`), identificando melhorias de processo, gaps de artefatos e ajustes de papéis entre symbiotas.

### 7.3 Decisões de ciclo

- [x] Decisão 1 — Visão precisa mudar?
  - [ ] Se **sim**:
    - [ ] `current_phase = mdd`
    - [ ] `next_recommended_step = mdd.etapa_01_concepcao`
  - [x] Se **não**:
    - [x] Decisão 2 — Há mais ValueTracks a implementar?
      - [ ] Se “continuar”:
        - [ ] `current_phase = bdd`
        - [ ] `next_recommended_step = bdd.etapa_01_mapeamento`
      - [x] Se “completo”:
        - [x] Antes de considerar o ciclo completo, verificar:
          - [x] Para cada ValueTrack crítico que dependa de integrações externas (ex.: providers reais, MCPs, gateways), existe **pelo menos um cenário BDD marcado com `@e2e`** passando em ambiente controlado.
          - [x] Os testes de integração correspondentes (`pytest -m e2e` ou suíte equivalente) foram executados com sucesso pelo menos uma vez neste ciclo.
          - [x] Qualquer limitação conhecida (ex.: provider ainda simulado) está explicitamente registrada em `project/docs/feedback/cycle-XX.md` e **não** é mascarada como entrega completa.
        - [x] Somente após esses critérios, marcar `end_ciclo_completo`.
        - [x] Consolidar as melhorias de processo identificadas na revisão geral do ciclo em `project/recommendations.md`, com:
          - `owner_symbiota` explícito,
          - `status` inicial (`pending`),
          - notas sobre a discussão/validação com stakeholders.
        - [x] Garantir que o `sprint_coach` leia `project/recommendations.md` no planejamento da próxima sprint e acione as recomendações pertinentes.

> Revisão e registro de aprendizados ao final da fase 7 (Feedback):
> - `jorge_the_forge` é responsável por consolidar aprendizados de processo e atualizar artefatos de feedback;
> - `bill_review` pode ser invocado para revisar implicações técnicas identificadas no feedback, mas o registro formal de aprendizados é conduzido por Jorge.

---

## 8. Regras específicas para symbiotas (resumo rápido)

- `tdd_coder`:
  - [ ] Nunca iniciar implementação se `specs/roadmap/BACKLOG.md` não existir.
  - [ ] Em caso de ausência, registrar no contexto: “É necessário rodar Roadmap Planning antes do TDD” e solicitar intervenção de `roadmap_coach`.
  - [ ] **Escopo restrito a testes**: só criar/alterar `tests/**` (step definitions e testes); **nunca** alterar `src/**`. Se a implementação exigir mudanças em runtime/código de produção, registrar/usar item de backlog e acionar o `forge_coder` na fase 6 (Delivery/Sprint).
- `forge_coder`:
  - [ ] Implementar e commitar código principalmente durante a fase de Delivery (sprints), seguindo TDD e a arquitetura definida em Execution.
  - [ ] Trabalhar sempre em cima de itens do backlog definidos e aprovados; não inventar escopo novo durante a sprint.
- `roadmap_coach`:
  - [ ] Sempre produzir pelo menos: `TECH_STACK.md`, `HLD.md`, `LLD.md`, `ROADMAP.md`, `BACKLOG.md`.
- `execution_coach`:
  - [ ] Garantir que o fluxo BDD → Roadmap Planning → TDD seja respeitado, sem pular etapas.
  - [ ] Manter `current_phase` e `next_recommended_step` coerentes ao transitar entre `execution.roadmap_planning`, `execution.tdd` e `delivery.sprint`.
- `mark_arc`:
  - [ ] Conduzir a análise arquitetural nas etapas 00 e 01 de Roadmap Planning, alinhando decisões à arquitetura ForgeBase.
  - [ ] Apoiar a criação de TECH_STACK, ADRs, HLD e LLD coerentes com as regras do ForgeBase.
- `bdd_coach`:
  - [ ] Garantir que **todo ValueTrack** relevante do MDD está coberto por features e mapeado em `tracks.yml`.
- `sprint_coach`:
  - [ ] Facilitar Sprint Planning e Session Mini-Planning, mantendo `planning.md`, `sessions/*.md` e `progress.md` atualizados.
  - [ ] Coordenar o trabalho do `forge_coder` dentro de cada sessão de sprint.
- `delivery_coach`:
  - [ ] Coordenar a fase de Delivery como um todo, garantindo que sprint e review sigam o processo descrito em `process/delivery/`.
  - [ ] Orquestrar a execução de `bill_review` e `jorge_the_forge` no final de cada sprint.
- `bill_review` e `jorge_the_forge`:
  - [ ] Usar este arquivo como referência de “fluxo ideal” ao avaliar compliance.

Este arquivo deve ser atualizado incrementalmente durante a execução
para refletir o estado real do projeto e servir de **roteiro único**
para agentes humanos e symbiotas.
