# Project Recommendations — forgeCodeAgent

> Documento vivo mantido por **Jorge the Forge** com recomendações de processo e técnicas
> que devem ser consideradas nas próximas sprints.
> Deve ser lido pelo **Sprint Coach** no início de **cada sprint**.

---

## Estrutura

Cada recomendação deve ser registrada com:

- `id`: identificador curto (ex.: R-001).
- `source`: onde foi identificada (ex.: sprint-1/review.md, jorge-process-review, MDD review).
- `description`: descrição objetiva da recomendação.
- `owner_symbiota`: quem deve agir (ex.: sprint_coach, forge_coder, tdd_coder).
- `status`: `pending` | `done` | `cancelled`.
- `notes`: comentários curtos sobre decisões ou execução.

---

## Recomendações Atuais

### R-001 — Medir cobertura de testes por sprint

- `id`: R-001
- `source`: project/sprints/sprint-1/jorge-process-review.md
- `description`: Incluir medição e registro de cobertura de testes (pytest-cov ou similar) nas próximas sprints e registrar o valor em `review.md` e/ou `progress.md`.
- `owner_symbiota`: sprint_coach (coordena) + forge_coder (executa medição)
- `status`: done
- `notes`:
  - Estrutura implementada na Sprint 2:
    - `pytest-cov` adicionado em `dev-requirements.txt`;
    - `process/env/README.md` atualizado com instruções de cobertura;
    - Sprint 2 `planning.md`/`progress.md`/`review.md` orientam a medição via `pytest --cov`.
  - A execução do comando e registro do valor passa a ser parte do ritual de cada sprint.

### R-002 — Refinar datas reais e story points/capacity

- `id`: R-002
- `source`: project/sprints/sprint-1/jorge-process-review.md
- `description`: Ajustar datas reais, story points e capacidade/velocity nos artefatos de sprint (planning/progress) a partir da Sprint 2, para que deixem de ser placeholders e reflitam a cadência real.
- `owner_symbiota`: sprint_coach
- `status`: done
- `notes`:
  - Sprint 2 já incorpora datas/estimativas mais concretas em `planning.md` e `progress.md`.
  - Recomenda-se continuar refinando estes valores nas próximas sprints com base em histórico real.
