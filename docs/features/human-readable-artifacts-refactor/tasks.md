# Implementation tasks

## Contracts and state model

- [x] **T01 Define layout and presentation contracts** — covers AC-01, AC-09
- [x] **T02 Add manifest, state, recovery schemas and vocabulary** — depends on T01; covers AC-07

## Deterministic status and recovery

- [x] **T03 Implement status and recovery state engine** — depends on T02; covers AC-02–AC-06
- [x] **T04 Implement feature-state validator** — depends on T03; covers AC-07
- [x] **T05 Implement safe legacy migration** — depends on T03; covers AC-10

## Stage protocol migration

- [x] **T06 Migrate backbone and change skills to layout-v2** — depends on T02; covers AC-08, AC-09
- [x] **T07 Add status skill and convergence gates** — depends on T03 and T06; covers AC-02, AC-08

## Verification and documentation

- [x] **T08 Add recovery/migration tests and plugin self-validation** — depends on T04, T05, T07;
  covers AC-11
- [x] **T09 Update examples and user documentation** — depends on T07; covers AC-12
