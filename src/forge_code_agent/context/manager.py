from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from forge_code_agent.context.session_manager import ContextSessionManager
from forge_code_agent.context.summarizer import Summarizer
from forge_code_agent.mcp_server.integration import ensure_mcp_server
from forge_code_agent.runtime.agent import CodeAgent


@dataclass
class CodeManager:
    """
    Orquestrador de CodeAgents e contexto de sessão.

    Responsável por:
    - gerenciar instâncias de CodeAgent por provider/workdir;
    - gerenciar ContextSessionManager por session_id;
    - expor uma API de alto nível (run/stream/switch_provider).
    """
    logs_dir: Path = field(default_factory=lambda: Path("logs") / "codeagent")
    summarizer_factory: Callable[[CodeAgent, ContextSessionManager], Summarizer] | None = field(
        default=None, repr=False
    )
    _sessions: dict[str, ContextSessionManager] = field(init=False, default_factory=dict)
    _agents: dict[tuple[str, str], CodeAgent] = field(init=False, default_factory=dict)

    def _resolve_workdir(self, workdir: Path | str | None) -> Path:
        if workdir is None:
            return Path.cwd()
        return Path(workdir)

    def _get_agent(self, provider: str, workdir: Path) -> CodeAgent:
        key = (provider, str(workdir.resolve()))
        if key in self._agents:
            return self._agents[key]
        agent = CodeAgent(provider=provider, workdir=workdir)
        self._agents[key] = agent
        return agent

    def _get_session(self, session_id: str) -> ContextSessionManager | None:
        return self._sessions.get(session_id)

    def _create_session(self, session_id: str, workdir: Path | None, provider: str | None) -> ContextSessionManager:
        mgr = ContextSessionManager(session_id=session_id, logs_dir=self.logs_dir)
        mgr.workdir = workdir
        mgr.current_provider = provider
        self._sessions[session_id] = mgr
        return mgr

    def _get_or_create_session(
        self,
        session_id: str,
        workdir: Path | None,
        provider: str | None,
    ) -> ContextSessionManager:
        session = self._get_session(session_id)
        if session is None:
            return self._create_session(session_id, workdir, provider)

        # Atualiza provider/workdir se ainda não definidos na sessão.
        if session.workdir is None and workdir is not None:
            session.workdir = workdir
        if session.current_provider is None and provider is not None:
            session.current_provider = provider
        return session

    def run(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        session_id: str | None = None,
        workdir: Path | str | None = None,
        timeout: float | None = None,
        **options: Any,
    ):
        """
        Executar um prompt de código em uma sessão de contexto.

        - resolve session_id/workdir/provider;
        - chama CodeAgent.run;
        - registra a interação no ContextSessionManager;
        - persiste um snapshot da sessão em logs_dir.
        """
        # session_id simples: se não fornecido, usamos um carimbo baseado em cwd.
        if session_id is None:
            session_id = "session-default"

        resolved_workdir = self._resolve_workdir(workdir)

        # Provider padrão: primeiro o explicitamente informado, depois o da sessão, por fim "codex".
        session = self._get_session(session_id)
        effective_provider = provider or (session.current_provider if session else None) or "codex"

        agent = self._get_agent(effective_provider, resolved_workdir)
        session = self._get_or_create_session(session_id, resolved_workdir, effective_provider)

        result = agent.run(prompt, timeout=timeout, **options)

        session.record_interaction(prompt, result)
        # Metadados MCP agora são responsabilidade do CodeManager: garantimos
        # um handle estável associado ao workdir, sem acoplar a lógica ao
        # CodeAgent em si.
        try:
            mcp_handle = ensure_mcp_server(resolved_workdir)
            result.metadata.setdefault(
                "mcp",
                {
                    "workdir": str(mcp_handle.workdir),
                    "endpoint": mcp_handle.endpoint,
                    "started": mcp_handle.started,
                },
            )
        except Exception:
            # Integração MCP não deve quebrar a execução principal.
            pass

        # Aplicar resumo, se um Summarizer tiver sido configurado para o manager.
        summarizer: Summarizer | None = None
        if self.summarizer_factory is not None:
            summarizer = self.summarizer_factory(agent, session)
        session.summarize_if_needed(summarizer)

        # Snapshot simples a cada run; otimizações (como rotação) podem vir depois.
        session.save()

        return result

    def stream(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        session_id: str | None = None,
        workdir: Path | str | None = None,
        timeout: float | None = None,
        **options: Any,
    ):
        """
        Executar um prompt em modo streaming utilizando CodeAgent.stream.

        Nesta fase, o streaming via CodeManager não persiste contexto nem
        aplica resumo automaticamente; o foco é fornecer uma API consistente
        de alto nível para automações. A integração completa com
        ContextSessionManager poderá ser adicionada em sprints futuras.
        """
        if session_id is None:
            session_id = "session-default"

        resolved_workdir = self._resolve_workdir(workdir)
        session = self._get_session(session_id)
        effective_provider = provider or (session.current_provider if session else None) or "codex"

        agent = self._get_agent(effective_provider, resolved_workdir)
        self._get_or_create_session(session_id, resolved_workdir, effective_provider)

        yield from agent.stream(prompt, timeout=timeout, **options)

    def switch_provider(self, session_id: str, new_provider: str) -> None:
        """
        Trocar o provider associado a uma sessão.

        A próxima chamada de run/stream usará o novo provider, mantendo o contexto.
        """
        session = self._get_session(session_id)
        if session is None:
            # Sessão ainda não existe; criamos uma casca que será preenchida no próximo run().
            self._create_session(session_id, workdir=None, provider=new_provider)
        else:
            session.current_provider = new_provider

    def get_session_context(self, session_id: str) -> list[dict[str, Any]]:
        """
        Obter o contexto de uma sessão como lista de eventos.
        """
        session = self._get_session(session_id)
        if session is None:
            return []
        return session.get_context()
