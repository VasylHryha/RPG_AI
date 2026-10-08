# Owner recheck: Stage A

Disposition: static findings fixed; final reviewer confirmed no material issue remains from this review; focused nonfight checks pass; real-host integration and every fight/training/data gate remain pending.

Reviewer family: Codex. A separate reviewer agent performed the recheck. It was a same-family review, not cross-family acceptance. No numeric quality score was assigned. No fights, training or reviewer test runs occurred.

Owner request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

| Finding | Disposition |
|---|---|
| Missing oracle shell/planner inputs | Copied public snapshot now records all own/enemy airborne shells, team/damage and per-gun launch/splash constants. Both packers consume them. |
| Export returned None | Export returns the exact written payload; five native sequence tests pass. |
| Conflict checks used unobserved fresh world/peer queries | Keys use the actual cached bank, each individual memoryless query, or full joint recurrent prefixes. Float32 input precision is used. The regression changes only a peer query and correctly finds the local unit conflict. |
| Ungated full parity | Whole-job locks, process admission, live RAM/cap monitoring, streamed native RPC, measured five-sequence projection and resumable per-sequence receipts added. |
| Stale records | Reviewer withdrew the original diagnosis: snapshot binding clears records each tick. An additional living-own-ID filter and exact label identity coverage check remain. |
| Stale history control | Fresh pre-tick self history is now a cheap query channel; partner history remains in the declared shared 5 Hz bank. |
| Missing phase/forcing diagnostics | Outcomes report K, effective J and forcing parameter movement. Native fight logs/readouts retain physical phase rates, forcing and spacing, separately from shared react/body behavior. No attack reset exists. These are diagnostics, not coupling-necessity proof. |
| Unmonitored timing sample | Sample uses live TRAIN_CAP reductions and process/RAM monitoring throughout loading, refresh, steps and diagnostics. |
| Resume trusted derived metrics | Completion raw bytes and requests are hash-bound, then reparsed to verify metrics, frame count and public trajectory identity. |
| minRange had HP normalization | Both packers divide minimum range by 100 pixels. |
| Different recurrent-neighbor communication | N1r now receives neighbor mean memory on the same eight-neighbor geometry graph as N2. Whole-policy comparison remains the interpretation. |
| Optional aim head first appeared after an unlabeled occurrence | The SQL record now preserves the first observed value separately for each head. Regression covers no-aim, aim A and aim B under the same actual unit input. |
| Projection omitted shuffled window reloads | Fight order and within-fight windows shuffle identically across arms; each fight loads once per epoch. A measured reload allowance is included alongside refresh, validation and step timing. |
| Expensive ungated audit | Audit now uses whole-job process/lock/RAM/live cap guards, combines heads into one SQL record/unit with batched operations, and projects from <=20 existing shards. Zero conflicts do not prove finite-memory sufficiency. |

Final complete source batch compiled in 24.33 s. Initial focused batch: 11 passed, 1 host-only skip in 6.37 s. The final reviewer then found the optional-aim edge; after that complete correction batch, final focused validation passed 11 tests with 1 host-only skip in 3.06 s. The successful initial run was repeated only because review required a source/regression change. It runs stored synthetic native inference only, zero combat steps and zero optimizer steps. The host-only three-second full-army network integration test is implemented but was not executed because the owner explicitly prohibits sandbox fights. All fit/data/outcome commands retain their host gates.

The task explicitly says not to touch docs/PLAN_CURRENT.md; this file records the recheck and dispositions instead. Existing tracked files, accepted code, engine/adapters and A0 receipts are unchanged. Changed paths appear only in the task's UNCOMMITTED_STAGEA.txt manifest.

Final separate reviewer confirmation: the optional-head merge preserves the first observed value for each head, and the no-aim → aim A → aim B regression covers the reported edge. No material issue remains from this review. Host integration, collection, training and outcome qualification remain pending.
