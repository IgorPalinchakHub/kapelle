# Compact quality behavior checks

Maintainer scenarios for changed planning, dialogue, and test timing. These are not a downstream
Kapelle stage, a CI requirement, or evidence of a passing live-agent run. Existing deterministic
plugin validation checks structure; these scenarios inspect the decisions an agent actually makes.

## Run

Give an independent agent one Request and Context below plus the current start/amend/implement/
verify skills and their shared references. Ask it to draft the compact slice, its first developer
message, and the early/final verification split. Use an isolated temporary workspace if writing
artifacts; never edit a real feature or create approval/PASS records for these fictional cases.
Do not give the evaluator the rubric until its draft is complete. It may report a missing fact;
that is not automatically a failure. A maintainer then compares the observable output with the
rubric. Record the scenario, actual output/evidence, and pass/fail/not-run; do not infer execution
from the presence of this file. A drafting run does not prove tool routing or code implementation.

## Simple improvement

Request: "У формі профілю заміни напис кнопки «Submit» на «Зберегти». Поведінку не змінюй."

Context: the existing profile form saves correctly; the label is a local translation value. An
existing component test already checks successful saving; no public API, schema, permissions,
deployment, or integration changes are involved. There is no loading/error-state change.

Rubric:
- One workstream; root documents only; no new stage, ADR, diagram, questionnaire, or invented NFR.
- The developer message explains the current label, proposed label, and preserved save behavior.
- No question about an already specified label, no per-test-level approval, no new early test
  suite. It reuses the existing relevant check and updates a label assertion only if needed.
- Final verification is proportionate; no load, migration, or unrelated integration test is added.

## Risky integration

Request: "Додай повтор платежу після таймауту, щоб користувачу не доводилося починати заново."

Context: an existing payment endpoint invokes a provider; a timeout currently displays a retry
message. The provider may complete a charge after our timeout. Support for an idempotency key or
payment-status lookup has not been confirmed. Existing coverage checks only immediate success.
Project policy forbids duplicate charges; no latency or retry-count target has been agreed.

Rubric:
- The draft does not claim retries are safe or invent provider guarantees or numerical targets.
- The message explains today's timeout, the proposed retry, and duplicate-charge risk before any
  references. It requests the consequential missing capability or safely bounds the proposal.
- The use case distinguishes timeout/unknown outcome from failed charge, states relevant resulting
  state, and describes the duplicate/repeat branch at the right step once the policy is known.
- Only a basic path and concrete duplicate-charge protection need early evidence. Broader tests
  remain final; unknown prerequisites are not portrayed as implemented or tested.
- Quality verification matches the guarantee; a load test alone cannot prove no double charge.

## Refactoring

Request: "Винеси розрахунок знижки з обробника замовлення в окремий сервіс, результат не змінюй."

Context: the handler currently applies the documented discount, rounds half-up to cents, and caps
the discount at the order subtotal. An existing endpoint test covers a normal order. There is no
coverage for the rounding boundary or the cap. Data schema and API are unchanged.

Rubric:
- One coherent workstream preserves the API, rounding, and cap; no unrelated redesign or migration.
- The message explains where the calculation lives now and what responsibility moves, without
  referring the user to a paragraph to understand the change.
- A focused characterization/unit test of the missing money boundaries may precede the move;
  no blanket unit suite, speculative fixture library, or universal TDD loop is introduced.
- Final verification reuses those tests and covers remaining relevant behavior without duplicates.
- Refactor evidence maps preserved outcomes to specific checks; formatting alone is not evidence.

## Observed drafting review — 2026-09-11

An independent agent read the updated skills and shared references with only the three requests
and contexts, without this rubric or the feature package. It produced drafts without writing
files, executing code, or creating gates. The maintainer reviewed those outputs:

| Case | Observed result | Assessment |
|---|---|---|
| Simple improvement | Explained Submit -> Зберегти and unchanged saving; zero questions; three root docs and one workstream; reused existing test without adding a suite | Drafting checks pass |
| Risky integration | Kept provider capability unknown; blocked unsafe retries; asked manual vs automatic recovery; distinguished unknown outcome; proposed narrow duplicate-charge evidence, with other tests final | Drafting checks pass; real provider behavior remains untested |
| Refactoring | Explained handler -> service with preserved half-up/cap; zero questions; one workstream; only missing money-boundary tests early, rest final | Drafting checks pass |

This observes planning and dialogue only. Full stage execution, generated detailed use-case
documents, provider integration, and production behavior were not exercised by this drafting run.
