# 🧠 forgeCodeAgent — Sua Ponte entre CLIs de Código e Automação Real
_Da linha de comando ao pipeline, sem reescrever tudo a cada engine nova._

> O forgeCodeAgent converte CLIs de engines de código em um runtime Python flexível, ideal para times que querem IA de código local, barata e sob controle.

---

## 🎯 Problema
Engines de código evoluem rápido. Hoje é uma CLI inspirada em Codex, amanhã é uma nova versão do Claude Code, depois surge um provider totalmente diferente.

Sem uma camada de runtime:
- cada mudança de engine vira um projeto de refatoração;
- o risco de quebrar automações aumenta com cada atualização de CLI;
- fica difícil manter governança e observabilidade sobre o que a IA está fazendo com o seu código.

---

## 💡 Solução
O forgeCodeAgent nasce para ser a camada estável entre seu ecossistema Python e as CLIs de engines de código:

- runtime agnóstico ao provider, configurado por parâmetros;
- suporte a streaming incremental de saída, útil para CLIs “falantes”;
- tool calling integrado, executando funções Python com segurança;
- escrita estruturada de arquivos no workspace, alinhada a Git e processos internos.

Com ele, você pode experimentar novas engines sem reescrever seu sistema de automação.

---

## ⚙️ Como Funciona

| Etapa | Descrição |
|-------|-----------|
| 1 | Configure o forgeCodeAgent com o provider de código desejado e o contexto do projeto. |
| 2 | Dispare suas tarefas (gerar módulo, refatorar pasta, criar testes) via API Python ou CLI própria. |
| 3 | O runtime coordena a execução da CLI, interpreta o JSON e aplica tool calling. |
| 4 | Os artefatos gerados são salvos no repositório, prontos para revisão e versionamento. |

---

## 🌟 Benefícios

✅ Menos acoplamento às CLIs e mais foco em valor de negócio.  
🚀 Liberdade para trocar de engine sem reescrever automações inteiras.  
🔒 Compatível com ambientes com restrições de rede e políticas de segurança rígidas.  
🧩 Pensado para trabalhar em conjunto com ForgeBase e ForgeProcess.  

---

## 🧭 Caso de Uso / Exemplo
Uma empresa quer permitir que times internos rodem “sprints assistidas por IA de código” sem expor código para fora.

Com o forgeCodeAgent como runtime:
- cada sessão de trabalho aciona engines de código via CLI local;
- as alterações são gravadas em branches ou workspaces isolados;
- o time consegue medir impacto e segurança sem depender de APIs externas.

---

## 📈 Evidências ou Depoimentos (exemplo)

> “Nosso time de plataforma finalmente conseguiu padronizar a forma de falar com diferentes engines de código, mantendo tudo dentro da nossa infraestrutura.” — *Líder de Plataforma*

---

## 📩 Chamada à Ação (CTA)
Quer testar essa camada de runtime no seu contexto?

👉 [Registre seu interesse para os pilotos fechados](#) e co-construa o forgeCodeAgent conosco.

---

## 📎 Rodapé / Créditos
_Versão C do site de validação do forgeCodeAgent, focada em liberdade de escolha de engine e governança de automação._ 

