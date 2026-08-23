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

Новий або явно переглянутий slice коротко фіксує:

- поточну поведінку, зміну, результат і те, що має залишитися незмінним;
- поточну affected architecture, resulting architecture і technical delta;
- `Changes`, `Done when` та `Verify` для кожного active workstream; завершена legacy-історія не
  потребує backfill.

Кожен active `AC-NN` scenario покривається workstream, а його `Verify` пояснює focused evidence.
Validator знаходить missing, unknown і uncovered scenarios без окремого task DAG.

Для доменної поведінки, складного use case або публічного контракту плагін за потреби додає
`design/domain-model.md`, `specs/<use-case>.md` або `contracts/`. Candidate use cases наперед не
деталізуються.

Diagram додається лише коли текстом важко показати boundary, ordering, lifecycle, data flow або
refactoring delta. Kapelle використовує найменший Mermaid visual у `design.md` чи `design/<aspect>.md`
і одразу пояснює його простою мовою. Проста зміна не отримує diagram заради шаблону.

Якщо потрібне рішення developer-а, Kapelle спочатку рекомендує evidence-backed варіант і називає
його мінус. Зазвичай показуються два варіанти. Короткий code example додається лише коли він реально
прояснює API, schema, control flow або compatibility; reversible defaults не перетворюються на
питання.

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

`verify` звіряє реалізацію з документами та оновлює їх до підтвердженого as-built стану. Детальні
`specs/`, `design/`, contracts або diagrams додаються лише за реальним тригером; проста зміна
залишається в компактних root-документах.

Якщо всі applicable перевірки вже виконані вручну або в іншій сесії:

```text
/kapelle:verify <slug> --developer-verified "Увесь запланований verification batch пройдено."
```

Такий PASS буде явно позначено як підтверджений developer-ом без captured output.

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
