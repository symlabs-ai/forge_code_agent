from __future__ import annotations

import argparse
from pathlib import Path

from forge_code_agent.mcp_server import MCPServerConfig, run_stdio_server


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge-code-agent-mcp-server",
        description=(
            "Servidor MCP local mínimo para o forgeCodeAgent (Fase 1). "
            "Implementa um loop simples JSON-RPC sobre stdin/stdout."
        ),
    )
    parser.add_argument(
        "--workdir",
        type=str,
        default=".",
        help="Diretório de trabalho (workspace raiz) para as tools MCP.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(argv)

    workdir = Path(ns.workdir).resolve()
    config = MCPServerConfig(workdir=workdir)
    run_stdio_server(config)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
