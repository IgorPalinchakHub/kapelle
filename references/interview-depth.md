# Interview depth

Interview depth controls questions and adversarial agent runs, never coverage.

`--interview=auto|lean|standard|deep` is accepted by `start` and `spec`. `auto` is the default:

| Evidence | Depth |
|---|---|
| XS/S, established pattern, no risk trigger | `lean` |
| M or moderate ambiguity | `standard` |
| L/XL or any risk trigger | `deep` |

## Behavior

- `lean`: inline consistency challenge; ask only one consolidated blocking question; do not
  dispatch critic or devil's advocate.
- `standard`: business analysis plus one combined critic pass; ask at most three material
  questions; one correction pass.
- `deep`: business analyst, separate fresh critic, separate devil's advocate, at most one
  consolidated question round and one correction pass.

Every depth still covers actors, main and alternative flows, rules, failures, permissions,
compatibility, integrations, and measurable acceptance criteria. New evidence may escalate depth;
the stage must state why. It never silently reduces an explicitly requested depth.
