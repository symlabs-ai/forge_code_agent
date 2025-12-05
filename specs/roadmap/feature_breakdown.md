# feature_breakdown — forgeCodeAgent

> Versão: 0.1 (draft)  
> Responsável: roadmap_coach  
> Fonte: `specs/bdd/tracks.yml`, features BDD, `dependency_graph.md`

---

## 1. Tracking

- VALUE Track 1: `value_forge_core_code_agent_execution`
  - Feature BDD: `specs/bdd/10_forge_core/10_code_agent_execution.feature`
- VALUE Track 2: `value_forge_core_tools_and_files`
  - Feature BDD: `specs/bdd/10_forge_core/11_code_agent_tools_and_files.feature`
- SUPPORT Track: `support_observability_code_agent_resilience`
  - Feature BDD: `specs/bdd/50_observabilidade/50_code_agent_resilience.feature`

---

## 2. Tarefas — Track: value_forge_core_code_agent_execution

### T1. Modelos de domínio e contratos básicos

- Criar tipos de domínio:
  - `ProviderId`, `ExecutionRequest`, `ExecutionResult`.
- Definir `ExecutionResult.status` (`success|error|partial`), `provider`, `content`, `metadata`.
- Garantir que o contrato casa com os cenários BDD de execução básica.

### T2. Registry e interface de ProviderAdapter

- Implementar `ProviderAdapter` protocol e registry interno.
- Adicionar providers:
  - `CodexProviderAdapter` (MVP),
  - hooks para `ClaudeProviderAdapter` / `GeminiProviderAdapter`.

### T3. Execução `run()` via subprocess

- Implementar `CodeAgent.run()`:
  - construir comando a partir de `ExecutionRequest`;
  - executar via `subprocess.run(..., timeout=...)`;
  - capturar stdout/stderr.
- Converter saída em `ExecutionResult` com status e provider corretos.

### T4. Execução `stream()` via subprocess

- Implementar `CodeAgent.stream()`:
  - executar via `subprocess.Popen(...)`;
  - emitir eventos/chunks em ordem;
  - sinalizar fim de stream.
- Expor API capaz de reconstruir a resposta completa, conforme BDD.

### T5. Suporte a troca de provider sem refatorar fluxo

- Garantir que `CodeAgent` use apenas `ProviderId` e registry, sem `if` específicos de provider.
- Adicionar testes BDD que trocam provider em configuração, mantendo o mesmo código de automação.

---

## 3. Tarefas — Track: value_forge_core_tools_and_files

### T6. Engine de tool calling

- Implementar `ToolCallingEngine` com:
  - registro de tools (`register_tool`);
  - execução de chamadas recebidas dos providers;
  - retorno de resultados/erros.

### T7. Integração de tool calling na execução

- Integrar eventos de tool calling ao fluxo de execução:
  - ProviderAdapter detecta tool calls;
  - `ToolCallingEngine` executa funções Python;
  - resultados são incorporados ao `ExecutionResult`.

### T8. Adapter de workspace e persistência de arquivos

- Implementar `FilesystemWorkspaceAdapter`:
  - validação de paths contra o `workdir`;
  - escrita/atualização de arquivos gerados pela engine/tool.
- Alinhar com cenário BDD de persistência de arquivos no workspace.

### T9. Sandbox de workspace (path traversal)

- Implementar validação de path:
  - resolver `target = (workdir / user_path).resolve()`;
  - rejeitar se `target` não estiver dentro do `workdir`.
- Mapear erros para `WorkspaceSecurityError`.

---

## 4. Tarefas — Track: support_observability_code_agent_resilience

### T10. Modelo de erros e exceções

- Criar tipos de erro:
  - `ProviderNotSupportedError`,
  - `ProviderExecutionError`,
  - `ParsingError`,
  - `WorkspaceSecurityError`,
  - `ToolExecutionError`,
  - `ProviderTimeoutError`.
- Conectar erros às features de resiliência BDD.

### T11. Tratamento de provider não suportado

- Validar provider na inicialização do `CodeAgent` ou na criação de `ExecutionRequest`.
- Lançar `ProviderNotSupportedError` quando o provider não existir no registry.

### T12. Tratamento de falhas de CLI

- Mapear códigos de saída diferentes de zero e erros de subprocess para `ProviderExecutionError`.
- Incluir stderr relevante no erro e/ou em `ExecutionResult.errors`.

### T13. Tratamento de interrupção de streaming

- Detectar interrupção prematura do processo em `stream()`.
- Emitir eventos parciais e marcar `ExecutionResult.status="partial"`, conforme BDD.

### T14. Tratamento de JSON malformado

- Detectar falhas de parsing de JSON.
- Lançar/registrar `ParsingError` e preservar `raw_events` para debug.

### T15. Timeouts e captura de stderr

- Implementar timeouts configuráveis em `run()` e `stream()`.
- Capturar e expor stderr em objeto de erro estruturado, sem vazar informação excessiva.

---

## 5. Observações para Estimates/Backlog

- T1–T5 formam o núcleo do **ValueTrack de execução básica**; recomendável agrupar em um primeiro lote de implementação.
- T6–T9 representam o **ValueTrack de tools + arquivos**, que pode ser iniciado após T1–T3 estarem razoavelmente estáveis.
- T10–T15 são parte do **SupportTrack de resiliência**; algumas tarefas (como T11–T12) são pré-requisito para qualquer uso em CI.

Estes IDs (T1...T15) devem ser reutilizados em `specs/roadmap/estimates.yml` e `specs/roadmap/BACKLOG.md` para manter rastreabilidade TASK → FEATURE → TRACK.

