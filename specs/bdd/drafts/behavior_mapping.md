# Mapeamento de Comportamentos — forgeCodeAgent

> **Data:** 2025-12-05
>
> **Responsável:** bdd_coach
>
> **Status:** Rascunho

---

## ValueTrack: Execução de Agentes de Código via CLI

**Tipo:** VALUE
**Domínio:** 10_forge_core
**Referência MDD:** `docs/visao.md`

---

### Comportamentos Identificados

#### 1. Executar prompt de código com um provider configurado (sucesso)

**Ação (O QUÊ o usuário faz):**
O desenvolvedor configura um `CodeAgent` com um provider de código (por exemplo, `codex`) e um `workdir`, envia um prompt de código para `run()` e espera a conclusão da execução.

**Resultado esperado (O QUÊ ele vê):**
O runtime chama a CLI correspondente, a engine de código gera a resposta e o desenvolvedor recebe o resultado de forma estruturada (texto/código), com um campo explícito de status (sucesso/erro).

**Critério de validação (COMO validar):**
- A CLI é invocada com os parâmetros esperados para o provider configurado.
- A chamada retorna sem erro de subprocesso.
- O objeto de resposta do `CodeAgent` indica sucesso de forma explícita e contém o conteúdo gerado.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Run code prompt with configured provider
  GIVEN there is a CodeAgent configured with provider "codex" and a valid working directory
  WHEN the developer sends a code prompt for execution
  THEN the runtime executes the provider CLI
  AND the developer receives a structured code response with a clear success status
```

---

#### 2. Executar prompt com streaming incremental (sucesso)

**Ação (O QUÊ o usuário faz):**
O desenvolvedor chama `stream()` em um `CodeAgent` configurado para acompanhar a saída da engine de código em tempo real.

**Resultado esperado (O QUÊ ele vê):**
O runtime expõe um fluxo incremental de eventos/mensagens, permitindo que o desenvolvedor consuma o código gerado aos poucos, sem esperar o término completo da execução, e sinaliza de forma inequívoca o fim do stream.

**Critério de validação (COMO validar):**
- A CLI é invocada em modo compatível com streaming.
- O runtime entrega mais de um chunk de saída, preservando a ordem.
- Há um evento ou flag explícito indicando conclusão do stream.
- Não há perda de dados entre o que veio da CLI e o que foi entregue ao chamador.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Consume streamed code response incrementally
  GIVEN there is a CodeAgent configured with streaming support for provider "codex"
  WHEN the developer calls stream() with a code prompt
  THEN the runtime delivers response events incrementally
  AND the developer can reconstruct the full response from the stream
  AND the end of the stream is clearly indicated
```

---

#### 3. Trocar de provider sem alterar o código de automação

**Ação (O QUÊ o usuário faz):**
O desenvolvedor muda a configuração de provider (por exemplo, de `"codex"` para `"claude"` ou `"gemini"`) mantendo o mesmo fluxo de automação (mesmo código que usa `CodeAgent`). Essa configuração pode ser feita via variável de ambiente, arquivo de configuração (ex.: YAML) ou outro mecanismo externo ao código.

**Resultado esperado (O QUÊ ele vê):**
O mesmo código de orquestração continua funcionando, agora chamando a CLI do novo provider, sem necessidade de refatorações estruturais.

**Critério de validação (COMO validar):**
- O fluxo de automação (scripts/tests) permanece idêntico.
- O `CodeAgent` passa a invocar a CLI do novo provider.
- Os resultados indicam que o prompt foi processado pela engine correta, sem erros de integração.

**Cenário BDD futuro (configuração sem refatoração de código):**
```gherkin
SCENARIO: Switch provider while keeping the same automation flow
  GIVEN there is an automation flow that uses a CodeAgent with provider "codex"
  AND this flow is passing
  WHEN the provider is changed to "claude" only in configuration
  THEN the flow continues to execute successfully
  AND the CLI invoked becomes the "claude" provider CLI
```

---

#### 6. Carregar configuração de provider a partir de arquivo YAML (configuração avançada)

**Ação (O QUÊ o usuário faz):**
O desenvolvedor mantém um arquivo de configuração (por exemplo, `forge_code_agent.yml`) que define o provider padrão e, opcionalmente, parâmetros específicos de CLI por provider. O código de automação cria o `CodeAgent` a partir desse arquivo, sem precisar codificar o provider diretamente no código Python.

**Resultado esperado (O QUÊ ele vê):**
O mesmo fluxo de automação continua funcionando, e o provider ativo (e sua CLI) passa a ser determinado pelo arquivo YAML. Alterar o provider no YAML (por exemplo, de `"codex"` para `"claude"`) muda o comportamento da execução sem necessidade de alterar o código de automação.

**Critério de validação (COMO validar):**
- Existe um arquivo de configuração YAML legível pelo runtime.
- O `CodeAgent` consegue ser instanciado “from config” usando esse arquivo.
- Com o YAML apontando para provider `"codex"`, o fluxo executa usando `"codex"`.
- Ao alterar o YAML para `"claude"`, o mesmo fluxo passa a executar com `"claude"`, sem mudanças no código Python.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Select provider from YAML configuration file
  GIVEN there is an automation flow that creates a CodeAgent from a configuration file
  AND the YAML configuration sets the provider to "codex"
  WHEN the developer runs the automation flow
  THEN the provider "codex" is used to execute the CLI
  AND when the YAML configuration is changed to set the provider to "claude" without changing the automation code
  THEN the same automation flow executes successfully using the "claude" provider CLI
```

---

#### 4. Executar tool calling com função Python registrada (sucesso)

**Ação (O QUÊ o usuário faz):**
O desenvolvedor registra uma tool Python (por exemplo, `gerar_arquivo`) no `CodeAgent` e envia um prompt que faz a engine disparar um tool calling para essa função.

**Resultado esperado (O QUÊ ele vê):**
O runtime recebe a chamada de tool no JSON da engine, executa a função Python correspondente com os argumentos corretos e devolve o resultado para a engine, que incorpora a saída na resposta final.

**Critério de validação (COMO validar):**
- O JSON de tool calling é recebido e interpretado corretamente.
- A função Python registrada é chamada com argumentos coerentes.
- A resposta final da engine reflete o resultado produzido pela tool.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Execute tool calling with registered Python function
  GIVEN there is a CodeAgent with a tool "generate_file" registered to a Python function
  WHEN the code engine requests execution of the "generate_file" tool via JSON
  THEN the runtime executes the corresponding Python function with the provided arguments
  AND the final response from the engine includes the result of the tool execution
```

---

#### 5. Persistir arquivos gerados no workspace (sucesso)

**Ação (O QUÊ o usuário faz):**
O desenvolvedor chama `run()` com um prompt que instrui a engine a criar ou atualizar arquivos de código no projeto.

**Resultado esperado (O QUÊ ele vê):**
Ao final da execução, os arquivos esperados existem dentro do `workdir`, com conteúdo correspondente ao código gerado pela engine, sem escrever fora do workspace.

**Critério de validação (COMO validar):**
- Os arquivos esperados são criados/atualizados dentro do diretório de trabalho configurado.
- O conteúdo dos arquivos corresponde ao que foi gerado pela engine.
- Não há escrita em caminhos fora do workspace (ex.: diretórios pai).

**Cenário BDD futuro:**
```gherkin
SCENARIO: Persist generated files in the workspace
  GIVEN there is a CodeAgent configured with an empty working directory
  WHEN the developer executes a prompt that generates a code module
  THEN the runtime creates the corresponding files inside the working directory
  AND the file contents reflect the code generated by the engine
  AND no files are written outside the configured workspace
```

---

## ValueTrack: Confiabilidade e Resiliência de Execução

**Tipo:** SUPPORT
**Domínio:** 50_observabilidade
**Referência MDD:** `docs/visao.md`

---

### Comportamentos Identificados

#### 1. Provider inexistente ou não suportado

---

**Condição (QUANDO ocorre):**
O desenvolvedor configura o `CodeAgent` com um provider que não está implementado ou não é suportado pelo runtime.

**Tratamento esperado (COMO o sistema reage):**
O runtime falha de forma explícita e controlada, retornando um erro claro (ex.: exceção específica) indicando provider inválido, sem tentar invocar nenhuma CLI.

**Critério de validação:**
- Nenhum subprocesso é disparado.
- A mensagem de erro indica o nome do provider inválido.
- O status de erro é fácil de capturar nos testes automatizados.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Fail to configure unsupported provider
  GIVEN a developer tries to create a CodeAgent with provider "unknown"
  WHEN the agent is initialized
  THEN the runtime fails with a clear error indicating the provider is not supported
  AND no CLI is executed
```

---

#### 2. Falha na execução da CLI (erro de subprocesso)

**Condição (QUANDO ocorre):**
O runtime tenta executar a CLI de um provider válido, mas há erro de execução (comando não encontrado, saída de erro, timeouts).

**Tratamento esperado (COMO o sistema reage):**
O runtime captura o erro, sinaliza falha com informação suficiente para diagnóstico (mensagem e, se possível, stdout/stderr relevantes), sem travar ou ficar em estado inconsistente.

**Critério de validação:**
- O erro de subprocesso é traduzido para uma exceção/resultado específico do runtime (por exemplo, um tipo `ProviderExecutionError`).
- Logs ou mensagens incluem detalhes mínimos (comando, código de saída).
- O chamador consegue diferenciar erro de engine de erro de runtime.

**Cenário BDD futuro:**
```gherkin
SCENARIO: Handle failure while executing provider CLI
  GIVEN the CLI for provider "codex" is not available in the environment
  WHEN the runtime tries to execute a code prompt
  THEN the runtime returns a provider execution error
  AND the message allows identifying that the command could not be found
```

---

### Edge Cases (Opcional)

#### 1. Saída parcial com interrupção

**Descrição:**
Durante uma execução em streaming, a CLI é interrompida (ex.: cancelamento, erro de rede local ou time-out), resultando em saída parcial.

**Comportamento esperado:**
O runtime deve sinalizar claramente que a resposta é incompleta, expondo o que foi gerado até o momento e o motivo da interrupção, para permitir decisões conscientes do chamador (repetir, retomar, descartar).

**Cenário BDD:**
```gherkin
SCENARIO: Indicate that streamed response was interrupted
  GIVEN a CodeAgent is executing a prompt in streaming mode
  AND the CLI is interrupted before completion
  WHEN the runtime delivers the events to the caller
  THEN the developer receives the chunks that were already generated
  AND the developer is informed that the response was interrupted before completion
```

---

#### 2. JSON de saída malformado vindo da CLI

**Descrição:**
Durante uma execução, a CLI retorna um JSON inválido ou malformado, impossibilitando o parsing direto da resposta.

**Comportamento esperado:**
O runtime detecta o problema de parsing, registra informação suficiente para diagnóstico e retorna um erro claro, sem mascarar o problema nem corromper o estado interno.

**Cenário BDD:**
```gherkin
SCENARIO: Handle malformed JSON output from CLI
  GIVEN a provider CLI returns malformed JSON in its output
  WHEN the runtime tries to parse the response
  THEN the runtime raises a clear parsing error
  AND the error contains enough information to debug the malformed output
```

---

## Resumo de Mapeamento

| ValueTrack | Tipo | Comportamentos | Cenários BDD |
|-----------|------|----------------|--------------|
| Execução de Agentes de Código via CLI | VALUE | 6 | 6 |
| Confiabilidade e Resiliência de Execução | SUPPORT | 4 | 4 |

**Total:** 10 comportamentos → 10 cenários BDD

---

## Próximo Passo

- [ ] Revisão com PO/Stakeholder
- [ ] Aprovação do mapeamento
- [ ] Avançar para Subetapa 2: Escrita de Features Gherkin

---

**Autor:** bdd_coach
**Revisado por:** _a definir_
**Data de aprovação:** _a definir_
