# Deliverable 1b — corrected, fixture-verified, cross-family re-review pending

The Claude D1 review input and original delivery docs/receipts/exports are preserved under frozen/. Only this pre-data slice was edited. Living external docs are not pinned; other labs, STATUS, docs/PLAN_CURRENT.md and PLAN_CURRENT_APPEND.md were left untouched. No fights, teacher collection, training/optimizer fitting or ES physical evaluation ran.

The single separate same-family recheck is OWNER_RECHECK_D1B.md. Its original CHANGES_REQUIRED snapshot identified B1 (non-gun cache lookup) and B2 (actual drill dispatch coverage). Role guards and real-scaffold D1/D2 fixtures fix both; the final focused tests exercise them. This does not self-approve the cross-family collection gate.

## Finding dispositions

| Finding | Disposition and evidence |
|---|---|
| H1 | Decision-tick opportunity only, including the decision tick's native prep increment. Decoder records/gates opportunity bits, masks share the rule, Cast checks cached bits. Native cooldown+2/winding+3 parity and Python teacher/mask parity fixtures. Automatic ready+6 release remains separate. |
| M1 | One primary per survival/offense axis; participation diagnostic. Whole-draw paired-t intervals, discrete .005/.015/.030 spending over looks50/100/200, .10 margin retained. Equal paired SD≈.20 student reaches NONINFERIOR at200; signed±.10 and margin-exceeding±.20 fixtures. Exact-margin crossing and t-approximation limitations documented. |
| M2 | Eight scripted60-tick actual-overlay coreStep lifecycle cases: start/winding, permission and automatic release, cooldown expiry, entry aim veto, pre-walk target no-launch consumption, walk across aim boundary, death and body bound. Prep increment permits first-ready release; act-entry aim checked before walk; projection says release_pending, actual consume alone logs released. |
| M3 | Both live non-slow shell teams enter PlannerInput; own_shell wire kind/column22, damage/200 column23; unchanged1008width. Encoder parity plus actual teacher projected-shell count test. |
| M4 | Round0 teacher pool retained; all training trajectories weighted by gun-decision rows per round/visitor stratum. No min-cap truncation; empty strata fail. Real teacher visitor test. |
| M5 | Separate neighbor mean8 and per-candidate cosine12 in N1r, no cyclic alias. Slots0/8 opposite-group fixture and native/Python full-sequence parity.72,153 parameters within0.4% of N2. |
| M6 | N1/N1r share A=B=.5/share=.125/J=0 phase-free drift; N2 adds its declared J=.5 phase modulation. Identical drift goal projection under Hold, explicit attribution limits. |
| M7 | D1 actual opponent hold/castOk=false/no shell; D2 native gun decision/prep/lob fire with packs disabled, no opponent planner. Named requests/records/terminal, rear infantry geometry. Two60-tick real-scaffold dispatch fixtures. |
| L1 | Latest cached provisional aim replaces start aim until lock; native fixture asserts replacement then permission lock. |
| L2 | All action fields, goal/multiplier/aim and drift compared across18-tick N1/N1r/N2 sequences. Death pruning plus initial persistent-ID topology remap tested. |
| L3 | Launch-reset action→mode channel declared. frozen_phase and no_reset retain phase at launch; native reset intervention fixture. K0/no_geometry_to_mode still retain reset and are scoped accordingly. |
| L4 | ES evaluated incumbent retained on ties/survival deterioration; common ten-panel IDs enforced across arms/candidates/incumbent; evaluated clipped displacements drive update. Value-only harness/tests. Matched geometry/phase kick harness isolates explicit recorded-context channels; actual ES evaluator/trainer deferred. |
| L5 | Streamed row cap raised to1MiB; bounded unit/threat counts retained, terminal maximum_record_bytes added, projection uses full raised raw reserve. Actual maximum row/RSS/CPU/disk measurement belongs to the authorized timing sample, not this no-fight delivery. |
| L6 | Native worlds vary only enemy energy/cost/skills and RNG; snapshot bytes and policy outputs invariant. |
| L7 | Tactic pairing claim removed; own_guns_alive added beside all-body strict_win. Local PLAN/recheck tracking updated; PLAN_CURRENT_APPEND.md and external plan reserved for Claude unchanged as requested. |
| Recheck B1/B2 | Artillery role guards plus real own/enemy infantry drill fixtures passed; snapshot verdict preserved with implementer disposition. |

## Verification

Native build passed in 28.022s (BUILD_D1B_01 logs). Focused final batch:56passed/1failed in 8.898s wrapper, failure only exact equality of a cosine to1. After adding a1e-12 tolerance, the sole failed test passed in 2.169s wrapper;56unchanged passed checks were deselected. Total57 current cases verified, no passed checks repeated. TEST_ATTEMPT_03 preserves the failure; TEST_ATTEMPT_04/TESTS record the retry. Native receipt includes 183 isolated assertions,18seam ticks, eight60-tick scripted lifecycle scenarios and two60-tick real drill/scaffold dispatch scenarios. No fight outcome metrics read.

One inference-helper warning in the full batch notes float conversion of a gradient-bearing tensor during deterministic goal decoding; fitting uses differentiable logits/dynamics, not this deployment decoder. It had no numerical/parity failure. BUILD.json retains build-time pins; post-build changes were only the failed test assertion and explicit one-test-resume bookkeeping, disclosed in DELIVERY.json. No native source changed after build. Current fixture exports match tested architecture/counts; original exports are frozen.

Projection re-run: feature1008, expected40s decision bytes=1,676,800,000, joint bytes=2,549,760,000, hard150s total disk allowance=1,271,264,105,472 bytes under worst-case1MiB rows. Symbolic CPU/resource projection only; no feasibility or collection approval claimed.

## Next commands — teacher collection

Cross-family re-review and a sealed collection/resource/timing inventory precede execution. An authorized executor supplies SEED,FIGHT,CELL,GUNS,ORIENTATION from fresh collection entropy (never reporting/fixture entropy). The separate <=20-fight timing sample runs first on these actual paths and records terminal maximum_record_bytes plus RSS/CPU/wall/disk before full collection. No dataset packer/trainer or fresh inventory is delivered here.

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
: "${SEED:?sealed seed required}" "${FIGHT:?sealed fight ID required}" "${CELL:?cell required}" "${GUNS:?gun count required}" "${ORIENTATION:?orientation required}"
"$SLICE/_local/mlenv/bin/python" "$SLICE/requests.py" --cell "$CELL" --guns "$GUNS" --seed "$SEED" --fight "$FIGHT" --orientation "$ORIENTATION" > "$SLICE/_local/teacher_request.json"
"$SLICE/_local/build/net_host" --collect < "$SLICE/_local/teacher_request.json" > "$SLICE/_local/teacher_${FIGHT}.jsonl"
```

.git is read-only (`test -w .git` false). No staging or commit attempted. UNCOMMITTED_D1B.txt lists every task file; intended provenance trailer: Assisted-by: Codex:GPT-6.
