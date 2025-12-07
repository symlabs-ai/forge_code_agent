# Current Plan — MCP Fase 1 (Servidor Local Mínimo)

> Escopo imediato: implementar a Fase 1 do plano MCP (`docs/TOOL_CALLING_MCP_PLAN.md`) com um servidor MCP local mínimo,
> tools básicas de filesystem e integração inicial com o `CodeAgent` (sem ainda plugar nos adapters dos providers).

---

## 1. Servidor MCP local mínimo

- [ ] Criar módulo `src/forge_code_agent/mcp_server/` com:
  - [ ] entrypoint `python -m forge_code_agent.mcp_server` que inicia um servidor MCP local;
  - [ ] configuração simples via flags/env (ex.: `--workdir`, `--socket` ou `--stdio`);
  - [ ] ciclo de vida básico (run loop até EOF / sinal).
- [ ] Implementar tools mínimas baseadas em `FilesystemWorkspaceAdapter`:
  - [ ] `read_file(path)` — devolve conteúdo de arquivo dentro do workspace;
  - [ ] `write_file(path, content)` — grava conteúdo respeitando sandbox de workspace;
  - [ ] `list_dir(path)` — lista arquivos/pastas relativos ao workspace.

---

## 2. Integração leve com CodeAgent

- [ ] Adicionar helper `ensure_mcp_server(workdir: Path) -> MCPServerHandle` em módulo dedicado
      (ex.: `src/forge_code_agent/mcp_server/integration.py`):
  - [ ] calcular identificação única do servidor por `workdir`;
  - [ ] (Fase 1) expor estrutura de handle com informações de conexão (mesmo que ainda não usadas);
  - [ ] preparar ponto de extensão para iniciar o servidor em background em Fase 2.
- [ ] Conectar `CodeAgent` ao conceito de MCP apenas via `ExecutionResult.metadata`:
  - [ ] reservar campos como `mcp_enabled` / `mcp_endpoint` / `run_id` (sem preencher ainda, se não houver servidor ativo).

---

## 3. Testes e validação mínima

- [ ] Criar testes unitários para as tools MCP:
  - [ ] `read_file` lendo arquivo existente no `tmp_path`;
  - [ ] `write_file` criando/atualizando arquivo no workspace com proteção de path traversal;
  - [ ] `list_dir` listando apenas caminhos dentro do workspace.
- [ ] Adicionar teste simples de bootstrap:
  - [ ] validar que `python -m forge_code_agent.mcp_server` consegue inicializar com um `workdir` de teste
        (mesmo que o protocolo MCP ainda não seja exercitado de ponta a ponta).

---

## 4. Critérios de conclusão da Fase 1 (MCP)

- [ ] Módulo `mcp_server` presente e importável.
- [ ] Tools mínimas (`read_file`, `write_file`, `list_dir`) cobertas por testes automatizados.
- [ ] Entry point `python -m forge_code_agent.mcp_server --workdir <dir>` executa sem erro fatal em ambiente de desenvolvimento.
- [ ] `docs/TOOL_CALLING_MCP_PLAN.md` continua alinhado com a implementação (Fase 1 marcada como em progresso/concluída).

---

## 5. Configuração manual do Codex para usar o MCP local

Para validar a integração com Codex na ponta a ponta, é necessário registrar o servidor MCP do forgeCodeAgent no Codex:

- [ ] Rodar o script de registro:
  - `./examples/mcp/codex_register_mcp_server.sh`
- [ ] Confirmar, quando solicitado, que deseja adicionar a entrada MCP (isso atualiza `~/.codex/config.toml`).
- [ ] Verificar que o servidor MCP está configurado:
  - `codex mcp list` deve listar `forge-code-agent` apontando para `python -m forge_code_agent.mcp_server --workdir project/demo_workdir`.

Essa configuração é pré‑requisito para os próximos demos Codex+MCP descritos em `docs/TOOL_CALLING_MCP_PLAN.md`.
