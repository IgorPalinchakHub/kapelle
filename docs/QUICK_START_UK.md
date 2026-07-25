# Kapelle: короткий порядок

Якщо фіча вже реалізована і потрібно відновити її product specification та as-built architecture:

```text
/kapelle:reconstruct <slug> "<feature scope>"
```

Далі виконуйте exact next command із `STATUS.md`. Повна інструкція:
[RECONSTRUCTION_UK.md](RECONSTRUCTION_UK.md).

## Нова фіча

```text
/kapelle:start configurable-invoice-status-in-pipe \
  "Allow invoice status in Pipe to be configured"
```

Default `--lane=auto --interview=auto`.

Якщо задача XS/S і без risk triggers, Kapelle запропонує fast lane: `spec.md`, структурований
`design.md` і `tasks.md` створюються за один виклик та мають одне planning approval.

```text
/kapelle:start <slug> --revise "<feedback>"
/kapelle:start <slug> --approve
```

Для M/L/XL або ризикової задачі використовується standard lane:

```text
/kapelle:spec <slug>
/kapelle:spec <slug> --approve
/kapelle:design <slug>
/kapelle:design <slug> --detail
/kapelle:design <slug> --approve
/kapelle:plan <slug>
/kapelle:plan <slug> --approve
```

`design --approve` нічого не виправляє: PASS займає один deterministic validator + запис gate,
FAIL повертає окрему команду `design --revise`. Для старого завеликого overview спочатку явно
запустіть `/kapelle:design <slug> --compact`, потім окремо `--approve`.

Після planning обидва lanes мають однаковий процес:

```text
/kapelle:base-functional-tests <slug> --validation=ask
/kapelle:implement <slug> --checkpoint=task --validation=ask
/kapelle:unit-tests <slug> --validation=ask
/kapelle:verify <slug> --validation=ask
```

Після manual testing:

```text
/kapelle:finalize <slug> --version=1.0
```

Зміни вимог або дизайну:

```text
/kapelle:amend <slug> "<feedback>"
```

## Існуюча legacy feature directory

Старий pipeline не запускається. Спочатку:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply --lane=standard
```

Після міграції виконайте exact next command із `STATUS.md`.

## Відновлення

```text
/kapelle:status <slug>
```

Якщо `_kapelle/` видалено, lane відновлюється з marker у `proposal.md`. Approvals і validation
evidence не вигадуються.
