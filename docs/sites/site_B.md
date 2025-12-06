# 🧠 forgeCodeAgent — Runtime Python para Engines de Código
_Uma única API Python para múltiplas engines de código._

> Uma única API Python. Troque de engine de código (Codex → Claude → Gemini) **sem refatorar nada**.

---

## 🎯 Problema
Se você já tentou automatizar uma CLI de engine de código, conhece o cenário:
- cada provider tem flags, parâmetros, formatos de saída e comportamentos próprios;
- o parsing do stdout e o manejo de tool calling vivem quebrando a cada mudança de versão;
- qualquer mudança de engine significa, na prática, reescrever scripts inteiros e ajustar pipelines.

No outro extremo, APIs remotas resolvem uma parte do problema — mas em troca de custo por token e acoplamento forte a um vendor.

---

## 💡 Solução
O forgeCodeAgent oferece um runtime Python padronizado para engines de código:

- abstração de provider (`provider="codex"`, `"claude"`, `"gemini"`, etc.);
- métodos `run()` e `stream()` para orquestrar prompts e sessões de código;
- interpretação consistente de JSON no stdout, inclusive tool calling;
- escrita de arquivos gerados diretamente no repositório.

Você ganha um ponto único de integração, sem perder a liberdade de escolher (e trocar) sua engine preferida.

### Suporte inicial de CLIs

```text
Suporte inicial:
✔ Codex-like
✔ Claude Code
✔ Gemini Code
(Pronto para expandir: Grok Code e outros)
```

### Exemplo rápido de uso

```python
agent = CodeAgent(provider="claude", workdir="./app")
agent.run("gere o módulo de autenticação")
```

---

## ⚙️ Como Funciona

| Etapa | Descrição |
|-------|-----------|
| 1 | Configure o `CodeAgent` com o provider e o `workdir`. |
| 2 | Chame `run()` ou `stream()` com o prompt desejado. |
| 3 | O runtime aciona a CLI correspondente via `subprocess`. |
| 4 | O forgeCodeAgent processa o JSON de saída, tratando tool calling e eventos de forma uniforme. |
| 5 | Arquivos e alterações são gravados no workspace, alinhados ao fluxo Git do seu time. |

---

## 🌟 Benefícios

✅ **Governança unificada**: logs, workspace controlado e padronização de fluxos.
✅ **Redução de lock-in**: troque de engine sem mudar o código de automação.
✅ **Custo previsível**: execução local, sem custo por token quando usado com engines locais.
✅ **DX melhorada**: menos tempo lutando com `subprocess` e parsing manual; mais tempo focado em valor de negócio.
🧪 Base sólida para TDD/automação em projetos que seguem ForgeBase/ForgeProcess.

---

## 🧭 Caso de Uso / Exemplo
Um time quer que cada PR abra com um “diff sugerido” de melhorias gerado por uma engine de código.

Com o forgeCodeAgent:
- 1. um job de CI chama `CodeAgent` com o provider configurado;
- 2. o runtime executa a CLI, interpreta o JSON e escreve sugestões em arquivos sob `project/reviews/`;
- 3. revisores analisam os diffs sugeridos e aprovam o que faz sentido;
- 4. o fluxo se adapta caso a empresa troque de engine no futuro, sem refatorar o pipeline.

---

## 📈 Evidências ou Depoimentos (exemplo)

> “Depois de padronizar em torno do forgeCodeAgent, conseguimos experimentar diferentes engines de código sem mexer no pipeline.” — *Equipe de DevEx*

---

## 📩 Chamada à Ação (CTA)
Quer uma camada única para orquestrar engines de código na sua stack?

👉 Quer unificar engines de código na sua empresa com uma única API?
Inscreva seu time nos testes iniciais do forgeCodeAgent e avalie o impacto em cenários reais de desenvolvimento.

---

## 📎 Rodapé / Créditos
_Conteúdo baseado na visão de produto e sumário executivo do projeto forgeCodeAgent (Fase MDD)._
