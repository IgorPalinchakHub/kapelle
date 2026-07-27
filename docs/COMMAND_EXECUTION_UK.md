# Kapelle: порядок виконання команд

Основний процес:

```text
start base -> approve -> implement
                          |
              amend next slice -> approve -> implement
                          |
                        verify
```

## 1. `/kapelle:start <slug> "<опис задачі>"`

### Що задати

- `<slug>` — стабільна назва фічі, бажано з номером ticket;
- короткий опис бажаного бізнес-результату;
- відомі обмеження або важливі приклади, якщо вони є.

Приклад:

```text
/kapelle:start CLS-14829-post-bulk-invoices "Додати масове створення invoice з вибраних замовлень"
```

### Що відбувається

Плагін один раз досліджує релевантний існуючий код, тести й аналоги. Він знаходить проєктні skills,
інструкції та architecture-rules subagent. Explorer додається лише коли неясна зона відповідальності;
critic — лише для суттєвої неоднозначності або ризику.

Плагін формує високорівневу карту всієї відомої фічі: actors, use cases, бізнес-правила, компоненти,
domain/data ownership та інтеграції. У реалізаційних деталях він планує лише мінімальний
production-shaped walking skeleton: один наскрізний flow через потрібні шари. `tasks.md` має один
workstream, максимум три checkbox, якщо без цього slice незручно рев’ювати. Наступні можливі вимоги
залишаються hypotheses у `Candidate capabilities`.

### Результат

- `spec.md` — high-level feature map, committed behavior, use cases, правила і candidates;
- `design.md` — high-level system design і технічний шлях першого slice;
- за тригером `specs/<use-case>.md`, `design/domain-model.md`, contract, ADR або sequence;
- `tasks.md` — walking-skeleton workstream;
- `STATUS.md` — поточний стан і наступна команда.

За потреби попросіть точкові правки:

```text
/kapelle:start <slug> --revise "<що саме змінити>"
```

Коли три файли погоджені:

```text
/kapelle:start <slug> --approve
```

`--approve` нічого не генерує і не запускає агентів: лише перевіряє поточні fingerprints та створює
approval для поточного slice.

## 2. `/kapelle:implement <slug>`

Рекомендований виклик:

```text
/kapelle:implement <slug> --checkpoint=workstream --validation=ask
```

### Що задати

- `<slug>`;
- checkpoint:
  - `workstream` — рекомендовано, контроль після цілісного результату;
  - `task` — частіший контроль для ризикової роботи;
  - `none` — виконати всі готові workstream;
- validation:
  - `ask` — спочатку показати точні команди;
  - `allow` — дозволити focused checks;
  - `skip` — відкласти їх до `verify`.

### Що відбувається

Main agent сам реалізує погоджений end-to-end slice, застосовуючи знайдений project skill і
закешовані architecture rules. Перший skeleton має пройти через реальний endpoint/command,
use-case service, domain та persistence/integration boundary і дати мінімальний стабільний
результат. Порожні майбутні endpoints/services не створюються. Обов’язкових planner → implementer
→ reviewer subagent-циклів немає. Reviewer використовується для high-risk змін або на пряме
прохання.

Перед production-кодом можуть бути додані базові functional/characterization tests для endpoint,
command, worker або public use-case method. Unit-тести поки не пишуться. Повний PHPStan/lint/full
suite також не запускається під час звичайного development.

### Результат

- реалізований бізнес-результат workstream;
- короткий список змінених зон;
- observable behavior і важливий trade-off;
- focused checks: passed або deferred;
- два варіанти: додати наступну вимогу через `amend` або завершувати scope через `verify`.

## 3. `/kapelle:amend <slug> "<feedback>"`

Використовуйте як нормальний наступний крок, щоб додати бізнесову або технічну вимогу до вже
працюючої бази, а також для зміни активного slice.

### Що задати

```text
/kapelle:amend CLS-14829-post-bulk-invoices "Для archived order bulk invoice створювати не можна"
```

### Результат

Плагін перевіряє поточну реалізацію, переносить лише запитану вимогу з candidate у committed
behavior, за потреби створює детальний use-case spec, оновлює domain model/contracts і додає один
найменший vertical slice. Інші candidates не деталізуються. Попередній approval стає stale, після
чого потрібно:

```text
/kapelle:start <slug> --approve
```

Важкий revision lifecycle створюється лише після PASS verification, для high-risk зміни або на
пряме прохання.

## 4. `/kapelle:verify <slug>`

Коли всі погоджені slices реалізовані і нових вимог поки не потрібно:

```text
/kapelle:verify <slug> --validation=ask
```

### Що задати

- validation policy `ask|allow|skip`;
- за бажанням — додаткові manual checks або конкретну команду проєкту.

### Що відбувається

Сам виклик `verify` означає, що developer вважає поточний накопичений scope достатнім. Плагін
звіряє код зі spec/design, планує й пише всі unit-тести, формує один
risk-based batch із applicable functional, unit, integration/contract, static-analysis, lint і
build checks. Неактуальні категорії пропускаються з коротким поясненням.

Failed required check дає `FAILED`. Skipped/cancelled required check дає `validation-deferred`.
Жоден із цих станів не може бути PASS.

### Результат

- узгоджені `spec.md` і `design.md`;
- написані unit-тести;
- один `_kapelle/verification.json`;
- короткий звіт тестів, ризиків і manual checks;
- команда фінального підтвердження.

Після PASS і ручного рев’ю:

```text
/kapelle:verify <slug> --approve
```

Ця команда лише створює final approval. Діаграми, release JSON, version number, commit або push не є
обов’язковими для завершення Kapelle.

## 5. `/kapelle:status <slug>`

### Що задати

Лише slug:

```text
/kapelle:status <slug>
```

### Результат

Оновлений `STATUS.md`: progress по workstream, blockers/deferred validation, файли для рев’ю й одна
точна наступна команда. Якщо `_kapelle/` видалено, state відновлюється без вигадування approvals чи
PASS evidence.

## 6. `/kapelle:migrate <slug>`

Для feature directory зі старим workflow:

```text
/kapelle:migrate <slug>
/kapelle:migrate <slug> --apply
```

Перший виклик — dry-run. Другий додає lightweight marker і routing, зберігаючи старі документи та
history. Старі команди `spec`, `design`, `plan`, `base-functional-tests`, `unit-tests`, `finalize`
лише показують нову команду й нічого не виконують.

## 7. `/kapelle:reconstruct <slug>`

Для документації функціоналу, який уже реалізований:

```text
/kapelle:reconstruct <slug> "<частина існуючого функціоналу>"
```

Це окремий documentation-only процес. Він не переходить до planning, implementation, tests або
completion.
