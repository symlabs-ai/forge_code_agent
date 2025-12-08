#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Sprint 5 Demo: PR Assistido (FULL Streaming)"
echo "========================================================="
echo
echo "Este script mostra PR assistido com *streaming* para Codex e Claude:"
echo " 1) Codex em modo stream-json com --reasoning-with-output."
echo " 2) Claude em modo stream-json com --reasoning-with-output."
echo "Não usa CodeManager/sessões; o foco aqui é apenas visualizar o stream."
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

# Comandos de streaming para Codex e Claude.
export FORGE_CODE_AGENT_CODEX_STREAM_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"
export FORGE_CODE_AGENT_CLAUDE_STREAM_CMD="claude -p --output-format stream-json --verbose --dangerously-skip-permissions"

WORKDIR="${REPO_ROOT}/project/pr_assist_streaming_demo_workdir"
mkdir -p "${WORKDIR}"

echo "[setup] Preparando workspace de PR streaming em: ${WORKDIR}"
mkdir -p "${WORKDIR}/src" "${WORKDIR}/tests"

cat > "${WORKDIR}/src/service.py" << 'PY'
def add(a: int, b: int) -> int:
    """Soma dois inteiros."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtrai dois inteiros."""
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

PROMPT="Você está em um workspace com um pull request. \
Os arquivos alterados estão listados em pr_files.txt. \
Leia esses arquivos, resuma as mudanças e sugira melhorias de código e de testes."

echo
echo "[1/2] PR assistido em STREAMING com provider codex"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "${PROMPT}" \
  --reasoning-with-output

echo
echo "[2/2] PR assistido em STREAMING com provider claude"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider claude \
  --workdir "${WORKDIR}" \
  --prompt "${PROMPT}" \
  --reasoning-with-output

echo
echo "Sprint 5 demo (PR assistido FULL streaming) concluída."
