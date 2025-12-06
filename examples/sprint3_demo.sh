#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 3 Demo (YAML config)"
echo "==========================================="
echo
echo "Este script demonstra:"
echo " 1) Criação de um CodeAgent a partir de um arquivo de configuração YAML simples."
echo " 2) Troca de provider (codex -> claude) alterando apenas o arquivo,"
echo "    sem mudar o código da automação."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-}:${REPO_ROOT}/src"

WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

CONFIG_FILE="${WORKDIR}/forge_code_agent.yml"

echo "[1/2] Configurando YAML com provider: codex"
cat > "${CONFIG_FILE}" << 'YAML'
provider: codex
YAML

python3 - << 'PY'
from pathlib import Path

from forge_code_agent.runtime.agent import CodeAgent

workdir = Path("project/demo_workdir")
config_path = workdir / "forge_code_agent.yml"

print("[Demo] Lendo configuração de:", config_path)
print(config_path.read_text(encoding="utf-8"))

def run_flow(prompt: str):
    agent = CodeAgent.from_config(config_path=config_path, workdir=workdir)
    return agent.run(prompt)

result = run_flow("print('hello from YAML-configured provider')")
print("Status:", result.status)
print("Provider usado:", result.provider)
PY

echo
echo "[2/2] Alterando YAML para provider: claude (sem mudar o código)"
cat > "${CONFIG_FILE}" << 'YAML'
provider: claude
YAML

python3 - << 'PY'
from pathlib import Path

from forge_code_agent.runtime.agent import CodeAgent

workdir = Path("project/demo_workdir")
config_path = workdir / "forge_code_agent.yml"

print("[Demo] Nova configuração de:", config_path)
print(config_path.read_text(encoding="utf-8"))

def run_flow(prompt: str):
    agent = CodeAgent.from_config(config_path=config_path, workdir=workdir)
    return agent.run(prompt)

result = run_flow("print('hello from YAML-configured provider after change')")
print("Status:", result.status)
print("Provider usado:", result.provider)
PY

echo
echo "Demo da Sprint 3 concluída (configuração via YAML)."
