# TOOL CALLING via MCP para forgeCodeAgent

## 1. Motivação

O forgeCodeAgent nasceu para ser um **runtime CLI-first para engines de código** (Codex-like, Claude Code, Gemini Code, etc.), com:

- execução `run()` / `stream()` via subprocessos;
- parsing de stdout (JSON/JSONL);
- escrita de arquivos no workspace;
- integração futura com tool calling.

Hoje existe um mecanismo interno de “extensões” (engine de funções Python + hooks `before_run`/`after_run`), mas ele **não é tool calling de LLM** no sentido tradicional: quem decide executar as funções é a automação (caller), não o modelo. Para ter:

> “Durante a execução, o coding agent chamar funções Python locais que alteram sua linha de raciocínio”

precisamos de um protocolo em que **o próprio provider** peça as tools. A abordagem mais alinhada com o ecossistema atual é usar **MCP (Model Context Protocol)**, que já é suportado pelos três coding agents.

Esta proposta descreve como usar MCP para implementar tool calling “real” em cima das CLIs existentes, sem depender de APIs HTTP proprietárias.

---

## 2. Objetivo

Habilitar um fluxo em que:

1. O desenvolvedor chama `CodeAgent.run()` / `CodeAgent.stream()` usando um provider via CLI (codex/claude/gemini).
2. O provider, rodando em CLI, decide usar uma tool (por exemplo, `read_file`, `run_tests`, `write_file`), e emite um `toolCall` MCP.
3. Um **MCP server local**, mantido pelo forgeCodeAgent, recebe esse `toolCall`, executa uma função Python local (com acesso ao workspace, git, etc.) e devolve o resultado ao provider.
4. O provider continua a geração **na mesma sessão**, incorporando o resultado da tool ao raciocínio.

Do ponto de vista do usuário:

- continua usando apenas `CodeAgent.run`/`stream` + CLI-first (`python -m forge_code_agent.cli`);
- mas agora obtém **tool calling real** (LLM decide quando chamar a tool, e o resultado afeta o raciocínio em tempo real).

---

## 3. Situação Atual (Resumo)

### 3.1. Runtime / CodeAgent

- `CodeAgent` (`src/forge_code_agent/runtime/agent.py`):
  - Orquestra `ExecutionRequest` → `ProviderAdapter.run/stream` → `ExecutionResult`.
  - Tem engine interno de funções Python (`ToolCallingEngine`) que hoje é usado como:
    - `register_tool(name, func)`,
    - `run(..., tool_calls=[...])`,
    - `execute_tool_call(...)`.
  - Possui hooks:
    - `add_before_run_handler(handler: (ExecutionRequest) -> Any)`;
    - `add_after_run_handler(handler: (ExecutionRequest, ExecutionResult) -> Any)`.

Esse mecanismo funciona como **extensões/eventos internos** (pós-processamento, pré-processamento), mas **não altera o fluxo do provider em tempo real**. O provider não sabe que houve tools; ele só vê prompts/respostas.

### 3.2. Providers via CLI

- `CodexProviderAdapter` / `ClaudeProviderAdapter` / `GeminiProviderAdapter`:
  - constroem comandos CLI (`codex exec`, `claude -p ...`, `gemini run ...`);
  - usam `subprocess.run` (modo run) e `Popen` + leitura linha-a-linha (modo stream);
  - expõem apenas stdout/stderr/exit code ao runtime.

Os CLIs reais já exibem **eventos internos avançados** (como `run_shell_command`, `write_file`, etc.), mas o forgeCodeAgent hoje apenas:

- consome esses eventos como texto/JSON para `raw_events` e debug;
- **não consegue interferir** na execução interna de tool calling dessas CLIs.

### 3.3. Limitações do desenho atual

- O “tool calling” atual é:
  - dirigido pelo caller (via parâmetro `tool_calls` em `run()`),
  - sempre pós-processamento (é executado depois do `adapter.run()`),
  - invisível para o provider.
- Não há como o provider, por si, disparar uma função Python local via forgeCodeAgent dentro de uma única sessão CLI, pois:
  - a comunicação é unidirecional (stdout do provider → runtime);
  - não há canal para devolver resultados enquanto o processo ainda está gerando saída.

Conclusão: o mecanismo atual é útil como **hook de automação local**, mas não entrega o “tool calling de LLM” que altera o raciocínio do coding agent em tempo real.

---

## 4. Proposta: Tool Calling via MCP Server Local

### 4.1. Ideia Central

Todos os três coding agents mencionados suportam MCP (Model Context Protocol). A ideia é:

- **Subir um MCP server local**, implementado pelo forgeCodeAgent, expondo ferramentas Python (read/write file, run tests, lint, etc.);
- Configurar as CLIs de Codex/Claude/Gemini para **conectar-se a esse MCP server**;
- Deixar que **os próprios coding agents**, via MCP, peçam tools ao server durante a execução.

Assim:

- a origem do tool call passa a ser o LLM (via CLI);
- o forgeCodeAgent se torna o “fornecedor de tools” via MCP;
- os resultados das tools são reinjetados na conversa do LLM no mesmo turno.

### 4.2. Fluxo de Execução (High-Level)

```text
Dev → CodeAgent.run/stream → ProviderAdapter (CLI)
       ↓
  codex/claude/gemini CLI ↔ MCP Server (forgeCodeAgent)
       ↓
   LLM raciocina usando resultados das tools
       ↓
stdout JSONL → ProviderAdapter.stream → ExecutionResult.raw_events
```

Passo a passo:

1. Dev chama `CodeAgent.run(prompt, provider="codex", workdir=...)`.
2. `CodeAgent` monta `ExecutionRequest` e chama `CodexProviderAdapter.run`/`stream`.
3. `CodexProviderAdapter`:
   - garante que o MCP server local esteja rodando (ou falha cedo com erro configurável);
   - injeta no ambiente (`env`) as variáveis esperadas pela CLI para descobrir o MCP server (host/port/socket);
   - invoca `codex exec ...` normalmente.
4. A CLI do Codex/Claude/Gemini abre conexão MCP com o servidor local e, quando o modelo decide, emite um `toolCall` (por exemplo, `read_file`):

   ```json
   {
     "type": "toolCall",
     "toolName": "read_file",
     "arguments": { "path": "src/app.py" }
   }
   ```

5. O MCP server do forgeCodeAgent:
   - traduz esse `toolCall` para uma função Python local (e.g. `workspace.read_file("src/app.py")`);
   - executa a função com as devidas garantias de segurança (sandbox de workspace);
   - devolve o resultado via protocolo MCP (`toolResult`).
6. O coding agent continua o raciocínio, agora sabendo o conteúdo de `src/app.py`, e emite novo texto/código para stdout (que será coletado pelo `ProviderAdapter` normalmente).

Do ponto de vista de `CodeAgent` e da automação:

- nada muda na assinatura: continua sendo `run`/`stream` + `ExecutionResult`;
- mas `raw_events` pode passar a capturar também os eventos MCP relevantes (para observabilidade).

---

## 5. Arquitetura Proposta

### 5.1. Novos Componentes

**a) MCP Tools Engine (domínio)**

- Um componente de domínio, análogo ao `ToolCallingEngine`, responsável por:
  - registrar ferramentas lógicas (por exemplo: `read_file`, `write_file`, `run_tests`, `list_changed_files`);
  - executar essas funções recebendo argumentos tipados;
  - aplicar regras de segurança (workspace boundaries, timeouts).
- Pode reutilizar internamente o que hoje existe em `ToolCallingEngine`, mas com semântica mais clara de “tools de automação”, não “tool calling LLM”.

**b) MCP Server Adapter**

- Processo (ou thread) separado, rodando um servidor MCP:
  - expõe as tools registradas no MCP Tools Engine;
  - fala o protocolo MCP (JSON-RPC, streams etc., conforme spec);
  - é configurado com o **mesmo workspace** do CodeAgent (ou um sub‑workspace dedicado).

**c) CLI Adapters com Suporte a MCP**

- Extensões em:
  - `CodexProviderAdapter`,
  - `ClaudeProviderAdapter`,
  - `GeminiProviderAdapter`,
para:

- iniciar (ou garantir) o MCP server antes de invocar a CLI;
- propagar configuração de conexão ao MCP via variáveis de ambiente ou flags específicas, por exemplo:

  ```text
  MCP_SERVER_URL=localhost:9000
  MCP_SERVER_TOKEN=...
  ```

### 5.2. Integração com CodeAgent

O `CodeAgent` **não precisa** conhecer MCP diretamente. Ele continua a orquestrar:

- `ExecutionRequest` → `ProviderAdapter.run/stream` → `ExecutionResult`;
- hooks `before_run`/`after_run` para logging, métricas, etc.

A única “integração” adicional pode ser:

- um handler `before_run` opcional que garanta que o MCP server esteja ativo para providers que declaram `supports_mcp=True`;
- um enriquecimento opcional de `ExecutionResult.raw_events` com alguns metadados do MCP server (para auditoria).

---

## 6. Comparação com outras Abordagens

### 6.1. Abordagem atual (hooks internos)

- **Prós**:
  - simples, 100% sob controle do runtime;
  - funciona offline, mesmo com providers que não têm qualquer noção de tools.
- **Contras**:
  - quem decide executar funções Python é o caller, não o LLM;
  - sem impacto em tempo real na linha de raciocínio do coding agent;
  - não escala bem para fluxos complexos de agente.

### 6.2. Orquestrador multi-turn via CLI (sem MCP)

- Idéia: `CodeAgent` roda `codex exec` várias vezes, interpretando o output como plano/ações e intercalando execuções Python.
- **Prós**:
  - não depende de cooperação explícita do provider além de seguir um formato de texto/JSON combinado em prompt;
  - funciona com qualquer CLI que responde em texto.
- **Contras**:
  - é sempre “multi-turn”: cada tool exige uma nova chamada CLI;
  - não aproveita tool calling nativo nem capacidades avançadas já existentes nas CLIs;
  - maior latência e potencial de complexidade no state management.

### 6.3. MCP Server Local (proposta)

- **Prós**:
  - tool calling **dirigido pelo LLM**, em linha com APIs modernas;
  - integração uniforme para múltiplos providers via protocolo aberto;
  - mantém CLI-first: tudo continua orquestrado via subprocess;
  - separa bem responsabilidades: provider cuida de raciocínio, forgeCodeAgent cuida de ferramentas e workspace.
- **Contras**:
  - exige implementação e operação de um MCP server;
  - depende de configuração correta dos CLIs para falar com esse MCP;
  - aumenta a superfície de observabilidade e debug (mais uma camada entre usuário e provider).

---

## 7. Limitações e Considerações

1. **Dependência de suporte MCP real nas CLIs**
   - A proposta assume que `codex`, `claude` e `gemini` suportam MCP como “clientes”;
   - se alguma CLI ainda não expuser isso de forma utilizável, precisaremos:
     - de um modo híbrido (MCP quando disponível, hooks internos quando não);
     - ou de um ValueTrack separado para “tool calling sem MCP” (multi-turn).

2. **Segurança e sandboxing**
   - As tools expostas via MCP devem respeitar as mesmas regras de segurança do workspace:
     - nenhuma gravação fora do `workdir` configurado;
     - proteção contra path traversal;
     - timeouts e limites de recursos (ex.: não travar rodando `pytest` por tempo infinito).

3. **Observabilidade**
   - Será importante capturar, de forma opcional, eventos de MCP para auditoria:
     - quais tools foram chamadas,
     - com quais argumentos,
     - qual foi o resultado básico (sucesso/erro, resumo);
   - sem, contudo, vazar dados sensíveis ou logs excessivos em ambientes de produção.

4. **Complexidade de depuração**
   - O pipeline passaria a ser:

     ```text
     script → CodeAgent → ProviderAdapter → CLI → MCP → workspace
     ```

   - Precisaremos de mensagens de erro claras para casos como:
     - MCP server não disponível;
     - tool não registrada;
     - falha na chamada MCP;
     - incompatibilidade de versão/protocolo.

5. **Compatibilidade com o desenho atual**
   - O engine atual de funções Python (`ToolCallingEngine`) e os hooks `before_run`/`after_run` **podem ser reusados**:
     - o MCP server pode usá-los como backend para resolver e executar tools;
     - o flush de resultados em `ExecutionResult.tool_calls` pode continuar existindo para cenários que não dependem de MCP.

---

## 8. Caminho de Implementação (alto nível)

Um possível plano incremental:

1. **Spike MCP Server mínimo**
   - Implementar um MCP server local em Python com 2–3 tools simples:
     - `read_file(path)`,
     - `write_file(path, content)` (respeitando workspace),
     - opcional: `run_tests(pattern)`.
   - Integrar esse server com o `FilesystemWorkspaceAdapter`.

2. **Configurar um provider de referência para usar MCP**
   - Escolher um provider (por exemplo, codex) e:
     - descobrir/configurar as flags/env necessárias para apontar o CLI para o MCP server;
     - criar um script de demo (`examples/mcp/codex_tools_demo.sh`) que mostra o fluxo ponta-a-ponta.

3. **Adicionar BDD para tool calling via MCP**
   - Feature `40_mcp_*` com cenários do tipo:

     ```gherkin
     Scenario: Provider uses MCP tool to inspect workspace file
       Given a CodeAgent configured with provider "codex" and MCP tools enabled
       And a file "tetris.py" exists in the workspace
       When the developer asks the agent to "analyse the tetris implementation"
       Then the provider uses an MCP tool to read "tetris.py"
       And the final answer reflects the contents of the file
     ```

4. **Generalizar para Claude e Gemini**
   - Replicar a configuração de MCP nos adapters de `claude` e `gemini`;
   - Criar demos equivalentes em `examples/claude` e `examples/gemini`.

5. **Integração com o processo / ValueTracks**
   - Atualizar `specs/roadmap/feature_breakdown.md` e `specs/roadmap/estimates.yml` com tasks específicas de MCP;
   - Marcar pelo menos um cenário `@e2e` para cada provider que use MCP;
   - Ajustar `process/process_execution_state.md` para incluir MCP como dependência de encerramento de ciclo quando o ValueTrack de tool calling estiver incluído no escopo.

---

## 9. Conclusão

Usar um **MCP server local** como backend de tools para os coding agents é, hoje, o caminho mais sólido para implementar tool calling “de verdade” em um ambiente CLI-first como o do forgeCodeAgent:

- mantém o controle de automação e segurança do lado do forgeCodeAgent;
- permite que Codex/Claude/Gemini decidam quando chamar ferramentas, afetando o raciocínio em tempo real;
- evita dependência direta de APIs HTTP proprietárias, usando um protocolo aberto (MCP);
- encaixa bem com a arquitetura atual (Clean/Hex, adapters, ValueTracks) e com a visão de longo prazo registrada em `docs/hipotese.md` e nos Roadmaps.

Os próximos passos práticos são iniciar um spike de MCP server mínimo e ancorar essa evolução em um novo ValueTrack + BDD específico, garantindo que tool calling via MCP se torne critério explícito de encerramento de ciclo nos processos do projeto. +

### 8.1 Diagrama de Componentes (MCP + CodeManager + Providers)

```mermaid
flowchart LR
    subgraph Client
      A[CLI / Script Python]\n(CodeManager.run/stream)
    end

    subgraph Core["forgeCodeAgent Core"]
      CM[CodeManager]
      CSM[ContextSessionManager]
      CA[CodeAgent]
    end

    subgraph Providers["Provider CLIs"]
      PC[Codex CLI]
      PL[Claude CLI]
      PG[Gemini CLI]
    end

    subgraph MCP["MCP Layer"]
      MS[MCP Server\n(forge_code_agent.mcp_server)]
      MT[MCP Tools Engine\n(read_file, write_file, list_dir, run_tests,...)]
    end

    subgraph Workspace["Workspace / Filesystem"]
      WS[(FilesystemWorkspaceAdapter)]
    end

    A --> CM
    CM --> CSM
    CM --> CA
    CA --> PC
    CA --> PL
    CA --> PG

    PC <--> MS
    PL <--> MS
    PG <--> MS

    MS --> MT
    MT --> WS
```
