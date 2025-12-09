from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from forge_code_agent.adapters.workspace import FilesystemWorkspaceAdapter
from forge_code_agent.mcp_server.protocol import (
    MCPFramingState,
    read_next_json_line,
    write_json_response,
)


@dataclass(slots=True)
class MCPServerConfig:
    """
    Configuração mínima para o servidor MCP local.

    Fase 1: apenas modo stdio, um workspace e um loop simples JSON‑RPC,
    com opção de modo read-only para ferramentas que escrevem em disco.
    """

    workdir: Path
    read_only: bool = False


@dataclass(slots=True)
class MCPRequestContext:
    """
    Contexto de request dentro do servidor MCP.

    Inclui o adapter de workspace já protegido contra path traversal.
    """

    workspace: FilesystemWorkspaceAdapter


JsonLike = dict[str, Any]
ToolFunc = Callable[[MCPRequestContext, JsonLike], JsonLike]


def _make_workspace(workdir: Path) -> FilesystemWorkspaceAdapter:
    return FilesystemWorkspaceAdapter(workdir)


def read_file_tool(ctx: MCPRequestContext, params: JsonLike) -> JsonLike:
    """
    Tool mínima: lê um arquivo dentro do workspace.

    Espera:
        {"path": "relative/path/to/file.py"}
    """
    from pathlib import Path as _Path

    raw_path = params.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError("read_file.path must be a non-empty string")

    target = (ctx.workspace.workdir / raw_path).resolve()
    ctx.workspace.ensure_within_workspace(target)
    try:
        content = target.read_text(encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - comportamento de erro simples
        raise FileNotFoundError(f"File not found inside workspace: {raw_path}") from exc

    return {
        "path": str(_Path(raw_path)),
        "content": content,
    }


def write_file_tool(ctx: MCPRequestContext, params: JsonLike) -> JsonLike:
    """
    Tool mínima: escreve um arquivo dentro do workspace usando o adapter.

    Espera:
        {"path": "relative/path/to/file.py", "content": "..."}
    """
    raw_path = params.get("path")
    content = params.get("content")

    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError("write_file.path must be a non-empty string")
    if not isinstance(content, str):
        raise ValueError("write_file.content must be a string")

    target = ctx.workspace.write_file(raw_path, content)
    return {
        "path": str(target),
        "relative_path": raw_path,
    }


def list_dir_tool(ctx: MCPRequestContext, params: JsonLike) -> JsonLike:
    """
    Tool mínima: lista arquivos/pastas dentro do workspace.

    Espera:
        {"path": "."}   # opcional, default "."
    """
    from pathlib import Path as _Path

    raw_path = params.get("path", ".")
    if not isinstance(raw_path, str) or not raw_path:
        raw_path = "."

    base = (ctx.workspace.workdir / raw_path).resolve()
    ctx.workspace.ensure_within_workspace(base)

    if not base.exists():
        raise FileNotFoundError(f"Directory does not exist inside workspace: {raw_path}")
    if not base.is_dir():
        raise NotADirectoryError(f"Path is not a directory inside workspace: {raw_path}")

    entries: list[dict[str, Any]] = []
    for entry in base.iterdir():
        entries.append(
            {
                "name": entry.name,
                "is_dir": entry.is_dir(),
            }
        )

    return {
        "path": str(_Path(raw_path)),
        "entries": entries,
    }


def get_builtin_tools(read_only: bool = False) -> dict[str, ToolFunc]:
    """
    Registro de tools MCP disponíveis na Fase 1.

    Mantido simples para permitir evolução futura sem quebrar contratos.
    """

    tools: dict[str, ToolFunc] = {
        "read_file": read_file_tool,
        "list_dir": list_dir_tool,
    }
    if not read_only:
        tools["write_file"] = write_file_tool
    return tools


def _mcp_tool_descriptors(read_only: bool = False) -> list[dict[str, Any]]:
    """
    Descritores das tools no formato aproximado do protocolo MCP.

    Mantemos os schemas simples para esta fase; o objetivo é expor as
    ferramentas de filesystem de forma introspectável para o cliente MCP.
    """
    return [
        {
            "name": "read_file",
            "description": "Read a UTF-8 text file from the workspace.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
        # write_file só é exposto quando o servidor não está em modo read-only.
        *(
            []
            if read_only
            else [
                {
                    "name": "write_file",
                    "description": "Write a UTF-8 text file into the workspace.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "relative_path": {"type": "string"},
                        },
                        "required": ["path", "relative_path"],
                    },
                }
            ]
        ),
        {
            "name": "list_dir",
            "description": "List files and directories inside the workspace.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "entries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "is_dir": {"type": "boolean"},
                            },
                            "required": ["name", "is_dir"],
                        },
                    },
                },
                "required": ["path", "entries"],
            },
        },
    ]


def run_stdio_server(config: MCPServerConfig) -> None:
    """
    Loop simples estilo JSON‑RPC sobre stdin/stdout.

    Suporta dois modos:

    - Protocolo MCP aproximado (JSON-RPC 2.0):
        * initialize
        * tools/list
        * tools/call
    - Atalho interno de debug:
        * {"id": "...", "method": "ping"} → {"result": {"status": "ok"}}

    Esse servidor é suficiente para experimentos locais com Codex/Claude/Gemini
    enquanto o suporte completo ao MCP amadurece.
    """
    import json
    import sys

    workspace = _make_workspace(config.workdir)
    ctx = MCPRequestContext(workspace=workspace)
    tools = get_builtin_tools(read_only=config.read_only)

    stdin_buffer = sys.stdin.buffer
    framing_state = MCPFramingState(mcp_mode=False, log_path=config.workdir / ".mcp_debug.log")

    while True:
        raw_line = read_next_json_line(stdin_buffer, framing_state)
        if raw_line is None:
            # EOF ou framing inválido → encerramos o loop.
            break
        if not raw_line:
            # Linha em branco / ignorada; seguimos para próxima.
            continue

        try:
            request = json.loads(raw_line)
        except Exception as exc:  # pragma: no cover - erro de parsing simples
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "message": f"Invalid JSON: {exc}",
                },
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}
        jsonrpc = request.get("jsonrpc") or "2.0"

        # Atalho de debug fora do protocolo MCP.
        if method == "ping":
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {"status": "ok"},
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        # Notificações MCP que não exigem resposta.
        if method == "notifications/initialized":
            # Conforme JSON-RPC/MCP, notificações não esperam resposta.
            continue

        # Métodos principais do protocolo MCP (forma aproximada).
        if method == "initialize":
            result: JsonLike = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": False,
                    },
                },
                "serverInfo": {
                    "name": "forge-code-agent-mcp",
                    "version": "0.1.0",
                },
            }
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": result,
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        if method in {"tools/list", "tools.list"}:
            result = {
                "tools": _mcp_tool_descriptors(read_only=config.read_only),
            }
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": result,
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        if method in {"tools/call", "tools.call"}:
            name = params.get("name")
            arguments = params.get("arguments") or {}
            tool = tools.get(str(name))
            if tool is None:
                response = {
                    "jsonrpc": jsonrpc,
                    "id": req_id,
                    "error": {
                        "message": f"Unknown tool: {name}",
                    },
                }
                write_json_response(response, framing_state, sys.stdout)
                continue

            try:
                tool_result = tool(ctx, arguments)
            except Exception as exc:  # pragma: no cover - erros de tool são retornados de forma opaca
                response = {
                    "jsonrpc": jsonrpc,
                    "id": req_id,
                    "error": {
                        "message": str(exc),
                    },
                }
                write_json_response(response, framing_state, sys.stdout)
                continue

            # Resposta em formato MCP: conteúdo textual simples.
            # Para uso mais avançado, poderíamos evoluir para estruturas
            # diferentes (text/json), mas por ora mantemos uma string única.
            text_repr = json.dumps(tool_result, ensure_ascii=False)
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": text_repr,
                    }
                ]
            }
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": result,
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        # Fallback: tentar despachar para tools internas usando o nome do método.
        tool = tools.get(str(method))
        if tool is None:
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "error": {
                    "message": f"Unknown method: {method}",
                },
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        try:
            result = tool(ctx, params)
        except Exception as exc:  # pragma: no cover - erros de tool são retornados de forma opaca
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "error": {
                    "message": str(exc),
                },
            }
            write_json_response(response, framing_state, sys.stdout)
            continue

        response = {
            "jsonrpc": jsonrpc,
            "id": req_id,
            "result": result,
        }
        write_json_response(response, framing_state, sys.stdout)
