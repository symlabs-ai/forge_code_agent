forgeCodeAgent — MCP demos (Codex)
==================================

Esta pasta contém scripts experimentais para integrar o forgeCodeAgent
como **MCP server local** com o Codex CLI.

Scripts principais:

- `examples/mcp/codex_register_mcp_server.sh`
  - Registra o servidor MCP local do forgeCodeAgent no Codex:
    - `forge-code-agent` apontando para `python -m forge_code_agent.mcp_server`.
  - Afeta a configuração global em `~/.codex/config.toml`.
  - Após rodar, `codex mcp list` deve mostrar a entrada `forge-code-agent`.

Uso típico:

1. Ative o ambiente do projeto (`.venv`) se desejar.
2. Rode:

   ```bash
   ./examples/mcp/codex_register_mcp_server.sh
   ```

3. Depois execute seus fluxos habituais com `codex exec ...` dentro de um
   workspace que o servidor MCP conhece (por exemplo `project/demo_workdir`).

Nesta fase, o servidor MCP implementa apenas um protocolo JSON-RPC mínimo
para tools de filesystem (`read_file`, `write_file`, `list_dir`) e **a
integração completa com o protocolo MCP oficial ainda será evoluída**
nas próximas fases do plano descrito em `docs/TOOL_CALLING_MCP_PLAN.md`.
