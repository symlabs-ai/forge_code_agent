# ARCHITECTURAL_DECISIONS_APPROVED — forgeCodeAgent

> Versão: 0.1
> Responsável: mark_arc + stakeholders
> Fonte: `specs/roadmap/ARCHITECTURAL_QUESTIONNAIRE.md`

Decisões arquiteturais consolidadas para o MVP do forgeCodeAgent, alinhadas às features BDD e ao ForgeProcess.

---

## 1. Domínio e Camadas (Clean/Hex)

### 1.1 Separação de domínio vs adapters

- **Domínio (puro, sem I/O)**:
  - Tipos e regras centrais:
    - `ProviderId` (ex.: `"codex"`, `"claude"`, `"gemini"`).
    - `ExecutionRequest` (provider, prompt, modo run/stream, timeout, flags, workdir lógico).
    - `ExecutionResult` (status, provider, content, tool_calls, errors, raw_events, metadata).
    - `ToolDefinition` (nome, assinatura, política de erro).
    - `ToolCall` (nome, args, resultado/erro).
  - Regras de negócio:
    - definição de sucesso vs falha vs parcial;
    - quando marcar resultado como parcial;
    - contrato de segurança de workspace (paths fora do workdir lógico são inválidos).

- **Adapters (I/O/bordas)**:
  - `CliProviderAdapter`: traduz `ExecutionRequest` em comando `subprocess` e faz parsing bruto de stdout/stderr.
  - `FilesystemWorkspaceAdapter`: leitura/escrita em disco seguindo regras do domínio.
  - `ToolRegistryAdapter`: registro e dispatch de funções Python.
  - `LoggingAdapter` / `MetricsAdapter`: integração opcional com ForgeBase ou outras plataformas.

Domínio nunca usa diretamente `subprocess`, `os` ou filesystem; tudo passa por ports/adapters.

### 1.2 Borda de integração com ForgeBase

- forgeCodeAgent assume o **ForgeBase como base arquitetural explícita**:
  - reusa `EntityBase`, `UseCaseBase`, `PortBase`, `AdapterBase` conforme `docs/product/guides/forgebase_guides/referencia/arquitetura.md`;
  - organiza pastas e imports de forma compatível com `from forgebase.[module] import ...`.
- Integração com ForgeBase ocorre via:
  - reuso das classes base do ForgeBase no domínio/aplicação/adapters;
  - ports específicos (`LoggerPort`, `MetricsPort`, possivelmente `SessionStorePort`) que podem ser implementados por `forgebase.infrastructure`/`observability`.
- O runtime continua utilizável em contexto não‑ForgeBase, desde que:
  - a dependência `forgebase` esteja disponível,
  - e ports de logging/métricas possam operar em modo no-op quando nenhuma stack ForgeBase completa estiver configurada.

---

## 2. Modelo de Providers e Extensibilidade

### 2.1 Abstração de providers

- Interface única para providers, por exemplo:

  ```python
  class ProviderAdapter(Protocol):
      id: ProviderId
      def build_command(self, request: ExecutionRequest) -> list[str]: ...
      def supports_streaming(self) -> bool: ...
      def supports_tool_calling(self) -> bool: ...
      def parse_stdout_chunk(self, line: str) -> ProviderEvent: ...
  ```

- Implementações concretas:
  - `CodexProviderAdapter`
  - `ClaudeProviderAdapter`
  - `GeminiProviderAdapter`

- Registro via registry interno: `provider_id -> adapter`.
- Configuração no MVP via código (`CodeAgent(provider="codex")`); YAML de providers fica para etapas futuras.

### 2.2 Registro de novos providers

- MVP: **sem sistema de plugins dinâmico**; usar módulos internos versionados.
  - Registry estático, por exemplo:

    ```python
    PROVIDERS = {
        "codex": CodexProviderAdapter(),
        "claude": ClaudeProviderAdapter(),
        "gemini": GeminiProviderAdapter(),
    }
    ```

- Evolução futura: plugin system baseado em entry points / manifesto ForgeBase.
- Contrato: novos providers não alteram a interface de `CodeAgent` nem a forma de uso de `ExecutionRequest/ExecutionResult`.

---

## 3. Execução via CLI (subprocess)

### 3.1 Biblioteca de subprocesso

- MVP utiliza apenas **`subprocess` da stdlib**:
  - `run()`: `subprocess.run(...)`.
  - `stream()`: `subprocess.Popen(...)` + loop em `stdout`.
- Nada de asyncio no MVP; se necessário, um adapter assíncrono futuro pode ser criado sem mudar o domínio.

### 3.2 Gestão de timeouts e cancelamento

- Timeout exposto **por chamada**, com default global:
  - `CodeAgent.run(prompt, timeout=...)`
  - `CodeAgent.stream(prompt, timeout=...)`
- Prioridade:
  1. valor passado na chamada;
  2. valor configurado no `CodeAgent`;
  3. default do provider/global.
- Implementação:
  - `run()`: usa `subprocess.run(..., timeout=timeout)`.
  - `stream()`: controla tempo e encerra o processo ao estourar o timeout.
- Cancelamento manual:
  - MVP considera um método `cancel()` no handler de stream (encerrando o processo).

### 3.3 Captura de stdout/stderr

- `stdout`:
  - `run()`: acumulado em memória e parseado ao final.
  - `stream()`: processado linha a linha (ou chunk) para gerar eventos.
- `stderr`:
  - sempre capturado;
  - resumo relevante exposto em `ProviderExecutionError`;
  - conteúdo completo enviado para logging (via `LoggerPort`), com cuidado para não vazar informação sensível.

---

## 4. Parsing, Tool Calling e JSON

### 4.1 Formato de ExecutionResult

- Definição mínima:

  ```python
  @dataclass
  class ExecutionResult:
      status: Literal["success", "error", "partial"]
      provider: ProviderId
      content: str | None
      raw_events: list[dict]  # eventos canônicos (AgentEvents) com campo `raw` preservando o payload original
      tool_calls: list[ToolCall]
      errors: list[ExecutionError]
      metadata: dict[str, Any]
  ```

- `status` e `provider` são obrigatórios;
- `content` pode ser `None` quando só houver arquivos gerados;
- estrutura é o contrato base para os cenários BDD.

### 4.2 Parsing de JSON malformado

- Estratégia:
  1. tentar parse normal (linha/chunk);
  2. em caso de falha:
     - marcar `status="error"` ou `"partial"` conforme contexto;
     - registrar `ParsingError` específico em `errors`;
     - guardar trecho bruto em `raw_events`.
- Sem heurísticas de “correção” de JSON no MVP.
- Em streaming:
  - entregar os chunks válidos já parseados;
  - emitir evento final de erro.

### 4.3 Engine de tool calling

- Lógica em componente de domínio:

  ```python
  class ToolCallingEngine:
      def register_tool(self, name: str, func: Callable): ...
      def handle_tool_call(self, call: ToolCall) -> ToolResult: ...
  ```

- Fluxo:
  - ProviderAdapter detecta evento de tool calling no JSON;
  - cria `ToolCall` de domínio;
  - `ToolCallingEngine` resolve e executa a função Python;
  - resultado é incorporado ao `ExecutionResult` e/ou devolvido à engine conforme protocolo.
- Segurança:
  - apenas tools registradas via API podem ser chamadas;
  - erro de tool → `ToolExecutionError` dentro de `ExecutionResult.errors`, sem derrubar o runtime.

---

## 5. Workspace, Arquivos e Segurança

### 5.1 Sandbox de workspace

- Cada `CodeAgent` possui um `workdir` obrigatório, resolvido para `Path(workdir).resolve()`.
- Qualquer path vindo de engine/tools:
  - é combinado com o `workdir` e resolvido (`target = (workdir / user_path).resolve()`),
  - é validado com regra de domínio equivalente a `is_relative_to(workdir)`.
- Paths absolutos externos ou que escapem do `workdir` geram `WorkspaceSecurityError`.

### 5.2 Formato de artefatos gravados

- Convenções:
  - código gerado e arquivos de usuário: dentro do `workdir`, após normalização segura;
  - metadados/logs de execução: em subpasta `.forgecode` dentro do `workdir`, ex.:
    - `runs/<timestamp>.json|yml`;
    - `tools/<run_id>.log` (opcional).

Tudo permanece versionável via Git e não polui o espaço principal de código.

---

## 6. Observabilidade e Erros

### 6.1 Modelo de erros

- Tipos principais:
  - `ProviderNotSupportedError`
  - `ProviderExecutionError`
  - `ParsingError`
  - `WorkspaceSecurityError`
  - `ToolExecutionError`
  - `ProviderTimeoutError` (wrapper do timeout de subprocess)

- Exposição:
  - erros graves de configuração/ambiente (provider inexistente, workspace inválido) podem ser lançados como exceptions;
  - erros de execução da engine podem ser exceptions ou `ExecutionResult` com `status="error"` — BDD favorece pelo menos um tipo distinto (`ProviderExecutionError`) e registro em `errors`.

### 6.2 Integração com observabilidade

- Logging:
  - via `logging` stdlib (loggers `forgecode.runtime`, `forgecode.provider.*`).
- Métricas:
  - via `MetricsPort`, implementação no-op por default.
  - métricas mínimas:
    - execuções por provider;
    - falhas por provider;
    - tempo médio de execução;
    - timeouts.

---

## 7. Stack Tecnológico e CLI

### 7.1 Stack

- Python 3.12+ obrigatório.
- Core do runtime baseado apenas em stdlib:
  - `subprocess`, `pathlib`, `dataclasses`, `typing`, `logging`.
- Dependências opcionais (para CLI própria):
  - `click` ou `typer`.
- `pydantic` e afins ficam fora do MVP.

### 7.2 CLI própria

- Haverá uma CLI fina sobre a API Python:
  - `forge-code-agent run ...`
  - `forge-code-agent stream ...`
- Função:
  - facilitar uso em scripts/CI;
  - servir como ferramenta de teste local.

---

## 8. Providers Prioritários e Escopo Inicial de Uso

### 8.1 Ordem de providers no MVP

- Provider de referência: **Codex-like**.
- Segundo provider prioritário: **Claude Code**.
- Terceiro provider (próxima fase): **Gemini Code**.

### 8.2 Fluxos de uso foco

- Fluxo 1: geração de módulo + testes
  - aplicar CodeAgent para criar módulo de serviço e testes correspondentes em diretório alvo.
- Fluxo 2: PR assistido
  - usar CodeAgent em job de CI para produzir sugestões de melhoria em `project/reviews/` a partir de diffs/arquivos.

---

## 9. Tolerância a Risco

- Falhas de CLI:
  - não podem ser silenciosas; precisam gerar erro explícito, log e métrica.
- Perda de saída em streaming:
  - aceitável apenas se:
    - chunks gerados forem entregues;
    - resultado marcado como parcial;
    - erro registrado.
- Falhas de tool calling:
  - podem ser tratadas como erro de tool isolado, sem derrubar o runtime;
  - BDD exige que o erro seja visível em `ExecutionResult.errors`.

Em resumo:
- baixa tolerância a falhas silenciosas;
- média tolerância a resultados parciais quando claramente sinalizados;
- alta exigência de transparência e diagnósticos.
