# ADR 002 — ProviderAdapter registry

## Status

Proposed

## Contexto

O runtime deve suportar múltiplos providers de código (Codex-like, Claude, Gemini), sem duplicar lógica de orquestração nem acoplar `CodeAgent` a detalhes de cada CLI.

## Decisão

- Definir um `ProviderAdapter` protocol para encapsular:
  - construção de comandos de CLI;
  - suporte a streaming e tool calling;
  - parsing de saída.
- Manter um registry interno `ProviderId -> ProviderAdapter` para resolução em tempo de execução.
- Fornecer implementações internas para `codex`, `claude` e `gemini` no MVP.

## Consequências

- Simplifica a escolha de provider em `CodeAgent`.
- Permite adicionar novos providers sem mudar a interface pública.
- Exige disciplina para manter adapters coerentes e bem testados.

