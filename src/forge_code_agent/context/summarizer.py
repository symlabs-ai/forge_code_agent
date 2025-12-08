from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from forge_code_agent.runtime.agent import CodeAgent


class Summarizer(Protocol):
    """
    Estratégia de resumo para contexto de sessões.

    Recebe uma lista de mensagens/eventos normalizados e devolve um texto
    de resumo. Implementações podem usar LLMs, heurísticas simples, etc.
    """

    def summarize(self, messages: list[dict[str, Any]]) -> str:  # pragma: no cover - protocolo
        ...


@dataclass
class AgentSummarizer:
    """
    Summarizer padrão baseado em um CodeAgent.

    Usa o provider/ambiente do próprio agente para gerar um resumo textual
    a partir de uma lista de mensagens/eventos.

    Observação importante:
    - Este summarizer chama o provider real; por isso, não é utilizado nos
      testes unitários. Os testes exercitam apenas a integração genérica de
      `Summarizer` com o `ContextSessionManager`.
    """

    agent: CodeAgent

    def summarize(self, messages: list[dict[str, Any]]) -> str:
        # Construímos um prompt simples que pede resumo objetivo do histórico.
        # Mantemos em alto nível para permitir evolução futura sem quebrar
        # chamadas existentes.
        from textwrap import indent

        lines: list[str] = []
        for msg in messages:
            role = msg.get("role", "assistant")
            text = msg.get("text", "")
            lines.append(f"{role}: {text}")

        joined = "\n".join(lines)
        prompt = (
            "Resuma o contexto a seguir, focando em decisões, TODOs e "
            "informações que precisam ser carregadas para as próximas "
            "interações. Seja objetivo e estruturado.\n\n"
            "=== CONTEXTO ===\n"
            f"{indent(joined, '  ')}\n"
            "=== FIM DO CONTEXTO ===\n\n"
            "Resumo:"
        )

        result = self.agent.run(prompt)
        return result.content or ""
