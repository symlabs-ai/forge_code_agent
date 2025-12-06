# 🚀 Aprovação de MVP — forgeCodeAgent

## 1. Contexto e Decisão
O forgeCodeAgent passou pela fase de MDD com:
- hipótese inicial registrada em `docs/hipotese.md`;
- visão consolidada em `docs/visao.md`;
- síntese estratégica em `docs/sumario_executivo.md`;
- pitch de valor em `docs/pitch_deck.md`;
- três variações de site de validação (`site_A`, `site_B`, `site_C`) e resultados consolidados em `docs/resultados_validacao.md`.

Os experimentos indicaram tração clara para a proposta de um **runtime Python unificado para engines de código via CLI**, em especial na narrativa que enfatiza:
- API única para múltiplos providers;
- capacidade de trocar de engine sem refatorar automações;
- operação local, sem custo por token quando usado com engines locais.

**Decisão**: avançar para o desenvolvimento de um MVP do forgeCodeAgent.

---

## 2. Resultados-Chave da Validação

| Indicador | Resultado | Interpretação |
|----------|-----------|---------------|
| Conversões (manifestação de interesse em piloto) | Versão B com ~2× mais conversões que A e C | Forte aderência à narrativa de API única + multi-provider. |
| Tempo médio na página | Versão B com maior tempo de leitura | Conteúdo é lido com atenção, indicando interesse real. |
| Feedback qualitativo | Stakeholders técnicos e de produto positivos | Entendimento claro do problema e da proposta de valor. |

---

## 3. Escopo do MVP

| Elemento | Incluir no MVP? | Observações |
|---------|-----------------|-------------|
| Runtime básico `CodeAgent` | ✅ | API `run()/stream()` com configuração de provider e workdir. |
| Suporte a provider principal (Codex-like) | ✅ | Provider de referência para validar arquitetura. |
| Suporte a segundo provider (Claude ou Gemini) | ✅ | Validar multi-provider real, mesmo que com escopo limitado. |
| Tool calling básico (execução de funções Python) | ✅ | Necessário para demonstrar integração prática. |
| Escrita de arquivos no workspace com rastreabilidade mínima | ✅ | Alinhado com ForgeBase/ForgeProcess (YAML + Git). |
| Observabilidade avançada / dashboards | ❌ | Posterior ao MVP; focar em logs simples no início. |
| Suporte a todos os providers do roadmap (ex.: Grok Code) | ❌ | Fica para ciclos posteriores, após validar o núcleo. |

---

## 4. Objetivos do MVP
- Validar que a API `CodeAgent(provider, workdir).run()/stream()` é suficiente para cobrir os principais casos de uso.
- Demonstrar, em ao menos 2 projetos piloto, a capacidade de trocar de engine sem refatorar automações.
- Integrar o forgeCodeAgent a pelo menos um fluxo ForgeProcess (por exemplo, TDD/Execution ou Delivery/CI).

---

## 5. Riscos e Cuidados

| Risco | Mitigação |
|-------|-----------|
| Complexidade de manter compatibilidade com CLIs em evolução | Definir adaptadores por provider, com contratos mínimos e testes de integração. |
| Escopo do MVP crescer demais (scope creep) | Manter foco em 1–2 providers e funcionalidades essenciais (runtime, tool calling básico, escrita em disco). |
| Expectativa de “produto pronto” após MVP | Comunicar claramente que o MVP é técnico e voltado a pilotos controlados. |

---

## 6. Stakeholders e Responsáveis

| Nome | Função | Responsabilidade |
|------|--------|------------------|
| Stakeholders ForgeBase | Aprovadores de visão e escopo | Decisão sobre continuidade e ajustes estratégicos. |
| MDD Coach | Facilitação do processo MDD | Garantir integridade dos artefatos e da decisão. |
| Tech Lead / Execution Coach | Liderança técnica do MVP | Definir arquitetura, backlog técnico e acompanhar execução. |

---

## 7. Próximos Passos
- Iniciar fase de BDD para mapear comportamentos e cenários, com base na visão e no escopo aprovado.
- Estruturar o roadmap técnico inicial (`specs/roadmap/`) durante a fase de Execution.
- Selecionar 1–2 projetos piloto onde o forgeCodeAgent será exercitado em fluxos reais (por exemplo, geração de módulos, refatorações assistidas ou PR assistido).

Esta aprovação autoriza formalmente o início do trabalho de especificação comportamental (BDD) e planejamento técnico (Execution) do forgeCodeAgent.
