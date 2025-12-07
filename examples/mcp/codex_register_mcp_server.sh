#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Codex MCP server register"
echo "==========================================="
echo
echo "Este script registra o servidor MCP local do forgeCodeAgent"
echo "no Codex, usando o subcomando 'codex mcp add'."
echo
echo "Nada é executado contra providers ainda — apenas configuração."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

echo "Repo root : ${REPO_ROOT}"
echo "Workspace : ${WORKDIR}"
echo

echo "Comando que será registrado no Codex MCP:"
echo "  codex mcp add forge-code-agent --env PYTHONPATH=\"${REPO_ROOT}/src\" -- python -m forge_code_agent.mcp_server --workdir \"${WORKDIR}\""
echo
echo "ATENÇÃO: isso cria/atualiza uma entrada global em ~/.codex/config.toml."
echo "         Revise se deseja essa configuração antes de continuar."
echo

read -r -p "Prosseguir com o registro no Codex MCP? [y/N] " ANSWER
case "${ANSWER:-n}" in
  y|Y)
    ;;
  *)
    echo "Operação cancelada."
    exit 0
    ;;
esac

# Garantir ambiente Python visível para o comando registrado
if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

# Registramos o servidor MCP como stdio, usando o Python do ambiente atual
# e garantindo que o pacote forge_code_agent seja encontrado via PYTHONPATH.
codex mcp add forge-code-agent \
  --env "PYTHONPATH=${REPO_ROOT}/src" \
  -- "${PYTHON_BIN}" -m forge_code_agent.mcp_server --workdir "${WORKDIR}"

echo
echo "Registro concluído. MCP servers configurados:"
codex mcp list || true
