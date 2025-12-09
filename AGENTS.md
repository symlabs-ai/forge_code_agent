# Symbiotas e Agents — Guia Rápido

## Sobre o repositório

Este é o repositorio do projeto forgeCodeAgent

Desenvolvedores precisam executar agentes de IA de forma programática, local e sem custo por token, mas os motores disponíveis (Codex-like, Claude, Gemini, etc.) funcionam apenas via CLI interativa e não oferecem API, streaming ou tool calling integrável ao Python.

O modulo python forgeCodeAgent encapsula as CLIs de motores locais (Codex-like, Claude, Gemini, com suporte futuro a Grok Code) via subprocesso, oferecendo uma API Python simples (`run()`, `stream()`), parsing de JSON emitido pelo stdout, suporte a tool calling executando funções Python registradas e gravação automática dos arquivos gerados no workspace informado.

## Referências Obrigatórias

- Guia de agentes do ForgeBase: `docs/product/guides/forgebase_guides/agentes-ia/` (início rápido, descoberta, ecossistema).
- Regras do ForgeBase: `docs/product/guides/forgebase_guides/usuarios/forgebase-rules.md` (Clean/Hex, CLI-first, offline, persistência YAML + auto-commit Git).
- Prompts de cada symbiota: `process/symbiotes/<nome>/prompt.md`.
- Contexto MDD/BDD: `docs/product/`, `specs/bdd/`, `specs/adr/`. #pode ainda não existir
- Execucao do processo: `/process/process_execution_state.md`

## Defaults para qualquer symbiota

- Clean/Hex: domínio é puro; adapters só via ports/usecases; nunca colocar I/O no domínio.
- CLI-first e offline: validar via CLI; evitar HTTP/TUI no MVP; sem rede externa por padrão.
- Persistência: sessões/estados em YAML; auto-commit Git por step/fase quando habilitado.
- Plugins: só executar se houver manifesto claro; respeitar permissões (rede=false por padrão).
- Documentar sessões/handoffs em `project/docs/sessions/` quando aplicável.

## Symbiotas de Código/Tests (TDD)

- Consultar: `docs/product/guides/forgebase_guides/agentes-ia/guia-completo.md`, `docs/product/guides/forgebase_guides/usuarios/forgebase-rules.md`, prompts em `process/symbiotes/tdd_coder/` e `process/symbiotes/test_writer/`.
- Seguir BDD → TDD: features em `specs/bdd/`, steps em `tests/bdd/`, código em `src/` seguindo camadas ForgeBase.
- Usar exceções específicas, logging/métricas do ForgeBase; Rich apenas para UX em CLI.

## Outros Symbiotas

- Sempre ler o prompt do symbiota em `process/symbiotes/<nome>/prompt.md` e aplicar as regras gerais acima quando interagirem com runtime/processos/artefatos.

## Outras observações

- Sempre que o usuário pedir para carregar, impersonar, interpretar uma persona de symbiota ou agente. Responda a ele sempre com o nome do symbiota na cor verde entre chaves: [bill_review] diz: Estou começando a analisar ....
