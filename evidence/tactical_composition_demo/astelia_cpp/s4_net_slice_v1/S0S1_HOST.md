# S0/S1 development handoff

Authority: design revision 3, commit `cac370a4ab08af98d59cccd63ecaa7c3f66a81ac`, decisions 0035–0037 and this owner build request. S0/S1 only; no fits, S2 outcomes, broad C3 panel, hidden enemy inputs or RRG claims. Living documents are not hash-pinned. Existing source, data, receipts and CONTRACT.md remain read-only. PLAN_CURRENT.md is unchanged at the owner's request; the separate recheck and disposition live beside this handoff.

S0 streams the immutable sealed 200-fight collection. It verifies receipts/raw bytes, reports counts by cell/guns/split, old and prospective autonomous input conflicts at stored float32 precision, .02-bin occupancy, full-versus-retained-eight reaction goals and explicit missing group provenance. Decision-level family occurrences are not distinct joint plans. No collision means unresolved coverage. Shift remains dropped. S0 never executes native code.

S1 has four declared cells: D2-2, D2-10, moving/dodging M2-2 and M2-10. Native enemy guns remain the opponent; M2 adds public sinusoidal strafing only when the native decision permits firing, with native shell/cast reactions taking precedence. Own scaffolds are held as in the existing drill. Cooldowns vary .0/.12/.24 s by insertion order, initial prep is zero, both orientations alternate within each paired cell. Native Game rules, 1400×800 arena, 150 s horizon, lob/splash/body/resource/target/aim/release locks are reused. A separate copied planner preserves gun binding and records the source focus and led centre while creating candidates; it cannot derive focus from the unit's provisional target. Only currently startable guns are projected ready. Singles/leftovers are empty, delayed entries are rejected/countable, fewer than two feasible assignments are empty. Commands expire after 3 game seconds and retain focus/shape through windup. At the first release opportunity they refresh exactly once, even when reaction declines release. Script references choose among the declared 33 legal candidates. No learned networks run.

The maximum extent is 20 pairs per cell, 160 arm-fights including the timing sample. Initially collect 10 pairs/cell (80 arm-fights). The sample is exactly 20 arm-fights: 2 pairs in each cell plus one additional pair in each 10-gun cell. Sample fights remain pilot data and are not repeated. Every physical invocation uses the repository process ownership gate and the existing common collection/training locks; discovery failure blocks launch. Cap authority is the owner's `s4_shape_lab_v1/raw/LAB_CAP.json` (currently 10,800 s). Failed attempts count and are retained, with no automatic retry. Project the maximum extent as charged time plus twice the maximum measured sample fight time times remaining fights, and check measured RSS/disk. The factor two is a planning margin, not a proven bound. Runtime timeouts enforce the cap.

Raw, snapped/native and shape-subtracted miss are evaluator-side shadows against the same commanded locked focus. Raw-request and autonomous shadow flight times each use their own distance/lob and observed focus interpolation; native uses its realized landing time. Death/terminal/missing/late-launch reasons retain counts. Admission uses raw conservative miss; intentional shape is no exemption. Sparse matches require coverage work. Spatial assignment change means a focus change or a gun-bound supported point change greater than splash/4 against the autonomous script on the same wrapper-arm state. Physical response requires a root shell more than splash/4 from the same-state autonomous snapped shadow at first release, joined to its root plan/cast. Admission counts the conjunction on at least 5% of commanded decisions; paired cross-arm trajectory patterns stay diagnostic because they can diverge chaotically. Impact counts join actual impacts to those root shells.

Paired spread uses sample SD plus the design's Gaussian chi-square upper SD; constant differences have no zero MDE, censored clear time is diagnostic, exchange uses ratio-of-totals jackknife pseudovalues. All cells/axes and raw draws stay reported. The MDE gate plans detection of a nonzero effect, not 80% probability of the complete useful/CI/harm verdict: the point-threshold rule alone has about 50% probability when the true effect is exactly the threshold. Per-axis candidate-N harm half-widths and point-threshold planning effects are reported as extra diagnostics; no pilot can establish final harm safety. The requested revision-3 raw miss veto is retained, despite the later review’s suggested relaxation; shape and dodge response can make it fail, requiring a prospective owner-approved wrapper/design revision.

The pilot selects at most two cells and records numeric roster/HP effects, final 100/200 N and interval rules; outcome entropy remains held pending a separate S2 allocation/checkpoint contract.

Run these host commands from the repository root. The native build does not run fights. Do not run sample/collect here in Codex's restricted sandbox.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
PYTHON="$SLICE/_local/mlenv/bin/python"
"$PYTHON" "$SLICE/s1_build.py" admit
"$PYTHON" "$SLICE/s1_pilot.py" seal
"$PYTHON" "$SLICE/s1_pilot.py" sample
"$PYTHON" "$SLICE/s1_pilot.py" project
"$PYTHON" "$SLICE/s1_pilot.py" collect
"$PYTHON" "$SLICE/s1_pilot.py" report
```

S1_BUILD.json and its local native binary already exist; `admit` checks them. Rebuilding a genuinely absent build uses `s1_build.py build`, preserving original objects. Stop on any native/gate/projection failure. Read the measured projection and tell the owner its maximum-extent time before collection. Native build measured 11.34 s, no fights. The historical v2 mean is 2.18 s/fight: an unverified initial estimate is about 45 s for sample and 3–6 min for the initial 80 fights; this new script/planner path has not been timed. `project` supplies the measured estimate after the <=20-fight host sample. S0 measured 221.74 s for all 200 logs; focused final tests measured 0.52 s (16 passed, complete reporting batch). Initial failed arithmetic/interpreter attempts and a failed fixture test are retained separately; no fight was executed. The process ownership gate is intentionally not bypassed in the restricted sandbox.

A twenty-pair extension is permitted only for unresolved wrapper coverage or detectability, never to chase a favorable effect. Explicitly name the cells; do not extend a lock/residual/snap/miss failure without a prospective wrapper revision:

```sh
"$PYTHON" "$SLICE/s1_pilot.py" extend --cells M2-2 M2-10
"$PYTHON" "$SLICE/s1_pilot.py" report --cells M2-2 M2-10
```

The second report has a distinct name and preserves the ten-pair report. These example cells must actually meet the extension reason. Enemy native player-shot dash events are counted as required by decision 0037’s addendum; zero are expected, and shell avoidance is public stepping, not dash-readiness evidence. Before any S3 work, the owner must approve a replacement privileged variable that actually affects shells.

No later training/validation/outcome seed pool may reuse S1_PILOT_SEED_EXCLUSIONS.json. Commit raw pilot evidence or a complete hashed host evidence inventory and the compact JSON/markdown together before others build on pilot selection. Pilot evidence cannot certify S2 or tactical utility.

## Delivery and commit boundary

S0 output and its three source dependencies are staged. The sandbox rejected the commit with `fatal: Unable to create .../.git/index.lock: Operation not permitted`. Finish the required S0 commit on the host; these explicit paths exclude unrelated work:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
git add "$SLICE/s0_analysis.py" "$SLICE/s0_arithmetic.py" "$SLICE/s1_public.py" "$SLICE/S0_ANALYSIS.json" "$SLICE/S0_ANALYSIS.md"
git commit -m "Add read-only S0 collection-v2 analysis" -m "Assisted-by: Codex:GPT-6" -- "$SLICE/s0_analysis.py" "$SLICE/s0_arithmetic.py" "$SLICE/s1_public.py" "$SLICE/S0_ANALYSIS.json" "$SLICE/S0_ANALYSIS.md"
```

S1 is build/test ready for the host timing sample, not empirically admitted. The script generates its measured maximum-extent projection only after that <=20-fight sample. Expect seconds for admit/seal/project, about 45 s initially estimated for the sample, and 3–6 min initially estimated for all 80 initial arm-fights; refresh both fight estimates from PROJECTION.json before proceeding. `report` is read-only over hashed pilot receipts and should take seconds. The four-cell cap and at-most-two tactical-cell freeze remain operative.
