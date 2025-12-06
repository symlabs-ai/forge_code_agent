#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 4 Demo (CLI + E2E baseline)"
echo "==========================================="
echo
echo "Este script demonstra a CLI oficial do forgeCodeAgent:"
echo " 1) Execução de prompt via 'run' com provider 'codex'."
echo " 2) Execução via YAML com provider 'codex'."
echo " 3) Execução via YAML com provider 'claude' (mesmo fluxo, só muda config)."
echo " 4) Execução simples com provider 'gemini' (quando configurado)."
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

# Configurações de providers reais (podem ser ajustadas conforme o ambiente).
# Aqui usamos exatamente os comandos recomendados para integração:
#
#  Codex (run, JSONL):
#    codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -C <workdir> "prompt"
#
#  Claude (run, JSON):
#    claude -p --output-format json --dangerously-skip-permissions --add-dir <workdir> -- "prompt"
#
#  Gemini (run, JSON):
#    gemini --output-format json --yolo "prompt"   (usando cwd=<workdir>)
#
# Os adapters acrescentam -C/--add-dir/cwd quando necessário; aqui definimos
# o comando base de forma explícita, sobrescrevendo qualquer valor anterior
# das variáveis para garantir um ambiente reproduzível.
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CLAUDE_CMD="claude -p --output-format json --dangerously-skip-permissions"
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"

WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

echo "[1/4] CLI run com provider codex"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "Qual é a capital do Brasil?"

echo
echo "[2/4] CLI run com YAML (provider codex)"

CONFIG_FILE="${WORKDIR}/forge_code_agent.yml"

echo "provider: codex" > "${CONFIG_FILE}"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --config "${CONFIG_FILE}" \
  --workdir "${WORKDIR}" \
  --prompt "Qual é a capital do Brasil?"

echo
echo "[3/4] CLI run com YAML (provider claude)"
echo "provider: claude" > "${CONFIG_FILE}"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --config "${CONFIG_FILE}" \
  --workdir "${WORKDIR}" \
  --prompt "Qual é a capital do Brasil?"

echo
echo "[4/4] CLI run com provider gemini"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider gemini \
  --workdir "${WORKDIR}" \
  --prompt "Qual é a capital do Brasil?"

echo
echo "Sprint 4 demo concluída (CLI básica funcional, multi-provider real)."
