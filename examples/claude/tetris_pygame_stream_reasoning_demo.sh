#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Demo: Tetris (pygame) — Streaming Reasoning (Claude)"
echo "========================================================="
echo
echo "Este script pede ao provider 'claude' para:"
echo "  - \"produza um jogo de tetris em python usando pygame\""
echo "  - usando o diretório de trabalho como workspace do agente."
echo "Usamos o modo 'stream' com --reasoning-with-output, imprimindo"
echo "tanto reasoning quanto mensagens finais (quando disponíveis)."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

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

# Comando real do Claude para streaming JSON.
export FORGE_CODE_AGENT_CLAUDE_STREAM_CMD="claude -p --output-format stream-json --verbose --dangerously-skip-permissions"

WORKDIR="${REPO_ROOT}/examples/output"
mkdir -p "${WORKDIR}"

echo "[1/1] Streaming de reasoning/output do Tetris (pygame) com provider claude"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider claude \
  --workdir "${WORKDIR}" \
  --prompt "produza um jogo de tetris em python usando pygame" \
  --reasoning-with-output

echo
echo "Streaming (Claude) concluído. Verifique ${WORKDIR} para quaisquer arquivos gerados."
