# Архівний план рефакторингу артефактів Kapelle

## 1. Мета

Головна ціль рефакторингу — зробити SDLC-процес Kapelle зрозумілим і легко контрольованим для
користувача, не втрачаючи надійність machine-readable state, архітектурні правила, task graph,
validation evidence та change lifecycle.

Після рефакторингу:

- користувач читає невелику кількість простих Markdown-артефактів;
- усі файли, призначені лише для LLM і runtime Kapelle, знаходяться в одній службовій папці
  `_kapelle/`;
- `_kapelle/` можна видалити без втрати можливості продовжити роботу над фічею;
- Kapelle може відновити внутрішній стан із людських артефактів, ADR, контрактів, поточного коду,
  тестів і проєктних архітектурних правил;
- після recovery плагін не вигадує втрачені approvals, review verdicts або результати validation.

## 2. Основний принцип

Kapelle розділяє артефакти на два класи.

### 2.1. Людські артефакти

Це канонічний опис фічі та її поточного плану:

- `STATUS.md`;
- `proposal.md`;
- `spec.md`;
- `design.md`;
- `tasks.md`;
- `test-plan.md`;
- `contracts/*.md`;
- `adr/*.md`.

Вони мають бути:

- короткими;
- структурованими;
- придатними для code review;
- зрозумілими без знання внутрішньої реалізації Kapelle;
- достатніми для відновлення execution state.

### 2.2. Внутрішні артефакти Kapelle

Усі machine-readable, LLM-only, audit і telemetry файли зберігаються під `_kapelle/`.

Вони забезпечують:

- швидке продовження роботи;
- точні fingerprints;
- task dependency graph;
- scoped architecture guidance;
- execution plans;
- validation decisions;
- review evidence;
- immutable change history;
- telemetry.

Видалення `_kapelle/` може призвести до втрати історичного evidence, але не повинно блокувати
продовження роботи над фічею.

## 3. OpenSpec-подібна модель

Kapelle не копіює OpenSpec буквально, але використовує той самий зрозумілий для користувача потік:

```text
proposal -> spec -> design -> tasks -> implement -> validate -> review
```

Відмінність Kapelle полягає в сильнішому execution harness:

- проєктні architecture rules;
- backend/frontend/data coordination;
- deterministic task validation;
- adaptive agent orchestration;
- requirement-change lifecycle;
- validation policy;
- recovery з поточного коду.

Орієнтири:

- https://openspec.dev/docs/overview
- https://github.com/Fission-AI/OpenSpec

## 4. Цільова структура фічі

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md
  design.md
  tasks.md
  test-plan.md

  contracts/
    <contract>.md

  adr/
    0001-<decision>.md

  _kapelle/
    manifest.json
    state.json
    size.json
    surface-plan.json
    task-plan.json

    changes/
      <change-id>/
        state.json
        revisions/
        reconciliation.json

    architecture-guidance/
      design.json
      tasks.json

    task-runs/
      <task-id>.json

    validation/
      <task-id>.json
      feature.json

    reviews/
      <review-id>.json

    telemetry/
      execution.jsonl

    history/
```

У корені фічі не повинно бути JSON, JSONL, fingerprint sidecars, agent plans або runtime logs.

## 5. Людські артефакти

### 5.1. `STATUS.md`

`STATUS.md` — головна точка входу до фічі.

Користувач повинен за 20–30 секунд зрозуміти:

- що реалізується;
- яка зміна або ревізія активна;
- на якій стадії знаходиться процес;
- що завершено;
- які є blockers;
- які validation checks відкладені;
- чи можна робити feature review або ship;
- яку команду виконувати наступною.

Приклад:

```md
# Dealer Stock Invoice Option

Status: Validation deferred
Active change: real-invoice-preparation, revision r001
Current stage: implementation
Progress: 16/22 tasks completed
Ready to ship: No

## Scope

Replace preview-only invoice data with real backend preparation.

## Current blockers

- Real database integration validation is unavailable.
- Container lint is blocked by unrelated repository errors.
- Manual CRM validation is pending.

## Workstreams

| Workstream | Status | Progress |
|---|---|---:|
| Contracts | Done | 5/5 |
| Backend preparation | Done | 6/6 |
| RPC integration | Validation deferred | 2/3 |
| Frontend integration | Validation deferred | 3/5 |

## Review now

- proposal.md
- spec.md
- design.md
- tasks.md
- test-plan.md

## Next action

/kapelle:implement dealer-stock-invoice-option --validation=allow
```

`STATUS.md` є generated projection. Він не є незалежним source of truth і повинен детерміновано
перебудовуватися з людських документів та `_kapelle/state.json`.

### 5.2. `proposal.md`

Описує:

- проблему;
- мету;
- очікуваний результат;
- scope;
- non-goals;
- вплив на користувача;
- очікуваний системний impact;
- основні ризики;
- unresolved product decisions.

Документ відповідає на питання: «Навіщо і що саме змінюємо?»

### 5.3. `spec.md`

Описує observable behavior:

- actors;
- requirements;
- acceptance criteria;
- scenarios;
- edge cases;
- constraints;
- security expectations;
- compatibility expectations.

`spec.md` не повинен містити:

- agent routing;
- stage handoff;
- fingerprints;
- runtime state;
- telemetry;
- назви внутрішніх schemas;
- implementation logs.

### 5.4. `design.md`

`design.md` замінює `sad.md` і для більшості фіч поглинає корисну частину `sequences.md`.

Містить:

- affected modules and surfaces;
- backend/frontend/data boundaries;
- runtime flows;
- integration points;
- architecture rules;
- contract ownership;
- error handling;
- security boundaries;
- important alternatives;
- links to ADR and contracts.

Окремий `sequences.md` створюється лише для великих або справді складних runtime flows.

### 5.5. `tasks.md`

Це людське представлення реалізації:

```md
## Backend preparation

- [x] T01 Implement scoped invoice source
- [x] T02 Implement row classification
- [ ] T03 Expose authorized prepare action
  - Blocked by: container validation
  - Covers: AC-04, AC-05, AC-25

## Frontend integration

- [x] T04 Replace mock preparation
- [ ] T05 Validate popup lifecycle
  - Status: validation pending
```

Для кожної задачі користувачу достатньо бачити:

- id;
- outcome;
- workstream;
- dependency, якщо вона суттєва;
- status;
- covered acceptance criteria;
- blocker;
- validation state.

Детальні `files_hint`, provider/consumer topology, architecture-guidance paths та schema fields
зберігаються в `_kapelle/task-plan.json`.

### 5.6. `test-plan.md`

Містить:

- загальну test strategy;
- acceptance-criteria coverage;
- contract та integration coverage;
- required automated commands;
- optional commands;
- manual runtime checks;
- explicit skips і deferrals.

Фактичні результати окремих запусків зберігаються в `_kapelle/validation/`.

### 5.7. `contracts/`

Містить лише контракти, корисні для розробника:

- request/response shape;
- application boundary;
- public interface;
- frontend/backend handoff;
- event or message contract;
- compatibility rules.

Internal sync reports і contract validation metadata зберігаються в `_kapelle/`.

### 5.8. `adr/`

ADR залишається людським артефактом і джерелом архітектурних рішень.

ADR повинен містити:

- context;
- decision;
- alternatives;
- consequences;
- status;
- supersession links.

## 6. Внутрішня папка `_kapelle/`

### 6.1. `manifest.json`

Містить:

- layout version;
- plugin schema version;
- feature slug;
- paths до людських документів;
- fingerprints;
- recovery metadata;
- останній успішний state build.

### 6.2. `state.json`

Містить агрегований runtime state:

- current stage;
- active change;
- current revision;
- task counts;
- blockers;
- deferred validation;
- review readiness;
- ship readiness;
- next command.

### 6.3. `surface-plan.json`

Залишається machine-readable coordination model:

- aspects;
- modules;
- dependencies;
- contracts;
- integration checks.

### 6.4. `task-plan.json`

Містить повний execution graph:

- workstreams;
- tasks;
- dependencies;
- acceptance-criteria coverage;
- contract providers and consumers;
- integration-check ownership;
- risk;
- file ownership;
- validation requirements.

### 6.5. `task-runs/<task-id>.json`

Об'єднує поточні окремі файли:

```json
{
  "task": {},
  "architecture_guidance": {},
  "strategy": {},
  "plan": {},
  "approval": {},
  "implementation": {},
  "review": {},
  "validation": {}
}
```

Telemetry залишається окремим append-only JSONL.

## 7. Recovery invariant

Нова обов'язкова гарантія:

> Видалення `_kapelle/` не повинно унеможливлювати продовження роботи над фічею.

Для відновлення повинно бути достатньо:

```text
proposal.md
spec.md
design.md
tasks.md
test-plan.md
contracts/
adr/
поточного коду і тестів проєкту
проєктних архітектурних правил
```

Kapelle може відновити:

- scope;
- acceptance criteria;
- architecture surfaces;
- contract topology;
- workstreams;
- task graph;
- імовірний implementation progress;
- validation requirements;
- minimal next route.

Kapelle не може достовірно відновити після видалення:

- попередні explicit approvals;
- старі agent verdicts;
- token і cost telemetry;
- історичні command outputs;
- validation evidence, якого немає в проєкті або CI.

Плагін не повинен вигадувати це evidence.

## 8. Recovery flow

Recovery автоматично запускається через:

```text
/kapelle:status <slug>
```

або перед будь-якою feature stage, якщо `_kapelle/manifest.json` відсутній або пошкоджений.

```text
DETECT
  -> READ HUMAN ARTIFACTS
  -> INSPECT CURRENT CODE AND TESTS
  -> LOAD PROJECT ARCHITECTURE RULES
  -> REBUILD MACHINE STATE
  -> RECONCILE DOCS AND CODE
  -> REPORT GAPS
  -> SELECT MINIMAL NEXT STAGE
```

### 8.1. Detect

Kapelle перевіряє:

- наявність `_kapelle/`;
- валідність `manifest.json`;
- layout version;
- fingerprints людських документів;
- частково видалений internal state.

### 8.2. Read human artifacts

Kapelle відновлює:

- scope із `proposal.md`;
- requirements і AC зі `spec.md`;
- aspects та boundaries із `design.md`;
- tasks і progress із `tasks.md`;
- contracts із `contracts/`;
- decisions із `adr/`;
- validation expectations із `test-plan.md`.

### 8.3. Inspect current project state

Explorer аналізує:

- поточну реалізацію;
- релевантні модулі;
- frontend/backend/data surfaces;
- тести;
- конфігурацію;
- фактичні contracts;
- repository precedents.

Потім семантично знайдений project architecture-rules subagent повертає правила для конкретних
компонентів.

### 8.4. Rebuild machine state

Kapelle генерує:

```text
_kapelle/manifest.json
_kapelle/state.json
_kapelle/surface-plan.json
_kapelle/task-plan.json
_kapelle/architecture-guidance/recovery.json
_kapelle/recovery.json
```

### 8.5. Reconcile docs and code

Кожна задача отримує recovery disposition:

```text
not-started
implemented-unverified
validated
needs-rework
superseded
unknown
```

Правила:

- `[x]` у `tasks.md` означає, що задача заявлена як виконана;
- після втрати `_kapelle` вона стає `implemented-unverified`;
- `validated` повертається лише після повторного validation або надійного project/CI evidence;
- відсутність evidence не повинна автоматично запускати повторне редагування коду.

### 8.6. Select minimal route

Kapelle не повторює весь SDLC без необхідності:

- є лише proposal і spec — продовжити з design;
- є design, але немає tasks — виконати decompose;
- є tasks і частина коду — reconcile та implement залишок;
- код виглядає завершеним — validation та feature-review;
- requirements не відповідають коду — показати drift і запропонувати change;
- немає validation evidence — запропонувати validation без повторної implementation.

## 9. Recovery statuses

До vocabulary потрібно додати feature states:

```text
recovered
recovered-with-gaps
external-development
externally-implemented-unverified
```

Та task state:

```text
implemented-unverified
```

Приклад:

```md
Status: Recovered with gaps
Ready to ship: No

Kapelle internal state was rebuilt from feature documents and current code.

## Recovered

- 18 requirements
- 12 tasks
- 6 contracts
- 2 ADRs
- backend and frontend implementation paths

## Evidence unavailable

- Previous task approvals
- Agent review results
- Three validation command results

## Reconciliation

- 8 tasks appear implemented but require validation
- 2 tasks remain incomplete
- 2 tasks require clarification

## Next

/kapelle:implement dealer-stock-invoice-option --validation=ask
```

## 10. Оновлений artifact invariant

Поточний принцип `Artifact is state` потрібно уточнити:

> Human-readable feature artifacts are durable state. `_kapelle/` contains derived execution state,
> evidence and acceleration data and may be rebuilt.

Не все в `_kapelle/` є звичайним кешем:

- task graph можна відновити;
- surface plan можна відновити;
- architecture guidance можна отримати повторно;
- approvals, telemetry та історичні validation results після видалення втрачаються.

Втрата історичного evidence знижує certainty, але не блокує продовження роботи.

## 11. Мапінг поточних артефактів

| Поточний артефакт | Цільовий артефакт |
|---|---|
| `.size` | `_kapelle/size.json` |
| `sad.md` | `design.md` |
| `sequences.md` | секція в `design.md` або optional `sequences.md` |
| `surface-plan.json` | `_kapelle/surface-plan.json` |
| `tasks.json` | `_kapelle/task-plan.json` |
| `_audit/plans/*` | `_kapelle/task-runs/<task-id>.json` |
| `_audit/architecture-guidance/*` | `_kapelle/architecture-guidance/*` |
| `_audit/test-strategies/*` | `_kapelle/task-runs/<task-id>.json` |
| `_audit/validation-decisions/*` | `_kapelle/validation/<task-id>.json` |
| `_audit/implementation.jsonl` | `_kapelle/task-runs/*` |
| `_audit/implementation-telemetry.jsonl` | `_kapelle/telemetry/execution.jsonl` |
| `_review/*` | `_kapelle/reviews/*` плюс human summary у `STATUS.md` |
| `changes/*/active-state.json` | `_kapelle/changes/<id>/state.json` |
| artifact-state sidecars | `_kapelle/changes/<id>/artifacts/` |
| reconciliation JSON | `_kapelle/changes/<id>/reconciliation.json` |
| `ship.md` | readiness/release section у `STATUS.md` або human `release.md` після завершення |

Людські `change.md`, amendments і важливі рішення потрібно перенести в `proposal.md`, `spec.md`,
`design.md` або ADR до видалення старої структури.

## 12. Presentation contract

Потрібно додати:

```text
references/feature-layout.md
references/artifact-presentation.md
```

Для кожного людського документа першими повинні бути:

1. короткий summary;
2. scope;
3. ключові рішення;
4. unresolved питання;
5. посилання на деталі.

Орієнтовні межі:

- `STATUS.md` — до 100 рядків;
- `proposal.md` — до 150 рядків;
- `spec.md` — приблизно 150–250 рядків для M/L;
- `design.md` — приблизно 150–250 рядків;
- `tasks.md` — компактні workstreams і checklist;
- `test-plan.md` — strategy, coverage summary і команди.

Це не жорсткі line limits. Значне перевищення повинно змушувати агента винести деталі в contract,
ADR або `_kapelle/`.

Stage handoff не записується всередину людських артефактів.

## 13. Спрощення decomposition

Canonical tasks мають означати одиниці реалізації або незалежної cross-aspect validation.

Правила:

- створення контрактного документа не стає implementation task автоматично;
- contract freeze представляється gate усередині workstream;
- workstream відповідає завершеному технічному результату;
- не створювати окремий workstream для кожної пари задач;
- validation task потрібна лише для окремої значущої integration перевірки;
- task title описує результат, а не процес.

Для M-фічі орієнтир:

- 3–7 workstreams;
- 7–15 задач.

Перевищення є сигналом переглянути size, task boundaries або можливість поділу scope. Це не жорстке
обмеження і не може послаблювати architecture, AC coverage чи validation.

## 14. Feature-level consistency validation

Потрібно додати:

```text
scripts/build_feature_status.py
scripts/rebuild_feature_state.py
scripts/validate_feature_state.py
dispatcher/feature-manifest.schema.json
dispatcher/feature-state.schema.json
dispatcher/recovery-report.schema.json
```

Validator повинен знаходити:

- active change та одночасно current `SHIPPABLE`;
- review або ship для старої revision;
- completed task із required deferred validation;
- stale task plan;
- невідповідність `STATUS.md` внутрішньому state;
- historical scope, представлений як current;
- manual drift у generated `STATUS.md`;
- manual drift у generated sections `tasks.md`;
- відсутній або неправильний next action;
- неправдиве відновлення validation evidence.

## 15. Нова команда `/kapelle:status`

Потрібно додати:

```text
skills/status/SKILL.md
```

Команда:

1. читає людські артефакти;
2. перевіряє `_kapelle/`;
3. запускає recovery за потреби;
4. оновлює `STATUS.md`;
5. показує короткий статус у чаті;
6. визначає мінімальну наступну команду;
7. не запускає git operations;
8. не запускає validation commands без відповідної політики;
9. не виконує implementation edits.

## 16. Етапи реалізації

### Етап 1 — Layout і presentation contract

- Додати `references/feature-layout.md`.
- Додати `references/artifact-presentation.md`.
- Описати human/internal artifact classes.
- Оновити `AGENTS.md` і `CLAUDE.md`.
- Заборонити handoff і runtime metadata в людських документах.

### Етап 2 — Human-readable artifacts

- Додати `proposal.md`.
- Перейменувати `sad.md` у `design.md`.
- Додати `tasks.md`.
- Додати `STATUS.md`.
- Спростити `test-plan.md`.
- Зробити `sequences.md` optional.

### Етап 3 — `_kapelle/`

- Додати internal manifest.
- Перенести machine-readable state.
- Об'єднати per-task evidence.
- Оновити logical artifact paths і dependency graph.

### Етап 4 — Status engine

- Реалізувати deterministic status builder.
- Додати `/kapelle:status`.
- Автоматично оновлювати status після кожної backbone stage.

### Етап 5 — Recovery engine

- Виявляти відсутній або пошкоджений `_kapelle/`.
- Читати людські документи.
- Аналізувати поточний код і тести.
- Знаходити project capabilities та architecture-rules subagent.
- Перебудовувати machine state.
- Формувати recovery dispositions.
- Визначати minimal next route.

### Етап 6 — Lifecycle consistency

- Розширити граф: `validation -> feature-review -> ship`.
- Прив'язати review і ship до revision/fingerprints.
- Додати external-development/recovery states.
- Не вимагати повного повторного pipeline після recovery.

### Етап 7 — Migration

Додати:

```text
scripts/migrate_feature_layout.py <feature-dir> --dry-run
scripts/migrate_feature_layout.py <feature-dir> --apply
```

Migration повинна:

- створити `proposal.md`;
- перетворити `sad.md` у `design.md`;
- сформувати `tasks.md`;
- перемістити internal state у `_kapelle/`;
- зберегти requirements, contracts, ADR та історичний evidence;
- показати неоднозначності до запису;
- бути idempotent;
- не виконувати git operations.

### Етап 8 — Documentation, validation і reinstall

- Оновити `README.md`.
- Оновити `docs/USAGE.md`.
- Оновити `docs/COMMAND_EXECUTION_UK.md`.
- Додати legacy та recovery fixtures.
- Запустити plugin validation і unit tests.
- Оновити plugin cachebuster стандартним helper.
- Перевстановити локальний плагін.
- Перевірити його в новій Codex-задачі.

## 17. Рекомендована послідовність комітів

1. `refactor: define human and internal feature artifact layout`
2. `feat: add deterministic feature status model`
3. `feat: add kapelle status command`
4. `refactor: produce readable proposal design and tasks artifacts`
5. `refactor: consolidate internal state under _kapelle`
6. `feat: rebuild feature state from documents and current code`
7. `refactor: simplify decomposition and task evidence`
8. `fix: track review and ship freshness across revisions`
9. `feat: migrate legacy feature layouts`
10. `docs: document readable artifacts and recovery workflow`

## 18. Documentation convergence gate

Kapelle повинен завершувати фічу двома різними, але узгодженими специфікаціями:

- продуктовою специфікацією для product/project manager і QA;
- технічною специфікацією для розробника.

Фіча не може отримати фінальний review або ship readiness, доки обидва документи не описують
фактичну реалізацію, а не лише початковий план.

### 18.1. `spec.md` — продуктова специфікація

Основна аудиторія:

- product manager;
- project manager;
- business analyst;
- QA;
- developer, якому потрібно зрозуміти очікувану поведінку.

Документ повинен містити:

- проблему і продуктову ціль;
- користувачів, actors і permissions;
- основні user flows;
- функціональні вимоги;
- acceptance criteria;
- business rules;
- edge cases;
- error outcomes, видимі користувачу;
- non-goals;
- constraints;
- compatibility expectations;
- явно відкладені можливості.

Документ не повинен вимагати від PM знання:

- назв класів і сервісів;
- файлових шляхів;
- framework internals;
- dependency graph;
- agent/runtime metadata;
- fingerprints;
- implementation telemetry.

Product/project manager повинен мати можливість прочитати `proposal.md` і `spec.md` та зрозуміти:

- навіщо створена фіча;
- що саме вона робить;
- що вона навмисно не робить;
- як перевірити очікуваний результат;
- які частини залишені для наступних змін.

### 18.2. `design.md` — технічна специфікація

Основна аудиторія:

- developer;
- tech lead;
- architect;
- reviewer;
- developer, який буде змінювати або підтримувати фічу пізніше.

Документ повинен містити:

- system context;
- affected components і modules;
- backend/frontend/data responsibilities;
- component boundaries;
- основні runtime flows;
- API, RPC, event та application contracts;
- data model;
- migrations або явний `no schema change`;
- authorization і access boundaries;
- error handling;
- concurrency, ordering та idempotency, якщо вони актуальні;
- observability;
- backward compatibility;
- deployment або rollout considerations, якщо вони актуальні;
- ключові implementation decisions;
- посилання на ADR;
- testing і validation approach;
- відомі технічні обмеження;
- відхилення фінальної реалізації від початкового design.

Розробник повинен мати можливість відкрити:

```text
design.md
contracts/
adr/
```

і зрозуміти архітектуру фічі без повторного дослідження всього репозиторію.

### 18.3. As-built requirement

Перед `feature-review` Kapelle повинен виконати фінальну синхронізацію:

```text
proposal <-> final scope
spec <-> observable implementation
design <-> technical implementation
contracts <-> providers and consumers
tasks <-> implemented work
test-plan <-> acceptance criteria and validation
ADR <-> actual architectural decisions
```

Якщо знайдено розбіжність:

- документація оновлюється, якщо код відповідає погодженим вимогам;
- implementation повертається на reconciliation, якщо код не відповідає spec;
- requirement change проходить change lifecycle, якщо поведінка була свідомо змінена;
- нове архітектурне рішення оформлюється або оновлюється в ADR;
- відкладена функціональність переноситься в explicit deferred scope або non-goals;
- contract drift блокує feature review до узгодження.

Kapelle не повинен автоматично переписувати product requirements під випадкову поточну поведінку
коду. Будь-яка зміна observable behavior потребує явного reconciliation і, коли необхідно,
підтвердження користувача.

### 18.4. Convergence verdict

Перед feature review потрібно сформувати machine-readable verdict:

```text
_kapelle/reviews/documentation-convergence.json
```

Verdict повинен містити:

- revision;
- fingerprints;
- перевірені human artifacts;
- знайдені implementation paths;
- requirement mismatches;
- design mismatches;
- contract mismatches;
- undocumented decisions;
- unresolved deferrals;
- status: `PASS | CHANGES_REQUIRED | BLOCKED`.

Короткий результат показується в `STATUS.md`:

```md
## Documentation readiness

- Product specification: Current
- Technical specification: Current
- Contracts: Current
- ADR: Current
- As-built convergence: PASS
```

### 18.5. Final human-readable feature package

Після завершення фічі користувач отримує:

```text
proposal.md      # навіщо створили фічу
spec.md          # що фактично робить фіча — для PM і QA
design.md        # як фактично побудована фіча — для developer
contracts/       # точні технічні межі
adr/             # причини важливих рішень
tasks.md         # що було реалізовано
test-plan.md     # як результат перевірено
STATUS.md        # фінальний стан і readiness
```

Ці документи повинні залишатися придатними як довготривала документація фічі після видалення
`_kapelle/`.

### 18.6. Ship gate

`/kapelle:ship` повинен відмовити, якщо:

- `spec.md` не відповідає observable behavior;
- `design.md` не відповідає фактичній архітектурі;
- contract provider або consumer не відповідає `contracts/`;
- реалізоване важливе архітектурне рішення не відображене в ADR;
- documentation convergence verdict відсутній, stale або не має `PASS`;
- required validation залишається deferred;
- human artifacts посилаються на superseded scope як на current.

Успішний ship означає:

> `spec.md` і `design.md` є актуальною продуктовою та технічною документацією фактично реалізованої
> фічі.

## 19. Критерії готовності

Рефакторинг завершено, якщо:

- користувач розуміє стан фічі, відкривши лише `STATUS.md`;
- для нормального review достатньо максимум шести людських документів;
- `_kapelle/` не потрібно читати під час звичайної роботи;
- у корені фічі немає LLM-only JSON, JSONL, telemetry або sidecars;
- `tasks.md` відповідає `_kapelle/task-plan.json`;
- зміна requirements одразу відображається в status;
- current та historical revisions не можуть одночасно виглядати актуальними;
- роботу поза Kapelle можна позначити та пізніше reconciliate;
- видалення `_kapelle/` не блокує продовження;
- recovery не вигадує approvals або validation results;
- recovery визначає мінімальну наступну stage;
- `spec.md` придатний для product/project manager і QA;
- `design.md` придатний для developer, tech lead та architect;
- documentation convergence перевіряє обидві специфікації проти фактичної реалізації;
- feature review і ship блокуються без актуального convergence verdict;
- architecture-rule coverage зберігається;
- backend/frontend/data coordination не послаблюється;
- acceptance-criteria coverage залишається детерміновано перевірюваним;
- schema validation, task-plan validation та feature-state validation проходять;
- існуючі plugin checks і task-validator tests залишаються зеленими.

## 20. Обов'язковий recovery integration test

1. Пройти фічу до середини implementation.
2. Зберегти людські артефакти та поточний код.
3. Видалити `_kapelle/`.
4. Запустити `/kapelle:status <slug>`.
5. Перевірити, що плагін:
   - відновив scope;
   - відновив acceptance criteria;
   - відновив architecture surfaces;
   - відновив contracts;
   - відновив task graph;
   - знайшов реалізований код;
   - позначив виконане без evidence як `implemented-unverified`;
   - не вигадав validation evidence;
   - визначив мінімальний наступний крок;
   - не вимагає повторювати specify/design/decompose без потреби.
6. Запустити необхідну validation.
7. Перевірити, що після успішної validation відповідні задачі отримали підтверджений status.

## 21. Перший рекомендований інкремент

Перший інкремент повинен включати:

1. feature layout contract;
2. `STATUS.md`;
3. `_kapelle/manifest.json`;
4. `_kapelle/state.json`;
5. `/kapelle:status`;
6. recovery з людських документів;
7. feature-state validator;
8. review/ship freshness.

Цей інкремент дасть найбільше покращення зрозумілості та recovery, ще не вимагаючи негайної
перебудови всього decomposition й implementation dispatcher.
