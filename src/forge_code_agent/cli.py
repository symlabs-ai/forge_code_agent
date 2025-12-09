from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from forge_code_agent.context.manager import CodeManager
from forge_code_agent.context.summarizer import AgentSummarizer
from forge_code_agent.domain.errors import ForgeCodeAgentError, ProviderExecutionError
from forge_code_agent.domain.events import normalize_stream_line
from forge_code_agent.runtime.agent import CodeAgent


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge-code-agent",
        description="forgeCodeAgent CLI - run and stream code prompts via configured providers",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--provider",
            help="Provider id (e.g. codex, claude, gemini). If omitted, uses FROM env/config.",
        )
        p.add_argument(
            "--workdir",
            type=str,
            default=".",
            help="Working directory for generated files and execution context.",
        )
        p.add_argument(
            "--config",
            type=str,
            help="Path to configuration file (e.g. forge_code_agent.yml) with provider and other settings.",
        )
        p.add_argument(
            "--timeout",
            type=float,
            default=None,
            help="Optional timeout in seconds for provider execution.",
        )
        p.add_argument(
            "--write-to-file",
            type=str,
            help="If provided, write the final content to this file inside the workdir.",
        )
        p.add_argument(
            "--prompt",
            type=str,
            required=True,
            help="Code prompt to be executed by the provider.",
        )

    run_parser = subparsers.add_parser("run", help="Execute a code prompt and print the final result.")
    add_common_options(run_parser)
    run_parser.add_argument(
        "--session-id",
        type=str,
        help=(
            "Optional session identifier to enable context persistence via CodeManager. "
            "When provided, CodeManager is used automatically."
        ),
    )
    run_parser.add_argument(
        "--use-code-manager",
        action="store_true",
        help=(
            "Use the CodeManager to manage sessions/context instead of a one-off CodeAgent. "
            "If --session-id is provided, this flag is implied."
        ),
    )
    run_parser.add_argument(
        "--auto-summarize",
        action="store_true",
        help=(
            "When used with --session-id/--use-code-manager, enable automatic context summarization "
            "based on an internal prompt using the current provider."
        ),
    )

    stream_parser = subparsers.add_parser("stream", help="Execute a code prompt and stream partial results.")
    add_common_options(stream_parser)
    stream_parser.add_argument(
        "--reasoning-only",
        action="store_true",
        help="When set, try to parse JSONL lines and print only reasoning messages (Codex --json mode).",
    )
    stream_parser.add_argument(
        "--reasoning-with-output",
        action="store_true",
        help="Parse JSONL lines and print both reasoning and agent messages with simple prefixes.",
    )
    stream_parser.add_argument(
        "--events-json",
        action="store_true",
        help="Emit canonical AgentEvents as JSON lines (no human formatting).",
    )

    tools_demo_parser = subparsers.add_parser(
        "tools-demo",
        help="Demonstrate an after_run hook by generating a file via a registered Python function.",
    )
    add_common_options(tools_demo_parser)

    return parser


def _create_agent_from_args(args: argparse.Namespace) -> CodeAgent:
    workdir = Path(args.workdir)
    if args.config:
        return CodeAgent.from_config(config_path=Path(args.config), workdir=workdir)

    if args.provider:
        return CodeAgent(provider=args.provider, workdir=workdir)

    # Fallback: from_env, default provider inside runtime.
    return CodeAgent.from_env(workdir=workdir)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(argv)

    agent = _create_agent_from_args(ns)
    prompt: str = ns.prompt
    timeout: float | None = ns.timeout
    write_to_file: str | None = getattr(ns, "write_to_file", None)
    reasoning_only: bool = getattr(ns, "reasoning_only", False)
    reasoning_with_output: bool = getattr(ns, "reasoning_with_output", False)
    events_json: bool = getattr(ns, "events_json", False)

    try:
        if ns.command == "run":
            extra: dict[str, Any] = {}
            if write_to_file:
                extra["write_to_file"] = write_to_file

            # Integração opcional com CodeManager para sessões de contexto.
            use_code_manager: bool = getattr(ns, "use_code_manager", False)
            session_id: str | None = getattr(ns, "session_id", None)
            auto_summarize: bool = getattr(ns, "auto_summarize", False)

            # Sessões sempre usam CodeManager; se houver session-id, implicamos use_code_manager.
            if session_id and not use_code_manager:
                use_code_manager = True

            if use_code_manager:
                workdir_path = Path(ns.workdir)
                if auto_summarize:
                    # Criamos um CodeManager com uma fábrica de Summarizer baseada no
                    # CodeAgent atual. O summarizer usa o próprio provider para gerar
                    # resumos quando os limites de contexto forem ultrapassados.
                    def _summarizer_factory(agent_for_sum: CodeAgent, _session) -> AgentSummarizer:
                        return AgentSummarizer(agent=agent_for_sum)

                    manager = CodeManager(summarizer_factory=_summarizer_factory)
                else:
                    manager = CodeManager()
                result = manager.run(
                    prompt,
                    provider=ns.provider,
                    session_id=session_id,
                    workdir=workdir_path,
                    timeout=timeout,
                    **extra,
                )
            else:
                result = agent.run(prompt, timeout=timeout, **extra)

            # Para o MVP, imprimimos apenas o conteúdo bruto gerado, precedido de metadata mínima.
            print(f"[forge-code-agent] provider={result.provider} status={result.status}")
            if result.content:
                print(result.content)
            return 0 if result.status == "success" else 1

        if ns.command == "stream":
            # Para stream, mantemos CodeAgent direto por enquanto; CodeManager/Context
            # podem ser adicionados em sprints futuras se necessário.
            events = agent.stream(prompt, timeout=timeout)
            if not events_json:
                print(f"[forge-code-agent] streaming provider={agent.provider}")
            full: list[str] = []

            for ev in events:
                chunk = ev.get("content", "")
                if not chunk:
                    continue

                if events_json:
                    # Modo orientado a máquina: emitimos AgentEvents como JSON lines.
                    import json as _json

                    normalized_events = normalize_stream_line(agent.provider, chunk)
                    for ev_norm in normalized_events:
                        sys.stdout.write(_json.dumps(ev_norm) + "\n")
                    sys.stdout.flush()
                    continue

                if reasoning_only or reasoning_with_output:
                    normalized_events = normalize_stream_line(agent.provider, chunk)
                    if not normalized_events:
                        continue

                    for ev_norm in normalized_events:
                        kind = ev_norm.get("kind")
                        text = ev_norm.get("text") or ""
                        raw = ev_norm.get("raw")

                        if reasoning_only:
                            if kind == "reasoning" and text:
                                sys.stdout.write(text + "\n")
                                sys.stdout.flush()
                            # Em modo reasoning-only, ignoramos qualquer outra coisa.
                            continue

                        # reasoning_with_output
                        if kind == "reasoning" and text:
                            sys.stdout.write(f"[REASONING] {text}\n")
                            sys.stdout.flush()
                        elif kind == "message" and text:
                            sys.stdout.write(f"[OUTPUT] {text}\n")
                            sys.stdout.flush()
                        elif kind == "log" and text:
                            # Eventos de log (system, tool_use, comandos, etc.) aparecem explicitamente.
                            sys.stdout.write(f"[LOG] {text}\n")
                            sys.stdout.flush()
                        elif kind == "raw":
                            # Para compatibilidade com os testes, linhas não JSON ou
                            # payloads sem shape esperado aparecem brutas.
                            if isinstance(raw, str):
                                sys.stdout.write(raw)
                                if not raw.endswith("\n"):
                                    sys.stdout.write("\n")
                            else:
                                # Se raw vier como dict, voltamos a serializá-lo.
                                import json as _json

                                sys.stdout.write(_json.dumps(raw) + "\n")
                            sys.stdout.flush()
                        else:
                            # Outros tipos permanecem silenciosos por enquanto.
                            continue
                else:
                    full.append(chunk)
                    sys.stdout.write(chunk)
                    sys.stdout.flush()

            print()  # newline after stream
            # Opcional: poderia inspecionar eventos para status, por ora assumimos sucesso.
            return 0

        if ns.command == "tools-demo":
            filename = write_to_file or "tool_generated.py"
            tool_content = prompt

            # Demo de hook pós-execução: após a execução do provider,
            # gravamos um arquivo simples no workspace usando o conteúdo
            # passado como prompt.
            def after_run_generate_file(request, result, _agent: CodeAgent = agent) -> None:
                _agent.write_file(filename, tool_content)

            agent.add_after_run_handler(after_run_generate_file)

            result = agent.run("generate file via after_run hook", timeout=timeout)

            print(
                f"[forge-code-agent] tools-demo provider={result.provider} "
                f"status={result.status} file={filename}"
            )

            return 0 if result.status == "success" else 1

        parser.error(f"Unknown command: {ns.command}")
        return 1
    except ProviderExecutionError as exc:
        # Exibe detalhes da falha da CLI do provider para facilitar diagnóstico.
        msg = f"[forge-code-agent] provider execution error (code={exc.returncode})"
        print(msg, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1
    except ForgeCodeAgentError as exc:
        print(f"[forge-code-agent] runtime error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
