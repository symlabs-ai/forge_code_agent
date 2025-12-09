from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

JsonLike = dict[str, Any]


@dataclass(slots=True)
class MCPFramingState:
    """
    Representa o estado de framing do protocolo MCP.

    - mcp_mode=True  → uso de headers Content-Length + corpo JSON.
    - mcp_mode=False → modo JSON newline simples (usado em testes internos).
    """

    mcp_mode: bool = False
    log_path: Path | None = None


def _log_raw(line: str, state: MCPFramingState, prefix: str) -> None:
    """
    Loga uma linha bruta no arquivo de debug, se configurado.
    Erros de escrita são ignorados (somente debug).
    """
    if not state.log_path:
        return
    try:
        with state.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{prefix}: {line}\n")
    except Exception:
        # Logging MCP é best-effort e nunca deve quebrar o servidor.
        pass


def read_next_json_line(stdin_buffer: BinaryIO, state: MCPFramingState) -> str | None:
    """
    Lê o próximo payload JSON (como string) de stdin_buffer, suportando:

    - Modo newline JSON simples (linha começando em '{' ou '[');
    - Modo MCP com headers `Content-Length: N` seguidos de corpo.

    Retorna:
        - string JSON (sem newline) em caso de sucesso;
        - None quando o stream se encerra ou framing é inválido.
    """
    first_line = stdin_buffer.readline()
    if not first_line:
        return None

    if not first_line.strip():
        # Linha em branco isolada; ignoramos e deixamos o caller decidir repetir.
        return ""

    stripped_first = first_line.lstrip()
    # Heurística: linha começando com "{" ou "[" → modo newline JSON simples.
    if stripped_first.startswith(b"{") or stripped_first.startswith(b"["):
        try:
            line = first_line.decode("utf-8").strip()
        except UnicodeDecodeError:
            return ""
        _log_raw(line, state, "RAW-JSON")
        return line

    # Caso contrário, assumimos framing estilo MCP:
    # headers (incluindo Content-Length) + linha em branco + corpo JSON.
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
        # Framing inválido: devolvemos None para permitir encerramento limpo.
        return None

    state.mcp_mode = True
    body = stdin_buffer.read(content_length)
    if not body:
        return None

    try:
        line = body.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None

    _log_raw(line, state, "RAW-MCP")
    return line


def write_json_response(payload: JsonLike, state: MCPFramingState, stdout) -> None:
    """
    Escreve um payload JSON em stdout respeitando o modo atual (MCP ou newline).

    - Em modo MCP → `Content-Length: N` + corpo JSON.
    - Em modo simples → JSON + newline.
    """
    import json

    encoded = json.dumps(payload)
    if state.mcp_mode:
        data = encoded.encode("utf-8")
        stdout.write(f"Content-Length: {len(data)}\r\n\r\n")
        stdout.write(encoded)
    else:
        stdout.write(encoded + "\n")
    stdout.flush()
