# Plano de Implementação — MCP como Tool Calling para CodeAgents

## 1. Visão do Produto

**Objetivo**: permitir que Codex/Claude/Gemini, via CLI, usem um **MCP server local** para chamar tools Python que:

- leem/escrevem arquivos no workspace;
- rodam testes/comandos controlados;
- expõem informações de projeto (diffs, estrutura, etc.);
- sem sair do fluxo natural do coding agent (tool calling “de verdade”).

**Experiência esperada para o usuário**:

- Continua usando `CodeAgent.run/stream` e `python -m forge_code_agent.cli`.
- Não precisa pensar em MCP diretamente: se MCP estiver configurado e tools habilitadas, o agente de código já sabe usá-las.
- Tem observabilidade clara: quais tools foram chamadas, com quais argumentos, quanto custou/quanto tempo levou.

---

## 2. Capacidades Centrais Necessárias

1. **MCP server local robusto**
   - Processo separado (ou thread) com ciclo de vida controlado.
   - Tools expostas:
     - `read_file`, `write_file`, `list_dir`, `stat_file`.
     - `run_tests` (pytest), `run_lint` (ruff/mypy opcional).
     - `run_shell_safe` com escopo limitado.
   - Respeita o `workdir` e `FilesystemWorkspaceAdapter` (sem escapar do workspace).

2. **Integração por provider**
   - Codex CLI apontando para MCP server local (env/flags).
   - Claude CLI idem.
   - Gemini CLI idem.
   - Cada adapter sabe:
     - iniciar/garantir MCP up,
     - propagar configuração MCP correta para sua CLI.

3. **Modelo de eventos**
   - `AgentEvent` com `kind` (`reasoning`, `message`, `tool`, `log`, `raw`), `role`, `text`, `provider`, `raw`.
   - Eventos de tool MCP mapeados para `kind="tool"` com `tool_name`, `tool_args`, `tool_status`, `tool_duration_ms`.
   - `ExecutionResult.raw_events` como lista desses eventos.

4. **Processo/qualidade**
   - BDD `40_mcp_*` com cenários `@mcp @e2e`.
   - Critério de encerramento de ciclo: não fechar ciclo com MCP no escopo sem pelo menos um cenário `@mcp @e2e` passando.
   - Demos em `examples/` mostrando fluxos reais (Tetris, PR review, geração de módulo + testes) usando MCP.

---

## 3. Plano por Fases (Sprints / Ciclos)

### Fase 1 — MCP Server mínimo (Spike técnico)

**Objetivo**: ter um MCP server local funcional com 2–3 tools, integrado ao `workdir`.

- **Tarefas**:
  - Escolher abordagem de implementação MCP (lib oficial ou servidor mínimo JSON-RPC).
  - Criar `src/forge_code_agent/mcp_server/` com:
    - bootstrap (`start/stop`, porta/unix socket, config);
    - tools básicas sobre `FilesystemWorkspaceAdapter`:
      - `read_file(path)`,
      - `write_file(path, content)`,
      - `list_dir(path)`.
  - Integrar com `CodeAgent` via helper `ensure_mcp_server(workdir)` (sem plugar em adapters ainda).

- **Saída da Fase 1**:
  - MCP server local rodando e testado via script (`python -m forge_code_agent.mcp_server`).
  - Testes unitários/integrados para `read_file/write_file`.

---

### Fase 2 — Integração com Codex (primeiro provider real)

**Objetivo**: Codex CLI usando MCP server local para chamar tools no workspace.

- **Tarefas**:
  - Descobrir/configurar como Codex CLI encontra MCP servers (env/flags).
  - Estender `CodexProviderAdapter` para:
    - chamar `ensure_mcp_server(request.workdir)` antes de `Popen`;
    - propagar env necessários para MCP (ex.: `MCP_SERVER_URL`, `MCP_SERVER_TOKEN`).
  - BDD:
    - criar `specs/bdd/40_mcp/40_mcp_tools.feature` com cenário `@mcp @e2e` usando Codex + MCP `read_file` em um arquivo de workspace.
    - implementar steps em `tests/bdd/test_mcp_tools_steps.py`.
  - Demo:
    - `examples/mcp/codex_tools_demo.sh`: mostra Codex lendo `tetris.py` via MCP e comentando o código.

- **Saída da Fase 2**:
  - Fluxo Codex + MCP passando e2e (demo + cenário `@mcp @e2e`).
  - `TOOL_CALLING_MCP_PROPOSAL.md` atualizado com detalhes de Codex.

---

### Fase 3 — Expandir para Claude e Gemini

**Objetivo**: ter Codex, Claude e Gemini com mesmo nível MCP.

- **Tarefas**:
  - Claude:
    - entender flags/env MCP;
    - adaptar `ClaudeProviderAdapter` para garantir MCP ativo e propagado;
    - adicionar cenário BDD específico se houver diferenças (nomes de tools, etc.).
  - Gemini:
    - repetir o processo em `GeminiProviderAdapter`.
  - Demos:
    - `examples/mcp/claude_tools_demo.sh`,
    - `examples/mcp/gemini_tools_demo.sh`.
  - Atualizar `examples/run_codex.sh`, `run_claude.sh`, `run_gemini.sh` para incluírem os demos MCP.

- **Saída da Fase 3**:
  - Multi-provider MCP funcional com pelo menos um demo real por provider.
  - Reuso do mesmo MCP server (mesmo conjunto de tools) para todos.

---

### Fase 4 — Eventos, observabilidade e UX

**Objetivo**: tornar MCP/tool calling auditável, confiável e fácil de entender.

- **Tarefas**:
  - Estender `AgentEvent` com `kind="tool"`, `tool_name`, `tool_args`, `tool_status`, `tool_duration_ms`.
  - MCP server, ao receber `toolCall`, deve:
    - gerar `AgentEvent` de `kind="tool"` e anexar a `ExecutionResult.raw_events` (via algum canal compartilhado);
    - retornar resultado ao provider normalmente.
  - Persistência:
    - definir log de sessão `.forgecode/runs/<run_id>.jsonl` com sequência de `AgentEvent`s + metadados;
    - gravar `run_id` e path do log em `ExecutionResult.metadata`.
  - CLI/UI:
    - `forge-code-agent run --log-events` (ou similar) para exibir contagem de tools e resumo;
    - script `examples/mcp/view_last_run_events.sh` para inspeção rápida de sessões.

- **Saída da Fase 4**:
  - Tool calling via MCP funcional e rastreável (quem chamou o quê, quando, com que resultado).
  - Base pronta para dashboards ou integrações externas.

---

### Fase 5 — Hardening (segurança, resiliência, performance)

**Objetivo**: levar MCP/tool calling para nível “produto de mercado”.

- **Tarefas**:
  - Segurança:
    - garantir que nenhuma tool MCP permite escapar do `workdir`;
    - permitir modo “read-only” (sem `write_file`/`run_shell`);
    - permitir desabilitar tools sensíveis por config.
  - Resiliência:
    - definir comportamento em falha MCP (fallback sem tools vs erro explícito);
    - timeouts por tool e por sessão MCP.
  - Performance/concorrência:
    - suportar múltiplos runs concorrentemente, com isolamento por sessão/run;
    - avaliar se MCP server é único por projeto ou por `CodeAgent`.
  - DX/Config:
    - adicionar `forge_code_agent_mcp.yml` com:
      - lista de tools habilitadas,
      - timeouts,
      - flags de segurança (ex.: “proibir run_shell em CI”).

- **Saída da Fase 5**:
  - MCP/tool calling em nível “produto”: seguro por padrão, configurável quando necessário, e com comportamento previsível em caso de falhas.

---

## 4. Integração com o ForgeProcess

- ValueTracks:
  - adicionar ValueTrack `40_mcp_tools` em `specs/bdd/tracks.yml` cobrindo:
    - tool calling via MCP,
    - observabilidade de tools,
    - segurança de workspace + tools.

- Processo (`process/process_execution_state.md`):
  - ao incluir `40_mcp_tools` no escopo do ciclo:
    - exigir pelo menos um cenário `@mcp @e2e` verde antes de encerrar o ciclo;
    - rodar os demos MCP em `examples/mcp` como parte do tour final da sprint/ciclo.

- Handoff / melhorias contínuas:
  - `project/recommendations.md`: registrar ajustes finos (latência, ferramentas perigosas, configs de segurança) que surgirem durante uso real para alimentar próximas sprints.
