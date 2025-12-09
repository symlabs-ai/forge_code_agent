#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 6 Demo: MCP + Sessões + CLI UX"
echo "==========================================="
echo
echo "Este script demonstra os principais resultados da Sprint 6:"
echo " 1) Servidor MCP modularizado ainda respondendo a ping/initialize/tools."
echo " 2) Persistência de sessões com arquivo 'current' e retenção de snapshots."
echo " 3) Uso simplificado de '--session-id' na CLI, implicando CodeManager."
echo

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR_MCP="$ROOT_DIR/project/demo_workdir_sprint6"
WORKDIR_SESSION="$ROOT_DIR/project/demo_session_sprint6"
LOGS_DIR="$ROOT_DIR/logs/codeagent"

mkdir -p "$WORKDIR_MCP" "$WORKDIR_SESSION"

echo "[1/3] MCP server ping (newline JSON)"
echo "-------------------------------------------"
python3 -m forge_code_agent.mcp_server --workdir "$WORKDIR_MCP" << 'EOF' | head -n 1
{"jsonrpc": "2.0", "id": "1", "method": "ping", "params": {}}
EOF
echo

echo "[2/3] Execução via CLI com session-id (CodeManager implícito)"
echo "-------------------------------------------"
SESSION_ID="sprint6-demo-session"

python3 -m forge_code_agent.cli run \
  --provider codex \
  --workdir "$WORKDIR_SESSION" \
  --prompt "Diga 'hello from sprint6 demo'" \
  --session-id "$SESSION_ID"

echo
echo "Snapshots de sessão em $LOGS_DIR (mostrando arquivos da sessão $SESSION_ID):"
ls -1 "$LOGS_DIR"/session_${SESSION_ID}_*.json || echo "(nenhum snapshot encontrado)"
echo

echo "[3/3] Streaming com reasoning+output (verificando UX de flags)"
echo "-------------------------------------------"
python3 -m forge_code_agent.cli stream \
  --provider codex \
  --workdir "$WORKDIR_SESSION" \
  --prompt "Explique em duas frases o que esta demo faz" \
  --reasoning-with-output

echo
echo "Sprint 6 demo concluída (MCP + sessões + CLI UX)."
