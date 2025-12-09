# Ambiente de Execução — forgeCodeAgent / ForgeProcess

Este diretório concentra os arquivos e instruções para preparar o **ambiente local** necessário para seguir o ForgeProcess neste projeto:

- instalação do **ForgeBase** (núcleo de arquitetura e bases Clean/Hex);
- configuração de **virtualenv, testes e hooks de pre-commit** (Ruff, pytest, etc.).

Use este guia sempre que for iniciar o trabalho em uma máquina nova ou preparar o ambiente para o `tdd_coder`.

---

## 1. Instalar o ForgeBase

Referência: `docs/product/guides/forgebase_guides/forgebase_install.md`

### 1.1 Instalação rápida (uso como biblioteca)

Em um virtualenv já criado para este projeto:

```bash
pip install git+https://github.com/symlabs-ai/forgebase.git
```

Isso é suficiente para ter acesso a:

- `forgebase.domain` (EntityBase, exceptions),
- `forgebase.application` (UseCaseBase, PortBase),
- `forgebase.adapters` (AdapterBase),
- módulos de logging/observability do ForgeBase.

### 1.2 Instalação para desenvolvimento do próprio ForgeBase (opcional)

Se você também vai desenvolver/alterar o ForgeBase:

```bash
git clone https://github.com/symlabs-ai/forgebase.git
cd forgebase
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

No contexto deste projeto (forgeCodeAgent), o mínimo necessário é que **`forgebase` esteja instalável/importável** no virtualenv em que os testes/TDD serão executados.

---

## 2. Setup de Git / Pre-commit / Ruff

Este diretório contém o arquivo `git-dev.zip`, cujo conteúdo e instruções originais (documentadas em `temp/setup-git.txt`) definem o setup padrão de Git/pre-commit usado no ForgeBase.

### 2.1 Conteúdo de `git-dev.zip`

De acordo com `temp/setup-git.txt`, o zip inclui:

- `pre-commit-config.yaml`:
  - define hooks como:
    - trailing whitespace,
    - EOF fixer,
    - check-added-large-files,
    - check-yaml,
    - Ruff com `--fix` usando `scripts/ruff.toml`.
- `ruff.toml`:
  - configuração do lint:
    - line-length 88,
    - regras E/F/I/B/UP/C4/SIM/RET/N,
    - ignores compatíveis com Black.
- `install_precommit.sh`:
  - script para instalar dependências de dev, registrar hooks e rodar baseline.
- `dev-requirements.txt`:
  - dependências mínimas para rodar os hooks e a suíte de testes:
    - `pre-commit`,
    - `ruff`,
    - `pytest`, `pytest-bdd`,
    - `pytest-cov` (para medir cobertura de testes por sprint),
    - (e demais ferramentas opcionais conforme repo principal).

### 2.2 Passo a passo para usar em outro projeto (como este)

Dentro do diretório do projeto (este repo), faça:

1. **Extrair os arquivos do zip**
   - Descompacte `process/env/git-dev.zip` em um local apropriado (por exemplo, na raiz ou em `scripts/`), preservando:
     - `pre-commit-config.yaml`,
     - `ruff.toml`,
     - `install_precommit.sh`,
     - `dev-requirements.txt`.

2. **Criar/ativar o virtualenv do projeto**

   O ambiente deste projeto deve ser um virtualenv chamado **`.venv` na raiz do repositório** (não versionado — já está listado em `.gitignore`):

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Instalar dependências de hooks e testes**

   Na raiz onde está `dev-requirements.txt`:

   ```bash
   pip install -r dev-requirements.txt
   ```

4. **Instalar hooks de pre-commit**

   ```bash
   pre-commit install --config pre-commit-config.yaml
   # ou rode o script:
   bash install_precommit.sh
   ```

5. **Rodar baseline nos arquivos existentes**

   ```bash
   pre-commit run --config pre-commit-config.yaml --all-files
   ```

### 2.3 Observações importantes

- Se você colocar os arquivos em outro diretório (por exemplo, `scripts/`), ajuste:
  - o caminho passado em `--config` (`pre-commit run --config scripts/pre-commit-config.yaml --all-files`);
  - os caminhos internos no `install_precommit.sh`, se necessário.
- Ruff roda com autofix; **revise as mudanças** antes de commitar.
- Se quiser estender o ambiente (pytest, mypy, import-linter, deptry, etc.), use `dev-requirements.txt` do repo principal como referência.

---

## 3. Como isso se encaixa no ForgeProcess

No `process/process_execution_state.md`, na fase **Execution**:

- a etapa **5.1.2 (Definição Arquitetural e Stack)** deve:
  - definir a versão de `forgebase`;
  - garantir que `forgebase` está instalado/importável no virtualenv;
  - preparar o ambiente de testes e pre-commit conforme este guia.
- antes de iniciar **5.2 (TDD Workflow)**, o checklist exige:
  - `ROADMAP.md` e `BACKLOG.md` criados;
  - ForgeBase instalado;
  - ambiente de testes + pre-commit configurados (`pytest`, `pytest-bdd`, `pre-commit`, `ruff`).

Em resumo:
**este README.md ensina a montar o ambiente (ForgeBase + testes + pre-commit) necessário para que symbiotas como `tdd_coder` e `forge_coder` possam trabalhar com segurança e dentro das regras do ForgeProcess.**

---

## 4. Checklist rápido de verificação do ambiente

Depois de seguir os passos acima, execute localmente (na raiz do projeto, com `.venv` ativado):

```bash
# 1) Verificar se o ForgeBase está instalável/importável
python -c "import forgebase; print('forgebase OK:', forgebase.__version__)"

# 2) Verificar se pytest está disponível (incluindo plugins como pytest-bdd/pytest-cov)
pytest --version

# 3) Rodar coleta de testes BDD (apenas coleta, sem executar)
pytest --collect-only tests/bdd -q

# 4) Rodar pre-commit em modo baseline (opcional, mas recomendado)
pre-commit run --config pre-commit-config.yaml --all-files
```

Se todos os comandos acima rodarem sem erro, o ambiente está pronto para a fase **Execution.tdd** e para o trabalho do `tdd_coder`.

> 💡 **Dica sobre imports em projetos com layout `src/`**
>
> Para evitar erros de `ModuleNotFoundError` ao rodar `pytest` antes de instalar
> o pacote via `pip`, é recomendável configurar o `pytest.ini` para incluir:
>
> ```ini
> [pytest]
> testpaths = tests
> pythonpath = src
> ```
>
> Isso permite que módulos como `forge_code_agent.*` sejam importados
> diretamente do diretório `src/` durante o TDD, sem exigir instalação prévia
> do pacote.

---

## 5. Script de automação: `setup_env.sh`

Para facilitar, existe um script na raiz do repositório que executa grande parte dos passos acima automaticamente:

```bash
bash setup_env.sh
```

O que ele faz:

- descompacta `process/env/git-dev.zip` na raiz (se `pre-commit-config.yaml` ainda não existir e se `unzip` estiver disponível);
- cria `.venv` na raiz, se ainda não existir;
- instala dependências de desenvolvimento a partir de `dev-requirements.txt` (se presente);
- instala o ForgeBase a partir do repositório oficial do GitHub;
- roda verificações rápidas:
  - import de `forgebase`,
  - `pytest --version` e coleta de testes BDD (se `tests/bdd` existir),
  - instalação e execução inicial de `pre-commit` se `pre-commit-config.yaml` e `pre-commit` estiverem disponíveis no `.venv`.

Após rodar o script, basta ativar o ambiente:

```bash
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows
```

E seguir normalmente com o ForgeProcess (Execution.tdd).
