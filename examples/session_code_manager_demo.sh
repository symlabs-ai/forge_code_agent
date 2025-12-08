#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Session Context Demo"
echo "==========================================="
echo
echo "Este demo mostra o uso do CodeManager + ContextSessionManager:"
echo "  - cria uma sessão com provider 'dummy';"
echo "  - troca o provider para 'dummy-2' mantendo o contexto;"
echo "  - persiste snapshots em logs/codeagent/session_*.json."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="${REPO_ROOT}/project/demo_workdir"
LOGS_DIR="${REPO_ROOT}/logs/codeagent"

mkdir -p "${WORKDIR}"
mkdir -p "${LOGS_DIR}"

echo "[info] Repo root : ${REPO_ROOT}"
echo "[info] Workdir   : ${WORKDIR}"
echo "[info] Logs dir  : ${LOGS_DIR}"
echo

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

SESSION_ID="demo-session"

echo "[1/3] Primeira execução com provider 'dummy'"
"${PYTHON_BIN}" - << PY
from pathlib import Path

from forge_code_agent.context.manager import CodeManager

repo_root = Path("${REPO_ROOT}")
logs_dir = repo_root / "logs" / "codeagent"
workdir = Path("${WORKDIR}")

manager = CodeManager(logs_dir=logs_dir)
result = manager.run(
    "Primeira pergunta na sessão",
    provider="dummy",
    session_id="${SESSION_ID}",
    workdir=workdir,
)
print(f"[python] provider={result.provider} status={result.status}")
PY

echo
echo "[2/3] Trocando provider para 'dummy-2' e rodando nova interação"
"${PYTHON_BIN}" - << PY
from pathlib import Path

from forge_code_agent.context.manager import CodeManager

repo_root = Path("${REPO_ROOT}")
logs_dir = repo_root / "logs" / "codeagent"
workdir = Path("${WORKDIR}")

manager = CodeManager(logs_dir=logs_dir)
manager.switch_provider("${SESSION_ID}", "dummy-2")
result = manager.run(
    "Segunda pergunta na mesma sessão",
    session_id="${SESSION_ID}",
    workdir=workdir,
)
print(f"[python] provider={result.provider} status={result.status}")

ctx = manager.get_session_context("${SESSION_ID}")
print(f"[python] total de eventos no contexto: {len(ctx)}")
PY

echo
echo "[3/3] Listando snapshots gravados em logs/codeagent"
ls -1 "${LOGS_DIR}" || true

echo
echo "Session Context demo concluído. Verifique os arquivos em ${LOGS_DIR} para inspecionar o contexto persistido."
