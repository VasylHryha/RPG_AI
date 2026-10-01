# C4 R003: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c4-r4-003`, registered in commit e796226; contracts completed in the next commit (manifest unchanged) |
| Responds to | the R002 review, CHANGES_REQUIRED (`evidence/c4_r002_review_codex/INDEPENDENT_REVIEW.md`); decision `docs/decisions/0003-c4-r003-review-fixes.md` |
| `results.json` SHA256 | `5a95025fc65487e00cf1012044535745fe212077d9b2f0ed2683b5ad6b42b1ab` (quote it in the review) |

**Pipeline:** `tools/verify.py --milestone c4`.
- **First attempt:** stopped at the mutation stage. The `hm_ignores_dose` mutant survived because a truth-table row was missing from the contracts. The panel did not run and no final world was simulated.
- **Fix:** the row was added in its own commit.
- **Successful run:** tests 6.0 s (26 contracts), smoke 8.1 s, mutation 78.3 s (32/32 detected), panel 119.9 s on 20 + 20 fresh final worlds. The machine was heavily loaded (load average about 70).

## Response to the R002 findings

| Finding | Fix | Contract and evidence |
|---|---|---|
| R1: recovery accepted fragmentation | The original members must be matched (Jaccard ≥ 0.9) in both the control and the kicked future, and the two matched components must agree. Each candidate's receipt stores `recovery_original_to_control`, `recovery_original_to_kicked` and `recovery_control_to_kicked` | Your reproduction is `test_recovery_rejects_a_group_that_fragments_in_both_futures`, with a positive control. Mutant `recovery_ignores_original` is detected. In R003 the identical arm had 0 of 39 candidates fragmenting; the heterogeneous arm had 7 of 44, all rejected |
| R2: conflicting formation rule | Explicit truth table in the manifest (`verdict_rules.truth_table`). Formation failure makes H-M INCONCLUSIVE, as in the approved proposal. Decision 0003 corrects the misstatement in 0002 | Every row is tested; mutants `hm_ignores_formation`, `formation_fail_not_supported` and `hm_ignores_dose` are detected |
| Observation: vacuous clump control | The clump endpoint reports NOT_TESTED without candidates; the gate needs a non-vacuous PASS in the identical arm | Both clump controls were non-vacuous in R003 (20 and 5 candidates, all rejected) |

## Results (registered rules)

**Implementation gates: all PASS.** Status: **REVIEW_READY**.

**Numerical checks:**
- RK4 error ratio: 17.1.
- Switching-limited dt error: ≤ 5.3e-4.
- Equivariance error: ≤ 7.1e-15.

### Identical-ω arm (primary)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 20/20 (Wilson 95% CI [0.84, 1.00]) | PASS |
| G→M | +0.0132 rad, CI [0.0120, 0.0145], n = 20; complete ablation 0 | PASS |
| M→G | +1.153 peak relative Rg, CI [0.94, 1.38], n = 20; J = 0 ablation 0 | PASS |
| Dose-response, G→M | 0.0060 → 0.0132 → 0.0322; high − low CI [0.023, 0.029] | PASS |
| Dose-response, M→G | 0.056 → 0.301 → 1.153; high − low CI [0.89, 1.33] | PASS |
| Not a clump | 20/20 rejected (all by criterion 5) | PASS |
| Effective state | 39/39 units within bounds | PASS |

G→M channels (descriptive): with only w = 1, 23% of the effect remains; with only the frozen topology, 94% remains.

**Hypotheses:** H-M **SUPPORTED_WITHIN_SCOPE**, H-C precursor **SUPPORTED_WITHIN_SCOPE**.

### Heterogeneous-ω arm (reported separately)

| Endpoint | Result | Verdict |
|---|---|---|
| Formation | 5/20 (CI [0.11, 0.47]) | FAIL |
| Causality and dose-response | n = 5 < 10 | INCONCLUSIVE (point estimates in the predicted direction) |
| Not a clump | 5 candidates, all rejected | PASS |
| Effective state | 4/5 units within bounds | FAIL |

Hypotheses: H-M INCONCLUSIVE (formation failure, per the truth table), H-C precursor NOT_SUPPORTED.

## Caveats (unchanged in kind)

1. **Complete ablations vanish by construction.** The evidence is the intact effects and the dose-response.
2. **R003 follows two earlier revisions.**
   - R001 was withdrawn before review; R002 received CHANGES_REQUIRED. Both are preserved.
   - Detector thresholds, model, doses and bounds are unchanged since R002. R003 changes only the recovery rule, the verdict table and the clump-vacuity handling.
3. **The identical arm is a synchronizing fixture.** Its frequency is 0, and G→M is measured through a probe kick.
4. **Scope.** This is known swarmalator dynamics: one N, one parameter set and one neighbour rule. It makes no novelty, hierarchy, task or efficiency claim.
5. **Generic closure is not shown.** The heterogeneous arm rarely forms resonators under the registered thresholds.
