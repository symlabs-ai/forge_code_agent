# 🔗 Handoff MDD → BDD — forgeCodeAgent

## 1. Resumo Executivo
O forgeCodeAgent foi validado na fase de MDD como um **runtime Python unificado para engines de código via CLI**, com foco em:
- API única para múltiplos providers (Codex-like, Claude Code, Gemini Code, etc.);
- capacidade de trocar de engine sem refatorar automações;
- operação local, sem custo por token quando usado com engines locais;
- alinhamento com princípios ForgeBase/ForgeProcess (Clean/Hex, CLI-first, offline, YAML + Git).

Este documento formaliza a transferência para o BDD Process, autorizando a especificação de comportamentos do sistema com base na visão e no MVP aprovado.

---

## 2. Visão do Produto
Resumo derivado de `docs/visao.md`.

| Aspecto | Descrição |
|---------|-----------|
| Propósito | Transformar CLIs de engines de código em um runtime Python plugável, testável e sem custo por token. |
| Público-alvo | Times de desenvolvimento, plataformas internas e equipes de automação que usam ou desejam usar engines de código via CLI. |
| Proposta de valor | Uma única API para orquestrar múltiplas engines de código, permitindo automações locais, governadas e desacopladas de vendors específicos. |
| Métrica de sucesso | Adoção em 1–2 pilotos reais com troca de engine sem refatoração significativa de automações. |

---

## 3. Escopo Aprovado do MVP
Resumo derivado de `docs/aprovacao_mvp.md`.

| Funcionalidade | Prioridade | Observações |
|----------------|-----------|-------------|
| `CodeAgent` com API `run()/stream()` | Alta | Núcleo do runtime; base para todos os casos de uso. |
| Suporte a provider principal (Codex-like) | Alta | Provider de referência para validar arquitetura e DX. |
| Suporte a segundo provider (Claude ou Gemini) | Média | Comprovar multi-provider; escopo inicial pode ser limitado. |
| Tool calling básico com funções Python | Alta | Essencial para integrar com workflows reais. |
| Escrita de arquivos no workspace (YAML + código) | Alta | Necessário para integração com ForgeBase/ForgeProcess. |
| Observabilidade avançada / dashboards | Baixa | Postergado para ciclos pós-MVP. |

---

## 4. Artefatos de Referência

| Artefato | Caminho | Relevância |
|----------|--------|-----------|
| Visão | `docs/visao.md` | Contexto de negócio e intenção central. |
| Sumário Executivo | `docs/sumario_executivo.md` | Estratégia, modelo de negócio e roadmap macro. |
| Pitch de Valor | `docs/pitch_deck.md` | Narrativa de valor para stakeholders. |
| Resultados da Validação | `docs/resultados_validacao.md` | Dados e interpretação dos testes A/B/C. |
| Aprovação de MVP | `docs/aprovacao_mvp.md` | Decisão formal de avançar para MVP. |

---

## 5. Glossário de Domínio

| Termo | Definição |
|-------|----------|
| Engine de código | Ferramenta de IA focada em geração, refatoração e compreensão de código (ex.: CLIs inspiradas em Codex, Claude Code, Gemini Code). |
| Runtime de agentes | Camada que orquestra chamadas a engines de código, gerenciando prompts, streaming, tool calling e escrita em disco. |
| Provider | Implementação específica de engine de código (ex.: `codex`, `claude`, `gemini`). |
| Tool calling | Mecanismo em que a engine pede ao runtime para executar funções específicas (tools) com parâmetros estruturados. |
| Workspace | Diretório de trabalho onde o forgeCodeAgent lê e grava arquivos (código, YAML, logs). |

---

## 6. Personas e Atores

| Persona | Descrição | Necessidades Principais |
|---------|-----------|------------------------|
| Dev Backend/Plataforma | Desenvolvedor que mantém pipelines, CLIs e ferramentas internas. | Automatizar uso de engines de código sem gambiarras; manter scripts simples e reutilizáveis. |
| Líder Técnico / DevEx | Responsável por DX e padrões internos. | Padronizar integrações com IA de código; reduzir lock-in e custo, mantendo governança. |
| Engenheiro de Automação / SRE | Cuida de confiabilidade e integrações com CI/CD. | Integrar engines de código a pipelines com previsibilidade, logs e segurança. |

---

## 7. Restrições e Premissas

| Tipo | Descrição | Impacto no BDD |
|------|-----------|----------------|
| Técnica | Operação CLI-first e preferencialmente offline. | Cenários devem considerar ausência de dependência em APIs remotas. |
| Técnica | Suporte inicial a um conjunto limitado de providers. | Features BDD devem focar no núcleo (multi-provider básico), não em todos os engines possíveis. |
| Negócio | Foco em uso interno/pilotos antes de exposição ampla. | Critérios de aceite podem priorizar integridade e governança em vez de escala. |

---

## 8. Critérios de Aceite Macro
- [ ] Permitir executar prompts de código via `CodeAgent.run()` com ao menos 2 providers distintos configuráveis.
- [ ] Permitir streaming incremental de saída com `CodeAgent.stream()`.
- [ ] Suportar tool calling básico que escreva/atualize arquivos no workspace.
- [ ] Integrar com ao menos um fluxo de processo (por exemplo, um passo de CI ou uma sessão de TDD/Execution).

---

## 9. Transferência de Responsabilidade

| Papel | Nome | Responsabilidade |
|-------|------|------------------|
| Product Owner / Stakeholder ForgeBase | _a definir_ | Priorização e validação de features BDD. |
| BDD Coach | _a definir_ | Facilitar mapeamento de comportamentos e escrita de features. |
| MDD Coach | _a definir_ | Suporte em dúvidas de contexto de mercado. |

---

## 10. Data e Assinaturas

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| Aprovador MDD | _a definir_ | _a definir_ | ✅ Aprovado |
| Receptor BDD | _a definir_ | _a definir_ | ✅ Recebido |

---

Este handoff encerra formalmente o ciclo MDD do forgeCodeAgent e inicia o trabalho de BDD, que deverá produzir `specs/bdd/**/*.feature` e artefatos correlatos com base neste contexto.
