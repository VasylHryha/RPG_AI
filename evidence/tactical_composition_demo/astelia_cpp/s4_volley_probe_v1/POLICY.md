DECLARED — implementation specification before development fights; one setting only.

This is a scripted feasibility overlay, not an RRG controller. Inputs, parameters and fresh development/engineering entropy are in DECLARATION.json. All four arms share the ten clusters and two orientations; controlled team is always 0. Fixed S4 world, 50 vs50, dt=1/30, 150s duration, game bodies, our default skills with Auto policy; sandboxAbilities=false makes barrage/slow inactive. Historical requests are unmodified.

P0 delegates exactly to the v6 attempt-2 stage-B resonator. P1–P3 call the same v6 prepare first. Gun movement and every other v6 knob stay fixed. Overrides do not read shell trajectories or engine internals.

Chosen gun: retain the living enemy gun while at least one own gun reaches it. Otherwise choose the gun reachable by the largest number of own living guns, then lowest ID. Eligibility uses inclusive native centre distance [minRange,range]. All eligible guns hold target none. Wait begins when eligibility is nonempty, independent of readiness. k=3 off-cooldown guns trigger; otherwise release at the first tick with at least one ready gun after max_hold=1.5s. No-ready cooldown time is not suppressible readiness. Acquire targets for 0.8s (native .7s windup), then return to waiting. A dead/unreachable chosen gun resets the cycle. Target acquisition is synchronized; native release/movement can still stagger or invalidate launches. No teleporting or privileged release.

P1: every eligible gun acquires the chosen gun on the release tick, including still-cooling guns, as requested.

P2: chosen gun plus its two nearest living enemy-gun neighbours (Euclidean distance, ID ties); maximum-cardinality legal matching assigns distinct ready eligible guns to these targets. Require three matched ready guns for a normal release. If the deadline expires, release the feasible smaller matching. Additional eligible guns take the first reachable neighbour (nearest-to-chosen order). Same acquisition tick/window as P1. With fewer than three enemies this naturally releases smaller nets at the deadline. If all enemy guns die, P1–P3 revert to baseline targeting to finish remaining units.

P3: P2 plus direct units = ranged, not melee. With >=4 enemy guns alive, keep baseline direct targeting but park safely located ranged units. Units already inside a band retreat to the nearest safe point of a 20px grid (12px margin); reject a retreat segment entering any expanded band that did not already contain the unit. If no safe segment exists, park. Actual movement, enemy motion and collisions can create band exposure; the report counts this explicitly. At <4 guns direct movement resumes v6. These physical limits prevent an absolute guarantee of remaining outside a moving enemy band.

Stop rows (yes/no):

| Condition | Action | Responsible role |
|---|---|---|
| Projected compute exceeds 3600s? | Stop and report PARTIAL/NOT_RUN | implementer |
| Combat reaches 1200s hard cap? | Kill children and report PARTIAL | implementer |
| Protected source/receipt/knob drift? | Stop delivery | implementer |
| Controller failure or ambiguous shell identity? | Stop and preserve raw evidence | implementer |
| Recheck has a required correction? | Fix before final delivery | implementer |

No tuning, judging, registration, status change or PLAN_CURRENT edit. Recheck tracking is local to this task because the owner's explicit exclusion takes precedence over the repository's plan-tracking convention.
