READY_TO_RUN

# Section-16 attribution, Part 1

One sequential native build passed in 24.38 seconds. The one affected test batch passed: 30 tests in 1.42 seconds (1.68 seconds including process startup). Synthetic legacy comparison verified 16290 v0–v4 action outputs and exact numeric bits against the pre-change controller. Design review is APPROVE_WITH_NOTES; implementation recheck findings are resolved. No fights or tuning have run. Do not run while C6 quiet-machine timing is active.

Exact future run command from repository root, after C6 timing finishes:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_attribution.py --execute --quiet-machine-finished --workers 10 --output evidence/tactical_composition_demo/astelia_cpp/s4_attribution_development
```

Cost: exactly 3,200 fresh development fights, including 80 regular trace captures (five common seeds × two orientations × two arms × four cells). The design estimates about ten minutes at the historical ten-worker rate. Allow roughly 10–30 minutes for streaming/compression and the new fixed-knob trajectories; this is an estimate, not a new timing measurement. Absolute cap is 60 minutes. One worker could exceed that cap. No tuning, extra replay captures, judging or S5 execution.

v3, H (hold only), F (focus only), HF (alias of historical v4) use the exact v3 stage-B B_best.json resonator/morale knobs in every cell. Historical safety defects remain deliberately present for attribution. No v5 rule is included.

The reserved ledger is S4_ATTRIBUTION_SEEDS.json. INPUT_PIN.json binds the design, review, knobs, ledger and runner helpers. Native admission additionally pins binary/build/source identity. The runner defaults to declaration only, requires explicit execution and quiet-machine completion, refuses pre-existing output and atomically marks the ledger used before any fights. Do not rerun the same development ledger after a partial attempt. Raw compressed traces, raw fight rows, hashes and endpoints are retained in the fresh output.

Counters: unit_intent_proxy_changes uses latent c hysteresis, initialize c≥0 and switch c>0.2/c<−0.2; pair_mode_changes counts each pair separately; unit_ticks_with_pair_mode_change counts at most once per own unit/tick. Focus-while-escaping uses the latent proxy; the narrower c<−0.2 count is also kept. These are not physical movement reversals. Expiry-inside-gun-reach uses prepare geometry and live enemy artillery's native legal annulus, between minimum and maximum range, inclusive, excluding the dead zone. Hold death releases count pair events, split own/enemy/both/missing and terminal reconciliation; living-pair holds are censored at terminal state. Full section-15 decision rows and undefined feasibility reasons remain in raw traces.

Statistics: S is own survivors minus enemy survivors. Average both orientations within each seed; descriptive normal 95% intervals use 100 seed clusters. Report all six paired cell contrasts and HF−H−F+v3 interaction per arm/head, gun survival and timeouts. No acceptance verdict. Conclusions concern fixed-v3-knob mechanism effects, not exact decomposition of the historically independently retuned package regression or selection of v5.

Validation scope: synthetic prepare/decide snapshots, exact action output/IEEE bits against namespace-isolated pre-change controller, cell isolation, old v4 hold contracts, clone cleanup, gun annulus, factory/configuration admission, counter/terminal cases, allocation/statistics/deadline/fake-worker tests. Full historical combat-summary fixtures are not rerun under the owner's no-fights instruction; their preservation is supported by unchanged engine rules and synthetic controller comparisons, not a new full combat replay.

Plan/recheck disposition: s4_attribution_checks/PLAN_AND_REVIEW.md. Root docs/PLAN_CURRENT.md is outside the user's permitted edit scope; paste-ready B3b status is recorded in the scoped plan. Independent Claude implementation review remains separate from Codex's review of Claude's design and the additional Codex recheck.
