#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Runner: Gemini demos"
echo "==========================================="
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -x "${REPO_ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.venv/bin/activate"
fi

GEMINI_DIR="${REPO_ROOT}/examples/gemini"

if [ ! -d "${GEMINI_DIR}" ]; then
  echo "Nenhuma pasta examples/gemini encontrada."
  exit 0
fi

for demo in "${GEMINI_DIR}"/*.sh; do
  [ -f "${demo}" ] || continue
  echo
  echo ">>> Executando Gemini demo: $(basename "${demo}")"
  echo "-------------------------------------------"
  bash "${demo}"
  echo "-------------------------------------------"
done
