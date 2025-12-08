#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Claude + MCP read_file demo"
echo "==========================================="
echo
echo "Este demo supõe que:"
echo " - o servidor MCP 'forge-code-agent' já foi registrado (via Codex ou config compartilhada);"
echo " - a CLI do Claude está instalada e autenticada."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKDIR="${REPO_ROOT}/project/demo_workdir_claude_mcp"
mkdir -p "${WORKDIR}"

echo "[info] Workspace: ${WORKDIR}"
echo

DEMO_FILE="${WORKDIR}/mcp_demo_file_claude.txt"
echo "[step] Criando arquivo de exemplo em ${DEMO_FILE}"
cat > "${DEMO_FILE}" << 'EOF'
Este é um arquivo de exemplo para o demo Claude + MCP.
Ele foi criado pelo script claude_tools_demo.sh
no repositório forgeCodeAgent.
EOF

echo
echo "[step] Chamando claude no workspace, pedindo explicitamente para usar a tool MCP read_file"
echo

PROMPT=$'Use o servidor MCP local "forge-code-agent" (se disponível) para chamar uma tool de leitura de arquivos.\n\nTarefa:\n- Use a tool para ler o arquivo "mcp_demo_file_claude.txt" no workspace atual.\n- Depois, explique em poucas linhas o conteúdo desse arquivo.\n\nSe o servidor MCP não estiver disponível, explique isso claramente.'

claude -p --output-format json --dangerously-skip-permissions --add-dir "${WORKDIR}" -- "${PROMPT}"

echo
echo "Demo Claude + MCP (read_file) concluído."
