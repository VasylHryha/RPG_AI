CHANGES_REQUIRED

Reviewer family: Claude (claude-opus-5-5); implementer family: Codex
Reviewed commit: b9579dc (`evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2/`)
Date: 2026-10-09
Scope: a read-only development recheck for the owner, capped at about 20 minutes. No Python, tests, builds, training or fights were run, and no `_local/` was touched. A stage B training run is in progress. The governing documents are decisions 0039, 0035, 0036 and 0038 (addenda 1–2), STAGEB_DIAGNOSIS and STAGEB_PROTOCOL. I also read Codex's OWNER_RECHECK_STAGEB2.md and INDEPENDENT_REVIEW.md.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## What holds

- **Pure tools.** `tools.py` and `tools.h` are pure. They hold no world handle, RNG, labels or fire rule. Both twins check every input for finite values. The math in the protocol table matches the code: lead, flight time, range projection, splash, clusters, dodge spot, behind-friend and threat. No react, V2 or P16 logic leaks in. Neither twin contains an argmin over safety or a trigger.
- **Python/native parity.** The Python `bank` and native `candidates` produce the same candidates in the same order with the same features. I checked all of these:
  - the windup law `(windup-prep)+/timeRate`;
  - lob and splash ×100;
  - hazard parsing for shells, shots, casts and fields;
  - feature 14 (splash fraction over predictions);
  - feature 15 (enemy threat at a 0.5 s lead with `max(1,reach)` and `max(.001,cdMax)`).
- **Labels and leakage.** Label mapping reads only the public frame. The teacher's executed command is used only as the label. The candidate bank reads no teacher fields.
- **Shadow labels in learned-dodge.** `shadow.cpp:14` swaps in a fresh `oracle` controller that has no `stage.weights`. The patched `react.cpp` and `react_rules.cpp` lines (`native_patch.py:29-32`) key off the executing controller's weights, so O's shadow labels keep their react dodges in learned-dodge DAgger. This is correct.
- **Protected sources.** Commit b9579dc touches no files under stagea/, stageb/ or rev2/. All 64 entries in `PROTECTED_SOURCE_BASELINE.json` match their current shasum. The untracked `stagea/PARITY_STAGEA.json` is not part of this commit.
- **Pairing.** `readout_run.py` pairs B2, Stage B network-only, the react-ON parent, O and T. Every policy in a pair shares the same seed, cell and orientation.
- **RRG claims.** The RRG note is honest. It explicitly does not claim `B_n→R_n→B_{n+1}`, recursion, self-recreation or superiority.

## High

### H1: a linear candidate scorer with no entity binding cannot select most enemy-specific candidates, and aim is decoupled from the target pointer
- **Where:** `models.py:70-71` (`logits=(features*scorer(h)[:,None,:]).sum(-1)/4`) and `native_patch.py:15` (`toolScores`). The features are listed at `candidates.py:52`: type one-hot, dx, dy, dist, splash fraction and threat.
- **Problem:** The score is linear in a 16-feature descriptor, so argmax can only ever return a vertex of the convex hull of the candidate feature vectors.
  - Consider the per-enemy direct, lead, band, approach and flank candidates. Within one type, they differ only in (dx, dy, |d|, splash, threat).
  - Take enemies on the same bearing at different ranges. They lie on a line in (dx, dy, |d|). A middle candidate is unselectable for every h unless splash or threat happens to lift it out of the hull.
  - The descriptor carries no identity or encoder embedding of the source enemy. The aim choice therefore has no access to the pointer's entity representation, and it is independent of the `target` head.
- **Failure scenario:** O artillery aims at the lead of enemy j, which is not a hull vertex. Coverage reports it as covered within 20 px. CE still cannot fit it, and stage B's "~99.7% aim wrong" persists under a new mechanism. Coverage cannot detect this, because it measures availability, not selectability. The protocol says so itself (STAGEB2_PROTOCOL.md "not that the linear candidate scorer can learn every label").
- **Fix:** Make candidate scores entity-aware, pointer-network style:
  - Give each candidate a source index (enemy, friend, hazard or none).
  - Score it as `w(h)·f_i + k(h)·encoded[source_i]/8`. This is the same bilinear form the target pointer already uses at `models.py:58`.
  - Add a small MLP over [f_i, h], or at least the pairwise product terms, so non-hull candidates become reachable.
  - Optionally add the target logit of `source_i` to the aim score. Aim and target then form one coherent decision without a scripted rule.
- **Tests:** Mirror the change in `toolScores`. Add a light fixture with three collinear enemies in which the middle lead point must be selectable.

### H2: the dodge vocabulary and features do not match O's known dodge geometry, and threat ignores hazards
- **Where:** `candidates.py:70-77` and `candidates.h:36-42`, compared with O's react in `s4_shape_lab_v6/build/react.cpp:43-66` (the source copied into the army build).
- **The mismatches:**
  - **Shots.** O moves `pos ± perp(shot.direction)*30` px. B2 emits a perpendicular step of `max(60, speed*.5)` ≥ 60 px. The nearest candidate is therefore at least 30 px off, which is outside the 20 px tolerance. Along an axis it is also not representable with the 24 px per-axis offset.
  - **Slow fields.** O moves radially away by 40 px: `pos + delta*(40/d)`. B2 emits only perpendicular steps of field radius + r + 12. No radial candidate exists.
  - **Shells and casts.** O evaluates 16 directions × extents {1, .6}·max(8, speed·(t_impact+.1)). B2 emits two perpendicular steps of splash + r + 12. They match only by coincidence.
  - **Enemy-motion "dodge" candidates (type 10 per enemy).** They do not correspond to any O behaviour.
  - **Feature 15 (threat).** It sums enemy units only (`candidates.py:86-89`, `candidates.h:28`). The descriptor has no feature for shell, cast or field exposure, so even a correct dodge point looks identical to an unsafe one.
- **Failure scenario:** Round-0 coverage shows a low dodge-row coverage. If it is read past, as H3 below allows, the learned-dodge arm trains on labels its vocabulary cannot express or discriminate. The arm then fails for a vocabulary reason, not a learning reason.
- **Fix:** Add pure geometric candidates that mirror the known public geometry, with no argmin:
  - ±30 px perpendicular to each public shot direction;
  - a radial 40 px step away from each field;
  - for blasts, a 16-direction ring at the two time-scaled extents, emitted once per unit, not per hazard, to bound the count.
  - Add a pure **blast-coverage count at the candidate** feature (count of shell or cast disks of radius+r+4 containing the point) and a time-to-first-impact feature.

  Choosing among these stays learned, so this complies with 0039 §2. Re-derive `MAX_MOVE` afterwards.

## Medium

### M1: the coverage stop condition is not a yes/no row, and training does not gate on its value
- **Where:** `train.py:49-50` checks only `status=='DONE'` and identity. The protocol row reads "Coverage materially incomplete…", with no threshold.
- **Problem:** AGENTS.md requires every stop row to be a yes/no question.
- **Failure scenario:** Any coverage value, including 0% on artillery aim or dodge rows, admits training.
- **Fix:** Pre-register numeric thresholds per role, head and category on the train split, for both candidate-only and bounded-residual coverage (for example ≥ 0.90 overall and ≥ 0.80 on dodge rows; the drafter chooses the values). Then refuse in `train.py` when any threshold fails, and record which ones.

### M2: coverage measures a different label than training fits for N2
- **Where:** `coverage.py:8` calls `mapped_labels(row, ids)` with no drift. `loss.py:32` subtracts the detached N2 drift before nearest-candidate mapping.
- **Problem:** For N2, the coverage denominator and the fitted residuals are different quantities.
- **Fix:** Report both the raw-goal coverage and the drift-adjusted coverage for N2 after round 0, using drift from the current checkpoint during DAgger rounds. At minimum, state this explicitly in the receipt's interpretation string.

### M3: the learned-dodge arm removes two things at once
- **Where:** `native_patch.py:29-32` turns off both the react goal layer and the body dash reflex (`gameReflexes`).
- **Problem:** Dash is a body skill outside the network's action space, like guard, which is kept. Removing it confounds "can the network copy react dodge" with "losing an uncopyable body skill". The protocol admits the confound, but the design does not separate it.
- **Fix:** Keep dash ON in the learned-dodge arm, so the only change is the react movement layer. That answers the owner's question ("can't we copy dodge with the network?"). Alternatively, add a react-ON/dash-OFF control on the same paired seeds.

### M4: the readout has no dodge-specific outcome measure
- **Where:** `readout_run.py:10-27`. It counts dash events (`dodges`), react rows, deaths and damage, but not damage taken by hazard source.
- **Problem:** The learned-dodge arm has react OFF, so `react_rows` is 0 by construction. Win and death totals cannot attribute a difference to dodging.
- **Fix:** Add own damage taken per source type (shell, shot, cast, field, melee), per role. On O-shadow `active` rows, add the fraction where the student's executed endpoint at impact time is outside the blast disk. This is the executed-action check the protocol already asks for, made a registered readout field.

### M5: "behind friend" for melee collapses to the enemy centroid
- **Where:** `candidates.py:68` and `candidates.h:35`.
- **Problem:** The behind-friend point is projected into the unit's own weapon band around the enemy centroid. For melee (lo=0, hi=reach of a few tens of px), every behind-friend candidate lands within reach of the centroid, which may be empty space between enemy groups. That is the opposite of rotating behind friends (owner rule: damaged units rotate, they do not leave).
- **Fix:** Also emit the unprojected (box-clamped) behind-friend point as a separate type, and let the network choose.

## Low

- **L1: wrong capacity claim.** `MAX_MOVE=996` (`candidates.py:8`, `candidates.h:5`, protocol) is stated as the bound at 64/64/64/64/32/32. The actual maximum is 1 + 5·64 + 63 + 2·64 + 2·192 = 896. This is harmless padding, but the stated bound is wrong. Correct the claim, or derive the constant in code, also in `native_patch.py:21` (`1194`).
- **L2: friendly shells as hazards.** Hazards include own-team shells (`candidates.py:72`), while O's react uses enemy shells only (`shadow.cpp:57` keeps `a[7]==1`). This adds noise candidates. Filter by team, or add a team bit to the descriptor.
- **L3: duplicate candidates.** Type 5 (band) and type 7 (approach) coincide whenever the unit is outside the band (`candidates.py:64-65`). The label always goes to type 5 (first tie). The duplicate costs capacity and makes the type-7 statistic uninformative. Drop type 7, or define it as the inner-edge approach.
- **L4: lead velocity differs from O's.** Lead uses instantaneous `velocity`, while O's live artillery aim uses smoothed `longVelocity` (see `shadow.cpp:63`, reconstruction note). Expect systematic lead offsets on manoeuvring targets. Coverage will show them. If it does, add a lead candidate from a public smoothed velocity, if one is observable.
- **L5: stale hazard tokens.** Hazard tokens refresh only at 5 Hz or on a unit-set change (`training.py:59`, `models.py:24`). A new shell can therefore be invisible to attention for up to 0.2 s, while candidate features are per tick. This cadence is inherited from 0038 addendum 2. After H2, the per-tick blast feature mitigates it. Note the limit in the protocol.
- **L6: cap source not stated.** DAgger uses `r.collect.a0().owner_cap()` (`dagger.py:56`), not a B2-specific cap. The protocol says B2 needs its own owner cap authority for training. State explicitly which cap governs B2 DAgger and look fights.

## Disposition requested

Fix H1 and H2 in one batch, together with M1, M3 and M5. Then run the focused light tests once at the end of the batch, including the new collinear-selectability and dodge-geometry fixtures. Re-run round-0 coverage before any B2 training. M2, M4 and the Low items can go in the same batch. No numeric quality score is assigned.
