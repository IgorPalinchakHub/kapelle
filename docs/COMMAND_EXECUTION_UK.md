# Детальний порядок виконання команд Kapelle

Цей документ описує порядок команд, необхідний input, внутрішні кроки, результати та важливі gates.
Для короткого copy-paste сценарію дивіться
[Kapelle: коротка інструкція та послідовність команд](QUICK_START_UK.md).

## 1. Загальна модель

Основний короткий flow:

```text
survey → specify → clarify → design → contracts? → decompose
       → plan-tests → implement → feature-review → ship
```

`sequences` і `data-model` — optional design enrichers, а не обов’язкові порожні stages.

Після кожного backbone stage:

1. відкрийте `docs/features/<slug>/STATUS.md`;
2. перегляньте вказані людські документи;
3. виконайте `/clear`;
4. запустіть exact next command із handoff або `STATUS.md`.

Стан не залежить від історії чату. Human-readable документи є durable state, а `_kapelle/`
містить derived execution state та evidence.

## 2. Структура фічі

```text
docs/features/<slug>/
  STATUS.md
  proposal.md
  spec.md
  design.md
  tasks.md
  test-plan.md
  contracts/
  adr/
  _context/
  _kapelle/
```

Користувач зазвичай читає лише перші шість документів, contracts та ADR. JSON, JSONL, fingerprints,
agent plans, reviews і telemetry знаходяться тільки в `_kapelle/`.

---

## 3. `/kapelle:survey [<slug>]`

### Що задати на вході

- без slug: bootstrap shared repository baseline;
- зі slug: стабільний kebab-case slug і коротка affected area;
- `--refresh-baseline`: explicit maintenance intent та подальше підтвердження.

### Що відбувається

- без slug і без baseline: `kapelle:explorer` мапить stack, boundaries, persistence, validation,
  project skills/subagents і architecture-rules capability;
- зі slug: аналізується лише current-branch scope фічі;
- `reflects_commit` використовується як provenance, не як freshness gate;
- worktree divergence не переписує shared map.

### Що отримуємо

```text
docs/architecture-map.md                         # bootstrap
docs/features/<slug>/_context/architecture.md   # feature scope
```

### Наступна команда

```text
/clear
/kapelle:specify <slug> "<problem and desired outcome>"
```

---

## 4. `/kapelle:specify <slug> ["<idea>"]`

### Що задати на вході

- authoritative slug/ticket;
- problem;
- desired observable outcome;
- actor/caller;
- scope/non-goals;
- відомі business/compatibility constraints.

Якщо supplied slug конфліктує лише з branch metadata, Kapelle ставить одне consolidated питання,
а не запускає ticket/scope/idea wizard.

### Що відбувається

- bounded preflight до source exploration;
- формуються proposal, actors, requirements, ACs, edge cases, NFR і open questions;
- size/execution depth записується internal;
- для M/L/XL виконується bounded adversarial requirements review.

### Що отримуємо

```text
proposal.md
spec.md
_kapelle/size.json
STATUS.md
```

`proposal.md` пояснює «навіщо/який scope», `spec.md` — observable behavior для PM/QA.

### Наступна команда

```text
/clear
/kapelle:clarify <slug>
```

---

## 5. `/kapelle:clarify <slug>`

### Що задати на вході

Slug. Додатково — відповіді лише на реально blocking ambiguities.

### Що відбувається

- delta sweep, без повторення specify;
- перевіряються vague terms, actors, failure outcomes, measurable NFR, AC conflicts;
- кожен blocking finding resolve або explicit defer.

### Що отримуємо

Оновлений `spec.md` і `STATUS.md`.

### Наступна команда

```text
/clear
/kapelle:design <slug>
```

---

## 6. `/kapelle:design <slug>`

### Що задати на вході

- slug;
- architecture constraints, якщо вони не закодовані в project rules;
- відомі rollout/security/compatibility requirements.

### Що відбувається

- читається feature `_context`, потім shared architecture baseline;
- визначаються backend/frontend/data/other aspects, modules, entrypoints;
- семантично знаходиться project architecture-rules subagent;
- project subagent може знайти narrower native skills/subagents;
- правила й precedents перевіряються перед technical decisions;
- описуються boundaries, runtime/failure flows, data/schema impact, authorization, contracts,
  observability, compatibility, rollout і alternatives;
- створюється aspect dependency/contract/integration graph.

### Що отримуємо

```text
design.md
adr/*.md
_kapelle/surface-plan.json
_kapelle/architecture-guidance/design.json
STATUS.md
```

### Що перевірити

- responsibilities backend/frontend/data не змішані;
- contract providers/consumers explicit;
- design містить schema change або explicit no-schema-change;
- runtime failure branches і security boundaries не пропущені;
- ADR описують важливі alternatives/consequences.

### Наступна команда

Якщо потрібні contract artifacts:

```text
/clear
/kapelle:contracts <slug>
```

Інакше:

```text
/clear
/kapelle:decompose <slug>
```

---

## 7. Optional `/kapelle:sequences <slug>`

Використовуйте лише для складних runtime/cross-aspect flows.

### Вхід

`design.md`, `_kapelle/surface-plan.json`, slug.

### Результат

- runtime-flow section у `design.md`;
- optional `sequences.md`, якщо inline flow став би нечитабельним;
- skip/evidence у `_kapelle/state.json`.

---

## 8. Optional `/kapelle:data-model <slug>`

Використовуйте для складного persistence/schema/migration design.

### Вхід

`spec.md`, `design.md`, `_kapelle/surface-plan.json`, scoped project rules.

### Результат

- оновлений data/schema section `design.md`;
- `_kapelle/data-model.json`;
- staged project migrations, якщо потрібні.

No-schema-change також записується явно.

---

## 9. `/kapelle:contracts <slug>`

### Що задати на вході

Slug і project-specific constraints, яких немає в design/rules.

### Що відбувається

- читаються `design.md` і `_kapelle/surface-plan.json`;
- native discovery знаходить capability для потрібного contract kind;
- contract зв’язується з provider/consumer aspects;
- виконується project-defined validation і generic drift check.

### Що отримуємо

```text
contracts/*.md
_kapelle/validation/contracts.json
STATUS.md
```

### Наступна команда

```text
/clear
/kapelle:decompose <slug>
```

---

## 10. `/kapelle:decompose <slug>`

### Що задати на вході

Slug. Planning context уже має бути у spec/design/contracts/ADR.

### Що відбувається

- scoped architecture guidance покриває всі planned aspects;
- size визначає `compact | standard | hierarchical`;
- створюються architecture-aligned workstreams;
- tasks мають outcome, primary aspect, deps, ACs, DoD, validation, risk, contracts, integration
  ownership і files hints;
- M орієнтир: 3–7 workstreams та 7–15 tasks;
- запускається deterministic graph/AC/contract/integration validator;
- M/L/XL отримує один critic pass і максимум одну correction.

### Що отримуємо

```text
tasks.md
_kapelle/task-plan.json
_kapelle/architecture-guidance/tasks.json
_kapelle/task-plan-validation.txt
_kapelle/reviews/decomposition.json
STATUS.md
```

`tasks.md` — компактний checklist. Повний graph і `files_hint` залишаються internal.

### Наступна команда

```text
/clear
/kapelle:plan-tests <slug>
```

---

## 11. `/kapelle:plan-tests <slug>`

### Що задати на вході

Slug та обов’язкові manual/compliance/environment checks, якщо їх не знає project capability.

### Що відбувається

- кожен AC та integration check отримує executable/inspectable validation;
- required/optional checks розділяються явно;
- test strategy відповідає task class, а strict TDD не є universal.

### Що отримуємо

```text
test-plan.md
STATUS.md
```

Run results пізніше зберігаються у `_kapelle/validation/`.

### Наступна команда

```text
/clear
/kapelle:implement <slug>
```

---

## 12. `/kapelle:implement <slug> [--validation=ask|allow|skip]`

### Що задати на вході

- slug;
- `--change=<id>` для approved change route;
- optional validation policy override;
- відповіді на plan approval;
- environment access для project checks.

### Що відбувається для кожної dependency-ready task

```text
UNDERSTAND → CLASSIFY → SELECT-CAPABILITY → GUIDANCE
→ TEST-STRATEGY → PLAN → APPROVE → IMPLEMENT → REVIEW → VALIDATE
```

- project skills/subagents вибираються за native descriptions;
- architecture-rules subagent повертає scoped rules;
- strategy: strict-tdd, characterization, scenario-first, contract-first, validation-first або
  validation-only;
- plan durable і revisions/fingerprints перевіряються;
- retry/agent-run loops bounded;
- sequential mode default;
- Agent Teams лише з runtime support, explicit approval і disjoint file ownership.

### Validation policy

- `ask`: показати exact batch і чекати `run-all | run-selected | skip-all`;
- `allow`: виконати batch;
- `skip`: нічого не запускати під час development.

Cancelled або skipped required checks дають `validation-deferred`, ніколи не `PASS`.

### Що отримуємо

```text
application code/tests
tasks.md                              # readable progress
_kapelle/task-plan.json              # exact states/graph
_kapelle/task-runs/<task-id>.json
_kapelle/validation/<task-id>.json
_kapelle/telemetry/execution.jsonl
STATUS.md
```

### Коли implementation зупиняється

- requirement/architecture amendment;
- stale plan fingerprints;
- missing architecture-rules capability;
- required approval відсутній;
- attempt limit;
- unsafe Agent Team ownership.

### Наступна команда

```text
/clear
/kapelle:feature-review <slug>
```

---

## 13. `/kapelle:feature-review <slug>`

### Що задати на вході

Slug, optional change id і changed-file evidence, якщо host його не надає.

### Що відбувається

Спочатку as-built convergence:

```text
proposal ↔ final scope
spec ↔ observable implementation
design ↔ technical implementation
contracts ↔ providers/consumers
tasks ↔ implemented work
test-plan ↔ validation
ADR ↔ actual decisions
```

Потім fresh read-only reviewer перевіряє ACs, architecture rules, contracts, tests, risks і
cross-aspect integration. Required deferred validation блокує PASS.

### Що отримуємо

```text
_kapelle/reviews/documentation-convergence.json
_kapelle/reviews/feature-review.json
STATUS.md
```

Verdict: `PASS | CHANGES_REQUESTED | BLOCKED`.

### Наступна команда при PASS

```text
/clear
/kapelle:ship <slug>
```

---

## 14. `/kapelle:ship <slug>`

### Що задати на вході

Slug і optional release/operational notes.

### Що відбувається

- перевіряються current convergence/review fingerprints;
- required validation повинна мати PASS;
- active change або stale docs блокують readiness;
- оновлюється generated status.

### Що отримуємо

```text
STATUS.md
_kapelle/state.json
release.md              # optional human release notes
```

Kapelle не робить commit, push, PR або merge.

---

## 15. `/kapelle:status <slug>`

### Коли використовувати

- хочете швидко зрозуміти стан;
- повернулися до фічі пізніше;
- development продовжувався поза Kapelle;
- `_kapelle/` видалений/пошкоджений;
- потрібно знайти minimal next stage.

### Що задати на вході

Існуючий slug. Feature directory має існувати.

### Що відбувається

- читаються human docs;
- перевіряється manifest/state;
- за потреби scoped agent аналізує current code/tests і architecture rules;
- internal state rebuild/reconcile;
- checked task без current validation стає `implemented-unverified`;
- втрачені approvals/reviews/telemetry/command output/validation перелічуються як evidence gaps;
- product requirements не переписуються під випадкову code behavior.

### Що отримуємо

```text
STATUS.md
_kapelle/manifest.json
_kapelle/state.json
_kapelle/recovery.json    # після recovery
```

### Важливо

`status` не редагує implementation code, не запускає validation, не мігрує legacy layout без
approval і не виконує git operations.

---

## 16. Legacy migration

### Dry run

```text
python3 scripts/migrate_feature_layout.py docs/features/<slug> --dry-run
```

Показує actions/collisions і нічого не змінює.

### Apply

```text
python3 scripts/migrate_feature_layout.py docs/features/<slug> --apply
```

Потребує explicit decision користувача. Migration:

- `sad.md` → `design.md`;
- root task/surface JSON → `_kapelle/`;
- створює readable proposal/tasks, якщо вони відсутні;
- зберігає legacy evidence в `_kapelle/history/legacy/`;
- rebuild-ить state/status;
- є idempotent.

---

## 17. `/kapelle:change`, `/kapelle:fix`, `/kapelle:resume-change`

### New change

```text
/kapelle:change <slug> --mode=enhancement "<observable change>"
/kapelle:change <slug> --mode=bugfix "<accepted behavior to restore>"
/kapelle:change <slug> --mode=refactor "<behavior-preserving change>"
```

Kapelle capture-ить baseline, AC/artifact impact, minimal route і чекає:

```text
approve
request changes: <feedback>
abort
```

Internal state:

```text
_kapelle/changes/<change-id>/
  change.json
  state.json
  revisions/
  artifact-state/
  reconciliation.json
  progress.jsonl
```

User-relevant scope/decision changes відображаються в proposal/spec/design/ADR.

### Bug shorthand

```text
/kapelle:fix <slug> "<bug description>"
```

Якщо expected behavior не існує в accepted spec, потрібна reclassification to enhancement.

### Mid-implementation amendment

```text
/kapelle:change <slug> --change=<id> --revise "<amendment>"
```

Implementation pause, immutable revision, transitive invalidation, task reconciliation і новий
route approval є обов’язковими.

### Resume

```text
/kapelle:resume-change <slug> --change=<id>
```

Resume відмовляє при unexplained fingerprint drift, stale upstream artifacts, incomplete
reconciliation або old implementation plan.

---

## 18. Допоміжні команди

### `/kapelle:classify-size <slug>`

Вхід: slug і proposal/spec.  
Результат: `_kapelle/size.json`.

### `/kapelle:glossary <slug>`

Вхід: ambiguous domain term та desired definition.  
Результат: human `CONTEXT.md`.

### `/kapelle:decide-adr <slug>`

Вхід: decision context, options, constraints.  
Результат: `adr/NNNN-<decision>.md`.

### `/kapelle:roadmap <slug>`

Вхід: priority/status change.  
Результат: roadmap artifact, якщо project використовує його.

---

## 19. Локальні deterministic checks

```text
python3 scripts/validate_task_plan.py \
  --tasks docs/features/<slug>/_kapelle/task-plan.json \
  --surface-plan docs/features/<slug>/_kapelle/surface-plan.json \
  --spec docs/features/<slug>/spec.md

python3 scripts/validate_feature_state.py docs/features/<slug>
python3 scripts/validate_plugin.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Ці plugin utilities не запускають project tests, PHPStan, linters, builds, network або git.
