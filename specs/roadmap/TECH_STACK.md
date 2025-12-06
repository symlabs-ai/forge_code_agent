# TECH_STACK — forgeCodeAgent

> Versão: 0.1
> Responsável: mark_arc
> Fonte: `specs/roadmap/ARCHITECTURAL_DECISIONS_APPROVED.md`

---

## 1. Linguagem e Runtime

- Linguagem: **Python 3.12+**
- Compatibilidade: somente 3.12+ oficialmente suportado no MVP.

---

## 2. Dependências Principais

### 2.1 ForgeBase (núcleo)

O forgeCodeAgent se acopla explicitamente ao núcleo do ForgeBase, seguindo a arquitetura descrita em `docs/guides/forgebase_guides/referencia/arquitetura.md`:

- Dependência obrigatória:
  - `forgebase` (versão compatível com este projeto).
- Imports estruturais esperados:
  - `from forgebase.domain import EntityBase`
  - `from forgebase.application import UseCaseBase, PortBase`
  - `from forgebase.adapters import AdapterBase`
  - `from forgebase.infrastructure.logging import logger_port` (ou módulo equivalente)
  - `from forgebase.observability import log_service, track_metrics`

As entidades e invariantes do domínio do forgeCodeAgent devem reutilizar essas bases, em vez de recriar classes equivalentes.

### 2.2 Core Libraries (stdlib)

Além do ForgeBase, o runtime usa apenas stdlib na sua lógica específica:

- `subprocess` — execução de CLIs de providers.
- `pathlib` — manipulação segura de paths e workspace.
- `dataclasses` — modelagem de tipos de domínio (`ExecutionRequest`, `ExecutionResult`, etc.).
- `typing` / `typing_extensions` — tipos (`Protocol`, `Literal`, `TypedDict`).
- `logging` — logging básico estruturado (integrado a ForgeBase via ports quando disponível).
- `enum` — `ProviderId` e enums auxiliares.

### 2.3 Dependências opcionais (CLI e testes)

- CLI própria:
  - `typer` (ou `click`) para `forge-code-agent` (camada fina sobre a API Python).
- Testes/BDD:
  - `pytest`, `pytest-bdd` (já implícitos via ForgeProcess/ForgeBase).

---

## 4. Organização de Módulos (proposta)

Estrutura lógica para o pacote `forge_code_agent`:

- `forge_code_agent/domain/`
  - `providers.py` — `ProviderId`, abstrações de provider (entidades/VOs especializados sobre `forgebase.domain`).
  - `models.py` — `ExecutionRequest`, `ExecutionResult`, `ToolDefinition`, `ToolCall`, erros de domínio (baseados em `forgebase.domain.exceptions`).
  - `tool_calling.py` — `ToolCallingEngine`.
  - `errors.py` — tipos de erro (`ProviderNotSupportedError`, etc.).
- `forge_code_agent/adapters/`
  - `cli/`
    - `base.py` — `ProviderAdapter` protocol.
    - `codex.py`, `claude.py`, `gemini.py` — providers concretos.
    - `registry.py` — registry `ProviderId -> ProviderAdapter`.
  - `workspace.py` — `FilesystemWorkspaceAdapter`.
  - `logging.py` — `LoggerPort` + implementação padrão (delegando para `forgebase.infrastructure.logging` quando presente).
  - `metrics.py` — `MetricsPort` + no-op (ou integração com `forgebase.observability`).
- `forge_code_agent/runtime/`
  - `agent.py` — implementação de `CodeAgent` (API pública).
  - `streaming.py` — helpers para execução em streaming.
- `forge_code_agent/cli/`
  - `main.py` — comandos `forge-code-agent run/stream`.

---

## 5. CLI e Ferramentas

- CLI alvo:
  - `forge-code-agent` (entry point console_script) com subcomandos:
    - `run` — executa prompt único.
    - `stream` — executa prompt em streaming (stdout).
- Implementação com `typer` (preferencial pela DX), mantendo dependência isolada em `forge_code_agent.cli`.

---

## 6. Observabilidade e Ports

- Ports:
  - `LoggerPort` — interface para logging.
  - `MetricsPort` — interface para métricas.
- Implementação default:
  - usa `logging` stdlib + no-op para métricas.
- Integração futura:
  - adaptadores ForgeBase podem implementar estes ports para enviar dados para a stack de observabilidade padrão.

---

## 7. Testes e BDD

- Testes comportamentais:
  - dirigidos pelas features em `specs/bdd/10_forge_core` e `specs/bdd/50_observabilidade`.
- Ferramentas:
  - `pytest`, `pytest-bdd`.
- Filosofia:
  - BDD → TDD para implementar o runtime seguindo os ValueTracks definidos.
