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

Architecture-rules subagent повертає правила для конкретних aspects/paths. `design.md` завжди має
секції:

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

### Результат

```text
design.md
design/*.md
contracts/*.md
adr/*.md
_kapelle/surface-plan.json
```

High-level `design.md` залишається коротким; окремі детальні документи створюються лише для
самостійних boundaries.

```text
/kapelle:design <slug> --detail
/kapelle:design <slug> --revise "<feedback>"
/kapelle:design <slug> --approve
```

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
