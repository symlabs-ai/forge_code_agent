#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Demo: Tetris (pygame) — Streaming (Gemini)"
echo "========================================================="
echo
echo "Este script pede ao provider 'gemini' para:"
echo "  - \"produza um jogo de tetris em python usando pygame\""
echo "  - usando o diretório de trabalho como workspace do agente."
echo "Usamos o modo 'stream' com --reasoning-with-output; o parsing"
echo "depende do formato JSON emitido pelo Gemini."
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

# Comando real do Gemini para streaming JSON.
export FORGE_CODE_AGENT_GEMINI_STREAM_CMD="gemini --output-format stream-json --yolo"

WORKDIR="${REPO_ROOT}/examples/output"
mkdir -p "${WORKDIR}"

echo "[1/1] Streaming de Tetris (pygame) com provider gemini"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider gemini \
  --workdir "${WORKDIR}" \
  --prompt "produza um jogo de tetris em python usando pygame" \
  --reasoning-with-output

echo
echo "Streaming (Gemini) concluído. Verifique ${WORKDIR} para quaisquer arquivos gerados."
