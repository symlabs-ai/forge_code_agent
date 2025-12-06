# BACKLOG — forgeCodeAgent

> Versão: 0.1
> Responsável: roadmap_coach
> Fonte: `feature_breakdown.md`, `estimates.yml`

---

## 1. Lista de Tarefas (T1–T15)

| ID  | Track                                   | Size | Prioridade | Status   | Feature BDD                                               |
|-----|-----------------------------------------|------|-----------|----------|-----------------------------------------------------------|
| T1  | value_forge_core_code_agent_execution   | S    | Alta      | DONE     | 10_code_agent_execution.feature                           |
| T2  | value_forge_core_code_agent_execution   | S    | Alta      | DONE     | 10_code_agent_execution.feature                           |
| T3  | value_forge_core_code_agent_execution   | M    | Alta      | DONE     | 10_code_agent_execution.feature                           |
| T4  | value_forge_core_code_agent_execution   | M    | Alta      | DONE     | 10_code_agent_execution.feature                           |
| T5  | value_forge_core_code_agent_execution   | S    | Alta      | DONE     | 10_code_agent_execution.feature                           |
| T6  | value_forge_core_tools_and_files        | M    | Média     | DONE     | 11_code_agent_tools_and_files.feature                     |
| T7  | value_forge_core_tools_and_files        | M    | Média     | DONE     | 11_code_agent_tools_and_files.feature                     |
| T8  | value_forge_core_tools_and_files        | M    | Média     | DONE     | 11_code_agent_tools_and_files.feature                     |
| T9  | value_forge_core_tools_and_files        | S    | Alta      | DONE     | 11_code_agent_tools_and_files.feature                     |
| T10 | support_observability_code_agent_resilience | S | Alta      | DONE     | 50_code_agent_resilience.feature                          |
| T11 | support_observability_code_agent_resilience | XS| Alta      | DONE     | 50_code_agent_resilience.feature                          |
| T12 | support_observability_code_agent_resilience | S | Alta      | DONE     | 50_code_agent_resilience.feature                          |
| T13 | support_observability_code_agent_resilience | S | Média     | DONE     | 50_code_agent_resilience.feature                          |
| T14 | support_observability_code_agent_resilience | S | Média     | DONE     | 50_code_agent_resilience.feature                          |
| T15 | support_observability_code_agent_resilience | S | Média     | DONE     | 50_code_agent_resilience.feature                          |

---

## 2. Próximas Tarefas Planejadas

Além das tarefas T1–T15 (núcleo do ciclo atual), o roadmap prevê um incremento de configuração avançada:

| ID  | Track                                   | Size | Prioridade | Status   | Feature BDD                                               |
|-----|-----------------------------------------|------|-----------|----------|-----------------------------------------------------------|
| T16 | value_forge_core_code_agent_execution   | M    | Média     | TODO     | 10_code_agent_execution.feature (cenário futuro via YAML) |

Notas:
- T16 implementa o comportamento “Select provider from YAML configuration file” mapeado em `specs/bdd/drafts/behavior_mapping.md`.
- A execução de T16 deve respeitar o fluxo BDD → TDD → Delivery:
  - BDD: detalhar/ativar o cenário correspondente em `.feature`.
  - TDD: `tdd_coder` cria testes para instanciar `CodeAgent` a partir de config YAML.
  - Delivery: `forge_coder` implementa o carregamento de configuração (ex.: `CodeAgent.from_config`).

---

## 2. Notas para o tdd_coder

- Começar pelas tarefas de **núcleo de execução** (T1–T5) e pelos erros mais estruturais (T10–T12), pois:
  - elas habilitam quase todos os cenários BDD de execução e resiliência básica;
  - a arquitetura já está definida em `TECH_STACK.md`, `HLD.md` e `LLD.md`.
- As tarefas de tool calling e arquivos (T6–T9) dependem da base de execução, mas devem ser iniciadas assim que run/stream estiverem minimamente estáveis.
  - A entrega de T8 inclui um demo CLI-first em `examples/valuetrack_tools_and_files.sh`, usando `--write-to-file` para persistir arquivos no workspace.
- Para cada tarefa:
  - escolher um cenário BDD relacionado;
  - implementar via TDD (ver `tests/bdd/*` já conectados às features);
  - manter rastreabilidade Tarefa → Cenário → Código.

---

## 3. Próximas Tarefas Planejadas (CLI-first + E2E)

Além das tarefas T1–T15 (núcleo do ciclo atual) e T16 (config via YAML), o roadmap inclui os seguintes incrementos para consolidar CLI-first e E2E:

| ID  | Track                                   | Size | Prioridade | Status   | Feature BDD                                               |
|-----|-----------------------------------------|------|-----------|----------|-----------------------------------------------------------|
| T16 | value_forge_core_code_agent_execution   | M    | Média     | DONE     | 10_code_agent_execution.feature                           |
| T17 | value_forge_core_code_agent_execution   | M    | Alta      | TODO     | 10_code_agent_execution.feature (@cli scenario)           |
| T18 | value_forge_core_code_agent_execution   | M    | Alta      | TODO     | 10_code_agent_execution.feature (@e2e provider real)      |
| T19 | value_forge_core_code_agent_execution   | S    | Média     | TODO     | 10_code_agent_execution.feature (demos via CLI/examples)  |

Notas:
- T17 deve introduzir uma CLI oficial (`forge-code-agent ...`) que exponha `run`/`stream`/`config` por cima da API `CodeAgent`.
- T18 deve garantir ao menos um caminho E2E para provider real (CLI/SDK) com cenário BDD `@e2e`, mesmo que rodado apenas em ambiente controlado.
- T19 cuida da padronização de scripts em `examples/` para demos por sprint e por ValueTrack, sempre via CLI oficial.
