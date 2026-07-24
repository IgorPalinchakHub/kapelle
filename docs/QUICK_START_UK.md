# Kapelle: коротка інструкція та послідовність команд

Це практичний порядок роботи без пояснення внутрішніх JSON-артефактів. Деталі кожної команди
наведені в [COMMAND_EXECUTION_UK.md](COMMAND_EXECUTION_UK.md).

## 1. Перед початком

Проєкт повинен мати:

- `AGENTS.md` або `CLAUDE.md` з проєктними правилами;
- native skills/subagents для технологій проєкту;
- subagent, який повертає архітектурні правила для заданої частини фічі;
- відомі команди тестів, lint/static analysis і build.

Оберіть стабільний slug у kebab-case:

```text
configurable-invoice-status-in-pipe
```

Усі артефакти фічі будуть у:

```text
docs/features/configurable-invoice-status-in-pipe/
```

## 2. Нова фіча: рекомендований порядок

### Крок 0. Shared architecture baseline

Виконується один раз для репозиторію, якщо `docs/architecture-map.md` ще відсутній:

```text
/kapelle:survey
```

Результат: загальна карта архітектури, validation commands і доступних project capabilities.

### Крок 1. Локальний контекст фічі

```text
/kapelle:survey configurable-invoice-status-in-pipe
```

На вході: slug і, за потреби, коротко affected area.

Результат:

```text
docs/features/configurable-invoice-status-in-pipe/_context/architecture.md
```

У worktree команда не переписує shared `docs/architecture-map.md`.

### Крок 2. Вимоги

```text
/clear
/kapelle:specify configurable-invoice-status-in-pipe "Allow invoice status in Pipe to be configured per applicable business rules"
```

На вході бажано вказати:

- проблему і бажану observable behavior;
- actor/caller;
- scope і non-goals;
- compatibility/business constraints;
- відомі edge cases.

Перевірте:

```text
proposal.md
spec.md
```

### Крок 3. Уточнення

```text
/clear
/kapelle:clarify configurable-invoice-status-in-pipe
```

Результат: blocking ambiguities вирішені або явно відкладені; acceptance criteria однозначні.

### Крок 4. Технічний дизайн

```text
/clear
/kapelle:design configurable-invoice-status-in-pipe
```

Kapelle знаходить project architecture-rules subagent, визначає backend/frontend/data/інші
аспекти, контракти та integration checks.

Перевірте:

```text
design.md
adr/
contracts/
```

За потреби складного runtime або data design:

```text
/kapelle:sequences configurable-invoice-status-in-pipe
/kapelle:data-model configurable-invoice-status-in-pipe
```

Ці дві команди необов’язкові.

### Крок 5. Контракти

Якщо фіча змінює API, events, DTO, schema boundary або frontend/backend interface:

```text
/clear
/kapelle:contracts configurable-invoice-status-in-pipe
```

Якщо окремі contract artifacts не потрібні, переходьте до decomposition.

### Крок 6. Декомпозиція

```text
/clear
/kapelle:decompose configurable-invoice-status-in-pipe
```

Перевірте `tasks.md`:

- tasks описують результати, а не мікрокроки;
- AC покриті;
- backend/frontend/data робота узгоджена контрактами;
- dependencies зрозумілі;
- tasks не надмірно дрібні.

Machine dependency graph зберігається в `_kapelle/task-plan.json`.

### Крок 7. План тестування

```text
/clear
/kapelle:plan-tests configurable-invoice-status-in-pipe
```

Перевірте `test-plan.md`: AC coverage, integration checks, required/optional commands і manual
checks.

### Крок 8. Реалізація

Безпечний default:

```text
/clear
/kapelle:implement configurable-invoice-status-in-pipe --validation=ask
```

Коли агент покаже validation batch:

- `run-all` — виконати всі команди;
- `run-selected` — виконати вибрані;
- `skip-all` — відкласти validation.

Інші режими:

```text
/kapelle:implement configurable-invoice-status-in-pipe --validation=allow
/kapelle:implement configurable-invoice-status-in-pipe --validation=skip
```

`skip` не означає `PASS`: required checks отримають стан `validation-deferred` і заблокують ship.

### Крок 9. Незалежний review

```text
/clear
/kapelle:feature-review configurable-invoice-status-in-pipe
```

Review порівнює реалізацію зі spec, design, contracts, ADR, tasks, test plan та project
architecture rules.

### Крок 10. Готовність до передачі

```text
/clear
/kapelle:ship configurable-invoice-status-in-pipe
```

Команда перевіряє readiness і не виконує `git commit`, `push`, merge або створення PR.

## 3. Що робити після кожної команди

1. Відкрийте `docs/features/<slug>/STATUS.md`.
2. Перегляньте human-readable файл, створений поточним stage.
3. Якщо результат неправильний — виправте вимоги/рішення до переходу далі.
4. Виконайте `/clear`.
5. Запустіть exact next command із `STATUS.md`.

`/clear` безпечний: наступний stage читає стан із файлів, а не з історії чату.

## 4. Продовження існуючої фічі

Починайте не зі `specify`, а зі status:

```text
/kapelle:status configurable-invoice-status-in-pipe
```

Команда перевірить документи й `_kapelle/`, відновить derived state за потреби та покаже мінімальний
наступний stage.

Якщо `_kapelle/` видалено, Kapelle може відновити планувальний стан із human docs і поточного коду,
але не вигадує втрачені approvals, validation output або review verdicts.

## 5. Зміна вже задокументованої фічі

Enhancement:

```text
/kapelle:change configurable-invoice-status-in-pipe --mode=enhancement "Add a fallback status for dealers without explicit configuration"
```

Bugfix:

```text
/kapelle:fix configurable-invoice-status-in-pipe "Configured invoice status is ignored for imported invoices"
```

Behavior-preserving refactor:

```text
/kapelle:change configurable-invoice-status-in-pipe --mode=refactor "Extract status resolution without changing observable behavior"
```

Якщо вимоги змінилися під час implementation:

```text
/kapelle:change configurable-invoice-status-in-pipe --change=<change-id> --revise "New requirement"
```

Після reconciliation та approval:

```text
/kapelle:resume-change configurable-invoice-status-in-pipe --change=<change-id>
```

## 6. Локальна перевірка плагіна

Після змін у Kapelle:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s scripts -p 'test_*.py'
git diff --check
```

Версії в manifests повинні мати однакову base semver:

```text
.claude-plugin/plugin.json  → 0.10.0
.codex-plugin/plugin.json   → 0.10.0+codex.<cachebuster>
```

Для оновлення локального Codex dev-plugin:

```bash
python3 /Users/ihorpal/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py .
python3 scripts/validate_plugin.py
codex plugin add kapelle@kapelle-dev
```

Після перевстановлення почніть новий thread, щоб Codex завантажив оновлені skills.
