# 🧠 forgeCodeAgent — Automatize suas CLIs de IA de Código
_Transforme qualquer CLI de IA de código em um runtime Python plugável, testável e sem custo por token._

> Pare de escrever scripts frágeis em torno de CLIs de IA.
> Uso local. Sem dependência de APIs remotas. Sem vazamento de código.

---

## 🎯 Problema
Times de desenvolvimento querem usar engines de código em automações reais, mas enfrentam dois obstáculos:
- CLIs interativas são difíceis de integrar com segurança a pipelines, bots internos e ferramentas próprias.
- APIs pagas introduzem custo por token e lock-in, o que nem sempre é aceitável em ambientes críticos ou restritos.

O resultado são scripts cheios de `subprocess`, regex e gambiarras que quebram a cada atualização de CLI.

---

## 💡 Solução
O forgeCodeAgent encapsula as CLIs de engines de código em um runtime Python simples:

- Uma API única: `CodeAgent(provider="codex").run(...)/stream(...)`.
- Parsing robusto do JSON emitido no stdout (incluindo tool calling).
- Execução de funções Python registradas como tools.
- Escrita automática de arquivos e alterações diretamente no seu workspace.

Você continua usando suas CLIs preferidas — mas com automação confiável, testável e padronizada.

### Antes / Depois (para devs)

**Antes (gambiarra):**

```python
subprocess.run(["codex", "exec", prompt, ...])
regex = parse_stdout(...)
```

**Depois (forgeCodeAgent):**

```python
CodeAgent("codex").run(prompt)
```

### Exemplos de CLIs encapsuladas

```bash
claude --dangerously-skip-permissions -p --output-format json "refatore este módulo"
codex exec "crie um tetris" --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check --output-format json
gemini code --json --prompt "gere testes para esta API"
```

---

## ⚙️ Como Funciona

**Pipeline mental:** `CLI` → `stdout` JSON → `forgeCodeAgent` → tools Python → arquivos no workspace.

| Etapa | Descrição |
|-------|-----------|
| 1 | Você configura o provider (`codex`, `claude`, `gemini`) e o diretório de trabalho. |
| 2 | O forgeCodeAgent dispara a CLI correspondente via `subprocess`, passando o prompt e parâmetros padronizados. |
| 3 | A saída JSON é lida em streaming, permitindo acompanhar tokens e eventos em tempo real. |
| 4 | Quando a engine pede tool calling, o runtime mapeia e executa suas funções Python registradas. |
| 5 | Os arquivos gerados/alterados são gravados no workspace, prontos para versionamento em Git. |

---

## 🌟 Benefícios

✅ Menos scripts frágeis e código colado em CLIs específicas.
🚀 Automação de agentes de código plugada em CI/CD, CLIs e ferramentas internas.
🔒 Uso local, sem dependência de APIs remotas nem envio de código para fora quando você usa engines locais.
🧩 Integração nativa com processos ForgeBase/ForgeProcess (YAML + Git, Clean/Hex, CLI-first).

---

## 🧭 Caso de Uso / Exemplo
Uma equipe de plataforma quer gerar automaticamente módulos de serviço e testes para novos microserviços.

Com o forgeCodeAgent, ela:
- define um template de tool calling para gerar arquivos;
- usa `CodeAgent` com o provider de código preferido;
- integra o fluxo a um comando interno de CLI.

Em vez de scripts ad hoc por engine, tudo passa a depender de uma única API Python configurável.

---

## 📈 Evidências ou Depoimentos (exemplo)

> “Conseguimos substituir três scripts diferentes por uma única integração com o forgeCodeAgent. Trocar de engine agora é só mudar um parâmetro de configuração.” — *Time de Plataforma (piloto)*

---

## 📩 Chamada à Ação (CTA)
Quer transformar suas CLIs de IA de código em infraestrutura de automação?

👉 Quer ser um dos primeiros times a rodar agentes de código 100% locais?
**Participe dos pilotos e receba suporte direto da equipe do ForgeBase.**

---

## 📎 Rodapé / Créditos
_Visão e hipótese derivadas de `docs/product/hipotese.md` e `docs/product/visao.md` do projeto forgeCodeAgent, dentro do ForgeProcess (MDD)._
