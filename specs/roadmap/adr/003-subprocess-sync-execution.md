# ADR 003 — Execução síncrona via subprocess stdlib

## Status

Proposed

## Contexto

O forgeCodeAgent precisa executar CLIs de providers em modos `run` e `stream`, mas o MVP deve permanecer simples, portável e fácil de testar, sem introduzir complexidade assíncrona prematura.

## Decisão

- Utilizar a stdlib `subprocess` para:
  - `run()`: `subprocess.run(..., timeout=...)`.
  - `stream()`: `subprocess.Popen(...)` com leitura incremental de stdout.
- Não introduzir asyncio no MVP; streaming será implementado com loops síncronos.

## Consequências

- Reduz complexidade inicial e dependências externas.
- Pode limitar a concorrência de execuções simultâneas, mas é aceitável no MVP.
- Deixa espaço para um adapter assíncrono futuro sem quebrar contratos de domínio.
