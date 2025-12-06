# ARCHITECTURAL_QUESTIONNAIRE — forgeCodeAgent

> Versão: 0.1 (draft)
> Responsável: mark_arc
> Fase: Execution / Roadmap Planning — Etapa 00 (Validação Arquitetural)

---

## 1. Contexto

O forgeCodeAgent é um runtime Python que encapsula CLIs de engines de código (Codex-like, Claude Code, Gemini Code, etc.) expondo uma API única (`CodeAgent.run()/stream()`) com:
- execução via `subprocess` e suporte a múltiplos providers;
- streaming incremental;
- tool calling com funções Python registradas;
- persistência de arquivos no workspace, com segurança de paths;
- foco em operação local/offline, alinhado ao ForgeBase (Clean/Hex, CLI-first).

As decisões abaixo devem alinhar arquitetura, stack e limites técnicos com:
- as features BDD em `specs/bdd/10_forge_core` e `specs/bdd/50_observabilidade`;
- os ValueTracks definidos em `specs/bdd/tracks.yml`;
- as restrições do ForgeProcess/ForgeBase.

---

## 2. Domínio e Camadas (Clean/Hex)

1. **Separação de domínio vs adapters**
   - Pergunta: Quais responsabilidades ficam no domínio puro do forgeCodeAgent (ex.: modelagem de providers, contratos de execução, resultados) e quais ficam em adapters (ex.: chamadas `subprocess`, filesystem, logging)?
   - Opções a discutir:
     - Domínio modela `Provider`, `ExecutionRequest`, `ExecutionResult`, `ToolCall`, sem referências a I/O.
     - Adapters concretos: `CliProviderAdapter`, `FilesystemWorkspaceAdapter`, `ToolRegistryAdapter`.

2. **Borda de integração com ForgeBase**
   - Pergunta: O forgeCodeAgent será um módulo “autônomo” acoplado a ForgeBase apenas por convenções, ou terá ports explícitos para integração (ex.: log/metrics, YAML sessions)?
   - Considerar:
     - Ports para logging/metrics que possam ser implementados via ForgeBase.
     - Estratégia para manter o runtime utilizável fora de projetos ForgeBase.

---

## 3. Modelo de Providers e Extensibilidade

3. **Abstração de providers**
   - Pergunta: Como será representado um provider (`codex`, `claude`, `gemini`) em código? Interface única? Registro dinâmico? Plugins?
   - Pontos:
     - Interface mínima: comandos suportados, flags padrão, modo streaming, suporte a tool calling.
     - Configuração via YAML/arquivo vs código.

4. **Registro de novos providers**
   - Pergunta: Como novas CLIs serão adicionadas ao runtime sem quebrar contratos existentes?
   - Opções:
     - Plugins com manifesto explícito (respeitando manifesto ForgeBase).
     - Módulos internos versionados (sem sistema de plugins no MVP).

---

## 4. Execução via CLI (subprocess)

5. **Biblioteca de subprocesso**
   - Pergunta: Usaremos apenas `subprocess` padrão ou alguma camada adicional (ex.: asyncio, wrappers) para lidar com streaming, timeouts e buffers?
   - Restrições:
     - CLI-first, offline; evitar dependências pesadas desnecessárias.

6. **Gestão de timeouts e cancelamento**
   - Pergunta: Como o timeout configurável (BDD resilience) será exposto e implementado? Global? Por chamada? Por provider?

7. **Captura de stdout/stderr**
   - Pergunta: Como capturar stdout (JSON/streaming) e stderr (diagnósticos) de forma segura, sem vazamento excessivo de logs, mas suficiente para depuração?

---

## 5. Parsing, Tool Calling e JSON

8. **Formato de resposta padrão**
   - Pergunta: Qual será o contrato interno de `ExecutionResult`? (ex.: `status`, `provider`, `content`, `raw`, `tool_calls`, `errors`).
   - Alinhar com features:
     - status explícito;
     - conteúdo de código;
     - identificação de provider.

9. **Parsing de JSON malformado**
   - Pergunta: Qual estratégia para lidar com JSON parcial/malformado vindo das CLIs? (ex.: fallback para raw logs, error type específico, tentativas de recuperação).

10. **Engine de tool calling**
    - Pergunta: Onde viverá a lógica que recebe JSON de tool calling, resolve a função Python e injeta o resultado de volta na resposta da engine?
    - Considerar:
      - segurança de execução de tools;
      - isolamento de exceções de tools vs exceções de runtime.

---

## 6. Workspace, Arquivos e Segurança

11. **Sandbox de workspace**
    - Pergunta: Como garantir que nenhuma escrita ocorra fora do `workdir` (proteção contra path traversal)?
    - Possíveis abordagens:
      - normalização de paths e checagem explícita (`path.resolve().is_relative_to(workdir)`).
      - listas de bloqueio (ex.: não permitir caminhos absolutos externos).

12. **Formato de artefatos gravados**
    - Pergunta: Haverá convenção para onde gravar:
      - arquivos de código gerados,
      - metadados de execuções (YAML, JSON),
      - logs/minutas de tool calling?

---

## 7. Observabilidade e Erros

13. **Modelo de erros**
    - Pergunta: Quais tipos de erro explícitos teremos? (ex.: `ProviderNotSupportedError`, `ProviderExecutionError`, `ParsingError`, `WorkspaceSecurityError`).
    - Como esses erros serão expostos ao chamador (ex.: exceptions Python, objetos de erro nos resultados, ambos)?

14. **Integração com observabilidade**
    - Pergunta: Mesmo no MVP, onde e como registrar métricas mínimas (número de execuções, falhas, timeouts)?
    - Integração futura com ForgeBase/Observabilidade: manter contrato flexível.

---

## 8. Stack Tecnológico (nível alto)

15. **Versão de Python e dependências**
    - Pergunta: Python 3.12+ apenas? Dependeremos de libs adicionais (ex.: `pydantic` para modelos, `typer`/`click` para CLI interna) ou manteremos o MVP 100% stdlib?

16. **Integração com CLI própria**
    - Pergunta: Haverá uma CLI do próprio forgeCodeAgent (ex.: `forge-code-agent run ...`), ou apenas API Python neste primeiro ciclo?

---

## 9. Perguntas Abertas para Stakeholders

17. **Prioridade entre providers**
    - Pergunta: Qual provider deve ser considerado “referência” para o MVP (ex.: Codex-like) e qual o segundo provider mais importante (Claude ou Gemini)?

18. **Escopo de uso inicial**
    - Pergunta: Quais são os 1–2 fluxos reais que mais precisamos suportar no primeiro ciclo? (ex.: geração de módulo, PR assistido, refatoração de pasta).

19. **Nível de tolerância a risco**
    - Pergunta: Qual é o nível aceitável de risco em termos de:
      - falha de CLI,
      - perda de saída streaming,
      - falhas em tool calling?

---

## 10. Próximos Passos

- Coletar respostas deste questionário com stakeholders técnicos (Tech Lead, DevEx, Plataforma).
- Consolidar decisões em `specs/roadmap/ARCHITECTURAL_DECISIONS_APPROVED.md`.
- Usar as decisões aprovadas como base para:
  - `TECH_STACK.md`
  - ADRs em `specs/roadmap/adr/*.md`
  - `HLD.md` e `LLD.md`
