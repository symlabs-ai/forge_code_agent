#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Session + Auto-Summarize Demo"
echo "========================================================="
echo
echo "Este demo mostra o CodeManager + ContextSessionManager com resumo automático:"
echo "  - cria uma sessão com provider 'dummy';"
echo "  - força um limite baixo de eventos para disparar summarize_if_needed();"
echo "  - usa AgentSummarizer (via CodeAgent) para gerar um resumo;"
echo "  - persiste snapshots em logs/codeagent/session_*.json e exibe o resumo."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="${REPO_ROOT}/project/demo_workdir_autosum"
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

SESSION_ID="autosum-demo-session"

echo "[1/3] Executando múltiplas interações na mesma sessão com limite baixo de eventos"
"${PYTHON_BIN}" - << PY
from pathlib import Path

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.context.summarizer import AgentSummarizer
from forge_code_agent.runtime.agent import CodeAgent

repo_root = Path("${REPO_ROOT}")
logs_dir = repo_root / "logs" / "codeagent"
workdir = Path("${WORKDIR}")

def summarizer_factory(agent: CodeAgent, _session) -> AgentSummarizer:
    return AgentSummarizer(agent=agent)

manager = CodeManager(logs_dir=logs_dir, summarizer_factory=summarizer_factory)

session_id = "${SESSION_ID}"

# Forçamos limites baixos de eventos/chars para disparar rapidamente o resumo.
session = manager._get_or_create_session(session_id, workdir, provider="dummy")  # type: ignore[attr-defined]
session.max_events = 6
session.max_summary_chars = 500

for i in range(8):
    prompt = f"Pergunta {i}: descreva rapidamente o estado atual do sistema."
    result = manager.run(
        prompt,
        provider="dummy",
        session_id=session_id,
        workdir=workdir,
    )
    print(f"[python] run {i} -> provider={result.provider} status={result.status}")

PY

echo
echo "[2/3] Carregando último snapshot da sessão e mostrando contagem de eventos/summaries"
"${PYTHON_BIN}" - << PY
from pathlib import Path

from forge_code_agent.context.session_manager import ContextSessionManager

logs_dir = Path("${LOGS_DIR}")
session_id = "${SESSION_ID}"

snapshots = sorted(logs_dir.glob(f"session_{session_id}_*.json"))
if not snapshots:
    raise SystemExit("Nenhum snapshot encontrado para a sessão de auto-summarize.")

last_snapshot = snapshots[-1]
print(f"[python] último snapshot: {last_snapshot.name}")

loaded = ContextSessionManager.load(last_snapshot)
print(f"[python] eventos atuais: {len(loaded.events)}")
print(f"[python] summaries registrados: {len(loaded.summaries)}")

if loaded.summaries:
    last_summary = loaded.summaries[-1]
    print("[python] resumo mais recente:")
    print("-------------------------------------------")
    print(last_summary.text)
    print("-------------------------------------------")

PY

echo
echo "[3/3] Listando arquivos de sessão em logs/codeagent"
ls -1 "${LOGS_DIR}" | grep "session_${SESSION_ID}_" || true

echo
echo "Session + Auto-Summarize demo concluído. Verifique ${LOGS_DIR} para inspecionar os snapshots e summaries."
