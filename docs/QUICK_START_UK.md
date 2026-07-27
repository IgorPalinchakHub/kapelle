# Kapelle: швидкий старт

Kapelle має три основні команди:

```text
start base -> implement -> amend next slice (за потреби) -> verify
```

## 1. Підготувати план

```text
/kapelle:start <slug> "<опис задачі>"
```

Отримаєте компактну карту фічі та перший slice:

- `spec.md` — високорівнева карта відомих use cases, committed behavior і candidates;
- `design.md` — високорівневий системний дизайн та детальний шлях першого slice;
- `tasks.md` — один walking-skeleton workstream.

Для доменної поведінки, складного use case або публічного контракту плагін за потреби додає
`design/domain-model.md`, `specs/<use-case>.md` або `contracts/`. Candidate use cases наперед не
деталізуються.

Правки:

```text
/kapelle:start <slug> --revise "<що змінити>"
```

Підтвердження плану:

```text
/kapelle:start <slug> --approve
```

## 2. Реалізувати

```text
/kapelle:implement <slug> --checkpoint=workstream --validation=ask
```

Плагін реалізує перший справжній наскрізний slice: endpoint/command, use-case service, domain та
persistence/integration boundary і мінімальний стабільний результат. Порожні майбутні endpoints і
services не створюються. Unit-тести на цьому етапі не пишуться.

Наступну вимогу додавайте так:

```text
/kapelle:amend <slug> "<наступна бізнесова або технічна вимога>"
/kapelle:start <slug> --approve
/kapelle:implement <slug>
```

## 3. Написати unit-тести і перевірити

```text
/kapelle:verify <slug> --validation=ask
```

Після PASS і ручної перевірки:

```text
/kapelle:verify <slug> --approve
```

## Якщо активна вимога змінилась

```text
/kapelle:amend <slug> "<нова вимога або feedback>"
```

## Статус або відновлення

```text
/kapelle:status <slug>
```

Для старої фічі Kapelle:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply
```
