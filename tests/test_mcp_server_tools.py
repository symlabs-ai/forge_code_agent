from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from forge_code_agent.adapters.workspace import FilesystemWorkspaceAdapter
from forge_code_agent.domain.errors import WorkspaceSecurityError
from forge_code_agent.mcp_server import (
    MCPRequestContext,
    list_dir_tool,
    read_file_tool,
    write_file_tool,
)


def test_mcp_tools_read_write_and_list_dir(tmp_path: Path) -> None:
    """
    As tools MCP mínimas devem conseguir ler/escrever arquivos dentro do workspace
    e listar o diretório, respeitando o sandbox.
    """
    workspace = FilesystemWorkspaceAdapter(tmp_path)
    ctx = MCPRequestContext(workspace=workspace)

    # write_file
    write_result = write_file_tool(ctx, {"path": "foo.txt", "content": "hello mcp"})
    written_path = Path(write_result["path"])
    assert written_path.exists()
    assert written_path.read_text(encoding="utf-8") == "hello mcp"

    # read_file
    read_result = read_file_tool(ctx, {"path": "foo.txt"})
    assert read_result["content"] == "hello mcp"
    assert read_result["path"] == "foo.txt"

    # list_dir
    list_result = list_dir_tool(ctx, {"path": "."})
    names = {entry["name"] for entry in list_result["entries"]}
    assert "foo.txt" in names


def test_mcp_tools_enforce_workspace_security(tmp_path: Path) -> None:
    """
    Caminhos com path traversal devem ser bloqueados pelas tools MCP.
    """
    workspace = FilesystemWorkspaceAdapter(tmp_path)
    ctx = MCPRequestContext(workspace=workspace)

    # Tentativa de escrita fora do workspace.
    try:
        write_file_tool(ctx, {"path": "../outside.txt", "content": "x"})
        raised = False
    except WorkspaceSecurityError:
        raised = True

    assert raised is True


def test_mcp_stdio_server_ping(tmp_path: Path) -> None:
    """
    O entrypoint `python -m forge_code_agent.mcp_server` deve inicializar e
    responder a chamadas JSON-RPC, incluindo o atalho "ping".
    """
    repo_root = Path(__file__).resolve().parents[1]

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [env.get("PYTHONPATH", ""), str(repo_root / "src")]
    )

    cmd = [
        sys.executable,
        "-m",
        "forge_code_agent.mcp_server",
        "--workdir",
        str(tmp_path),
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(repo_root),
        env=env,
    )

    try:
        assert proc.stdin is not None
        assert proc.stdout is not None

        request = {"jsonrpc": "2.0", "id": "1", "method": "ping", "params": {}}
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        proc.stdin.close()

        line = proc.stdout.readline().strip()
        assert line, "no response from MCP server"

        response = json.loads(line)
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == "1"
        assert response.get("result", {}).get("status") == "ok"
    finally:
        proc.wait(timeout=5)


def test_mcp_stdio_server_initialize_and_tools(tmp_path: Path) -> None:
    """
    O servidor MCP deve responder a initialize, tools/list e tools/call.
    """
    repo_root = Path(__file__).resolve().parents[1]

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [env.get("PYTHONPATH", ""), str(repo_root / "src")]
    )

    cmd = [
        sys.executable,
        "-m",
        "forge_code_agent.mcp_server",
        "--workdir",
        str(tmp_path),
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(repo_root),
        env=env,
    )

    try:
        assert proc.stdin is not None
        assert proc.stdout is not None

        # Prepara um arquivo para o tools/call read_file.
        target = tmp_path / "demo.txt"
        target.write_text("hello from mcp", encoding="utf-8")

        requests = [
            {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "tools/call",
                "params": {
                    "name": "read_file",
                    "arguments": {"path": "demo.txt"},
                },
            },
        ]

        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        proc.stdin.close()

        responses: dict[str, dict[str, object]] = {}
        for line in proc.stdout:
            stripped = line.strip()
            if not stripped:
                continue
            data = json.loads(stripped)
            resp_id = str(data.get("id"))
            responses[resp_id] = data

        # initialize
        init_resp = responses.get("1")
        assert init_resp is not None
        assert init_resp.get("jsonrpc") == "2.0"
        init_result = init_resp.get("result") or {}
        assert init_result.get("protocolVersion")

        # tools/list
        list_resp = responses.get("2")
        assert list_resp is not None
        tools_result = list_resp.get("result") or {}
        tools = tools_result.get("tools") or []
        tool_names = {t.get("name") for t in tools}
        assert "read_file" in tool_names

        # tools/call read_file
        call_resp = responses.get("3")
        assert call_resp is not None
        call_result = call_resp.get("result") or {}
        content_list = call_result.get("content") or []
        assert isinstance(content_list, list) and content_list
        text_item = content_list[0]
        assert text_item.get("type") == "text"
        assert "hello from mcp" in text_item.get("text", "")
    finally:
        proc.wait(timeout=5)
