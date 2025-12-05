# BACKLOG — forgeCodeAgent

> Versão: 0.1 (draft)  
> Responsável: roadmap_coach  
> Fonte: `feature_breakdown.md`, `estimates.yml`

---

## 1. Lista de Tarefas (T1–T15)

| ID  | Track                                   | Size | Prioridade | Status   | Feature BDD                                               |
|-----|-----------------------------------------|------|-----------|----------|-----------------------------------------------------------|
| T1  | value_forge_core_code_agent_execution   | S    | Alta      | TODO     | 10_code_agent_execution.feature                           |
| T2  | value_forge_core_code_agent_execution   | S    | Alta      | TODO     | 10_code_agent_execution.feature                           |
| T3  | value_forge_core_code_agent_execution   | M    | Alta      | TODO     | 10_code_agent_execution.feature                           |
| T4  | value_forge_core_code_agent_execution   | M    | Alta      | TODO     | 10_code_agent_execution.feature                           |
| T5  | value_forge_core_code_agent_execution   | S    | Alta      | TODO     | 10_code_agent_execution.feature                           |
| T6  | value_forge_core_tools_and_files        | M    | Média     | TODO     | 11_code_agent_tools_and_files.feature                     |
| T7  | value_forge_core_tools_and_files        | M    | Média     | TODO     | 11_code_agent_tools_and_files.feature                     |
| T8  | value_forge_core_tools_and_files        | M    | Média     | TODO     | 11_code_agent_tools_and_files.feature                     |
| T9  | value_forge_core_tools_and_files        | S    | Alta      | TODO     | 11_code_agent_tools_and_files.feature                     |
| T10 | support_observability_code_agent_resilience | S | Alta      | TODO     | 50_code_agent_resilience.feature                          |
| T11 | support_observability_code_agent_resilience | XS| Alta      | TODO     | 50_code_agent_resilience.feature                          |
| T12 | support_observability_code_agent_resilience | S | Alta      | TODO     | 50_code_agent_resilience.feature                          |
| T13 | support_observability_code_agent_resilience | S | Média     | TODO     | 50_code_agent_resilience.feature                          |
| T14 | support_observability_code_agent_resilience | S | Média     | TODO     | 50_code_agent_resilience.feature                          |
| T15 | support_observability_code_agent_resilience | S | Média     | TODO     | 50_code_agent_resilience.feature                          |

---

## 2. Notas para o tdd_coder

- Começar pelas tarefas de **núcleo de execução** (T1–T5) e pelos erros mais estruturais (T10–T12), pois:
  - elas habilitam quase todos os cenários BDD de execução e resiliência básica;
  - a arquitetura já está definida em `TECH_STACK.md`, `HLD.md` e `LLD.md`.
- As tarefas de tool calling e arquivos (T6–T9) dependem da base de execução, mas devem ser iniciadas assim que run/stream estiverem minimamente estáveis.
- Para cada tarefa:
  - escolher um cenário BDD relacionado;
  - implementar via TDD (ver `tests/bdd/*` já conectados às features);
  - manter rastreabilidade Tarefa → Cenário → Código.

