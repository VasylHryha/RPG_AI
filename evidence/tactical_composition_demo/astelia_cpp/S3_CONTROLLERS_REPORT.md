NOT_READY

S3 initially stopped at the contract check, 2026-10-05. The owner subsequently instructed Codex to handle/fix the blockers. Revision-3 corrections are now written in DESIGN_0G.md; implementation and verification are pending. Author family: Codex (GPT-6).
This is an implementation handoff report, not independent acceptance or experimental evidence.
Rechecked by the same author at HEAD `3a91e2f` on 2026-10-05, following the owner's request to challenge the report.

Starting HEAD: `dae8c555a9ed8daa0eefc2424f537f3fa8d8d3de`.
The initial review used revision 2 at `3a29450`. The amended execution contract is revision 3, with the corrections and their causes in section 11.
The only pre-existing dirty path was the untracked
`docs/reviews/tactical_0g_design_review_codex.md`; it is preserved and excluded from this commit.

The explicit stop instruction in [S3_CONTROLLERS_REQUEST_CODEX.md](S3_CONTROLLERS_REQUEST_CODEX.md) (line 6)
applies: “If the design is wrong or ambiguous anywhere, stop and write it in the report. Do not choose silently.”
The following issues require the drafter to correct the executable contract and record their causes in its self-audit.
No controller implementation, build, test suite, fight, tuning or recorded run was performed in this session.

## Initial design questions (resolved in revision 3; verification pending)

1. **The requested C4 RK4 reference is a different integration problem.**

   [DESIGN_0G.md](../DESIGN_0G.md) (line 114) requires phase integration with positions frozen at the snapshot.
   Section 8 check 1 ([line 200](../DESIGN_0G.md) (line 200)) nevertheless requires its RK4 step to equal
   `c4_reference/c4_reference_states.json` to `1e-9` with positions held.
   The reference generator calls the accepted model's full `rk4_step`
   ([make_c4_reference.py](../c4_reference/make_c4_reference.py) (line 47)). That function advances positions
   at every intermediate stage as well as phases ([c4_model.py](../../../geomind/c4_model.py) (line 105)).
   Its phase derivative recomputes `exp(-r*r)` from those intermediate positions
   ([c4_model.py](../../../geomind/c4_model.py) (line 100)). Holding neighbor indices does not hold positions or distance weights.
   Thus the stored `th_after_step` is not an oracle for the requested frozen-position phase step.
   This conclusion is from source inspection; no numerical discrepancy was measured and no test failure is claimed.

   There is also a near-contact law difference: S3 fixes `epsilon=0.01` and uses a true unit vector
   ([design line 82](../DESIGN_0G.md) (line 82)); the accepted model fixes `epsilon=1e-6` and computes displacement divided by
   `max(r, epsilon)` ([c4_model.py](../../../geomind/c4_model.py) (line 87)). The existing initial fixtures need not expose this
   difference, but exact equality to the accepted law cannot be asserted generally below the cutoffs.
   For one aligned ally at `r=0.005`, the S3 radial coefficient is `1.8-100=-98.2`, while C4's is
   `1.8-200=-198.2`. This is an algebraic example, not a measured fixture discrepancy. Exactly coincident
   positions give zero displacement in both laws, so coincidence alone does not demonstrate this difference.

   **Required resolution:** distinguish a full C4 reference check from the production frozen-position controller check.
   Specify which outputs and variants each check compares. A separate frozen-position oracle is one option;
   another is to revise the acceptance row to check the shared RHS against the stored reference and check production
   integration independently. The drafter chooses; a new oracle is not automatically required.
   The S3 regularization is already explicit, so it need not be replaced with C4's value; qualify the equality claim
   and cover the intended near-contact behavior. Preserve accepted C4 files and the existing committed reference.
   A separate full-C4 test kernel alone would not validate the production frozen-position step.

2. **Push-pull's hysteresis has no defined score or distance convention.**

   The shared rule retains a previous target when the best score improves by less than `eta=0.2`
   ([design lines 100-101](../DESIGN_0G.md) (line 100)). The push-pull row specifies nearest legal targeting and
   “Hysteresis as above” ([line 116](../DESIGN_0G.md) (line 116)), but defines neither `a_ij` nor a substitute score.
   Its two knobs, `G` and `f`, supply no target-scoring rule. Centre distance, surface gap, their negatives,
   reciprocal distance and normalized distance produce different switches and give `0.2` different meanings.

   For example, with a still-legal previous target at distance 1.0 and another at 0.9 model units,
   a score `-r` retains the previous target (`0.1 < 0.2`), whereas a score `-10*r` switches (`1.0 >= 0.2`).
   Both rank legal enemies by nearest distance and apply the specified hysteresis inequality, but give different baselines.

   **Required resolution:** give push-pull an exact nearest-distance convention and hysteresis score with units,
   or explicitly exempt it from hysteresis. This needs a drafter choice before implementation.

3. **The requested diagnostics are named but their computation is not specified.**

   [Design section 7](../DESIGN_0G.md) (line 178) fixes one-second logging, a three-second history and stable IDs.
   It does not define how to count distinct target-group phases (circular distance, separation threshold,
   or zero-resultant handling), or how spatial-phase candidates are formed from a window with deaths.
   Connected components, density clustering and complete-link clustering would give different candidate groups.
   The history window alone does not choose among them. It also does not say whether coherence is instantaneous
   or averaged over that window, or what phase diagnostics return for morale, push-pull and nearest.
   The latter arms have no circular phase state; silently mapping morale to phase would invent a diagnostic.

   The accepted C4 detector has an explicit component rule and threshold inputs
   ([c4_detect.py](../../../geomind/c4_detect.py), lines 7-17 and 39-60), but this design does not select that
   rule or specify its adaptation to changing combat membership. Merely mentioning C4 criteria does not select it.

   **Required resolution:** specify formulas, thresholds and window aggregation, including empty/undefined values.
   State whether phase diagnostics apply only to resonator; there is no requirement to invent phases for other arms.
   Clarify whether stable IDs mean member unit IDs only or also persistent cluster IDs. Persistent cluster tracking
   is not automatically required. Keep candidates diagnostic only.

4. **The normalization ledger assigns incompatible units to damage gain and pressure.**

   [Design section 2](../DESIGN_0G.md), lines 54-62, gives both `z` and `kappa` units `1/s`, but declares
   `P=kappa*(z_in-beta*z_out)` to have units `1/s`. The product has units `1/s^2`, which cannot be added to
   the `1/s` terms in the phase and morale derivatives. The pressure term in target scoring also appears as
   `tanh(P)` (line 100), whose argument needs a declared dimensionless normalization.

   **Required resolution:** correct the ledger, without automatically changing the equations or adding a knob.
   Dimensionless `kappa` would give the stated pressure units; a fixed one-second reference scale would make
   `tanh(P * 1 s)` dimensionless while preserving the intended numerical behavior. These are proposed resolutions
   for the drafter to confirm, not implementation choices made here.

5. **The empty/zero-resultant target-group fallback does not identify which quantity becomes zero.**

   [Design section 4](../DESIGN_0G.md), lines 114-119, writes `cos(theta_i-psi_ij)` followed by a definition
   of `psi_ij` and “0 when” the group is empty or its resultant is too small. This can mean alignment zero,
   or `psi_ij=0` and alignment `cos(theta_i)`. They differ: at `theta_i=pi`, those scores are 0 and -1.
   The separate rule that target coupling is zero when the group is undefined resolves the torque but does not
   explicitly resolve this score. For morale the analogous wording can mean alignment zero or `mu_ij=0`;
   at `m_i=0` those give 0 and 1.

   **Required resolution:** name the fallback value of alignment and the validity of the aggregate separately,
   for both arms. Preserve the already stated zero coupling for an undefined group. No new mechanism is needed.

## Adversarial recheck of the report

- The frozen-neighbor interpretation does not dismiss question 1: C4 holds neighbor identities but recomputes
  intermediate geometry. This is an oracle/acceptance conflict, not evidence that S3's chosen integration is inherently wrong.
- Removed the implication that a new oracle or a new epsilon is mandatory; those were overly prescriptive fixes.
- Strengthened question 2 with two scores that both obey nearest ranking and the hysteresis inequality.
- Narrowed question 3: the handoff does not explicitly demand phase diagnostics for every arm or persistent cluster IDs.
  It must state their scope, but those extra features are not requirements imposed by this report.
- Added the units conflict and the quantity-specific fallback question missed in the first pass.
- Fixed the report's repository links: `file.md:line` is a renderer convention, not a portable Markdown file target.
  Source lines are now stated in prose beside ordinary relative file links.
- Mid-range defaults, a declared refinement tolerance, JSON field names and conditional legacy output are implementation
  choices within the request. Their absence alone is not a design blocker. A conditional S3 summary and a separate test
  entry point can preserve legacy bytes while reporting failures and refusing production passthrough; that is not an
  unavoidable parity conflict. No implementation or execution of those choices is claimed.

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

Next step: implement and verify the owner-authorized revision-3 S3 contract. Claude reviews the completed source and engineering evidence. No readiness or independent acceptance is claimed yet.
