# Current Plan — Próximo Ciclo (MCP multi-provider + BDD Contexto + CLI-first)

> Este plano descreve o **próximo ciclo** do ForgeProcess para o forgeCodeAgent,
> partindo do estado atual em que:
> - `ContextSessionManager` e `CodeManager` estão implementados e testados;
> - MCP está centralizado no `CodeManager` (Codex já validado via demos);
> - a CLI expõe `--session-id`, `--use-code-manager` e `--auto-summarize`.

O foco agora é:

- elevar MCP para **multi-provider real** (Codex + Claude + Gemini);
- consolidar BDD/ValueTracks de contexto/sessões;
- reforçar a disciplina **CLI-first** com exemplos e documentação;
- iniciar o hardening de MCP (segurança e limites);
- e ancorar tudo isso em dois fluxos de valor concretos:
  - **PR assistido** (CodeAgent/CodeManager ajudando no review de PRs);
  - **Geração de módulo + testes** (workflow de criação de código + testes em um workspace real).

---

## 1. MCP Multi-Provider (Codex + Claude + Gemini)

- [x] Estender a integração MCP além do Codex:
  - [x] Adaptar adapters de `claude` e `gemini` para consumir MCP da mesma forma que o Codex (env/flags apropriados).
  - [x] Garantir que `CodeManager.run` injete metadata `"mcp"` para qualquer provider (já feito), e que os adapters façam uso dessa configuração.
- [x] Criar demos MCP por provider em `examples/mcp/`:
  - [x] `examples/mcp/claude_tools_demo.sh` — fluxo simples de leitura de arquivo via MCP.
  - [x] `examples/mcp/gemini_tools_demo.sh` — fluxo equivalente para Gemini.
- [x] Atualizar `examples/run_codex.sh`, `run_claude.sh`, `run_gemini.sh` para incluir os demos MCP no tour de fim de sprint/ciclo.

---

## 2. BDD — Contexto e Sessões (CodeManager + Summaries)

- [x] Criar uma feature dedicada a contexto/sessões:
  - [x] `specs/bdd/41_context/41_code_manager_sessions.feature` com cenários, por exemplo:
    - [x] Reutilizar contexto entre múltiplas execuções na mesma `session_id`.
    - [x] Trocar de provider (`codex` → `claude` ou `dummy` → `dummy-2`) mantendo histórico.
    - [x] Disparar `summarize_if_needed()` quando o tamanho do contexto exceder os limites.
- [x] Implementar steps em `tests/bdd/test_code_manager_context_steps.py`:
  - [x] Exercitar `CodeManager.run` com e sem `summarizer_factory`.
  - [x] Verificar eventos em `ContextSessionManager` e presença de `summaries` quando esperado.
- [x] Garantir que o ValueTrack relacionado (contexto/MCP) esteja refletido em `specs/bdd/tracks.yml`.

---

## 3. CLI-first — Sessões e Auto-Resumo

- [x] Documentar a CLI com sessões e auto-resumo:
  - [x] Adicionar seção específica em algum doc de referência (ex.: `docs/sites` ou guia de usuário) explicando:
    - uso de `python -m forge_code_agent.cli run --use-code-manager --session-id ...`;
    - comportamento de `--auto-summarize` e quando o resumo é aplicado (limites de eventos/chars);
    - relação entre `logs/codeagent/session_*.json` e as sessões criadas via CLI.
- [x] Criar um exemplo CLI-first que use diretamente o `main`:
  - [x] por exemplo, um script shell que chama a CLI algumas vezes com a mesma `session-id` e mostra onde os snapshots são gravados.
- [x] Opcional: alinhar texto de `process/PROCESS.md` e/ou `process/process_execution_state.md` para citar explicitamente o uso de sessões CLI como parte do “tour” de fim de ciclo (seguindo o princípio CLI-first).

---

## 4. Hardening Inicial de MCP (Segurança e Limites)

- [x] Reforçar regras de workspace no MCP server (`src/forge_code_agent/mcp_server`):
  - [x] Garantir que todas as tools (`read_file`, `write_file`, `list_dir`) usem `FilesystemWorkspaceAdapter.ensure_within_workspace` corretamente.
  - [x] Adicionar testes cobrindo paths maliciosos (`../`, absolutos) para cada tool.
- [x] Introduzir primeiros limites operacionais:
  - [x] timeouts básicos para operações potencialmente lentas (ex.: futuras tools de teste/lint);
  - [x] regra clara de fallback em caso de falha no MCP (por enquanto: erros de MCP não devem quebrar `run()`, mas devem ficar registrados em logs/metadata).
- [x] Ajustar a documentação de MCP:
  - [x] atualizar `docs/TOOL_CALLING_MCP_PLAN.md` e `docs/TOOL_CALLING_MCP_PROPOSAL.md` com o estado atual (Codex ✓, Claude/Gemini → próximo ciclo) e com quaisquer decisões de segurança introduzidas.

---

## 5. Critérios de Encerramento deste Ciclo

- [x] Pelo menos um demo MCP funcional para **cada** provider principal:
  - [x] Codex (já existente, mantido verde);
  - [x] Claude;
  - [x] Gemini.
- [x] Pelo menos um cenário `@mcp @e2e` passando que envolva MCP + CodeManager (pode ser focado inicialmente em Codex, mas idealmente estendido para multi-provider).
- [x] Uma feature BDD de contexto/sessões (`41_code_manager_sessions.feature`) cobrindo:
  - [x] reuso de contexto;
  - [x] troca de provider em uma mesma sessão;
  - [x] presença de pelo menos um `summary` persistido.
- [x] Documentação da CLI-first para sessões (incluindo `--auto-summarize`) publicada em `docs/`.

---

## 6. Próximos ValueTracks (PR assistido + módulo + testes)

### 6.1 ValueTrack: PR Assistido via CLI + MCP

**Descrição**: permitir que um PR seja analisado por um coding agent via CLI, usando MCP/tools para ler diffs/arquivos e sugerir melhorias.

Behaviors alvo (a serem detalhados em features BDD futuras):

- Executar um fluxo de PR assistido que:
  - lê os arquivos/diffs de um PR (via MCP `read_file` / futuras tools específicas);
  - gera comentários ou um resumo de mudanças;
  - roda a partir de um script CLI (`examples/sprintX_pr_assist_demo.sh`) que usa `forge-code-agent` como entrypoint.

### 6.2 ValueTrack: Geração de Módulo + Testes

**Descrição**: permitir que um agente de código gere um módulo Python e seus testes, persistindo arquivos em um workspace e (futuramente) rodando testes via MCP.

Behaviors alvo:

- A partir de um diretório de trabalho vazio ou semi-estruturado:
  - gerar um módulo (ex.: `src/app/auth.py`) e testes correspondentes (ex.: `tests/test_auth.py`);
  - persistir os arquivos no workspace via `CodeAgent`/CLI (`--write-to-file` ou comandos orientados a arquivos);
  - opcionalmente, invocar ferramentas MCP futuras (`run_tests`) para validar a geração.

Ao final do **próximo ciclo**, o objetivo é que o forgeCodeAgent tenha:

- fluxos de **PR assistido** exercitando MCP + CodeManager em workspaces reais;
- geração de **módulo + testes** via CLI e persistência em workspace;
- cenários BDD e demos CLI que encadeiem esses elementos em direção a um tour completo:
  - PR assistido (leitura de arquivos + sugestões);
  - geração de módulo + testes em um workspace real.

---

## 7. Estado deste Ciclo (MCP multi-provider + contexto)

- Itens 1–5 acima estão concluídos (MCP multi-provider, BDD de contexto/sessões, CLI-first e hardening inicial).
- As seções 6.1 e 6.2 definem os ValueTracks priorizados para o **próximo ciclo**: PR assistido e geração de módulo + testes.
