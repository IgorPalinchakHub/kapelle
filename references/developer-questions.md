# Developer question contract

Questions shown to the developer must stand on their own. Internal planning notation is useful for
Kapelle, but it is not useful context for a human decision.

## When to ask

Ask only when the answer blocks safe progress or materially changes product behavior,
architecture, data handling, compatibility, scope, or delivery risk. Otherwise use the
evidence-backed default and state the assumption in the review packet.

Do not ask the developer to choose a reversible implementation detail when repository evidence and
project rules support a safe default. Make that choice, state it as an assumption, and keep moving.

## Required form

Match the developer's language and keep one decision question concise, normally under 90 prose
words. A short code example does not count toward that prose target:

1. Say what Kapelle intends to implement in plain language.
2. Explain why this decision is needed and the concrete consequence of a wrong assumption.
3. When evidence supports a preferred choice, recommend it first and state its downside.
4. Give at most three real options. Normally give two real options. Make trade-offs explicit by
   putting the important benefit and cost/risk on the same line.
5. End with a direct question that can be answered without opening a feature artifact.

Preferred shape:

```text
Я хочу <короткий результат>. Потрібно вирішити <рішення>, тому що <наслідок>.

- Рекомендую <Варіант A> — <перевага>; <вартість або ризик>.
- <Варіант B> — <перевага>; <вартість або ризик>.

Що обираємо?
```

For a factual prerequisite, ask for the fact while still explaining the resulting alternatives:

```text
Я хочу безпечно перейменувати статус пакетного інвойсу. Старі записи з попереднім значенням
зламають читання після деплою.

- Таблиця порожня або записи можна видалити — проста зміна без міграції, але дані буде втрачено.
- Записи потрібно зберегти — додамо міграцію значень, але реалізація і деплой стануть складнішими.

Таблиця порожня, записи можна видалити чи їх потрібно мігрувати?
```

## Code examples when relevant

Add a code example only when an API shape, schema, type contract, control flow, or compatibility
difference would be materially harder to compare in prose. The example:

- is normally at most 12 lines;
- shows only the decision surface and relevant difference;
- may compare two signatures or minimal before/after fragments;
- never expands into a full implementation, setup, test suite, or unrelated framework code;
- never justifies asking a question that should be resolved by an evidence-backed default.

Preferred technical shape:

```text
Я хочу зробити відсутній інвойс явною помилкою. Рекомендую додати `get()`: наявний `find()`
залишиться сумісним, але тимчасово буде два методи.

    find(int $id): ?Invoice
    get(int $id): Invoice // throws InvoiceNotFound

- Додати `get()` — безпечна міграція; тимчасово два методи.
- Змінити `find()` — простіший API; потрібно одразу виправити всіх callers.

Чи зберігаємо сумісність через новий `get()`?
```

## Never expose as the question

- artifact, gate, blocker, acceptance-criterion, task, workstream, or DoD identifiers;
- phrases such as “the spec says”, “D1 requires”, “B-1 blocks”, or “according to the artifact”;
- raw critic, planner, validator, or subagent output;
- vague prompts such as “What is its state?”;
- a recommendation without the downside, or several unrelated decisions in one question.
- a large code sample, pseudo-implementation, or code that does not materially change the choice.

Internal identifiers may be recorded after the answer in machine state and human documents. They
must not be used to make the developer decode the question.
