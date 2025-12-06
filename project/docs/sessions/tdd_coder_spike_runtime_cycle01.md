# Sessão — TDD Coder — Spike de Runtime (cycle-01)

- Symbiota: `tdd_coder`
- Fase: `execution.tdd` (Phase 1–3, ciclo inicial)
- Status: spike técnico — **NÃO definitivo para produção**

## Contexto

Durante o cycle-01, o `tdd_coder` avançou além do escopo ideal de testes e
implementou código em `src/forge_code_agent/**` para viabilizar rapidamente
os cenários BDD de:

- execução básica (`10_code_agent_execution.feature`);
- tools e arquivos (`11_code_agent_tools_and_files.feature`);
- resiliência (`50_code_agent_resilience.feature`).

Esse código permitiu:

- validar os contratos de domínio (`ExecutionRequest`, `ExecutionResult`);
- exercitar adapters iniciais (CLI Codex e workspace);
- garantir que os cenários BDD estão bem formados e testáveis ponta a ponta.

## Decisão

Conforme ajuste de processo, o papel do `tdd_coder` passa a ser **apenas testes**
(ver `process/symbiotes/tdd_coder/prompt.md`). Logo:

- o código atual em:
  - `src/forge_code_agent/domain/**`
  - `src/forge_code_agent/runtime/**`
  - `src/forge_code_agent/adapters/**`
- deve ser tratado como **spike de referência**, e não como implementação final.

## Próximos passos — forge_coder

Na fase 6 (Delivery/Sprint), o symbiota `forge_coder` deve:

1. Revisar esse spike à luz de:
   - `specs/roadmap/TECH_STACK.md`
   - `specs/roadmap/HLD.md`
   - `specs/roadmap/LLD.md`
   - ADRs em `specs/roadmap/adr/*.md`.
2. Reimplementar/refatorar o runtime em `src/forge_code_agent/**`:
   - alinhando totalmente às bases do ForgeBase (EntityBase, UseCaseBase, ports/adapters);
   - mantendo todos os testes BDD/pytest verdes.
3. Atualizar o `specs/roadmap/BACKLOG.md` conforme necessário, marcando as tarefas
   que forem consolidadas como DONE pela implementação do forge_coder.
4. Em especial, ao tratar as tarefas ainda em `TODO` no backlog:
   - **T4 — Execução `stream()` via subprocess**:
     - implementar `CodeAgent.stream()`/adapters usando `subprocess.Popen(...)` ou equivalente,
       emitindo eventos/chunks em ordem e sinalizando fim de stream;
     - manter compatibilidade com o cenário BDD de streaming e com o teste que garante
       que o caminho passa pelo `ProviderAdapter` registrado para `"codex"`.
   - **T7 — Integração de tool calling na execução**:
     - integrar eventos de tool calling vindos dos providers com o `ToolCallingEngine`;
     - garantir que os resultados das tools sejam incorporados ao `ExecutionResult`
       sem quebrar o cenário BDD atual de tool calling (que hoje exercita a engine
       diretamente via `CodeAgent.execute_tool_call`).

Este arquivo documenta explicitamente que o papel de implementação de código de
produção em `src/` é do `forge_coder`, enquanto o `tdd_coder` permanece focado
em testes e BDD/TDD.
