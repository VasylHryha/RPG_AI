# Approved exploratory current-R4 Q/H pilot

Owner authorization: 3 October 2026, minimal diagnostic in
`docs/reviews/c6_unblocking_synthesis_gpt.md` §5 and choice A. This is exploratory,
not C6 evidence/readiness, a full unit-persistence test or a hypothesis verdict.
C6 stays BLOCKED / R006 STOP. No historical measurement is rescored.

## Fixed apparatus and inputs

Exactly 16 paired populations (32 Q/H arms), unchanged current R4 equations,
K=1, J=0.8, 24 elements, detector, recovery/causal thresholds and three-grid
numerics. The complete unchanged settings, dependency identities, fresh random
128-bit pilot-only entropy and schedule are in `SPEC.json`, committed before
sampling. No project/source/native build change, K/J search, coherent arm,
R007 development, descriptor assay, source operation, final entropy, mutation
or panel. Scratch scripts and all records stay in this directory.

The existing detailed construction in Claude Revision 3 §6 supplies the
prospective construction details left open in the GPT synthesis. Per pair:
`medium(rng(pilot_entropy,pair,1),model)`, independently evolve three grids for
100 C0 with no cohorts. Q retains the resulting quiet background. H sets the
8 nearest sites to (2,0), breaking equal-distance ties by site identity, to
radius 0.8744 with independent uniform phases from purpose 90. Assign the same
phases on all grids. Keep site frequencies, drive, geometry and all other
entries unchanged. This is a supplied limiting-condition patch; it is not
source-produced B_after. Scene origin/rotation stay at their generator defaults.

Introduce generation=1, episode=0 with purpose (10,1,0); perturb with purpose
(20,1,0). Every Q/H pair has identical x, theta, rates, IDs, tokens and probes;
only actual field and its initialized cohort carrier differ. At introduction,
Q must have zero sites above radius 0.485206 and H exactly eight. No redraw.
This scalar reference is a diagnostic boundary, not a proven basin boundary
for the driven diffusive field. Each original H patch site must remain above
it in the material carrier at every saved frame on all grids; every Q site
must stay below it. A condition failure makes the mechanism indeterminate.

Execute formation=100 C0 and existing `qualification` unchanged. Preserve
three full formation prefixes, input/background snapshots, all returned
candidate/recovery/causal values and scope refinement checks. Fine structural
candidate rows are explicitly unavailable from that helper; fine raw prefixes
remain available. A scratch GridSet subclass checkpoints completed original
calls; no observer or monkey patch is inserted in project code.

For the initially qualified selected candidate, clone its end grid, set the
selected inventory and output=0, and continue 100 C0. Use existing
`rolling_persistence` on original prefixes and all three continuation paths.
Preserve all rolling structural criteria and first loss. Identical pass masks
are required on all grids. No endpoint recovery/causal assay is added; retention
is structural retention only. Preserve actual and carrier amplitudes and
site frequencies. Record invalid/incomplete reasons and stage wall/CPU,
worker wall/CPU/peak RSS and storage bytes. Qualification combines recovery
and causal timing; individual assay timing and cache counts are unmeasured.

## Supervisor, dependency guard and single-use execution

Use the existing native artifact only, compare full prospectively committed
source/build/binary/helper/environment/source-pin identities before loading,
and check identities at checkpoints and after the run. Missing or mismatched
artifact means INCOMPLETE, without a build. Full audited source pin validation
runs before scientific work. No concurrent dependency/build edits are allowed.

Two worker processes, one arm per worker, pair-index order; Q first for even
pairs, H first for odd pairs. No outcome-dependent scheduling. Parent monitors
owned process groups including descendants every 0.1 s (ps calls capped at
2 s): 900 s total wall including setup/shutdown, 1800 s aggregate CPU, 2 GiB RSS
per worker group, 300 s per arm. Cancel globally at 870 s. Stop submissions,
discard the unsubmitted queue, TERM only owned process groups, allow at most
5 s grace, then KILL survivors and reap/account them. No executor shutdown
wait. CPU includes parent, completed workers and live owned descendants;
wait4 provides completion CPU and lifetime peak RSS. RSS sampling can overshoot
between samples; post-completion lifetime peaks are also checked. Setup and
serialization count in per-arm wall/CPU and parent wall caps. Supervisor I/O
uses local atomic replacement, fsync, and a shutdown reserve of 30 s.

An exclusive `run/` directory is the durable one-shot latch; no resume or retry
exists. A failed preflight consumes the one attempt. Atomic partial files are
saved before work and between completed scopes, alongside worker logs and
parent progress. A native scope killed before return has no trajectory claimed
for that unfinished scope. Shutdown preserves earlier checkpoints.

Run only after this specification/harness commit:
`.venv/bin/python evidence/c6_dev_pilot/r4_sensitivity/pilot.py --run`

## Predeclared exploratory interpretation (GPT synthesis §5.7)

Raw paired outcomes first. Missing/invalid arm, numerical inconsistency,
resource stop, pairing or dependency failure: INCOMPLETE takes precedence.
Partial arms/pairs are missing values, never negative outcomes. No replacement.

For all 16 complete pairs: Q qualifies >=14: quiet ceiling concern strengthened;
Q <=8: weakened; otherwise indeterminate. No population-level ceiling claim.
Report qualification difference Q-H, all forward and reverse discordances,
and structural retention separately with fixed denominators 16 (an initially
unqualified arm has no initially-qualified retained candidate). Conditional
retention denominators cannot replace these fixed denominators.

A useful qualification suppression signal requires at least four more Q
successes than H successes and at least four Q-success/H-failure pairs.
Report an analogous retention contrast separately. If Q is not quiet or H
fails its retained-patch condition, mechanism inference is INDETERMINATE.
Frequency stationarity is only an associated failing criterion: for initial
qualification H has no structurally accepted candidate and a minimum-size
candidate fails frequency alone; for retention H initially qualifies and its
first failed window fails frequency alone on all grids while Q retains.
Mixed failures, unrelated rejected clusters, recovery/causal-only failures do
not count. Do not attribute unique causation to frequency heterogeneity. The
stricter route-A algorithm in the older Claude review is not silently imported
into the owner-approved GPT rules. All output is an exploratory decision aid;
return to the owner after completion or incompletion; no next action automatic.

## Normalization ledger

| Quantity | Level / units / normalization |
|---|---|
| Positions, radius, kick | One material level, L0; existing radius/NN spacing rules |
| Phase / pattern / lock | rad; existing wrapping and circular statistics |
| Frequency stationarity | rad/C0, unchanged half-window tolerance 0.01 |
| Time and integration | C0; 100 formation, 30 detector, 100 continuation; dt=.005/.0025/.00125 |
| Actual/carrier amplitudes | Dimensionless z; site identity, no conflation |
| Initial qualification / retention | Counts out of fixed 16 per arm; missing reported explicitly |
| Wall/CPU, RSS, storage | Seconds, bytes; owner/evaluator-side diagnostics |

## Yes/no stop rows

| Yes condition | One action | Responsible role |
|---|---|---|
| Native/source/helper identity absent or mismatched? | Record INCOMPLETE and stop | Implementer |
| Initial high-site count or paired material/probes mismatch? | Record INCOMPLETE and stop | Implementer |
| Numerical/nonfinite/three-grid inconsistency? | Record INCOMPLETE and stop | Implementer |
| Resource cap or external cancellation? | Cancel owned work and preserve partial results | Implementer |
| Any missing arm or required trajectory? | Report INCOMPLETE | Implementer |
| H retention/Q quiet condition fails? | Report mechanism INDETERMINATE | Implementer |
| One attempt already started? | Refuse another execution | Implementer |
| Further study desired after this record? | Decide separately | Owner |

## Self-audit

The synthesis leaves prospective construction details to the specification.
The previously documented eight-site construction, clocks and entropy purposes
are used without looking at new outcomes. Harness validation uses synthetic
processes only, no pilot sampling or rehearsal. Existing qualification emits
coarse structural rows only; all finer trajectories are retained explicitly.
