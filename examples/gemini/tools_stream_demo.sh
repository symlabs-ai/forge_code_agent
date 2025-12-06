#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Demo: Tools + Streaming (Gemini)"
echo "========================================================="
echo
echo "Este script combina um hook pós-execução em Python via forge_code_agent"
echo "com streaming de reasoning/output do provider 'gemini'."
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

# Comandos reais do Gemini para run/stream em modo JSONL.
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"
export FORGE_CODE_AGENT_GEMINI_STREAM_CMD="gemini --output-format stream-json --yolo"

WORKDIR="${REPO_ROOT}/examples/output/tools_stream_gemini"
mkdir -p "${WORKDIR}"

TARGET_FILE="tool_stream_demo_gemini.py"
PROMPT_CONTENT="print('from tools+stream demo (gemini)')"

echo "[1/2] tools-demo com generate_file (provider gemini)"
"${PYTHON_BIN}" -m forge_code_agent.cli tools-demo \
  --provider gemini \
  --workdir "${WORKDIR}" \
  --write-to-file "${TARGET_FILE}" \
  --prompt "${PROMPT_CONTENT}"

if [ -f "${WORKDIR}/${TARGET_FILE}" ]; then
  echo "Arquivo gerado a partir do hook pós-execução encontrado: ${WORKDIR}/${TARGET_FILE}"
  echo "Conteúdo:"
  echo "-------------------------------------------"
  cat "${WORKDIR}/${TARGET_FILE}"
  echo
  echo "-------------------------------------------"
else
  echo "ERRO: arquivo ${WORKDIR}/${TARGET_FILE} não foi gerado pela tools-demo."
  exit 1
fi

echo
echo "[2/2] Streaming de reasoning+output descrevendo o arquivo gerado (provider gemini)"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider gemini \
  --workdir "${WORKDIR}" \
  --prompt "leia o arquivo ${TARGET_FILE} e descreva o que ele faz" \
  --reasoning-with-output

echo
echo "Demo Tools + Streaming (Gemini) concluída. Verifique ${WORKDIR} para os arquivos gerados."
