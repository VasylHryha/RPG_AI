# 0029: C6 option B, an engineering and runtime port of the unchanged R4 model

**Date:** 2026-10-05
**Owner's words:** "B", choosing among the options of `docs/reviews/c6_unblocking_synthesis_gpt.md` section 8 (decision 0027), as presented in this session:
- A: the quiet-against-high-background pilot;
- B: the engineering/resource route for the unchanged R4 model (a C++ port);
- C: pause.

## Decision

The owner chose **B: pursue the engineering and resource route for the unchanged C6 R4 model**. The drafter (Claude) recommended A first; the owner chose B.

## What is authorized

1. **Profiling** of complete R4 worlds on **existing smoke or development entropy only**. No final entropy.
2. **Porting the remaining hot paths to typed C++.** Today the element law (`native/c6/element_law.cpp`) and the field (`native/c6_r4/field.cpp`) are native; the orchestration, qualification forks and detection are Python. The scientific model, thresholds and protocol stay **unchanged**.
3. **Equivalence:** the ported path reproduces the current implementation on the stored fixtures and smoke worlds, exactly where the arithmetic is unchanged and within declared numerical tolerances elsewhere, with the tolerances declared before measurement.
4. **A measured runtime per complete world** against the registered readiness rule (`max(world seconds) × 40 / 2 × 1.5 ≤ 10800`, so each world ≤ 360 s), on non-final entropy.
5. **One cross-family review** of the port: Codex implements, Claude reviews.

## What is not authorized

- final entropy;
- an R007 registration;
- a mutation probe or a recorded panel;
- any change to the R4 science (laws, thresholds, criteria);
- any change to C0-C5 frozen files or committed receipts;
- any change to milestone status.

C6 stays `BLOCKED / R006 STOP` until the owner approves a new registered revision after this work.

## Note on the open science question

The synthesis's apparatus concern still stands: a changed background may suppress the next unit's qualification. B makes the model fast. It does not answer that concern. The answer comes from the next registered attempt (or a later pilot), now affordable.
