# 🎤 Pitch de Valor — forgeCodeAgent

## 🧠 1. A Ideia Central
Transformar CLIs de engines de código em um runtime Python unificado, local e sem custo por token, permitindo que times automatizem agentes de código com a mesma facilidade com que hoje chamam uma função.

---

## 🎯 2. O Problema
Hoje, quem quer usar motores de código como Codex-like, Claude Code ou Gemini Code em automações reais cai em um dos dois extremos:
- scripts frágeis em torno de CLIs interativas, com `subprocess`, regex e muita gambiarra; ou
- dependência de APIs remotas pagas, com custo por token e lock-in pesado.

Isso trava a adoção de IA de código em pipelines internos, especialmente em ambientes com forte exigência de segurança, governança e operação offline.

---

## 💡 3. A Solução
O forgeCodeAgent é o “driver universal” para engines de código baseadas em CLI.

Ele encapsula CLIs como `codex`, `claude` e `gemini code` em um runtime Python que oferece:
- métodos simples como `run()` e `stream()` para executar agentes de código;
- parsing robusto do JSON emitido no stdout, incluindo tool calling;
- execução direta de funções Python registradas como tools;
- gravação automática de arquivos e alterações no workspace do projeto.

Em vez de reescrever automações para cada engine ou API, o time integra uma vez com o forgeCodeAgent e troca de provider apenas por configuração.

---

## ⚙️ 4. Como Funciona

| Etapa | Descrição |
|-------|-----------|
| 1. Configuração | O time define o `provider` (ex.: `codex`, `claude`, `gemini`) e o `workdir`. |
| 2. Execução | O forgeCodeAgent dispara a CLI correspondente via `subprocess`, passando prompt e parâmetros padronizados. |
| 3. Streaming | A saída JSON do stdout é lida de forma incremental, permitindo streaming de tokens e eventos. |
| 4. Tool calling | Quando a engine emite chamadas de ferramenta, o runtime resolve e executa funções Python registradas. |
| 5. Escrita em disco | Arquivos gerados/alterados são escritos no workspace com governança alinhada ao ForgeProcess/ForgeBase. |

---

## 🚀 5. Oportunidade de Mercado
- Crescimento acelerado de engines de código e copilots, mas com foco em uso interativo.
- Aumento da preocupação com custo por token, privacidade de código e operação offline.
- Times de plataforma buscando padronizar integrações de IA dentro de empresas.

O forgeCodeAgent se posiciona como infraestrutura crítica nesse cenário: é a camada que torna essas engines realmente integráveis a pipelines, CLIs e ferramentas internas, sem exigir que cada time “reinvente” sua própria forma de falar com as CLIs.

---

## 🧩 6. Diferenciais Competitivos
✅ Unifica múltiplas CLIs de engines de código em uma única API Python.
✅ Focado em execução local e custo zero por token quando usado com motores locais.
✅ Tool calling nativo, com execução de funções Python e gravação de arquivos no workspace.
✅ Alinhado ao ForgeBase/ForgeProcess (Clean/Hex, CLI-first, offline, YAML + Git).
✅ Facilita trocar de provider sem reescrever automações.

---

## 🧭 7. Roadmap

| Fase | Objetivo | Resultado Esperado |
|------|----------|--------------------|
| Fase 1 | MVP com provider principal (Codex-like) | Runtime capaz de `run()/stream()` um engine, com parsing JSON e escrita em disco. |
| Fase 2 | Multi-provider (Claude Code, Gemini Code) | Abstração de providers estável e testada em cenários reais. |
| Fase 3 | Integração ForgeBase e tool calling avançado | Uso integrado em projetos ForgeProcess, com exemplos e casos piloto. |
| Fase 4 | Observabilidade e hardening | Logs estruturados, métricas básicas e estabilidade para uso em produção. |

---

## 💰 8. Modelo de Negócio
O forgeCodeAgent pode ser:
- open source, com monetização via serviços, suporte empresarial e extensões avançadas; e/ou
- base para ofertas de assinatura que incluam dashboards, observabilidade e plugins certificados.

O valor está na padronização e na governança: reduzir o custo de integrar engines de código a sistemas existentes e dar às empresas controle sobre como a IA toca seu código.

---

## 🧑‍💼 9. Time

| Nome | Função | Competência Principal |
|------|--------|------------------------|
| Core ForgeBase | Arquitetura e runtime | Clean/Hex, CLI-first, integração com processos ForgeProcess. |
| Colaboradores & Comunidade | Providers e extensões | Integrações com novas engines de código e melhorias de DX. |

---

## 🎯 10. Chamada à Ação (CTA)
Se sua equipe já usa CLIs de engines de código ou quer reduzir dependência de APIs remotas, o forgeCodeAgent é o próximo passo natural.

Participe dos pilotos iniciais, ajude a definir os primeiros providers suportados em profundidade e traga seus casos reais de automação de código.

> “Vamos transformar CLIs de IA de código em infraestrutura padrão de desenvolvimento — com autonomia, governança e custo previsível.”
