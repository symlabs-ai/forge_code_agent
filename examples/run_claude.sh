#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Runner: Claude demos"
echo "==========================================="
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -x "${REPO_ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.venv/bin/activate"
fi

CLAUDE_DIR="${REPO_ROOT}/examples/claude"

if [ ! -d "${CLAUDE_DIR}" ]; then
  echo "Nenhuma pasta examples/claude encontrada."
  exit 0
fi

for demo in "${CLAUDE_DIR}"/*.sh; do
  [ -f "${demo}" ] || continue
  echo
  echo ">>> Executando Claude demo: $(basename "${demo}")"
  echo "-------------------------------------------"
  bash "${demo}"
  echo "-------------------------------------------"
done
