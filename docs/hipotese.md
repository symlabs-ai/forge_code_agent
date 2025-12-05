# **Hipótese — Runtime de Agentes (forgeCodeAgent)**

## **Problema**

Desenvolvedores precisam executar agentes de IA de forma programática, local e sem custo por token, mas os motores disponíveis (Codex-like, Claude, Gemini, etc.) funcionam apenas via CLI interativa e não oferecem API, streaming ou tool calling integrável ao Python.

## **Solução Proposta**

O Runtime encapsula as CLIs de motores locais (Codex-like, Claude, Gemini, com suporte futuro a Grok Code) via subprocesso, oferecendo uma API Python simples (`run()`, `stream()`), parsing de JSON emitido pelo stdout, suporte a tool calling executando funções Python registradas e gravação automática dos arquivos gerados no workspace informado.

Exemplos conceituais de chamadas que o runtime deve encapsular:

* **Claude Code**

  ```bash
  claude \
    --dangerously-skip-permissions \
    -p \
    --output-format json \
    "faça um jogo de tetris em python"
  ```

* **Codex CLI**

  ```bash
  codex exec "faça um jogo de tetris em python" \
    --dangerously-bypass-approvals-and-sandbox \
    --skip-git-repo-check \
    --output-format json
  ```

* **Gemini Code**

  ```bash
  gemini code \
    --json \
    --prompt "faça um jogo de tetris em python"
  ```

Do ponto de vista do usuário Python, o uso seria:

```python
agent = CodeAgent(provider="codex", workdir="C:\\tetris")
agent.run("faça um jogo de tetris em python")
```

## **Contexto**

Motores locais gratuitos fornecem apenas fluxo interativo em terminal. APIs que oferecem automação e tool calling cobram por token. Não existe hoje um runtime que transforme múltiplas CLIs de LLM em um executor programável unificado com streaming, ferramentas e escrita de código em disco.

## **Sinal de Mercado**

Há crescimento acelerado de modelos locais e engines de código (Codex-like, Claude Code, Gemini Code, Grok Code), além de forte demanda por automação sem custo variável. Desenvolvedores buscam uma forma única de executar agentes completos sem depender de APIs remotas ou SDKs específicos de cada fornecedor.

## **Oportunidade Pressentida**

Criar um módulo Python que age como um “driver universal de agentes via CLI”, permitindo rodar prompts, gerar código, executar tool calling e operar em modo streaming apenas com subprocessos, suportando inicialmente Codex-like, Claude e Gemini, e preparando terreno para Grok Code sem quebra de interface.

## **Público-Alvo Inicial**

Desenvolvedores Python, equipes de automação, plataformas low-code/no-code e empresas que desejam IA local, barata e independente de provedores, mas que ainda querem liberdade para trocar o motor de código subjacente.

## **Impacto Esperado**

* Execução automatizada de agentes via CLI sem intervenção humana.
* Streaming contínuo lendo stdout incremental.
* Integração direta de tools Python com o mecanismo de tool calling da LLM.
* Geração de arquivos no diretório indicado pelo usuário.
* Redução total de vendor lock-in e eliminação do custo por token, com possibilidade de trocar de motor apenas alterando configuração.

## **Evidências**

Engines como Cloud Code/Codex, Claude Code e Gemini Code são amplamente adotadas mesmo oferecendo apenas modo interativo, evidenciando demanda reprimida por execução programática e unificada. Há reclamações gerais sobre custo por token nas APIs e interesse crescente por soluções locais baseadas em CLI.

## **Grau de Certeza**

90%

## **Próximo Passo Prático**

Implementar o MVP com wrapper de subprocesso multi-engine (Codex-like, Claude, Gemini), modo streaming, parser incremental de tool calling, registro de tools e escrita automática dos arquivos gerados no workspace, usando comandos equivalentes a:

```bash
python cli.py run "faça um jogo de tetris em python" --provider codex  -C .
python cli.py run "faça um jogo de tetris em python" --provider claude -C .
python cli.py run "faça um jogo de tetris em python" --provider gemini -C .
```
