#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — ValueTrack Demo: Execution via CLI"
echo "==========================================="
echo
echo "Este script demonstra, via CLI oficial (python -m forge_code_agent),"
echo "o ValueTrack de execução de agentes de código:"
echo " 1) Execução básica com provider 'codex'."
echo " 2) Uso de arquivo de configuração YAML para trocar provider (codex -> claude)."
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

# Configurações de providers reais, alinhadas com o sprint4_demo.sh.
# Estes comandos podem ser ajustados no futuro, mas aqui são fixados para
# garantir reprodutibilidade do demo de ValueTrack.
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CLAUDE_CMD="claude -p --output-format json --dangerously-skip-permissions"
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"

WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

echo "[1/2] Execução básica via CLI com provider codex"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "print('hello from valuetrack demo (codex)')"

echo
echo "[2/2] Execução via CLI usando arquivo de configuração (YAML) para trocar provider"

CONFIG_FILE="${WORKDIR}/forge_code_agent.yml"

echo "provider: codex" > "${CONFIG_FILE}"
echo
echo "  - Config atual (codex):"
cat "${CONFIG_FILE}"
echo

"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --config "${CONFIG_FILE}" \
  --workdir "${WORKDIR}" \
  --prompt "print('hello from valuetrack demo (yaml codex)')"

echo
echo "  - Alterando configuração para provider: claude"
echo "provider: claude" > "${CONFIG_FILE}"
cat "${CONFIG_FILE}"
echo

"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --config "${CONFIG_FILE}" \
  --workdir "${WORKDIR}" \
  --prompt "print('hello from valuetrack demo (yaml claude)')"

echo
echo "ValueTrack demo concluída."
