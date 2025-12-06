#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Runner: Codex demos"
echo "==========================================="
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ativar ambiente Python do projeto (.venv) se existir
if [ -x "${REPO_ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.venv/bin/activate"
fi

CODEx_DIR="${REPO_ROOT}/examples/codex"

if [ ! -d "${CODEx_DIR}" ]; then
  echo "Nenhuma pasta examples/codex encontrada."
  exit 0
fi

for demo in "${CODEx_DIR}"/*.sh; do
  [ -f "${demo}" ] || continue
  echo
  echo ">>> Executando Codex demo: $(basename "${demo}")"
  echo "-------------------------------------------"
  bash "${demo}"
  echo "-------------------------------------------"
done
