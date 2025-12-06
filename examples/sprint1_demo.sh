#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo " forgeCodeAgent — Sprint 1 Demo"
echo "==========================================="
echo
echo "Este script demonstra, de forma simples:"
echo " 1) Execução de prompt com tool calling integrado em CodeAgent.run()."
echo " 2) Streaming de resposta via CLI (adapter Codex-like usando subprocess.Popen)."
echo
echo "Ele cria um workspace de exemplo em 'project/demo_workdir',"
echo "executa o CodeAgent e imprime os resultados na tela."
echo

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-}:${REPO_ROOT}/src"

WORKDIR="${REPO_ROOT}/project/demo_workdir"
mkdir -p "${WORKDIR}"

echo "[1/2] Demo: run() com tool calling e escrita de arquivo"
python3 - << 'PY'
from pathlib import Path

from forge_code_agent.runtime.agent import CodeAgent

workdir = Path("project/demo_workdir")

agent = CodeAgent(provider="codex", workdir=workdir)


def generate_file(filename: str, content: str) -> dict:
    return {"filename": filename, "content": content}


agent.register_tool("generate_file", generate_file)

result = agent.run(
    "Demo prompt: gerar arquivo demo.py com print('hello from forgeCodeAgent')",
    tool_calls=[
        {
            "name": "generate_file",
            "args": {"filename": "demo.py", "content": "print('hello from forgeCodeAgent')"},
        }
    ],
    write_to_file="demo.py",
)

print("Status:", result.status)
print("Provider:", result.provider)
print("Tool calls:", result.tool_calls)

files = sorted(p.name for p in workdir.iterdir())
print("Arquivos no workspace:", files)
if (workdir / "demo.py").exists():
    print("\nConteúdo de demo.py:")
    print((workdir / "demo.py").read_text(encoding="utf-8"))
PY

echo
echo "[2/2] Demo: stream() via CLI (Codex-like)"
python3 - << 'PY'
from pathlib import Path

from forge_code_agent.runtime.agent import CodeAgent

workdir = Path("project/demo_workdir")
agent = CodeAgent(provider="codex", workdir=workdir)

events = list(agent.stream("Demo streaming prompt: mostrar eventos incrementais"))

print(f"Número de eventos recebidos: {len(events)}")
for idx, ev in enumerate(events, start=1):
    print(f"Evento {idx}: {ev}")

reconstructed = "".join(e["content"] for e in events)
print("\nResposta reconstruída contém o prompt?", "prompt" in reconstructed)
PY

echo
echo "Demo da Sprint 1 concluída."
