#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Codex + MCP read_file demo"
echo "==========================================="
echo
echo "Este demo supõe que:"
echo " - o servidor MCP 'forge-code-agent' já foi registrado via"
echo "   ./examples/mcp/codex_register_mcp_server.sh"
echo " - o Codex CLI está instalado e autenticado."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

echo "[info] Workspace: ${WORKDIR}"
echo

echo "[step] Verificando MCP servers registrados no Codex..."
codex mcp list || true
echo

DEMO_FILE="${WORKDIR}/mcp_demo_file.txt"
echo "[step] Criando arquivo de exemplo em ${DEMO_FILE}"
cat > "${DEMO_FILE}" << 'EOF'
Este é um arquivo de exemplo para o demo Codex + MCP.
Ele foi criado pelo script codex_read_file_demo.sh
no repositório forgeCodeAgent.
EOF

echo
echo "[step] Chamando codex exec no workspace, pedindo explicitamente para usar a tool MCP read_file"
echo

PROMPT=$'Use o servidor MCP local "forge-code-agent" (se disponível) para chamar uma tool de leitura de arquivos.\n\nTarefa:\n- Use a tool para ler o arquivo "mcp_demo_file.txt" no workspace atual.\n- Depois, explique em poucas linhas o conteúdo desse arquivo.\n\nSe o servidor MCP não estiver disponível, explique isso claramente.'

codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -C "${WORKDIR}" "${PROMPT}"

echo
echo "Demo Codex + MCP (read_file) concluído."
