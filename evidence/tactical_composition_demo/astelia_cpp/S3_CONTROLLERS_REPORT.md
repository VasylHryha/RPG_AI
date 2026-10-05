NOT_READY

S3 stopped at the contract check, 2026-10-05. Author family: Codex (GPT-6).
This is an implementation handoff report, not independent acceptance or experimental evidence.

Starting HEAD: `dae8c555a9ed8daa0eefc2424f537f3fa8d8d3de`.
The working design matches the revision-2 contract committed at `3a29450`.
The only pre-existing dirty path was the untracked
`docs/reviews/tactical_0g_design_review_codex.md`; it is preserved and excluded from this commit.

The explicit stop instruction in [S3_CONTROLLERS_REQUEST_CODEX.md](S3_CONTROLLERS_REQUEST_CODEX.md:6)
applies: “If the design is wrong or ambiguous anywhere, stop and write it in the report. Do not choose silently.”
The following issues require the drafter to correct the executable contract and record their causes in its self-audit.
No controller implementation, build, test suite, fight, tuning or recorded run was performed in this session.

## Blocking design questions

1. **The requested C4 RK4 reference is a different integration problem.**

   [DESIGN_0G.md](../DESIGN_0G.md:114) requires phase integration with positions frozen at the snapshot.
   Section 8 check 1 ([line 200](../DESIGN_0G.md:200)) nevertheless requires its RK4 step to equal
   `c4_reference/c4_reference_states.json` to `1e-9` with positions held.
   The reference generator calls the accepted model's full `rk4_step`
   ([make_c4_reference.py](../c4_reference/make_c4_reference.py:47)). That function advances positions
   at every intermediate stage as well as phases ([c4_model.py](../../../geomind/c4_model.py:105)).
   Its phase derivative recomputes `exp(-r*r)` from those intermediate positions
   ([c4_model.py](../../../geomind/c4_model.py:100)). Holding neighbor indices does not hold positions or distance weights.
   Thus the stored `th_after_step` is not an oracle for the requested frozen-position phase step.
   This conclusion is from source inspection; no numerical discrepancy was measured and no test failure is claimed.

   There is also a near-contact law difference: S3 fixes `epsilon=0.01` and uses a true unit vector
   ([design line 82](../DESIGN_0G.md:82)); the accepted model fixes `epsilon=1e-6` and computes displacement divided by
   `max(r, epsilon)` ([c4_model.py](../../../geomind/c4_model.py:87)). The existing initial fixtures need not expose this
   difference, but exact equality to the accepted law cannot be asserted generally below the cutoffs.

   **Required resolution:** distinguish a full C4 reference check from the production frozen-position controller check.
   Specify which outputs and variants each check compares, and provide a separate, explicitly frozen-position oracle
   if the production step must retain that design. State the intended near-contact regularization and its claim boundary.
   Preserve the accepted C4 files and the existing committed reference; add a new fixture if needed.
   A separate full-C4 test kernel is a possible solution, but testing that kernel alone would not validate the production step.

2. **Push-pull's hysteresis has no defined score or distance convention.**

   The shared rule retains a previous target when the best score improves by less than `eta=0.2`
   ([design lines 100-101](../DESIGN_0G.md:100)). The push-pull row specifies nearest legal targeting and
   “Hysteresis as above” ([line 116](../DESIGN_0G.md:116)), but defines neither `a_ij` nor a substitute score.
   Its two knobs, `G` and `f`, supply no target-scoring rule. Centre distance, surface gap, their negatives,
   reciprocal distance and normalized distance produce different switches and give `0.2` different meanings.

   For example, with a still-legal previous target at distance 1.0 and another at 0.9 model units,
   a negative-distance score retains the previous target, whereas strict nearest targeting switches immediately.
   Both implement part of the prose, but they are different baselines.

   **Required resolution:** give push-pull an exact nearest-distance convention and hysteresis score with units,
   or explicitly exempt it from hysteresis. This needs a drafter choice before implementation.

3. **The requested diagnostics are named but their computation is not specified.**

   [Design section 7](../DESIGN_0G.md:178) fixes one-second logging, a three-second history and stable IDs.
   It does not define how to count distinct target-group phases (circular distance, separation threshold,
   or zero-resultant handling), or how spatial-phase candidates are formed and tracked across time and deaths.
   Connected components, density clustering and complete-link clustering would give different candidate groups.
   The history window alone does not choose among them. It also does not say whether coherence is instantaneous
   or averaged over that window, or what phase diagnostics return for morale, push-pull and nearest.
   The latter arms have no circular phase state; silently mapping morale to phase would invent a diagnostic.

   **Required resolution:** specify the diagnostic formulas, thresholds, window aggregation and stable-ID matching;
   define empty/undefined values and the output for arms without phases. Keep candidates diagnostic only.

## Requested checks and results

| Check | Result in this session |
|---|---|
| Revision-2 contract identity | Verified by read-only comparison against `3a29450` |
| C4 RHS and RK4 reference to `1e-9` | NOT_RUN; source-level integration conflict above |
| Enemy-term sign at commitments -1, 0, 1 | NOT_RUN |
| Damage-rate recurrence | NOT_RUN |
| Decide-order independence | NOT_RUN |
| Empty legal set, dead target, coincidence, no enemies, zero resultant | NOT_RUN |
| Non-finite state/action failure reporting | NOT_RUN |
| Clone memory, RNG and parent isolation | NOT_RUN |
| Determinism | NOT_RUN |
| Fight cost relative to nearest, including opponent planning | NOT_RUN |
| 38 failure-free fights per arm | NOT_RUN |
| Step refinement | NOT_RUN; no tolerance or trajectories evaluated |
| 80 reference requests byte-identical | NOT_RUN; existing captures preserved |
| S2 passthrough fixtures byte-identical | NOT_RUN; existing captures preserved |
| Existing test suite once at end of change batch | NOT_RUN; stopped before code/test changes |

Default knobs used: **none**. No defaults were installed or evaluated. The request delegates midpoint defaults
and reporting of their values to the implementation session; that choice remains pending.

Deviations: the requested build and engineering verification were not started because the handoff's explicit stop condition fired.
Only this report was added. No design, engine, reference, receipt, gate, frozen file or milestone status was changed.

## Input identities

| Input | SHA256 |
|---|---|
| `../DESIGN_0G.md` | `02810a8a5d8b84526c7edeaf84ee46385a7f0fb42ebeee41e284b767005c840d` |
| `S3_CONTROLLERS_REQUEST_CODEX.md` | `d5e21ef22422e90b8c597fb24cd7120f2461952ce72b63bfcfabb83b343674d1` |
| `../c4_reference/c4_reference_states.json` | `f84c4fa69b8fbe95a4b0870af10317867b4cbe77a8cf735683015d1856c45cee` |
| `../c4_reference/make_c4_reference.py` | `992e678bf11f3420bc39b3f6a50f3f0d6bf461f133e19e74a7488bc843761e9a` |

Next gate: Claude/drafter review of these questions and an amended executable contract. S3 implementation remains pending;
the existing approval is acknowledged, but this report does not silently amend its design or claim readiness.
