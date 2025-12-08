#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 5 Demo: PR Assistido via CLI + MCP"
echo "==========================================="
echo
echo "Este script demonstra um fluxo de PR assistido usando a CLI oficial"
echo "do forgeCodeAgent com CodeManager e sessões:"
echo " 1) Prepara um workspace com arquivos modificados e pr_files.txt."
echo " 2) Executa uma análise de PR com provider 'codex'."
echo " 3) Reexecuta a análise com provider 'claude' na mesma sessão."
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
export FORGE_CODE_AGENT_CLAUDE_STREAM_CMD="claude -p --output-format stream-json --verbose --dangerously-skip-permissions"
export FORGE_CODE_AGENT_GEMINI_CMD="gemini --output-format json --yolo"

WORKDIR="${REPO_ROOT}/project/pr_assist_demo_workdir"
mkdir -p "${WORKDIR}"

echo "[setup] Preparando workspace de PR em: ${WORKDIR}"
mkdir -p "${WORKDIR}/src" "${WORKDIR}/tests"

cat > "${WORKDIR}/src/service.py" << 'PY'
def add(a: int, b: int) -> int:
    \"\"\"Soma dois inteiros.\"\"\"
    return a + b


def subtract(a: int, b: int) -> int:
    \"\"\"Subtrai dois inteiros.\"\"\"
    return a - b
PY

cat > "${WORKDIR}/tests/test_service.py" << 'PY'
from src.service import add, subtract


def test_add():
    assert add(1, 1) == 2


def test_subtract():
    assert subtract(2, 1) == 1
PY

cat > "${WORKDIR}/pr_files.txt" << 'EOF'
src/service.py
tests/test_service.py
EOF

SESSION_ID="pr-assist-session"

echo
echo "[1/2] PR assistido com provider codex (sessão ${SESSION_ID})"
"${PYTHON_BIN}" -m forge_code_agent.cli run \
  --provider codex \
  --workdir "${WORKDIR}" \
  --use-code-manager \
  --session-id "${SESSION_ID}" \
  --prompt "Você está em um workspace com um pull request. \
Os arquivos alterados estão listados em pr_files.txt. \
Leia esses arquivos, faça um resumo das mudanças mais importantes \
e sugira pelo menos duas melhorias de código ou testes."

echo
echo "[2/2] PR assistido com provider claude (STREAMING, mesmo workspace)"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider claude \
  --workdir "${WORKDIR}" \
  --prompt "Reanalise o mesmo pull request, focando em riscos de design, \
complexidade excessiva e oportunidades de simplificação. \
Liste recomendações objetivas para o time." \
  --reasoning-with-output

echo
echo "Sprint 5 demo (PR assistido) concluída. Verifique logs/codeagent para o contexto da sessão ${SESSION_ID}."
