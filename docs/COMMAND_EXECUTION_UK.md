# Детальний порядок команд Kapelle

Kapelle має один human-controlled процес:

```text
start → spec → design → plan → base-functional-tests
      → implement → unit-tests → verify → finalize
```

Для XS/S planning може пройти fast lane:

```text
start --lane=fast → один review/approval → base-functional-tests
```

Для документування вже реалізованої фічі є окремий documentation-only процес
`/kapelle:reconstruct`. Він не є альтернативним development pipeline і не переходить до `plan`,
`implement` чи release:

```text
scope → approve → spec → approve → design → approve → review → approve
```

## 1. `/kapelle:start <slug> "<raw task>"`

### Що задати на вході

- стабільний slug;
- необроблений опис задачі;
- optional `--lane=auto|fast|standard`;
- optional `--interview=auto|lean|standard|deep`.

### Що відбувається

- explorer знаходить поточну поведінку або project boundary;
- факти відділяються від requested behavior і assumptions;
- визначаються size, risks, lane та interview depth;
- project capabilities і architecture-rules subagent знаходяться семантично.

`lean` не запускає critic/devil subagents. `standard` робить один combined critic pass. `deep`
використовує business analyst, critic і devil's advocate.

### Що отримуємо

Standard:

```text
proposal.md
spec.md
_context/architecture.md
_kapelle/size.json
```

Fast додатково одразу створює `design.md`, `tasks.md`, surface/task plans і просить одне approval.

Правки:

```text
/kapelle:start <slug> --revise "<feedback>"
/kapelle:start <slug> --approve
```

## 2. Standard `/kapelle:spec <slug>`

### Вхід

Slug, optional interview depth і feedback.

### Робота

Описуються actors, main/alternative flows, rules, validations, subprocesses, component reactions,
failures, retry/idempotency, permissions, compatibility й acceptance criteria.

### Результат

```text
spec.md
specs/scenarios.md
specs/business-rules.md
specs/integrations.md       # лише коли потрібно
```

Approval:

```text
/kapelle:spec <slug> --approve
```

## 3. Standard `/kapelle:design <slug>`

### Робота

Перший виклик виконує тільки delta-discovery відносно вже зібраного `_context/`, запускає один
bounded architecture-rules lookup і один high-level critic без паралельного inline fallback.
`design.md` має ціль 150–220 рядків і hard limit 280 рядків / 2800 слів. Він завжди має секції:

1. Context and goal;
2. Scope and constraints;
3. Architecture rules applied;
4. Building blocks and responsibilities;
5. Runtime flows;
6. Data and domain impact;
7. Contracts and integrations;
8. Cross-cutting concerns;
9. Decisions and trade-offs;
10. Validation and rollout;
11. Open questions.

Структура перевіряється `scripts/validate_design.py`.

### Результат першого виклику

```text
design.md
_kapelle/surface-plan.json
_kapelle/architecture-guidance/design.json
```

Повні ADR, contracts, domain/status skeletons, transaction mechanics і call-site analysis тут не
створюються. Вони з'являються лише після підтвердження напрямку:

```text
/kapelle:design <slug> --detail
```

Після `--detail` отримуємо лише потрібні:

```text
design/*.md
contracts/*.md
adr/*.md
```

Правки й approval:

```text
/kapelle:design <slug> --revise "<feedback>"
/kapelle:design <slug> --approve
```

Approval-файли агент не формує вручну: canonical gate helper записує точну schema, повні SHA-256
та оновлює `STATUS.md`.

## 4. Standard `/kapelle:plan <slug>`

### Робота

Створюються low-coupling/high-cohesion vertical outcomes, dependencies, contract ordering,
integration ownership, AC coverage і file ownership. Graph перевіряється Python validator.

### Результат

```text
tasks.md
test-plan.md
_kapelle/task-plan.json
```

Production tasks не містять написання unit tests.

```text
/kapelle:plan <slug> --revise "<feedback>"
/kapelle:plan <slug> --approve
```

## 5. `/kapelle:base-functional-tests <slug>`

### Вхід

Slug і `--validation=ask|allow|skip`.

### Робота

До production code пишуться тільки базові functional tests для endpoint inputs/outputs/errors,
public use-case methods та critical contracts. Unit tests і exhaustive coverage виключені.

### Результат

Test files та `_kapelle/base-functional-tests.json`. Skip не є PASS.

## 6. `/kapelle:implement <slug>`

```text
/kapelle:implement <slug> --checkpoint=task --validation=ask
```

Агент знаходить project skills/subagents, отримує scoped architecture rules, планує й реалізує
production code. Unit tests не створюються.

Checkpoint:

- `task`;
- `workstream`;
- `none`.

Після checkpoint користувач отримує outcome, changed files, observable behavior, risks і next
action.

## 7. `/kapelle:unit-tests <slug>`

Запускається тільки після завершення всього production code. Аналізує changed/new units, пише всі
потрібні unit tests і записує fingerprinted evidence.

## 8. `/kapelle:verify <slug>`

Формує прозорий batch:

- functional;
- unit;
- integration;
- contract;
- static analysis;
- lint;
- build.

Required skip/cancel створює `validation-deferred`.

## 9. `/kapelle:amend <slug> "<feedback>"`

Версіонує поточний стан, класифікує impact, просить approval маршруту, оновлює canonical artifacts
та інвалідує downstream evidence. Повний restart не виконується.

## 10. `/kapelle:finalize <slug> --version=1.0`

Потребує PASS verification і підтвердження manual testing/debugging. Виконує as-built convergence,
fresh review, створює Mermaid diagrams і записує completed release.

## 11. `/kapelle:migrate <slug>`

Для feature directory без human-controlled marker:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply --lane=standard
```

Dry-run показує preserved files, gaps і next command. Apply додає durable marker та workflow state,
але не вигадує approvals, reviews або validation.

## 12. `/kapelle:status <slug>`

Відновлює derived state і показує exact next command. Видалення `_kapelle/` не видаляє lane:
він відновлюється з marker у `proposal.md`.

## Optional utilities

`survey`, `sequences`, `data-model`, `contracts`, `decide-adr`, `glossary`, `roadmap` можуть
доповнювати артефакти, але не є альтернативним конвеєром.

## 13. `/kapelle:reconstruct <slug> "<feature scope>"`

### Що задати

- новий slug для документаційного пакета;
- чітку межу існуючої фічі: entrypoints, модулі або observable flow, який треба пояснити.

### Послідовність

```text
/kapelle:reconstruct <slug> "<feature scope>"
/kapelle:reconstruct <slug> --approve
/kapelle:reconstruct <slug> --spec
/kapelle:reconstruct <slug> --approve
/kapelle:reconstruct <slug> --design
/kapelle:reconstruct <slug> --approve
/kapelle:reconstruct <slug> --review
/kapelle:reconstruct <slug> --approve
```

### Результат

```text
proposal.md
spec.md
specs/*.md
design.md
design/*.md
contracts/*.md                         # якщо окремий review справді корисний
_context/evidence-index.md
_kapelle/reconstruction.json
_kapelle/reconstruction-coverage.json
```

Agent сам семантично знаходить project skills/subagents. Project architecture-rules subagent
повертає правила саме для поточних aspects, modules, entrypoints і paths. Твердження маркуються як
`observed`, `inferred`, `declared` або `unknown`; observed/inferred мають точні посилання на код.

Завершення означає лише, що product/business specification та as-built architecture design
перевірені проти актуального evidence. Це не означає, що фіча release-ready.

Повна інструкція: [RECONSTRUCTION_UK.md](RECONSTRUCTION_UK.md).
