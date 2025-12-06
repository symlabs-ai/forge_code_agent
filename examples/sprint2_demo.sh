#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 2 Demo"
echo "==========================================="
echo
echo "Este script demonstra, de forma simples:"
echo " 1) Seleção de provider via configuração de ambiente (FORGE_CODE_AGENT_PROVIDER)."
echo " 2) Execução do mesmo código Python usando Codex, Claude e Gemini"
echo "    sem alterar o script — apenas trocando a configuração."
echo
echo "Ele cria/usa um workspace de exemplo em 'project/demo_workdir' e,"
echo "para cada provider, executa o CodeAgent via CodeAgent.from_env(),"
echo "imprimindo o provider escolhido e o trecho principal da resposta."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-}:${REPO_ROOT}/src"

WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

run_demo_for_provider() {
  local provider="$1"
  echo
  echo "-------------------------------------------"
  echo " Demo com provider: ${provider}"
  echo "-------------------------------------------"
  echo
  FORGE_CODE_AGENT_PROVIDER="${provider}" python3 - << 'PY'
from pathlib import Path
import os

from forge_code_agent.runtime.agent import CodeAgent

workdir = Path("project/demo_workdir")

provider = os.getenv("FORGE_CODE_AGENT_PROVIDER", "codex")
print(f"[Demo] FORGE_CODE_AGENT_PROVIDER={provider}")

agent = CodeAgent.from_env(workdir=workdir)
result = agent.run(f"Demo prompt: gerar código de exemplo para provider '{provider}'")

print("Status:", result.status)
print("Provider (ExecutionResult):", result.provider)
print("Primeiras linhas da resposta:")
content = (result.content or "").splitlines()
for line in content[:5]:
    print("  ", line)
PY
}

run_demo_for_provider "codex"
run_demo_for_provider "claude"
run_demo_for_provider "gemini"

echo
echo "Demo da Sprint 2 concluída (multi-provider via configuração)."
