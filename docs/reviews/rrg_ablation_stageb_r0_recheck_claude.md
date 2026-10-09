CHANGES_REQUIRED

Reviewer family: Claude (claude-opus-5-5); implementer: Codex
Reviewed commit: b83f7914f5b58145d675bc656a4b415967c269d9
Reviewed folder: `evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/rrg_ablation/`
Date: 2026-10-09
Scope: read-only owner recheck (request below, verbatim). I read the code and ran small JSON reads only. I did not run inference, training or tests. `RRG_ABLATION_STAGEB_R0.json` sha256 per provenance: `64c1c652fcca0c48d72eb05733abe4b8fc1eee1f8f63458c858d7540d781bc93`.

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Summary

The replay itself is sound. The interventions match their descriptions. Rows, windows and checkpoints are identical across arms, and the original outcome counts reproduce exactly. The measured numbers can be trusted.

The interpretation cannot be trusted yet. N2's target head has a hard-wired extra input that N1, N1h and N1r do not have: an exact-equality "which enemies are my neighbours currently targeting" bonus (+2 logits). Its strength depends on phase alignment between neighbours. K=0, frozen phase and no-geometry→mode all break that alignment. The same accuracy collapse would therefore happen if phase dynamics carried no information at all and coupling only acted as an on-switch for this engineered peer-assignment feature. The validation history fits that simpler reading: N2 already led by +8.7 pts (ranged) after epoch 1, while K was still at its initial value. The commit-message claim "first evidence that the geometry-driven phase coupling (not memory) carries the gain" is not supported until this confound is controlled. The Markdown report's own wording is more cautious, but it does not name the confound.

## Findings

### High

**H1. The N2 target head receives a privileged peer-assignment feature, gated by phase synchrony, which no control arm has.**
- Where: `stagea/models.py` (N2 branch), reproduced in `rrg_ablation/ablation_model.py` lines ~91-97: `peers = mask & (assignments[order]==target_id)`, followed by `targets[:,e+1] += 2*(z·group/|group|)`. Native: `stagea/stagea.cpp` line 97 (`+align[i][e]`). `assignments` comes from `stagea/data.py` line 48 (`u[15]`): each own unit's current engine target, taken from the pre-decision snapshot.
- What it is: for every enemy e, N2 gets an exact integer-equality indicator showing whether any of its up to eight neighbours within 300 px is currently assigned to e. It is weighted by the cosine between the unit's phase and that peer group's mean phase. The coefficient 2 is fixed, not learned. N1, N1h and N1r see targets only as the scalar `target/256` in tokens (and in their own query), reached through soft attention. To use that, a pointer head would have to learn an equality match between scalar IDs, which is hard. N1r is even packed with `assignments` (`data.py` line 92) but never uses them (`models.py` N1r branch). The protocol says "N1r and N2 use the same 136-coordinate readout input" (`stagea/STAGEA_PROTOCOL.md` line 5). That is true of the 136-vector but omits this extra target-logit readout and the fire readout. The input table (lines 7-12) does not list neighbour assignments at all.
- Failure scenario: a teacher that focus-fires and keeps its targets makes neighbours' current targets a strong predictor of a unit's next target. With K≈1 from initialisation, coupling pulls neighbouring phases together, the cosine approaches 1, and the bonus works as "+2 for enemies my neighbours are hitting". With K=0, frozen phase or omega-only, phases stay at their golden-ratio ID spread. The bonus becomes a ±2 term that is close to random. The gain disappears, and it falls *below* N1 where the noise hurts: K=0 is lower than N1 in 30 of 50 fights for artillery (median −2.0 pts). The JSON shows exactly this pattern, so the results do not separate "phase dynamics carry the information" from "phase is a synchrony gate for an engineered feature".
- Supporting evidence (validation history, `stageb/_local/round0/training/*.outcome.json`): at epoch 1, ranged/artillery target accuracy is N2 .682/.624 against N1 .595/.528 and N1r .596/.527. N2 at epoch 1 is already above N1's final ranged accuracy (.666). Learned K only moved from 1.000 to 1.009 and omega from 0 to 0.026 rad/s. The advantage is present before the coupling law has learned anything, which points to a structural readout rather than learned resonance.
- Fix: run the decisive control below before any mechanism claim, and add the peer-assignment readout to the protocol input table as an N2-only input. Treat a retrained N1 + peer-assignment indicator arm as the architecture-level control.

**H2. The commit message overstates the result and contradicts the data.**
- Where: commit b83f7914 subject: "first evidence that the geometry-driven phase coupling (not memory) carries the gain".
- Conflicts:
  - **"Geometry-driven":** the topology-only freeze keeps most of the gain (−1.5/−0.7 pts), and no-geometry→mode is not a separate geometry cut (see M1).
  - **"Not memory":** the phase is itself recurrent state, and N1r is not a valid memory control because it lacks the peer-assignment readout (H1).
  - **"Carries the gain":** H1 has not been ruled out.
- Failure scenario: later stages (B2 training, owner decisions, the roadmap) cite this commit as mechanism evidence for RRG resonance, when the effect may come from a hand-wired neighbour-target feature.
- Fix: committed history cannot be rewritten. Add a short correction note in the folder (for example `RRG_ABLATION_STAGEB_R0_CORRECTION.md`) and in `docs/PLAN_CURRENT.md` / `docs/IDEAS_AND_ROADMAP.md`, stating the bounded reading: "N2's gain requires neighbour phase alignment; whether alignment carries information or only gates the engineered peer-assignment readout is untested." Reword the conclusion paragraph of `RRG_ABLATION_STAGEB_R0.md` in the same way, through a report-only regeneration, as was done before. Do not touch the metrics JSON.

### Medium

**M1. The three "distinct" dynamics cuts are effectively one intervention, so they do not corroborate each other independently.**
- Learned omega is 0.0257 rad/s. With no-geometry→mode, every phase rotates by the same tiny common amount. Relative phases equal the frozen ones, and the JSON phase statistics for `N2_frozen_phase` and `N2_no_geometry_to_mode` are identical (ranged R .118, artillery R .069, same early/middle/late values). The target-alignment readout depends only on relative phase, so ranged target accuracy is 0.6529 in both arms. no-geometry→mode also zeroes K, so it includes the K=0 cut. A forcing-only cut (phase forcing set to 0, K kept) was never run, so the separate contribution of geometry and inputs to the phase was not tested.
- Failure scenario: a reader counts "three independent cuts all erase the gain" as triple confirmation, when in fact a single fact (alignment broken) was observed three times.
- Fix: say this explicitly in the report. If a geometry→mode claim is wanted, add a forcing-only cut (`phase_forcing=0`, K intact).

**M2. No control perturbs phase by an equal amount while keeping its structure.**
- Every dynamics cut both removes synchrony and moves the checkpoint into a joint state (late-fight tokens with dispersed phases) that it rarely met in training. Intact R rises from about .27 early to about .85 late. Frozen phase holds R near .07-.12 throughout. Dispersed phases did occur early in training, which weakens a pure off-distribution explanation but does not remove it. A phase shuffle across same-role units on each tick (marginal kept, pairing destroyed) and a forced-synchrony arm (all θ equal) are missing. The forced-synchrony arm matters most (see Decisive control).
- Fix: run the decisive control below. Optionally add a shuffle arm.

**M3. The protocol and fairness statement are incomplete about the N2-only readouts.**
- `STAGEA_PROTOCOL.md` describes equal parameter inventory and the "same 136-coordinate readout input" but not the two hard-wired N2 readouts: target alignment (H1) and the ±2·cos θ fire window. Training was otherwise matched: same budget sha, 3,200 gradient steps, 9,553,400 decision rows, selected epoch 10 for every arm, same rows and windows in this replay, and equal registered parameters. Fire accuracy shows no N2 advantage, so the fire readout is not the issue here. The target readout is.
- Fix: list both readouts as N2-specific inputs in the protocol and in every future N1-versus-N2 comparison report.

### Low

- **L1:** every arm selected its last epoch (10 of 10), so all were still improving. N1 was flattening (ranged .662-.666 over epochs 7-10). The comparison holds at a matched budget, not at convergence. Say so.
- **L2:** one checkpoint per arm, one training seed. Per-fight consistency is strong (N2 > N1 in 50/50 fights for both roles; minimum +1.2/+0.1 pts), but seed-to-seed variance of the gain is unknown.
- **L3:** the earlier recheck in `OWNER_RECHECK.md` was same-family (Codex reviewing Codex). AGENTS.md prefers the other family. This review covers that gap.
- **L4:** `docs/PLAN_CURRENT.md` and `docs/IDEAS_AND_ROADMAP.md` were not updated with this result or its limits ("docs/PLAN_CURRENT.md was not touched"). Add the bounded result together with the H2 correction.
- **L5:** topology-only also changes which peers feed the H1 readout (frozen first-tick edges). Its survival shows that the readout still works with original neighbours. It does not show that geometry is irrelevant or relevant. The report's current wording is acceptable, but this point should be stated.

## What checked out (questions 1 and 3)

- `ablation_model.py` differs from the pinned `stagea/models.py` only by the switch blocks: graph freeze, phase_forcing/K zeroing, the frozen θ update, drift zeroing and diagnostics. The intact path is tested as bit-identical over 20 ticks.
- `check.py` verifies training-source pins, the split, `TRAIN_BUDGET` windows, checkpoint/export identity and raw shard hashes. It reproduces original test counts exactly for N1, N1h, N1r and N2. The same `selected_starts` windows and full-prefix replay are used for every arm. The reset-disabled and drift-only identity reuses are structurally valid and asserted.
- Target accuracy uses argmax with no threshold, so the target comparison involves no threshold issue. Fire calibration uses each arm's own unchanged validation thresholds.

## Recommended decisive control

**Synchrony-gate substitution on the same N2 checkpoint, offline, with no retraining.** Add one arm, `N2_indicator_no_phase`. Run the phase dynamics as K=0 (or frozen), so phases carry no coupling information. Replace the target-alignment term `2*(z·group/|group|)*(|group|>0)` with its fully synchronised value `2*1[any masked neighbour assigned to e]`. Keep everything else, including the head's phase features, exactly as in the K=0 arm.

- If this arm recovers most of the +14.8/+15.5 pt ranged/artillery gain, the gain is the engineered peer-assignment readout. Phase coupling then only acts as its on-switch, and the "phase coupling carries the gain" reading is refuted.
- If it recovers little, and intact clearly beats it, then which neighbours are phase-coherent carries information beyond who targets what. The resonance reading is then substantially strengthened.

Cost: one extra arm on the same 50-fight replay, on the order of minutes on top of the existing ~12-minute replay. A mirror arm, intact dynamics with the peer-assignment term removed, is cheap to add in the same run. At architecture level, the follow-up is a retrained N1 with that same indicator, at the same budget. A one-pass data statistic needs no model at all: the share of ranged/artillery test rows whose label target is among the masked neighbours' current assignments. It shows how much of the gain this feature could explain at most.
