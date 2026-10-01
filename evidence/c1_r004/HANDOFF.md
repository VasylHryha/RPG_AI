# C1 R004 independent review handoff

C1 R004 (`geomind-c1-r4-004`) is **REVIEW_READY**, not accepted. Its author is the reviewer who judged R002 CHANGES_REQUIRED and then rechecked their own R003 repair ([CLAUDE_ACCEPTANCE.md](../c1_review/CLAUDE_ACCEPTANCE.md)). A **different reviewer** must decide R004 before C2. R001, R002 and R003 receipts are unchanged, and all 12 accepted C0 inputs are byte-identical.

## Design (replaces R003, which was global by construction)

- **State.** In-memory incremental structures: adjacency lists, per-node canonical degree lists, component member lists, anchors, and coordinates read relative to their component anchor. Degree upkeep reproduces the accepted C0 `bincount` degree bit for bit; a load-time check and a focused audit enforce this. Export and load produce and validate the canonical C0-format snapshot with the accepted C0 validator.
- **Input.** `apply` takes an additive delta (new nodes, edges and relations). `update(observation)` remains as a compatibility path that charges its O(V+E) diff.
- **Transaction.**
  - Every mutation is journaled, and any refusal undoes it.
  - One 100,000-operation cap covers every in-memory step: input, degree upkeep, frame reads, translation writes, anchor candidates, incident reads and certificate reads.
  - New nodes and old components are rigid frames, placed by a spanning tree of added edges. The largest frame stays fixed, so a bridge translates only the smaller component.
- **Dynamics.** The C0 residual law with the C0 step (`0.25 / max weighted degree`), using stable-ID queue rounds as in R002.
- **Certificate.** Local and explicit. It checks every node whose force may have changed: endpoints of added edges, new nodes, freed anchors, moved nodes and their neighbors. Forces must be below tolerance by a factor of `1 − 1e-6`. The soundness argument is in the `incremental.py` docstring, and a focused check asserts that every node whose force actually changed was certified.
- **Arms.** The *queue* arm has no fallback. The *fallback* arm adds a separately capped (5M operations) Jacobi-preconditioned CG solve on the affected components, warm-started from the queue workspace. Fallback commits are reported separately and never count as queue successes.
- **Pre-registration.** Endpoints and verdict rules were written into the manifest before the panel. They came after R002/R003 inspection and one smoke test on non-panel seed 7. Panel seeds start at 10,000,000.

## Reached evidence

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_r004/contracts.xml
.venv/bin/python -m geomind.run_c1 --output evidence/c1_r004 --contract-report evidence/c1_r004/contracts.xml
```

Fourteen focused checks PASS. The panel ran 80 interventions (4 sizes × 4 kinds × 5 seed-varied worlds) in 83.9 s, and all six gates PASS.

| Per-world medians (min–max in `results.json` → `cells`) | Queue-arm operations | In-memory update | Fresh recompute |
|---|---:|---:|---:|
| Consistent edge, 32 → 2,048 nodes | 27 → 36 | 0.22 ms at 2,048 | 43.7 ms |
| New node, 32 → 2,048 | 24 → 30 | 0.23 ms | 39.5 ms |
| Bridge, 2,048 (translates the 512-node smaller component) | 567 | 0.70 ms | 41.0 ms |
| Contradiction, every size | cap exhausted (0/20 resolved) | refused, byte-identical | — |
| Contradiction, fallback arm, 2,048 | 100k queue + 190k fallback | 0.16 s total | 64.9 ms |

- **Queue arm:** 60/60 non-contradiction updates commit correctly (maximum error `3.96e-11`), all with zero relaxation steps. 20/20 contradictions are explicitly unresolved, with proven cap exhaustion and byte-identical rollback.
- **Fallback arm:** 80/80 commit correctly (maximum error `6.29e-9`, energy gap ≤ `2.2e-16`), 20 of them through the fallback.
- **Fallback cost.** Its operations alone (median 34,877 at 512 nodes) are 7.0–7.8× fewer than a fresh sparse-LS solve's edge visits at 128–2,048 nodes. The arm is still slower end to end because it first exhausts the 100k queue cap.
- **Abstention.** All 792/792 excluded cross-component pairs abstain in both arms.
- **Retention and determinism.** Retention, query immutability and exact reload pass everywhere. When no fallback ran, the two arms produce byte-identical exports.
- **Registered H-L verdicts:**
  - consistent additive in-memory updates: **SUPPORTED_WITHIN_SCOPE** (locality ratios 1.33 and 1.25 against the ≤ 2 limit; every 2,048-node speed ratio < 0.02);
  - contradiction resolution by the local queue: **NOT_SUPPORTED** (resolution rate 0.0 at ≥ 128 nodes);
  - durable persistence: global by design, not tested for locality.
- **H-P** remains INCONCLUSIVE. Median frozen accuracy is 0.81 against 1.0 after either arm, but a store that includes the new constraints answers them by construction.

## Mutation probe

`evidence/c1_claude_review/mutation_checks_r004.json` records 23 deliberate defects against R004; the suite catches 18. The five survivors each remove a backup guard that another tested guard compensates for:

- the certificate margin;
- the fallback's final Python certificate, behind the CG true-gradient check;
- the forced certificate step, which affects only budget use;
- the local step-tolerance quiet check, behind the certificate plus forced step;
- the local force-norm guard, behind the residual-energy finiteness check.

## Smallest meaningful independent review batch

1. `pytest -q tests/test_c1.py --junitxml=<fresh dir>/contracts.xml`: fourteen checks, about 5–10 s.
2. Read-only identity check of `evidence/c1_r004/`: `results.json` `file_hashes` should equal the live files and `source/`. Gunzipped states should hash to the receipt's artifact hashes.
3. Read `incremental.py`'s certificate soundness argument against `_apply_structure`/`_relax`. That argument is what the H-L locality claim rests on.
4. Optionally run `.venv/bin/python evidence/c1_claude_review/mutation_checks.py <scratch dir> --live`, about 8 minutes including one 180 s timeout.

Rerun the panel (about 85 s) only after a source change, and only into a fresh directory.
