#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo " forgeCodeAgent — Demo: Tetris (pygame) — Streaming Reasoning + Output"
echo "========================================================="
echo
echo "Este script pede ao provider 'codex' para:"
echo "  - \"produza um jogo de tetris em python usando pygame\""
echo "  - usando o diretório de trabalho como workspace do agente."
echo "Aqui usamos o modo 'stream' com --reasoning-with-output, imprimindo"
echo "tanto as mensagens de raciocínio quanto a saída final do Codex."
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

# Comando real do Codex para streaming (JSONL linha a linha).
export FORGE_CODE_AGENT_CODEX_STREAM_CMD="codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check"

WORKDIR="${REPO_ROOT}/examples/output"
mkdir -p "${WORKDIR}"

echo "[1/1] Streaming de reasoning+output do Tetris (pygame) com provider codex"
"${PYTHON_BIN}" -m forge_code_agent.cli stream \
  --provider codex \
  --workdir "${WORKDIR}" \
  --prompt "produza um jogo de tetris em python usando pygame" \
  --reasoning-with-output

echo
echo "Streaming de reasoning+output concluído. Verifique ${WORKDIR} para quaisquer arquivos gerados (tetris.py, etc.)."
