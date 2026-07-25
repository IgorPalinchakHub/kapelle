# Reverse engineering існуючої фічі

`/kapelle:reconstruct` використовується, коли код уже існує, а потрібно відновити:

- бізнесову або продуктову специфікацію;
- фактичний архітектурний дизайн;
- зв'язок кожного важливого твердження з кодом, тестами, конфігурацією чи project rules.

Це skill і stateful documentation workflow всередині Kapelle. Окремий plugin або harness не
потрібний.

## Що створюється

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md                         # коротка продуктова карта
  specs/
    <scenario-or-rule>.md         # детальна бізнесова поведінка
  design.md                       # коротка архітектурна карта
  design/
    <component-or-flow>.md        # детальний as-built дизайн
  contracts/                      # тільки корисні окремі interfaces
  _context/
    evidence-index.md
  _kapelle/
    workflow.json
    reconstruction.json
    reconstruction-coverage.json
    architecture-guidance/
    approvals/
```

Overview-файли залишаються короткими й посилаються на detail-файли. Поділ виконується за
самостійними сценаріями, правилами, компонентами або інтеграційними boundaries — не за кожним
класом чи layer.

## Запуск

Початкова команда повинна задати конкретну межу:

```text
/kapelle:reconstruct order-cancellation \
  "Existing order cancellation from CMS action through backend workflow and external notifications"
```

Вдала межа містить observable flow, entrypoint або набір модулів. Формулювання “опиши весь
проєкт” надто широке: спочатку варто розділити його на фічі або bounded contexts.

## Фази

### 1. Scope

Agent знаходить entrypoints, actors, аспекти, межі та невідомі частини. Він створює `proposal.md`,
первинний evidence index і machine-readable scope.

Перевірте, чи включено потрібні frontend/backend/workers/data/integrations і чи exclusions
правильні. Потім:

```text
/kapelle:reconstruct <slug> --approve
```

### 2. Product/business specification

```text
/kapelle:reconstruct <slug> --spec
```

Agent простежує permissions, validation, main/alternative/error flows, domain transitions,
persistence, external effects, retries/idempotency та user-visible outcomes. Тести є evidence
поведінки, але не автоматично пояснюють product intent.

Після review:

```text
/kapelle:reconstruct <slug> --approve
```

### 3. As-built architecture

```text
/kapelle:reconstruct <slug> --design
```

Kapelle семантично знаходить project skills і subagents. Окремий project subagent повертає scoped
architecture rules для поточних aspects, modules, entrypoints і paths.

Архітектурні документи явно розрізняють:

- **As-built** — що фактично робить реалізація;
- **Rule** — яке project rule застосовується;
- **Deviation** — де реалізація відхиляється від правила.

Backend, frontend та інші аспекти аналізуються як один flow із shared contracts і dependencies.
Після review:

```text
/kapelle:reconstruct <slug> --approve
```

### 4. Evidence review

```text
/kapelle:reconstruct <slug> --review
```

Fresh reviewer перевіряє coverage, суперечності, business-to-design traceability, citations,
architecture deviations і unknowns. Результат:

- `PASS` — матеріальних прогалин немає;
- `PASS-WITH-GAPS` — прогалини явно описані, але пакет залишається корисним;
- `BLOCKED` — документація була б оманливою через суперечність або unsupported claim.

Після фінального review:

```text
/kapelle:reconstruct <slug> --approve
```

## Evidence та достовірність

Кожне важливе твердження має id `RC-NNN` і один тип:

- `observed` — прямо підтверджено executable code, schema, config або test;
- `inferred` — обґрунтований висновок із кількох observed facts;
- `declared` — написано у project docs/rules, але не підтверджено execution;
- `unknown` — поточних evidence недостатньо.

Observed та inferred claims містять точні repository-relative paths і line ranges. Coverage
fingerprint-ить усі процитовані source-файли та generated artifacts. Якщо код або документація
зміняться, review стає stale, а `STATUS.md` поверне:

```text
/kapelle:reconstruct <slug> --review
```

## Важливі обмеження

- Workflow не змінює production code, tests, config або migrations.
- Workflow не створює `tasks.md` чи `test-plan.md`.
- Workflow не запускає `plan`, `implement`, testing stages або `finalize`.
- `documented` не означає implemented, verified, release-ready або shipped.
- Silence не є approval; `--approve` затверджує тільки поточний gate із `STATUS.md`.
- Якщо вимоги описують бажану зміну, для неї треба окремо запустити development workflow через
  `/kapelle:start`, використовуючи reconstructed documents як context.
