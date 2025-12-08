#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 5 Demo: Módulo + Testes via CLI"
echo "==========================================="
echo
echo "Este script demonstra um fluxo de geração de módulo + testes usando"
echo "a CLI oficial do forgeCodeAgent com CodeManager e sessões:"
echo " 1) Prepara um workspace vazio."
echo " 2) Pede ao provider 'codex' para gerar módulo e testes."
echo " 3) Reexecuta com provider 'gemini' na mesma sessão."
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

# Configuração dos providers reais (ajuste conforme seu ambiente).
export FORGE_CODE_AGENT_CODEX_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CLAUDE_CMD="claude -p --output-format json --dangerously-skip-permissions"
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"

WORKDIR="${REPO_ROOT}/project/module_tests_demo_workdir"
mkdir -p "${WORKDIR}"

echo "[setup] Preparando workspace de módulo+testes em: ${WORKDIR}"
mkdir -p "${WORKDIR}/src" "${WORKDIR}/tests"

SESSION_ID="module-tests-session"

echo
echo "[1/2] Geração de módulo + testes com provider codex (sessão ${SESSION_ID})"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --use-code-manager \
  --session-id "${SESSION_ID}" \
  --prompt "Crie um pequeno serviço Python em src/generated_service.py com uma função pública, \
e crie o arquivo de testes correspondente em tests/test_generated_service.py. \
Escreva código executável e testes simples que possam ser rodados com pytest."

echo
echo "[check] Listando arquivos gerados em src/ e tests/"
echo "--- src/ ---"
ls -R "${WORKDIR}/src" || true
echo "--- tests/ ---"
ls -R "${WORKDIR}/tests" || true

echo
echo "[2/2] Nova chamada na mesma sessão com provider gemini (refinamento)"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider gemini \
  --workdir "${WORKDIR}" \
  --use-code-manager \
  --session-id "${SESSION_ID}" \
  --prompt "Revise o serviço e os testes existentes. \
Sugira melhorias nos nomes, docstrings e casos de teste. \
Se necessário, edite os arquivos para aplicar pequenas melhorias."

echo
echo "Sprint 5 demo (módulo + testes) concluída. Verifique ${WORKDIR} e logs/codeagent para o contexto da sessão ${SESSION_ID}."
