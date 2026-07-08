# Детальний порядок виконання команд Kapelle

Цей документ пояснює:

- у якому порядку запускати команди;
- що користувач передає на вході;
- які файли Kapelle читає;
- що відбувається всередині stage;
- які рішення може знадобитися підтвердити;
- які артефакти з’являються після завершення;
- яку команду запускати наступною.

## 1. Загальна модель використання

Kapelle працює поетапно. Кожна команда є окремим gated stage:

```text
survey → specify → clarify → design → sequences → data-model
       → contracts → decompose → plan-tests → implement → feature-review → ship
```

Після кожного stage:

1. Перегляньте створений артефакт.
2. Перевірте відкриті питання, припущення та explicit skips.
3. Виконайте `/clear`.
4. Запустіть точну наступну команду з handoff.

Виняток: якщо stage явно говорить не очищати контекст для короткого review/fix loop.

Kapelle отримує вхідні дані з чотирьох джерел:

| Джерело | Приклад |
|---|---|
| Аргументи команди | `<slug>`, `--mode`, `--change`, `--revise` |
| Поточне повідомлення користувача | опис фічі, expected behavior, обмеження |
| Артефакти на диску | `spec.md`, `sad.md`, `tasks.json` |
| Native project capabilities | project skills, subagents, rules, validation commands |

Conversation history не є durable state. Після `/clear` наступний stage відновлює контекст із файлів.

## 2. Як обрати початковий сценарій

### Нова фіча або нова поведінка в існуючому коді

Якщо `docs/features/<slug>/` ще не містить канонічних Kapelle-артефактів:

```text
/kapelle:survey <slug>
/clear
/kapelle:specify <slug> ["<feature idea>"]
```

Далі проходьте backbone stages за handoff.

Наявність старого application code не означає, що потрібно використовувати `change`. `change`
використовується, коли існує попередньо описана Kapelle-фіча.

### Зміна вже описаної фічі

Якщо існують `docs/features/<slug>/spec.md`, design і task artifacts:

```text
/kapelle:change <slug> --mode=enhancement "<опис>"
```

Для bugfix або refactor оберіть відповідний mode.

### Зміна вимог під час активної реалізації

```text
/kapelle:change <slug> --change=<change-id> --revise "<нова вимога>"
```

Не редагуйте старий implementation plan і не продовжуйте реалізацію вручну.

---

# Backbone нової фічі

## 3. `/kapelle:survey`

Команда має три режими.

### 3.1 Bootstrap shared baseline

```text
/kapelle:survey
```

### Що задати на вході

Нічого, крім команди. Запускайте поза feature worktree, бажано на integration branch.

### Що команда читає

- структуру репозиторію;
- project instructions;
- native project skills і subagents;
- test/build manifests;
- наявний `docs/architecture-map.md`.

### Що відбувається

Якщо baseline відсутній, `kapelle:explorer` досліджує:

- stack;
- module boundaries;
- wiring;
- persistence;
- test і validation commands;
- representative implementation patterns;
- project capabilities;
- наявність project architecture-rules subagent.

Якщо `docs/architecture-map.md` уже існує, команда не порівнює HEAD для автоматичного refresh і
повертає `BASELINE-READY`.

`reflects_commit` є provenance, а не freshness gate.

### Що отримуємо

При першому bootstrap:

```text
docs/architecture-map.md
```

Якщо baseline вже існує — жодного запису.

### Важливо

Feature branch divergence не дозволяє переписувати shared map.

### Наступна команда

```text
/kapelle:specify <slug>
```

Але для feature worktree краще спочатку виконати feature-scoped survey.

### 3.2 Feature-scoped survey

```text
/kapelle:survey <slug>
```

### Що задати на вході

- стабільний kebab-case slug;
- у поточному повідомленні або попередньому контексті — короткий опис фічі та ймовірно affected
  area.

Приклад:

```text
/kapelle:survey configurable-invoice-status-in-pipe

Фіча дозволяє конфігурувати статус invoice, який використовується у processing pipe.
```

### Що відбувається

- shared `architecture-map.md` читається як baseline;
- explorer перевіряє тільки current-branch scope, релевантний фічі;
- знаходяться affected modules, aspects, entrypoints і current precedents;
- перевіряється наявність project architecture-rules subagent;
- глобальна карта не створюється і не змінюється.

### Що отримуємо

```text
docs/features/<slug>/_context/architecture.md
```

### Важливо

Якщо shared baseline відсутній, feature-scoped survey все одно пише лише feature-local overlay.

### Наступна команда

```text
/clear
/kapelle:specify <slug>
```

### 3.3 Explicit baseline refresh

```text
/kapelle:survey --refresh-baseline
```

### Що задати на вході

- explicit maintenance intent;
- після аналізу — підтвердження запропонованих змін.

### Що відбувається

- Kapelle показує секції baseline, які потребують оновлення;
- очікує explicit approval;
- тільки після approval запускає повний refresh.

Не комбінуйте `--refresh-baseline` зі slug.

### Що отримуємо

Оновлений:

```text
docs/architecture-map.md
```

---

## 4. `/kapelle:specify <slug>`

```text
/kapelle:specify configurable-invoice-status-in-pipe \
  "Allow the invoice status used in the processing pipe to be configured while preserving the current default"
```

### Що задати на вході

Опишіть продуктову поведінку, не реалізацію:

- проблему;
- користувача або caller;
- expected outcome;
- success criteria;
- відомі обмеження;
- що точно не входить у scope.

Мінімально обов’язкові дані:

- authoritative slug/ticket;
- чи це нова specification або formalization відомої in-flight роботи, якщо це неоднозначно;
- problem і desired observable outcome.

Приклад input:

```text
Потрібно дозволити конфігурувати invoice status, який pipe встановлює після успішної обробки.
Поточний status повинен залишитися default для backward compatibility.
Не змінювати поведінку інших invoice transitions.
```

### Що команда читає

- спочатку лише факт існування feature directory та feature-local context;
- branch/ticket metadata, тільки якщо host або feature context уже її надав;
- feature idea з команди або поточного повідомлення;
- `docs/features/<slug>/_context/architecture.md`, якщо є;
- `docs/architecture-map.md`, якщо є;
- project context, необхідний для перевірки constraints.

### Що відбувається

- до повного input заборонені source search, commit inspection, git/shell discovery, читання
  unrelated specs як templates і запуск subagents;
- якщо ticket, scope та idea не визначені, агент запитує всі unresolved fields одним consolidated
  prompt, а не послідовним wizard;
- до узгодження authoritative slug feature directory не створюється;
- при зміні slug використовується тільки corrected slug;
- визначаються goals і non-goals;
- фіксуються actors і user stories;
- створюються measurable acceptance criteria;
- додаються NFR та open questions;
- визначається `.size` і execution depth;
- для standard/full depth може запускатися devil’s advocate;
- critic запускається лише для full depth або реального конфлікту з repository constraints.

На цьому stage не визначаються конкретні project skills або implementation routing.
Broad code mapping і implementation archaeology залишаються для `survey` та `design`.

### Що отримуємо

```text
docs/features/<slug>/spec.md
docs/features/<slug>/.size
```

### Що перевірити

- expected behavior сформульовано спостережувано;
- default/backward-compatible behavior зафіксовано;
- кожен важливий branch має acceptance criterion;
- implementation details не підміняють requirements;
- open questions мають owner або explicit deferral.

### Наступна команда

```text
/clear
/kapelle:clarify <slug>
```

---

## 5. `/kapelle:clarify <slug>`

```text
/kapelle:clarify configurable-invoice-status-in-pipe
```

### Що задати на вході

Зазвичай достатньо slug. Якщо після `specify` ви вже знаєте відповіді на open questions, додайте їх
у повідомленні.

### Що команда читає

```text
docs/features/<slug>/spec.md
```

### Що відбувається

- шукаються тільки unresolved або нові ambiguity;
- перевіряються vague terms, missing actors, NFR, conflicts і edge cases;
- на lean depth аналіз виконується inline;
- на standard/full depth subagent запускається лише для невирішених branches;
- уже закриті findings не аналізуються повторно.

Агент може поставити короткі уточнювальні питання. Якщо відповідь змінює observable behavior,
оновлюється spec.

### Що отримуємо

Оновлений:

```text
docs/features/<slug>/spec.md
```

### Що перевірити

- немає blocking ambiguity;
- deferred питання не впливають на поточний implementation route;
- acceptance criteria не суперечать одне одному.

### Наступна команда

```text
/clear
/kapelle:design <slug>
```

---

## 6. `/kapelle:design <slug>`

```text
/kapelle:design configurable-invoice-status-in-pipe
```

### Що задати на вході

Зазвичай slug. Додайте тільки constraints, які ще не записані у spec або project rules:

- deployment limitation;
- compatibility requirement;
- заборонений dependency;
- approved external contract.

Не вказуйте вручну project skill або subagent, якщо це не explicit project requirement.

### Що команда читає

- `spec.md`;
- optional `CONTEXT.md`;
- feature-local architecture overlay;
- shared architecture baseline;
- project skill/subagent descriptions.

### Що відбувається

1. Визначаються tentative aspects, modules, entrypoints і paths.
2. Семантично знаходиться project architecture-rules subagent.
3. Subagent повертає scoped architecture rules.
4. Результат перевіряється за `architecture-guidance.schema.json`.
5. При missing capability або blocking gaps stage відмовляється.
6. Project subagent може знайти додаткові вузькі project skills/subagents.
7. Створюється architecture design.
8. Будується aspect dependency graph.
9. Для ризикового або складного design запускається independent critic.

### Що отримуємо

```text
docs/features/<slug>/sad.md
docs/features/<slug>/surface-plan.json
docs/features/<slug>/adr/*.md
docs/features/<slug>/_audit/architecture-guidance/design.json
```

`surface-plan.json` описує:

- backend/frontend/database/інші project-defined aspects;
- dependencies;
- entrypoints;
- provider/consumer contracts;
- cross-aspect integration checks.

Він не містить mapping на skills або agents.

### Що може вимагати втручання

- відсутній architecture-rules subagent;
- правила суперечать запропонованому design;
- кілька materially different architecture options;
- irreversible або high-blast-radius decision.

### Що перевірити

- кожен design decision має rule або precedent evidence;
- frontend не залежить від backend internals;
- shared contracts мають provider і consumers;
- data/backend/frontend ordering зрозумілий;
- ADR створені для суттєвих рішень.

### Наступна команда

```text
/clear
/kapelle:sequences <slug>
```

---

## 7. `/kapelle:sequences <slug>`

```text
/kapelle:sequences <slug>
```

### Що задати на вході

Slug. Додатково можна вказати важливий runtime scenario, якщо його ще немає у spec.

### Що команда читає

```text
spec.md
sad.md
surface-plan.json
```

### Що відбувається

- описуються runtime flows;
- покриваються cross-aspect handoffs;
- додаються failure, retry та rejection branches;
- перевіряється відповідність aspect dependency graph.

Якщо runtime flow не застосовується, stage все одно створює artifact зі
`Status: SKIPPED-confirmed` і причиною.

### Що отримуємо

```text
docs/features/<slug>/sequences.md
```

### Що перевірити

- happy path;
- validation/rejection branches;
- provider/consumer interaction;
- failure recovery;
- відповідність acceptance criteria.

### Наступна команда

```text
/clear
/kapelle:data-model <slug>
```

---

## 8. `/kapelle:data-model <slug>`

```text
/kapelle:data-model <slug>
```

### Що задати на вході

Slug. Якщо є зовнішні schema constraints або migration limitations, переконайтеся, що вони вже
записані у spec/design або додайте їх у повідомленні.

### Що команда читає

```text
spec.md
sad.md
surface-plan.json
sequences.md
architecture guidance
repository precedents
```

### Що відбувається

- визначається data і persistence impact;
- підтримується один shared logical model для всіх aspects;
- explorer запускається тільки якщо persistence змінюється, а precedent evidence недостатньо;
- project capabilities визначають правильний migration/schema mechanism;
- міграції не вигадуються без project rules.

### Що отримуємо

```text
docs/features/<slug>/data-model.md
```

Також можуть з’явитися staged migration artifacts у project-defined format.

Якщо schema change не потрібний, `data-model.md` містить:

```text
Status: SKIPPED-confirmed
```

разом із доказом no-schema-change.

### Що перевірити

- field types і invariants;
- ownership даних;
- compatibility;
- migration/rollback implications;
- узгодженість з усіма consumer aspects.

### Наступна команда

```text
/clear
/kapelle:contracts <slug>
```

---

## 9. `/kapelle:contracts <slug>`

```text
/kapelle:contracts <slug>
```

### Що задати на вході

Slug. Якщо external API contract уже затверджений, передайте його location або переконайтеся, що
він записаний у design.

### Що команда читає

```text
sad.md
surface-plan.json
sequences.md
data-model.md
existing contracts
project capabilities
project architecture guidance
```

### Що відбувається

- для кожного declared entrypoint визначається потрібний contract artifact;
- native discovery знаходить project capability, яка вміє створити цей contract;
- contract зв’язується з provider aspect і consumer aspects;
- виконується project-defined validation;
- generic drift gate порівнює contract зі shared data model і sequences.

Stage не hardcode-ить OpenAPI, GraphQL, events, CLI чи інший contract kind.

### Що отримуємо

```text
docs/features/<slug>/contracts/
```

Якщо capability для contract kind відсутня, записується explicit unsupported result.

### Blocking cases

- contract field type суперечить shared model;
- required field пропущений;
- provider або consumer відсутній у `surface-plan.json`;
- project validation не проходить.

### Наступна команда

```text
/clear
/kapelle:decompose <slug>
```

---

## 10. `/kapelle:decompose <slug>`

```text
/kapelle:decompose <slug>
```

### Що задати на вході

Slug. Додатковий input зазвичай не потрібний: planning context має бути в попередніх artifacts.

### Що команда читає

- `spec.md`;
- `sad.md`;
- `surface-plan.json`;
- `sequences.md`;
- `data-model.md`;
- `contracts/*`;
- ADR;
- approved change impact, якщо використовується `--change`.

### Що відбувається

- перевіряється scoped architecture-guidance evidence для всіх planned aspects;
- обирається decomposition depth: `compact`, `standard` або `hierarchical`;
- L/XL feature розділяється на architecture-aligned workstreams;
- якщо XL містить independently shippable outcomes, stage повертає
  `BLOCKED-split-required` замість монолітного plan;
- feature розбивається на bounded, independently verifiable tasks;
- кожна task отримує acceptance criteria, Definition of Done і aspects;
- кожна task має один primary aspect, explicit validation, risk, contract role і ownership status;
- contract provider tasks ставляться перед consumer tasks;
- integration checks отримують owner tasks;
- будується dependency DAG;
- перевіряється відсутність cycles;
- перевіряється coverage acceptance criteria та integration checks.
- запускається `scripts/validate_task_plan.py`;
- для M/L/XL виконується один fresh-context critic pass і максимум один correction pass.

Tasks не містять skill names, agent names, provider names або routing labels.

### Що отримуємо

```text
docs/features/<slug>/tasks.json
docs/features/<slug>/tasks/*.md   # optional
docs/features/<slug>/_audit/task-plan-validation.txt
docs/features/<slug>/_audit/decomposition-review.json   # M/L/XL
```

`tasks.json` має стабільну верхньорівневу структуру:

```json
{
  "slug": "example-feature",
  "decomposition_depth": "standard",
  "architecture_guidance_path": "_audit/architecture-guidance/tasks.json",
  "workstreams": [
    {
      "id": "WS-PROVIDER",
      "intent": "...",
      "aspects": ["backend"],
      "depends_on": [],
      "completion_task_id": "T1",
      "completion_signal": "..."
    }
  ],
  "tasks": [
    {
      "id": "T1",
      "workstream_id": "WS-PROVIDER",
      "intent": "Establish the stable invoice contract",
      "deps": [],
      "acs": ["AC-01"],
      "dod": "...",
      "primary_aspect": "backend",
      "aspects": ["backend"],
      "provides_contracts": ["invoice-api"],
      "consumes_contracts": [],
      "integration_checks": [],
      "validation": [
        {
          "kind": "automated",
          "procedure": "...",
          "expected": "..."
        }
      ],
      "risk": "medium",
      "parallel_candidate": false,
      "ownership_status": "known",
      "files_hint": [],
      "status": "pending"
    }
  ]
}
```

### Що перевірити

- tasks не надто широкі;
- workstreams мають coherent outcome і completion signal;
- кожен workstream має completion task, яка залежить від усіх його tasks;
- dependency order відповідає contracts і aspects;
- усі AC покриті;
- integration validation не загублена;
- `files_hint` достатньо точні для можливого parallel execution.
- semantic validator і decomposition review мають PASS.

### Наступна команда

```text
/clear
/kapelle:plan-tests <slug>
```

---

## 11. `/kapelle:plan-tests <slug>`

```text
/kapelle:plan-tests <slug>
```

### Що задати на вході

Slug. Якщо існують обов’язкові manual, compliance або environment checks, додайте їх у повідомленні
або попередні artifacts.

### Що команда читає

```text
spec.md
surface-plan.json
tasks.json
data-model.md
contracts/
```

Для active change покриваються лише impacted AC і regression risks.

### Що відбувається

- кожен AC зв’язується з test level або inspectable validation;
- cross-aspect integration checks отримують executable owner;
- враховуються project test capabilities;
- не нав’язується strict TDD для всіх типів задач.

### Що отримуємо

```text
docs/features/<slug>/test-plan.md
```

### Що перевірити

- немає AC без validation;
- test boundary стабільний;
- contract та integration checks покриті;
- manual checks мають чітку процедуру й очікуваний результат.

### Наступна команда

```text
/clear
/kapelle:implement <slug>
```

---

## 12. `/kapelle:implement <slug>`

```text
/kapelle:implement <slug>
```

Для approved existing-feature change:

```text
/kapelle:implement <slug> --change=<change-id>
```

Політика запуску tests, PHPStan/static analysis, linters, build та інших project checks:

```text
/kapelle:implement <slug> --validation=ask
/kapelle:implement <slug> --validation=allow
/kapelle:implement <slug> --validation=skip
```

### Що задати на вході

- slug;
- `--change=<id>`, якщо виконується approved change route;
- optional `--validation=ask|allow|skip` для цього invocation;
- відповіді на approval prompts;
- environment access, необхідний для project validation.

Не потрібно вручну називати implementation skill або subagent. Kapelle має знайти їх через native
descriptions.

### Що команда читає

- `tasks.json`;
- `surface-plan.json`;
- усі upstream feature artifacts;
- project instructions;
- project skills/subagents;
- current change revision і fingerprints, якщо це change.

### Що відбувається перед code-writing

Для кожної dependency-ready task:

1. Перевіряється task graph і aspect ordering.
2. Визначається execution depth і task class.
3. Семантично знаходяться project skills/subagents для task aspects.
4. Project architecture-rules subagent повертає scoped rules.
5. Збирається optional general project guidance.
6. Обирається test strategy:
   - `strict-tdd`;
   - `characterization`;
   - `scenario-first`;
   - `contract-first`;
   - `validation-first`;
   - `validation-only`.
7. Створюється durable implementation plan.
8. Застосовується approval policy.

### Approval

Якщо approval потрібний, відповідайте:

```text
approve
request changes: <конкретний feedback>
reject
```

Мовчання не є approval.

### Що відбувається після approval

- test-author готує tests/fixtures, якщо strategy цього потребує;
- implementer виконує plan невеликими validated slices;
- risk-triggered tasks отримують fresh-context per-task review;
- lean low-risk task може відкласти independent review до mandatory feature-level review;
- формується один validation batch з точними командами, kind, scope і required/optional status;
- `ask` вимагає `run-all`, `run-selected` або `skip-all`;
- `allow` запускає batch без додаткового prompt;
- `skip` не запускає project validation під час development;
- зупинена користувачем команда записується як `cancelled` і автоматично не повторюється;
- task стає completed тільки після Definition of Done і потрібних gates.

Якщо required validation пропущена або скасована, task отримує
`validation-deferred`. Це дозволяє продовжити development, але не означає `PASS`. Повторний
`/kapelle:implement <slug> --validation=allow` спочатку виконає відкладені перевірки.

### Retry limits

Kapelle обмежує:

- edit attempts;
- загальну кількість agent runs на task.

При досягненні limit task стає `BLOCKED`, а evidence зберігається.

### Що отримуємо

- application code і tests у project-defined locations;
- оновлені task statuses;
- implementation plans;
- architecture-guidance evidence;
- strategy, approval, review і validation records.

```text
docs/features/<slug>/_audit/plans/
docs/features/<slug>/_audit/architecture-guidance/
docs/features/<slug>/_audit/implementation.jsonl
docs/features/<slug>/_audit/implementation-telemetry.jsonl
```

Kapelle не виконує git operations.

### Коли implementation зупиниться

- змінилися requirements або architecture;
- plan fingerprint більше не current;
- architecture rules мають blocking gaps;
- validation не проходить після дозволеної кількості attempts;
- validation явно пропущена або скасована — code-writing може продовжитися, але final review/ship
  залишаються заблокованими;
- required approval не отриманий;
- Agent Team ownership небезпечний або неоднозначний.

### Наступна команда

```text
/clear
/kapelle:feature-review <slug>
```

---

## 13. `/kapelle:feature-review <slug>`

```text
/kapelle:feature-review <slug>
```

Для change route:

```text
/kapelle:feature-review <slug> --change=<change-id>
```

### Що задати на вході

- slug;
- change id, якщо застосовується;
- changed-file або diff evidence, якщо host не може визначити його сам.

### Що команда читає

- implementation diff/changed files;
- spec, SAD, surface plan, sequences, model і contracts;
- task plans і validation evidence;
- scoped architecture guidance;
- change baseline та approved impact matrix.

### Що відбувається

Fresh-context `kapelle:reviewer` перевіряє:

- acceptance criteria;
- business invariants;
- approved-plan compliance;
- architecture rules;
- provider/consumer contracts;
- data-model consistency;
- test strategy;
- cross-aspect integration checks;
- unapproved behavioral або artifact drift.

### Що отримуємо

```text
docs/features/<slug>/_review/review-<date>.md
```

Verdict:

```text
PASS
CHANGES_REQUESTED
BLOCKED
```

### Якщо `CHANGES_REQUESTED`

Виконайте targeted correction через handoff. Не переходьте до ship.

### Наступна команда при PASS

```text
/clear
/kapelle:ship <slug>
```

---

## 14. `/kapelle:ship <slug>`

```text
/kapelle:ship <slug>
```

### Що задати на вході

Slug. Додатковий input потрібний лише для deployment або operational notes, яких немає в artifacts.

### Що команда читає

- останній PASS review;
- feature artifacts;
- validation evidence;
- operational і migration notes.

### Що відбувається

- перевіряється readiness;
- збираються відомості про validation, migrations, risks і follow-ups;
- створюється handoff для ручного delivery.

### Що отримуємо

```text
docs/features/<slug>/ship.md
```

### Важливо

Kapelle не:

- створює commit;
- push-ить branch;
- відкриває PR;
- merge-ить зміни.

Ці дії виконує developer.

---

# Existing-feature change lifecycle

## 15. `/kapelle:change`

### Enhancement

```text
/kapelle:change <slug> --mode=enhancement "<опис observable behavior change>"
```

### Bugfix

```text
/kapelle:change <slug> --mode=bugfix "<опис порушеної існуючої поведінки>"
```

### Refactor

```text
/kapelle:change <slug> --mode=refactor "<опис internal change>"
```

### Що задати на вході

- slug існуючої Kapelle-фічі;
- explicit mode або достатньо точний опис для classification;
- current behavior;
- desired behavior;
- відомий ticket/reference;
- compatibility constraints.

### Що команда читає

- canonical feature artifacts;
- current source і tests;
- contracts і schema;
- previous change records;
- repository precedents.

### Що відбувається

1. Explorer фіксує baseline поточної поведінки.
2. Створюється immutable revision `r001`.
3. Визначаються impacted acceptance criteria.
4. Обчислюються artifact impacts і transitive invalidation.
5. Critic перевіряє mode, hidden behavior changes і minimal route.
6. Створюється change state.
7. Користувачу показуються route, risks і planned artifact changes.
8. Очікується explicit approval.

### Що отримуємо

```text
docs/features/<slug>/changes/<change-id>/
  change.json
  change.md
  active-state.json
  artifact-state/
  revisions/r001/
    revision.json
    request.md
    impact.json
    baseline/
  progress.jsonl
```

### Що відповісти

```text
approve
request changes: <feedback>
abort
```

### Що запускати після approval

Тільки stages із надрукованого route:

```text
/kapelle:<stage> <slug> --change=<change-id>
```

Зберігайте `--change=<change-id>` в кожному handoff.

---

## 16. `/kapelle:fix`

```text
/kapelle:fix <slug> "<bug description>"
```

### Що задати на вході

- конкретний symptom;
- expected і actual behavior;
- reproduction, якщо відомий;
- feature slug.

### Що відбувається

- запускається той самий lifecycle, що `change --mode=bugfix`;
- defect зв’язується з існуючим acceptance criterion;
- якщо requirement відсутній або неправильний, bugfix зупиняється і пропонується enhancement;
- виконується тільки approved minimal route.

### Що отримуємо

Ту саму change artifact model, code/tests і progress evidence, що й для bugfix mode.

---

## 17. Зміна вимог: `--revise`

```text
/kapelle:change <slug> --change=<change-id> --revise "<amendment>"
```

### Що задати на вході

Нове формулювання requirement або architecture constraint. Воно повинно пояснювати, що саме
змінилося, а не лише просити “переробити”.

### Що відбувається

- усі нові implementation dispatch зупиняються;
- current task checkpoint-иться;
- створюється immutable `rNNN`;
- fingerprints порівнюються з попередньою revision;
- downstream artifacts стають stale;
- `change-reconciler` класифікує tasks:
  `keep`, `revalidate`, `rework`, `supersede`, `revert-required`;
- формується новий minimal route;
- потрібний новий approval.

### Що отримуємо

- нову revision directory;
- оновлені artifact states;
- `reconciliation.json`;
- новий approved route після confirmation.

---

## 18. `/kapelle:resume-change`

```text
/kapelle:resume-change <slug> --change=<change-id>
```

### Що задати на вході

Slug і exact change id. Активний state повинен бути `resumable`.

### Що команда читає

- current revision;
- `active-state.json`;
- artifact fingerprints;
- `reconciliation.json`;
- tasks;
- implementation plans;
- previous progress evidence.

### Що відбувається

- повторно обчислюються fingerprints;
- перевіряється, що stale artifacts усунені;
- перевіряється disposition кожної старої task;
- rework tasks отримують нові plans і strategies;
- revalidate tasks проходять validation;
- stale implementation plans блокуються;
- state переходить у `running`;
- implementation продовжується з першої pending або needs-rework task.

### Що отримуємо

- resume record у `progress.jsonl`;
- відновлений implementation lifecycle під current revision.

### Blocking cases

- unexplained file drift;
- unresolved stale artifact;
- incomplete reconciliation;
- plan з old revision або old `based_on` fingerprints.

---

# Допоміжні команди

## 19. `/kapelle:classify-size <slug>`

### Коли використовувати

- потрібно окремо переглянути size;
- scope суттєво змінився;
- `.size` відсутній.

### Вхід

Slug і feature idea/spec.

### Результат

```text
docs/features/<slug>/.size
```

Зазвичай `specify` вже створює `.size`, тому окремий запуск не обов’язковий.

---

## 20. `/kapelle:glossary <slug>`

### Коли використовувати

Коли domain term має неоднозначне або project-specific значення.

### Вхід

- slug;
- term;
- definition або питання, яке потрібно узгодити.

### Результат

```text
docs/features/<slug>/CONTEXT.md
```

Наступні design stages використовують узгоджену термінологію.

---

## 21. `/kapelle:decide-adr <slug>`

### Коли використовувати

Коли виникло окреме значуще architecture decision, особливо під час design або change route.

### Вхід

- decision context;
- options;
- constraints;
- consequences;
- approval, якщо рішення irreversible.

### Що відбувається

Команда використовує native project capabilities і applicable guidance, але не створює code.

### Результат

```text
docs/features/<slug>/adr/*.md
```

---

## 22. `/kapelle:roadmap <slug>`

### Коли використовувати

Для оновлення portfolio state фічі.

### Вхід

Slug і desired state/context: Now, Next, Later або Shipped.

### Результат

```text
docs/roadmap.md
```

Команда не є обов’язковою частиною feature backbone.

---

# Практичний сценарій: configurable-invoice-status-in-pipe

## Якщо Kapelle-артефактів ще немає

```text
/kapelle:survey configurable-invoice-status-in-pipe
/clear
/kapelle:specify configurable-invoice-status-in-pipe \
  "Allow the invoice status used in the processing pipe to be configured while preserving the current default"
/clear
/kapelle:clarify configurable-invoice-status-in-pipe
/clear
/kapelle:design configurable-invoice-status-in-pipe
/clear
/kapelle:sequences configurable-invoice-status-in-pipe
/clear
/kapelle:data-model configurable-invoice-status-in-pipe
/clear
/kapelle:contracts configurable-invoice-status-in-pipe
/clear
/kapelle:decompose configurable-invoice-status-in-pipe
/clear
/kapelle:plan-tests configurable-invoice-status-in-pipe
/clear
/kapelle:implement configurable-invoice-status-in-pipe
/clear
/kapelle:feature-review configurable-invoice-status-in-pipe
/clear
/kapelle:ship configurable-invoice-status-in-pipe
```

## Якщо це зміна вже описаної фічі

```text
/kapelle:change configurable-invoice-status-in-pipe \
  --mode=enhancement \
  "Allow invoice status in the processing pipe to be configured while preserving the current status as the default"
```

Після approval виконуйте тільки route, який повернув Kapelle.

---

# Критичні правила

1. Не створюйте placeholder artifact, щоб обійти missing-input gate.
2. Не пропускайте `--change=<id>` у change route.
3. Не продовжуйте implementation після requirement/architecture amendment без revision.
4. Не змінюйте shared `docs/architecture-map.md` із feature worktree.
5. Не називайте project skill/agent вручну, якщо native discovery може вибрати його за description.
6. Не приймайте silence як approval.
7. Не послаблюйте tests або acceptance criteria для проходження validation.
8. Не трактуйте skipped/cancelled tests, PHPStan або linters як `PASS`.
9. Не запускайте Agent Team без explicit approval і disjoint file ownership.
10. Не очікуйте git commit, push або PR від Kapelle.
11. Завжди використовуйте точний handoff, надрукований попереднім stage.
