# CLI Sessions & Context — forgeCodeAgent

Este documento descreve como usar a CLI oficial do forgeCodeAgent para:

- manter **sessões** com contexto persistente entre chamadas; e
- habilitar **resumo automático de contexto** (auto-summarize) quando o histórico crescer demais.

---

## 1. Conceitos

- **CodeAgent**: fachada de alto nível para um provider (`codex`, `claude`, `gemini`), usada pela CLI para executar prompts individuais.
- **CodeManager**: orquestrador de múltiplos `CodeAgent`s e de sessões:
  - gerencia `ContextSessionManager` por `session_id`;
  - persiste contexto em `logs/codeagent/session_<SESSION>_*.json`;
  - pode aplicar resumo automático via `Summarizer` (ex.: `AgentSummarizer`).
- **Sessão (`session-id`)**: identificador lógico (string) que agrupa várias execuções de prompts sob o mesmo contexto.

---

## 2. Executando com sessões via CLI

Comando base:

```bash
python -m forge_code_agent.cli run \
  --provider codex \
  --workdir ./project/demo_workdir \
  --prompt "Qual é a capital do Brasil?" \
  --use-code-manager \
  --session-id sess-demo
``+

Com isso:

- `--use-code-manager` faz a CLI usar `CodeManager.run(...)` em vez de `CodeAgent.run(...)` direto.
- `--session-id sess-demo` garante que o contexto (prompt + resposta + eventos) seja:
  - registrado em `ContextSessionManager(session_id="sess-demo")`;
  - persistido em `logs/codeagent/session_sess-demo_*.json`.

Várias execuções com o mesmo `--session-id` reutilizam o contexto:

```bash
python -m forge_code_agent.cli run \
  --provider codex \
  --workdir ./project/demo_workdir \
  --prompt "Agora, resuma a conversa até aqui." \
  --use-code-manager \
  --session-id sess-demo
```

---

## 3. Auto-summarize (resumo automático)

Além de usar sessões, é possível habilitar **resumo automático**:

```bash
python -m forge_code_agent.cli run \
  --provider codex \
  --workdir ./project/demo_workdir \
  --prompt "Explique o desenho arquitetural atual." \
  --use-code-manager \
  --session-id sess-demo \
  --auto-summarize
```

Quando `--auto-summarize` é usado:

- A CLI cria um `CodeManager` com `summarizer_factory` baseado em `AgentSummarizer`, que usa o próprio `CodeAgent`/provider como summarizer.
- Após cada `run()`, o `CodeManager` chama `ContextSessionManager.summarize_if_needed(summarizer)`:
  - Se o número de eventos (`max_events`) ou o tamanho em caracteres (`max_summary_chars`) exceder os limites, o contexto é resumido;
  - Um `ContextSummary` é adicionado à sessão;
  - Apenas os últimos `max_events` eventos são mantidos, evitando crescimento descontrolado.

Os snapshots contendo summaries continuam sendo persistidos em `logs/codeagent/session_<SESSION>_*.json`.

---

## 4. Inspecionando contexto e summaries

1. Rode alguns comandos com `--use-code-manager` e `--session-id` (com ou sem `--auto-summarize`).
2. Liste os snapshots da sessão:

```bash
ls logs/codeagent/session_sess-demo_*.json
```

3. Abra o arquivo mais recente para inspecionar eventos e summaries:

```bash
python - << 'PY'
from pathlib import Path
from forge_code_agent.context.session_manager import ContextSessionManager

logs_dir = Path("logs/codeagent")
snapshots = sorted(logs_dir.glob("session_sess-demo_*.json"))
if not snapshots:
    raise SystemExit("Nenhum snapshot encontrado.")

last = snapshots[-1]
session = ContextSessionManager.load(last)
print(f"Eventos: {len(session.events)}")
print(f"Summaries: {len(session.summaries)}")
if session.summaries:
    print("Último summary:")
    print(session.summaries[-1].text)
PY
```

---

## 5. Exemplos prontos

Os seguintes scripts em `examples/` demonstram sessões e auto-resumo:

- `examples/session_code_manager_demo.sh`
  Cria uma sessão, troca provider e mostra o contexto persistido.

- `examples/session_code_manager_autosummary_demo.sh`
  Usa `CodeManager` com summarizer para disparar `summarize_if_needed()` e imprime o resumo mais recente.

- `examples/sprint5_pr_assist_demo.sh`
  Demonstra um fluxo de **PR assistido**: prepara um workspace com arquivos modificados
  e `pr_files.txt`, executa a CLI com `--use-code-manager` + `--session-id` usando
  primeiro o provider `codex` e depois `claude` na mesma sessão.

- `examples/sprint5_module_and_tests_demo.sh`
  Demonstra um fluxo de **geração de módulo + testes**: prepara um workspace vazio,
  chama a CLI para gerar módulo e testes em `src/` e `tests/` com `codex`, e depois
  reexecuta com `gemini` na mesma sessão para sugerir/refinar melhorias.

Recomendação de processo:

- Ao final de cada sprint/ciclo, inclua pelo menos um demo baseado em CLI que:
  - use `--use-code-manager` + `--session-id`; e
  - demonstre onde o contexto/summaries foram gravados.
