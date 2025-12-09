# HLD — High Level Design — forgeCodeAgent

> Versão: 0.1 (draft)
> Responsável: mark_arc

---

## 1. Visão Geral

O forgeCodeAgent é composto por quatro áreas principais:

- **Domínio (sobre forgebase.domain)** — modelos e regras de negócio (providers, requests, results, errors) baseados em `EntityBase`/exceptions do ForgeBase.
- **Adapters (forgebase.adapters/infrastructure)** — integração com CLIs de providers, filesystem, logging/métricas (ports & adapters seguindo o padrão ForgeBase).
- **Runtime/Contexto** — `CodeAgent` (execução unitária) e `CodeManager`/`ContextSessionManager` (sessões, contexto e MCP).
- **CLI/MCP** — CLI oficial `forge-code-agent` e servidor MCP local para expor tools de workspace.

---

## 2. Componentes Principais

- `CodeAgent` (runtime):
  - expõe `run()` e `stream()` para execução unitária;
  - resolve `ProviderAdapter` via registry;
  - orquestra invocação da CLI do provider e persistência de arquivos.
- `ProviderAdapter`:
  - constrói comandos de CLI específicos de cada provider (Codex, Claude, Gemini);
  - processa stdout/stderr em eventos estruturados (reasoning, output, logs);
  - sinaliza suporte a streaming.
- `CodeManager` e `ContextSessionManager`:
  - `CodeManager` é a fachada orientada a sessões (CLI-first), resolvendo provider, workdir e `session_id`;
  - delega execuções concretas para `CodeAgent` e atualiza `ContextSessionManager`;
  - `ContextSessionManager` persiste eventos, resumos (`summaries`) e metadados em `logs/codeagent/session_*.json`.
- MCP Server (`forge_code_agent.mcp_server`):
  - servidor stdio que implementa o protocolo MCP e expõe tools como `read_file`, `write_file`, `list_dir`;
  - roda em processo separado, apontando para um `workdir` seguro;
  - é ativado via CLI de providers (Codex/Claude/Gemini) conforme configuração.
- `FilesystemWorkspaceAdapter`:
  - garante sandbox de workspace (sem path traversal);
  - escreve/atualiza arquivos de código e metadados dentro do diretório configurado.

---

## 2.1 Diagrama de Componentes (Mermaid)

```mermaid
flowchart LR
  subgraph Domain
    ER[ExecutionRequest]
    RES[ExecutionResult]
    FB[forgebase.domain\n(EntityBase, exceptions)]
  end

  subgraph Adapters
    PA["ProviderAdapter: codex | claude | gemini"]
    WS[FilesystemWorkspaceAdapter]
    LOG[LoggerPort]
    MET[MetricsPort]
  end

  subgraph Context
    CM[CodeManager]
    CSM[ContextSessionManager]
  end

  CLI[forge-code-agent CLI]
  CA[CodeAgent]
  MCP[(MCP Server)]
  PROVIDER_CLI[(Provider CLIs)]
  FS[(Filesystem)]

  CLI --> CM
  CM --> CA
  CM --> CSM

  CA --> ER
  CA --> PA
  CA --> WS
  CA --> LOG
  CA --> MET

  ER --> FB
  RES --> FB
  PA -->|"subprocess"| PROVIDER_CLI
  WS --> FS
  CM --> MCP
```

---

## 3. Fluxo de Execução (Alto Nível)

1. A CLI `forge-code-agent` recebe parâmetros (`run`/`stream`, provider, workdir, `session-id`, flags de streaming).
2. Se houver `session-id` ou `--use-code-manager`:
   - a CLI delega para `CodeManager`;
   - `CodeManager` resolve provider efetivo, workdir e carrega (ou cria) a sessão em `ContextSessionManager`.
3. `CodeManager` constrói um `ExecutionRequest` e delega a execução concreta para `CodeAgent` (`run()` ou `stream()`).
4. `CodeAgent`:
   - resolve o `ProviderAdapter` adequado;
   - constrói o comando da CLI do provider e o executa (`subprocess.run` ou `Popen`);
   - interpreta stdout/stderr em eventos estruturados (reasoning, output, logs);
   - delega gravação de arquivos ao `FilesystemWorkspaceAdapter` quando necessário;
   - retorna um `ExecutionResult` com status, conteúdo, eventos brutos e erros.
5. `CodeManager`:
   - atualiza a sessão em `ContextSessionManager` com os eventos e o resultado;
   - aplica sumarização de contexto quando aplicável;
   - persiste o snapshot em `logs/codeagent/session_*.json`.
6. MCP server:
   - é inicializado e usado pelos providers (via CLI) para executar tools de workspace (`read_file`, `write_file`, `list_dir`) quando configurado;
   - não é chamado diretamente pelo usuário, mas faz parte da infraestrutura de contexto/workspace.

### 3.1 Fluxograma do Fluxo de Execução

```mermaid
flowchart TD
  A[CLI receives command\n(run/stream + session-id?)] --> B{Use CodeManager?}
  B -->|yes| C[CodeManager loads/creates session]
  B -->|no| D[Direct call to CodeAgent]
  C --> E[Build ExecutionRequest and call CodeAgent]
  D --> E
  E --> F[Resolve ProviderAdapter and run CLI]
  F --> G[Read stdout/stderr as events]
  G --> H{Files to write?}
  H -->|yes| I[Write files via WorkspaceAdapter]
  H -->|no| J[Skip file writes]
  I --> K[Assemble ExecutionResult]
  J --> K[Assemble ExecutionResult]
  K --> L{Via CodeManager?}
  L -->|yes| M[Update session, maybe summarize, persist snapshot]
  L -->|no| N[Return result to CLI caller]
  M --> N
```

---

## 4. Integração com ForgeBase

- Via ports (`LoggerPort`, `MetricsPort`) injetáveis em `CodeAgent` ou no runtime.
- Sem dependência direta do pacote ForgeBase no core.
