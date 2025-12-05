# ADR 001 — Clean/Hex runtime baseado no ForgeBase

## Status

Proposed

## Contexto

O forgeCodeAgent precisa encapsular CLIs de engines de código (Codex-like, Claude, Gemini) sem acoplamento direto a detalhes de subprocesso, filesystem ou observabilidade, mantendo alinhamento com o ForgeBase (Clean/Hex, CLI-first) e reaproveitando o núcleo arquitetural do `forgebase/` (domain/application/adapters/infrastructure).

## Decisão

- Modelar o domínio como camada pura **sobre as bases do ForgeBase**, usando:
  - `EntityBase` / `value_object_base` para entidades/VOs específicas (ex.: `ProviderId`, `ExecutionRequest`, `ExecutionResult`, `ToolDefinition`, `ToolCall`);
  - regras de negócio para sucesso/falha, resultados parciais e segurança de workspace, implementadas em `forge_code_agent.domain` mas alinhadas a `forgebase.domain.exceptions`.
- Tratar I/O (CLI, filesystem, logging, métricas) por meio de adapters específicos:
  - `CliProviderAdapter`, `FilesystemWorkspaceAdapter`, `LoggerPort`, `MetricsPort`,
  - implementados como `AdapterBase`/Ports no sentido do `forgebase.application`/`forgebase.adapters`.
- Garantir que o domínio (em termos de invariantes e entidades) não dependa diretamente de `subprocess`, `os`, `pathlib` ou detalhes de infraestrutura.

## Consequências

- Facilita testes do domínio sem I/O real, reaproveitando padrões de teste cognitivo do ForgeBase.
- Permite trocar implementações de CLI/FS/observabilidade sem quebrar o domínio, integrando com a infraestrutura do ForgeBase via ports/adapters.
- Introduz complexidade adicional na separação de camadas, mas mantém o runtime coerente com a arquitetura modular do ForgeBase.
