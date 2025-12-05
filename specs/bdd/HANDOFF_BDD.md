# 🔗 Handoff BDD → Execution — forgeCodeAgent

## 1. Resumo Executivo
O forgeCodeAgent concluiu a fase BDD com um conjunto mínimo, porém consistente, de especificações comportamentais cobrindo:
- execução de prompts de código via diferentes providers de CLI;
- streaming incremental de saída;
- troca de provider sem refatorar automações;
- execução de tool calling com funções Python registradas;
- persistência segura de arquivos no workspace;
- resiliência a erros de configuração de provider, falhas de CLI, interrupções de streaming e JSON malformado.

Este handoff formaliza a transição da fase **BDD** para **Execution / Roadmap Planning**, permitindo que `mark_arc`, `roadmap_coach` e `execution_coach` usem essas especificações como base para arquitetura, backlog e TDD.

---

## 2. Visão do Produto
Resumo derivado de `docs/visao.md`.

| Aspecto | Descrição |
|---------|-----------|
| Propósito | Transformar CLIs de engines de código em um runtime Python plugável, testável e sem custo por token. |
| Público-alvo | Times de desenvolvimento, equipes de automação e plataforma que usam ou desejam usar engines de código via CLI. |
| Proposta de valor | Uma única API Python para orquestrar múltiplos providers de código, permitindo automações locais com governança e baixa dependência de vendors. |
| Métrica de sucesso | Adoção em 1–2 pilotos reais com troca de provider sem refatoração significativa de automações. |

---

## 3. Escopo Aprovado do MVP (perspectiva BDD)
Resumo derivado de `docs/aprovacao_mvp.md` e dos tracks em `specs/bdd/tracks.yml`.

| Funcionalidade | Prioridade | Observações |
|----------------|-----------|-------------|
| Execução de prompts via CLI com `CodeAgent.run()` | Alta | Com provider configurável e status de resposta explícito. |
| Streaming incremental com `CodeAgent.stream()` | Alta | Com indicação clara de término e suporte a interrupções. |
| Troca de provider sem refatorar automações | Alta | Mesmo fluxo de automação funciona ao trocar de `codex` para `claude`/`gemini`. |
| Tool calling com funções Python registradas | Alta | Resultado da tool integrado à resposta da engine. |
| Persistência de arquivos no workspace | Alta | Escrita restrita ao `workdir`, com proteção contra path traversal. |
| Tratamento de erros de provider/CLI/JSON | Média | Necessário para estabilidade, mapeado como SUPPORT track. |

---

## 4. Artefatos de Referência

| Artefato | Caminho | Relevância |
|----------|--------|-----------|
| Visão | `docs/visao.md` | Contexto de negócio e intenção central. |
| Sumário Executivo | `docs/sumario_executivo.md` | Estratégia e modelo de valor. |
| Resultados da Validação | `docs/resultados_validacao.md` | Dados e interpretação da validação de narrativa. |
| Aprovação de MVP | `docs/aprovacao_mvp.md` | Escopo aprovado de MVP. |
| Mapeamento de Comportamentos | `specs/bdd/drafts/behavior_mapping.md` | Base comportamental (VALUE e SUPPORT). |
| Tracks BDD | `specs/bdd/tracks.yml` | Ligação entre ValueTracks e features BDD. |
| Features BDD | `specs/bdd/10_forge_core/*.feature`, `specs/bdd/50_observabilidade/*.feature` | Especificações Given/When/Then de execução, tools/files e resiliência. |

---

## 5. Glossário de Domínio (visão BDD)

| Termo | Definição |
|-------|----------|
| CodeAgent | Abstração Python que encapsula CLIs de engines de código (providers) e oferece APIs `run()`/`stream()` e tool calling. |
| Provider | Engine de código específica que expõe uma CLI (ex.: `codex`, `claude`, `gemini`). |
| Tool | Função Python registrada que pode ser chamada pela engine via JSON (tool calling). |
| Workspace | Diretório de trabalho onde o runtime pode ler e escrever arquivos de código e metadados. |
| ValueTrack | Conjunto de comportamentos que entrega valor direto (execução, tools, arquivos). |
| SupportTrack | Conjunto de comportamentos que garante resiliência e diagnósticos (erros, timeouts, JSON). |

---

## 6. Personas e Atores (foco BDD)

| Persona | Descrição | Necessidades Principais |
|---------|-----------|------------------------|
| Dev de Plataforma | Mantém pipelines, CLIs internas e scripts de automação. | Automatizar engines de código sem scripts frágeis, com APIs claras e estáveis. |
| Líder Técnico / DevEx | Define padrões internos e experiência de desenvolvimento. | Padronizar uso de IA de código, reduzir lock-in e garantir governança. |
| Engenheiro de Automação / SRE | Integra ferramentas a CI/CD e monitora estabilidade. | Detecção clara de falhas, logs e erros diagnósticos para providers e CLIs. |

---

## 7. Restrições e Premissas Relevantes para Execution

| Tipo | Descrição | Impacto em Execution/Roadmap |
|------|-----------|------------------------------|
| Técnica | Operação CLI-first e preferencialmente offline. | Arquitetura deve evitar dependência em APIs remotas; foco em subprocessos e isolamento. |
| Técnica | Suporte inicial a poucos providers (Codex-like + 1 adicional). | Roadmap deve priorizar implementação profunda para poucos providers, não cobertura ampla. |
| Segurança | Escrita limitada ao workspace configurado. | Design deve considerar sandbox de paths e validação de caminhos vindos das engines. |

---

## 8. Critérios de Aceite Macro (para Execution/TDD)
- [ ] CodeAgent executa prompts via CLI com status explícito e sem acoplamento a um único provider.
- [ ] CodeAgent suporta streaming incremental com indicação clara de término e manejo de interrupção.
- [ ] Tool calling consegue executar funções Python registradas e integrar o resultado à resposta da engine.
- [ ] Arquivos gerados são persistidos apenas dentro do workspace, com proteção contra path traversal.
- [ ] Erros de provider/CLI/JSON/timeout são expostos de forma clara e diferenciada, suportando diagnósticos em observabilidade.

---

## 9. Transferência de Responsabilidade

| Papel | Nome | Responsabilidade |
|-------|------|------------------|
| Product Owner / Stakeholder ForgeBase | _a definir_ | Priorização e aceitação de backlog técnico derivado dos tracks BDD. |
| BDD Coach | bdd_coach | Suporte para esclarecimentos sobre cenários e comportamentos. |
| Execution Coach / mark_arc / roadmap_coach | _a definir_ | Conduzir Roadmap Planning, arquitetura e backlog com base nestes artefatos. |

---

## 10. Data e Assinaturas (lógica)

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| Aprovador BDD | _a definir_ | _a definir_ | ✅ BDD completo para MVP |
| Receptor Execution | _a definir_ | _a definir_ | ✅ Handoff recebido |

---

Este documento sinaliza que a fase BDD do forgeCodeAgent está completa para o escopo de MVP e que o próximo passo recomendado é iniciar a fase **Execution / Roadmap Planning**, conforme `process/execution/PROCESS.yml`.

