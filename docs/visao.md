# 🌍 Visão do Produto — forgeCodeAgent (Versão Revisada)

## 1. Intenção Central

Permitir que desenvolvedores Python executem agentes de IA de código de forma programática, local e sem custo por token, unificando múltiplas CLIs de motores (Codex-like, Claude Code, Gemini Code, futuramente Grok Code) em um único runtime com API simples.

O agente deve encapsular comandos reais como:

```bash
claude --dangerously-skip-permissions -p --output-format json "faça um jogo de tetris"
codex exec "faça um jogo de tetris" --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check --output-format json
gemini code --json --prompt "faça um jogo de tetris"
```

E expor uma API Python consistente:

```python
agent = CodeAgent(provider="codex", workdir="C:/tetris")
agent.run("faça um jogo de tetris em python")
```

---

## 2. Problema de Mercado

Today, engines como Codex-like, Claude Code e Gemini Code operam principalmente via interfaces de terminal interativas, sem APIs programáveis, sem streaming estruturado e sem tool calling integrável ao Python.

Quem precisa automatizar processos acaba montando scripts frágeis envolvendo `subprocess`, parsing manual, regex e heurísticas inconsistentes. No outro extremo, APIs remotas oferecem esses recursos, mas com custo por token e lock-in severo.

---

## 3. Hipótese de Valor

Se criarmos um runtime Python que encapsula essas CLIs de forma padronizada, oferecendo métodos como `run()` e `stream()`, parsing robusto de JSON do stdout e integração com tools Python, então desenvolvedores poderão:

* automatizar fluxos completos de geração/edição de código;
* trocar de engine apenas alterando configuração;
* operar sem custo variável;
* manter autonomia tecnológica em ambientes restritos.

---

## 4. Público-Alvo e Contexto

Desenvolvedores Python, equipes de automação e times de plataforma que:

* querem IA de código local, barata e sem APIs remotas;
* precisam integrar engines de código a pipelines corporativos;
* operam com políticas de segurança rígidas ou ambientes offline;
* desejam padronizar automações internas hoje feitas com scripts improvisados.

Casos de uso típicos:

* geração automática de módulos e boilerplates,
* refatoração assistida em monorepos,
* ferramentas internas de engenharia,
* orquestrações customizadas integradas ao ForgeProcess/ForgeBase.

---

## 5. Paisagem Competitiva

**Ollama / LM Studio**
→ bons para modelos genéricos, não para engines de código com fluxo de desenvolvimento.

**CLIs oficiais (Codex-like / Claude Code / Gemini Code)**
→ ótimas interativamente, frágeis via automação.

**APIs remotas (OpenAI, Anthropic, Gemini, DeepSeek)**
→ robustas, mas com custo alto e lock-in.

**Nenhuma opção atual oferece:**

* runtime unificado via CLI,
* API Python única para múltiplas engines,
* tool calling integrado,
* gravação estruturada de arquivos,
* alinhamento com ForgeBase/ForgeProcess.

---

## 6. Diferencial Estratégico

O forgeCodeAgent:

* é o **primeiro “driver universal” para engines de código baseadas em CLI**;
* substitui a necessidade de aprender parâmetros específicos de cada motor;
* implementa **streaming incremental real** vindo do stdout;
* executa **tool calling Python** disparado pelo JSON das engines;
* grava arquivos no workspace de forma governada (ForgeProcess);
* remove totalmente o custo por token;
* reduz lock-in ao mínimo — trocar engine é trocar um parâmetro.

---

## 7. Métrica de Validação Inicial

A visão estará validada quando houver:

* 5–10 equipes usando forgeCodeAgent em automações reais;
* redução observável de scripts ad hoc improvisados;
* casos de troca de engine sem refatorar código;
* aumento de confiabilidade em pipelines internos usando engines de código.

---

## 8. Horizonte de Desenvolvimento

**Semana 1–2**
Refinar visão, mapear constraints de subprocessos e parsing.

**Semana 3–4**
MVP com provider principal (Codex-like), API `run()/stream()`, parser JSON.

**Semana 5–6**
Adicionar Claude Code e Gemini Code; implementar tool calling.

**Semana 7–8**
Integração com ForgeBase/ForgeProcess; adicionar observabilidade mínima.

**Semana 9+**
Ergonomia, documentação, suporte a Grok Code e engines futuras.

---

## 9. Palavras-Chave e Conceitos

`runtime de agentes`, `CLI-first`, `subprocess`, `streaming incremental`,
`tool calling`, `governança de IA`, `ForgeBase`, `ForgeProcess`,
`múltiplos providers`, `offline-first`, `custo zero`, `engenharia de código`.

---

## 10. Tom Narrativo

Direto, pragmático, orientado a desenvolvedores.
Transparente sobre limitações e trade-offs.
Enfatiza autonomia, governança e padronização.
Alinhado com os princípios do ForgeBase e do ForgeProcess.

---
