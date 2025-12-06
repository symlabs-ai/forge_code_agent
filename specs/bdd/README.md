# BDD Specs — forgeCodeAgent

Este diretório contém as especificações BDD de alto nível do forgeCodeAgent, organizadas por domínio (prefixos `10_`, `20_`, `50_`, etc.) e alinhadas aos ValueTracks definidos em `specs/bdd/tracks.yml`.

## Estrutura

- `10_forge_core/`
  - `10_code_agent_execution.feature` — execução de prompts via CLI (`run`, `stream`, troca de provider).
  - `11_code_agent_tools_and_files.feature` — tool calling e persistência de arquivos no workspace.
- `50_observabilidade/`
  - `50_code_agent_resilience.feature` — erros de provider/CLI, interrupção de streaming, JSON malformado, timeout e captura de stderr.
- `drafts/`
  - `behavior_mapping.md` — mapeamento de comportamentos (VALUE e SUPPORT) usado como base para as features.

## Convenções

- Gherkin sempre em inglês (`Feature`, `Scenario`, `Given/When/Then/And`).
- Tags principais:
  - `@value`, `@support` — tipo de ValueTrack.
  - `@forge_core`, `@observability` — domínio.
  - `@ci-fast`, `@ci-int`, `@e2e` — classificação de execução.
  - Outras tags (`@tools`, `@workspace`, `@security`, etc.) refinam foco.

Os tracks e sua ligação com as features são definidos em `specs/bdd/tracks.yml`.
