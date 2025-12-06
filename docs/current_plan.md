# Current Plan — forgeCodeAgent (Streaming + Reasoning + Multi‑Provider)

> Escopo: próximos passos imediatos a partir dos demos Codex/Claude/Gemini (Tetris, streaming, reasoning).

---

## 1. BDD e Integração para Streaming/Reasoning

- [x] Adicionar cenários BDD para streaming por provider em `specs/bdd/10_forge_core/10_code_agent_execution.feature`:
  - [x] `stream()` com provider `codex` via API (CodeAgent.stream).
  - [x] `stream()` com provider `claude` via API.
  - [x] `stream()` com provider `gemini` via API.
- [x] Adicionar pelo menos um cenário `@cli @streaming`:
  - [x] Streaming via CLI oficial (`python -m forge_code_agent.cli stream`) com provider `codex`.
  - [ ] Opcional: marcar um cenário para ambientes que suportem provider real (`@e2e`).

---

## 2. Testes para Flags de Reasoning da CLI

- [x] Criar testes unitários/integração para `forge_code_agent.cli` cobrindo:
  - [x] `--reasoning-only` com provider simulado (linha JSON contendo `item.type=="reasoning"`).
  - [x] `--reasoning-with-output` com:
    - [x] linhas com `item.type=="reasoning"`;
    - [x] linhas com `item.type=="agent_message"`;
    - [x] linhas JSON sem o shape esperado (devem ser ecoadas brutas).
    - [x] linhas não JSON (texto puro).
- [x] Garantir que esses testes não dependam de CLIs externas (usar providers simulados / fixtures).

---

## 3. Demos Avançados de Tool Calling em Streaming

- [x] Estender os demos para incluir tool calling combinado com streaming:
  - [x] Codex:
    - [x] Demo que combina `tools-demo` (tool calling Python) + `stream` com `--reasoning-with-output`.
  - [x] Claude:
    - [x] Demo equivalente usando `FORGE_CODE_AGENT_CLAUDE_CMD`/`FORGE_CODE_AGENT_CLAUDE_STREAM_CMD`.
  - [x] Gemini:
    - [x] Demo equivalente usando `FORGE_CODE_AGENT_GEMINI_CMD`/`FORGE_CODE_AGENT_GEMINI_STREAM_CMD`.
- [x] Garantir que os demos continuem CLI‑first (sem lógica extra fora da CLI oficial).

---

## 4. Tour Multi‑Provider Tetris (Regressão Manual)

- [x] Consolidar os runners:
  - [x] `examples/run_codex.sh` — executar todos os demos em `examples/codex/`.
  - [x] `examples/run_claude.sh` — executar todos os demos em `examples/claude/`.
  - [x] `examples/run_gemini.sh` — executar todos os demos em `examples/gemini/`.
- [ ] Definir este tour como checklist de regressão manual por sprint:
  - [ ] Rodar os três scripts ao final da sprint.
  - [ ] Verificar:
    - [ ] geração/execução de Tetris (ou equivalente) por provider;
    - [ ] streaming funcionando (sem “dump” único ao final);
    - [ ] reasoning visível quando aplicável.

---

## 5. Critérios de Conclusão do Ciclo Atual

- [ ] Pelo menos um cenário BDD `@cli @streaming` passando para provider real.
- [ ] Tests cobrindo `--reasoning-only` e `--reasoning-with-output` verdes.
- [ ] Demos de tool calling em streaming funcionando para pelo menos um provider (Codex).
- [ ] Tour multi‑provider (`run_codex.sh`, `run_claude.sh`, `run_gemini.sh`) rodando sem erros em ambiente preparado.
