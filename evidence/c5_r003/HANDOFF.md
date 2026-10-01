# C5 R003: handoff for the independent review

## Identity

| Field | Value |
|---|---|
| Implementer | Claude (claude-opus-5-5) |
| Reviewer | the other model family (Codex): one review, about 15–20 minutes |
| Experiment | `geomind-c5-r4-003`, registered with the code in commit 2b53c54 |
| Responds to | the R002 review, CHANGES_REQUIRED (`evidence/c5_r002_review_codex/INDEPENDENT_REVIEW.md`); decision `docs/decisions/0006-c5-r003-review-fixes.md` |
| History | R001 withdrawn before review (decision 0005); R002 CHANGES_REQUIRED; both receipts preserved |
| `results.json` SHA256 | `e51ec5c1f77f7df215a8b9cb285c0f20d0b9c798125089c04d15a248eda2fc85` (quote it in the review) |

**Pipeline:** one run of `tools/verify.py --milestone c5`. Stage times:
- tests: 4.9 s (46 contracts);
- smoke: 36.8 s;
- mutation: 44.8 s (52/52 detected);
- panel: 287.4 s on 30 fresh final worlds, plus 225 fresh C4 harvest worlds.

## Response to the R002 findings

| Finding | Fix | Contract and evidence |
|---|---|---|
| F1 (high): no published level-2 state | `c5_units.compose_state` builds the parent's `ResonatorState` from its children's states only. Every accepted group stores `level2_state` and `children_states`. `level2_interface` endpoint and gate | `test_parent_state_is_published_with_the_shared_shape` (including recursion to level 3 and consumption by the coarse law), `test_group_runs_publish_the_parent`, the count and gate tests. R003: 17 published for 17 accepted candidates, no problems |
| F2 (medium): crossing hulls passed criterion 6 | Hull-area overlap by exact convex clipping, ≤ 0.2 | Your hexagons through the real `unit_validity` now fail: `test_criterion6_rejects_crossed_hulls_through_unit_validity`. Mutants `hull_overlap_vertices_only` and `clip_drops_crossings` are detected |
| F3 (low): coarse ties took more than k | Exactly k by a stable sort, own neighbours first | `test_coarse_neighbour_rule_takes_exactly_k_with_own_first_ties` (n_p = 8, cross excluded) |
| F4 (low): shared harvest sources | Source-isolated assignment; sources stored per world (`template_sources`); harvest ratio 1.5 | Your split case, through `assign_templates` and `build_worlds`. R003: 0 sources shared across worlds |

## Results (registered rules)

**Implementation gates: all PASS**, including `level2_interface`. Status: **REVIEW_READY**.

**Gate checks:**
- level1_pool: 150/150 units re-detected;
- both controls non-vacuous: 25 imposed candidates each, 0 accepted;
- same_rule_audit: final τ₂/τ₁ = 2.99, within [T/2, 2T].

| Endpoint | Result | Verdict |
|---|---|---|
| Formation (level 2) | 17/30 (Wilson [0.39, 0.73]) | PASS |
| Formation outcomes | FORMED 17, MERGED 4, DRIFTING 9; the C4 component rule sees 17/17 groups as one component | reported |
| Formation vs spread | 0.5δ: 16, δ: 17, 2δ: 16 | reported |
| G→M (s = 1.25) | +0.0307, CI [0.0222, 0.0399], n = 17; complete ablation exactly 0 | PASS |
| M→G (RMS 1.0) | +0.177, CI [0.137, 0.222]; J = 0 exactly 0 | PASS |
| Dose-response | G→M 0.0082 / 0.0307 / 0.0935; M→G 0.031 / 0.177 / 0.610 | PASS |
| Downward effect (b) | 0.029 rad, CI [0.020, 0.040] | PASS |
| Emergent transfer | 0.123 rad, CI [0.099, 0.148] | PASS |
| Effective state | 16/17 within bounds (94%) | PASS |
| Coarse vs full (open-loop) | Gain over no transfer +0.045 [0.031, 0.059]; over rigid +0.218 [0.196, 0.239]; **over relaxation +0.008 [−0.004, 0.019]**; 3/34 excitations flagged invalid | **INCONCLUSIVE** |
| Timescale separation | τ₂/τ₁ = 3.39, CI [2.61, 4.32], 0 censored | PASS |
| Level-2 interface | 17 published, 17 accepted, no problems | PASS (gate) |

**Hypotheses (truth table):**
- **H-M (level 2): SUPPORTED_WITHIN_SCOPE** (row 2). Formation, both causal directions with complete ablations, and both dose ladders all pass.
- **H-C first transition: INCONCLUSIVE** (row 4). Four of five composition endpoints pass. The zero-parameter port coarse law does not beat relaxation with the group's measured τ₂: the CI spans 0.

## Disclose plainly: formation sits near its threshold

Across the three revisions, level-2 formation was 15/30 (R001), 13/30 (R002) and 17/30 (R003). R003's PASS at the registered 0.5 is one draw from a rate near 0.5. R003's support for H-M therefore depends on formation crossing a threshold that its own evidence places near the true rate.

The three revisions differ in design, so they must not be pooled as one estimate:
- R002 used vertex overlap and shared harvest sources.
- R001 used a different dose ladder.

Settings were not tuned between revisions. The R003 changes were the review's fixes, chosen without R003 data. The reviewer should weigh how strongly the support statement should read.

## What the reviewer should check

1. Whether F1–F4 are fixed as the review asked, and whether the fixes introduce new gaps:
   - `compose_state`'s port rule and natural rate;
   - the hull-overlap threshold basis (development 99th percentile 0.100, maximum 0.132);
   - the source-isolation discards.
2. Whether the R003 changes stay within the approved design and the review's scope.
3. Whether the formation-near-threshold disclosure above is adequate.

## Limitations

- **One transition only:** R₀ → R₁, with staged assembly and per-unit rates set as a fixture.
- **Narrow scope:** one model and one parameter set, M = 5, unit sizes 6–16.
- **The C4 view:** the frozen C4 component rule sees every group as one component. The level-2 claim rests on criterion 6 and timescale separation.
- **Ablations hold by construction:** complete ablations remove their pathway, so the evidence is the intact effects and dose ladders.
- **The coarse result:** the port-level coarse law adds no demonstrated predictive value over relaxation with a measured time.
- **Not novel:** hierarchical synchrony and population reduction are known results.
