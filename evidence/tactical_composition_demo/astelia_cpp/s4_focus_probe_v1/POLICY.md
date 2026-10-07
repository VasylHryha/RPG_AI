DECLARED_BEFORE_FIGHTS

Single-setting descriptive scripted probe of DESIGN_0G 19.2. No RRG controller claim, tuning, registration, judging, status change or PLAN_CURRENT edit. Exact knobs, seeds, timing caps and all scalar parameters are in DECLARATION.json. Same 10 fresh development clusters × 2 orientations × 4 arms × regular/novice = 160 fights, controlled team0, paired seeds. Fixed S4 world: 50 vs50, game rules, dt=1/30s, duration150s, default own skills, Auto policy, sandboxAbilities=false (barrage/slow inactive on both sides). Native preparation, cooldown, reflex, collision, clipping and shell release remain authoritative.

Every arm runs the v6 attempt-2 stage-B resonator. P0 uses the exact original controller. P4–P6 run v6 prepare, then override only the described actions. Base v6 oscillator states and internal target memory remain the baseline computations; actual override targets affect later observed combat. Direct/melee equations and knobs are unchanged, but trajectories and observations naturally diverge across arms.

P4: each own gun independently selects the reachable living enemy gun with lowest remaining HP, ties by lowest id. Reach is inclusive centre distance [own minRange, own range], as the native artillery rule. If none is reachable, keep its complete v6 target choice, including non-guns. Never clear a target to hold or suppress a ready shot. Native windup/energy/cooldown still govern firing; existing windup can release at a changed target.

Shared anchor: lowest-HP living enemy gun reachable by at least one own gun, ties by id. If none is reachable (including no surviving own guns), lowest-HP living enemy gun overall. This resolves the singular 'focused enemy gun' for approach/P6 without changing P4's independent legal selection. Different gun reach sets can produce different focused targets; this is disclosed, not assumed to be perfect collective concentration.

P5: P4 targeting plus each own gun's movement toward a point on the radial line from its focused gun to itself at preferred centre distance max(own minRange, own range − 12px). If it has no reachable gun, use the shared anchor for approach but retain its v6 firing target. Desired goal = enemy position + preferred × normalized(enemy→own); coincident positions use +x. Multiplier1, stop0; multiplier0 only within1e-9px of the preferred distance. This replaces the full v6 gun movement command, including neighbour contribution; native collisions, clipping and reflexes may obstruct it. Direct/melee commands unchanged.

P6: P5 plus living direct/ranged units target the shared anchor if native direct reach permits it (centre distance minus both radii <= own range); otherwise keep their v6 target. Their movement remains v6; melee remains v6. Native line-of-fire blocking still applies and is not visible in this API; target reach does not guarantee a direct shot. No shell or hidden-world input is used.

All enemy guns gone: every overlay falls through to complete v6 actions. No hold windows, readiness thresholds, alternate settings or post-outcome repairs.

Stop conditions (yes/no):

| Condition | Action | Responsible role |
|---|---|---|
| Compute projection exceeds3600s? | Stop children and report PARTIAL/NOT_RUN | implementer |
| Combat reaches1200s or recount1200s? | Stop stage and report PARTIAL | implementer |
| Protected file, knob, source or binary drift? | Stop delivery and preserve evidence | implementer |
| Controller failure or ambiguous shell attribution? | Stop and preserve raw evidence | implementer |
| Required recheck correction? | Fix before dependent work/delivery | implementer |

Reports include elimination wins (enemy0, own>=1, t<150), timeouts, S, both sides' gun casualties, all own losses, targeted shell launches and distinct launches hitting enemy guns, first enemy gun kill time conditional on a kill (no-kill counts explicit), and own gun killers by team/role/id. Raw full30Hz observer data stay local with SHA256. All protected historical outputs must retain identity. Rechecks/dispositions are adjacent because the owner's explicit instruction excludes PLAN_CURRENT edits.
