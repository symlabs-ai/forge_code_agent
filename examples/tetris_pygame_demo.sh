#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Demo: Tetris em Python (pygame)"
echo "==========================================="
echo
echo "Este script pede ao provider 'codex' para:"
echo "  - \"produza um jogo de tetris em python usando pygame\""
echo "  - usando o diretório de trabalho como workspace do agente."
echo "Os arquivos gerados (por exemplo, tetris.py) serão salvos em examples/output/."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ativar ambiente Python do projeto (.venv) se existir
if [ -x "${REPO_ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.venv/bin/activate"
  PYTHON_BIN="python"
elif [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

export PYTHONPATH="${PYTHONPATH:-}:${REPO_ROOT}/src"

# Comando real do Codex (mesmo padrão dos outros demos).
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"

WORKDIR="${REPO_ROOT}/examples/output"
mkdir -p "${WORKDIR}"

echo "[1/1] Executando prompt de Tetris em Python (pygame) com provider codex"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "produza um jogo de tetris em python usando pygame"

echo
echo "Arquivos (se gerados) estarão em: ${WORKDIR}"
echo "Use 'ls ${WORKDIR}' para inspecionar e 'python tetris*.py' (dentro do venv) para testar."
