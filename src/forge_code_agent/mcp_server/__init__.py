from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from forge_code_agent.adapters.workspace import FilesystemWorkspaceAdapter


@dataclass(slots=True)
class MCPServerConfig:
    """
    Configuração mínima para o servidor MCP local.

    Fase 1: apenas modo stdio, um workspace e um loop simples JSON‑RPC.
    """

    workdir: Path


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


def get_builtin_tools() -> dict[str, ToolFunc]:
    """
    Registro de tools MCP disponíveis na Fase 1.

    Mantido simples para permitir evolução futura sem quebrar contratos.
    """

    return {
        "read_file": read_file_tool,
        "write_file": write_file_tool,
        "list_dir": list_dir_tool,
    }


def _mcp_tool_descriptors() -> list[dict[str, Any]]:
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
        },
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
    tools = get_builtin_tools()

    # Detecta dinamicamente se estamos falando no modo MCP (Content-Length)
    # ou em modo newline JSON simples (usado pelos testes internos).
    mcp_mode = False

    def send_response(payload: JsonLike) -> None:
        encoded = json.dumps(payload)
        if mcp_mode:
            data = encoded.encode("utf-8")
            sys.stdout.write(f"Content-Length: {len(data)}\r\n\r\n")
            sys.stdout.write(encoded)
        else:
            sys.stdout.write(encoded + "\n")
        sys.stdout.flush()

    stdin_buffer = sys.stdin.buffer
    log_path = config.workdir / ".mcp_debug.log"

    while True:
        first_line = stdin_buffer.readline()
        if not first_line:
            break

        if not first_line.strip():
            # Linha em branco isolada; ignoramos e seguimos.
            continue

        # Heurística: se a linha começar com "{" ou "[", tratamos como JSON puro
        # (modo newline usado nos testes internos).
        stripped_first = first_line.lstrip()
        if stripped_first.startswith(b"{") or stripped_first.startswith(b"["):
            try:
                line = first_line.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
            # Log request bruto para debug sem interferir na saída MCP.
            try:
                with log_path.open("a", encoding="utf-8") as log_file:
                    log_file.write(f"RAW-JSON: {line}\n")
            except Exception:
                pass
        else:
            # Caso contrário, assumimos framing estilo MCP:
            # um bloco de headers (incluindo Content-Length) seguido de uma
            # linha em branco e do corpo JSON.
            headers: list[bytes] = [first_line.rstrip(b"\r\n")]
            while True:
                header = stdin_buffer.readline()
                if not header:
                    break
                if header in (b"\r\n", b"\n", b""):
                    break
                headers.append(header.rstrip(b"\r\n"))

            content_length: int | None = None
            for h in headers:
                lower = h.lower()
                if lower.startswith(b"content-length:"):
                    try:
                        _, value = lower.split(b":", 1)
                        content_length = int(value.strip())
                    except Exception:
                        content_length = None
                    break

            if content_length is None or content_length < 0:
                # Framing inválido; encerramos.
                break

            mcp_mode = True
            body = stdin_buffer.read(content_length)
            if not body:
                break
            try:
                line = body.decode("utf-8").strip()
            except UnicodeDecodeError:
                break

            # Log request MCP bruto.
            try:
                with log_path.open("a", encoding="utf-8") as log_file:
                    log_file.write(f"RAW-MCP: {line}\n")
            except Exception:
                pass

        if not line:
            continue

        try:
            request = json.loads(line)
        except Exception as exc:  # pragma: no cover - erro de parsing simples
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "message": f"Invalid JSON: {exc}",
                },
            }
            send_response(response)
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
            send_response(response)
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
            send_response(response)
            continue

        if method in {"tools/list", "tools.list"}:
            result = {
                "tools": _mcp_tool_descriptors(),
            }
            response = {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": result,
            }
            send_response(response)
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
                send_response(response)
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
                send_response(response)
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
            send_response(response)
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
            send_response(response)
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
            send_response(response)
            continue

        response = {
            "jsonrpc": jsonrpc,
            "id": req_id,
            "result": result,
        }
        send_response(response)
