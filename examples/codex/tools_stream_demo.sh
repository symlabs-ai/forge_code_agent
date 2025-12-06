#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Demo: Tools + Streaming (Codex)"
echo "========================================================="
echo
echo "Este script combina um hook pós-execução em Python via forge_code_agent"
echo "com streaming de reasoning/output do provider 'codex'."
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

# Comandos reais do Codex para run/stream em modo JSONL.
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CODEX_STREAM_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"

WORKDIR="${REPO_ROOT}/examples/output/tools_stream_codex"
mkdir -p "${WORKDIR}"

TARGET_FILE="tool_stream_demo_codex.py"
PROMPT_CONTENT="print('from tools+stream demo (codex)')"

echo "[1/2] tools-demo com generate_file (provider codex)"
"${PYTHON_BIN}" -m forge_code_agent.cli tools-demo \
  --provider codex \
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
echo "[2/2] Streaming de reasoning+output descrevendo o arquivo gerado (provider codex)"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "leia o arquivo ${TARGET_FILE} e descreva o que ele faz" \
  --reasoning-with-output

echo
echo "Demo Tools + Streaming (Codex) concluída. Verifique ${WORKDIR} para os arquivos gerados."
