#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "== forgeCodeAgent / ForgeProcess env setup =="

# 1) Descompactar git-dev.zip se ainda não houver arquivos de pre-commit
if [ ! -f "pre-commit-config.yaml" ] && [ -f "process/env/git-dev.zip" ]; then
  if command -v unzip >/dev/null 2>&1; then
    echo "-- Unpacking process/env/git-dev.zip into repo root..."
    unzip -o process/env/git-dev.zip >/dev/null
  else
    echo "!! 'unzip' not found; please extract process/env/git-dev.zip manually."
  fi
fi

# 2) Criar .venv na raiz, se ainda não existir
if [ ! -d ".venv" ]; then
  echo "-- Creating .venv virtualenv in repo root..."
  PYTHON_BIN="python3.12"
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
  "$PYTHON_BIN" -m venv .venv
fi

VENV_BIN=".venv/bin"
if [ -d ".venv/Scripts" ]; then
  VENV_BIN=".venv/Scripts"
fi

PIP="$VENV_BIN/pip"
PYTHON="$VENV_BIN/python"

# 3) Instalar dependências de dev (pre-commit, ruff, pytest, etc.) se dev-requirements.txt existir
if [ -f "dev-requirements.txt" ]; then
  echo "-- Installing dev dependencies from dev-requirements.txt..."
  "$PIP" install -r dev-requirements.txt
else
  echo "!! dev-requirements.txt not found; skipping dev dependency install."
fi

# 4) Instalar ForgeBase (núcleo)
echo "-- Installing ForgeBase from GitHub..."
"$PIP" install git+https://github.com/symlabs-ai/forgebase.git

# 5) Verificações rápidas
echo "-- Verifying forgebase import..."
"$PYTHON" - << 'PY'
import forgebase
print("forgebase OK:", getattr(forgebase, "__version__", "unknown"))
PY

if command -v "$VENV_BIN/pytest" >/dev/null 2>&1; then
  echo "-- pytest version:"
  "$VENV_BIN/pytest" --version || true
  if [ -d "tests/bdd" ]; then
    echo "-- Collecting BDD tests (pytest --collect-only tests/bdd -q)..."
    "$VENV_BIN/pytest" --collect-only tests/bdd -q || true
  fi
else
  echo "!! pytest not found in .venv; ensure it is included in dev-requirements.txt."
fi

# 6) Pre-commit baseline (se config existir)
if [ -f "pre-commit-config.yaml" ]; then
  if command -v "$VENV_BIN/pre-commit" >/dev/null 2>&1; then
    echo "-- Installing pre-commit hooks..."
    "$VENV_BIN/pre-commit" install --config pre-commit-config.yaml || true
    echo "-- Running pre-commit baseline on all files..."
    "$VENV_BIN/pre-commit" run --config pre-commit-config.yaml --all-files || true
  else
    echo "!! pre-commit not found in .venv; ensure it is included in dev-requirements.txt."
  fi
else
  echo "!! pre-commit-config.yaml not found in repo root; did you extract git-dev.zip?"
fi

echo
echo "Done. To start working, activate the virtualenv with:"
echo "  source .venv/bin/activate    # Linux/macOS"
echo "  .venv\\Scripts\\activate     # Windows PowerShell/CMD"
