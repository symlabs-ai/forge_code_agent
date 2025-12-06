#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — ValueTrack Demo: Tools + Files"
echo "==========================================="
echo
echo "Este script demonstra o ValueTrack de hooks + arquivos:"
echo " 1) Execução via CLI com --write-to-file, persistindo código no workspace."
echo " 2) Verificação de conteúdo do arquivo gerado."
echo " 3) Demonstração de hook pós-execução via CLI (tools-demo) gerando arquivo."
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

# Configurações de providers reais para o demo.
# Forçamos comandos explícitos aqui para não herdar valores antigos do ambiente
# (como variantes com --output-format que não são mais suportadas pelo Codex).
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CLAUDE_CMD="claude -p --output-format json --dangerously-skip-permissions"
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"

WORKDIR="${REPO_ROOT}/project/tools_files_workdir"
mkdir -p "${WORKDIR}"

TARGET_FILE="generated_from_cli.py"
TOOL_FILE="tool_generated_from_cli.py"

echo "[1/3] CLI run com --write-to-file (provider codex)"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --write-to-file "${TARGET_FILE}" \
  --prompt "def generated_from_cli():\n    return 'ok'"

echo
echo "[2/3] Verificando arquivo gerado no workspace"
if [ -f "${WORKDIR}/${TARGET_FILE}" ]; then
  echo "Arquivo encontrado: ${WORKDIR}/${TARGET_FILE}"
  echo "Conteúdo:"
  echo "-------------------------------------------"
  cat "${WORKDIR}/${TARGET_FILE}"
  echo
  echo "-------------------------------------------"
else
  echo "ERRO: arquivo ${WORKDIR}/${TARGET_FILE} não foi gerado."
  exit 1
fi

echo
echo "[3/3] CLI tools-demo com tool generate_file (provider codex)"
"${PYTHON_BIN}" -m forge_code_agent.cli tools-demo \
  --provider codex \
  --workdir "${WORKDIR}" \
  --write-to-file "${TOOL_FILE}" \
  --prompt "print('from tool demo')"

if [ -f "${WORKDIR}/${TOOL_FILE}" ]; then
  echo "Arquivo gerado a partir do hook pós-execução encontrado: ${WORKDIR}/${TOOL_FILE}"
  echo "Conteúdo:"
  echo "-------------------------------------------"
  cat "${WORKDIR}/${TOOL_FILE}"
  echo
  echo "-------------------------------------------"
else
  echo "ERRO: arquivo ${WORKDIR}/${TOOL_FILE} não foi gerado pela tools-demo."
  exit 1
fi

echo
echo "ValueTrack hooks+files demo concluída (persistência de arquivo + hook pós-execução via CLI)."
