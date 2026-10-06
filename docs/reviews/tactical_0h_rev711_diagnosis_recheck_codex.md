CHANGES_REQUIRED

Reviewer family: Codex
Reviewed commit: 15cda3eac14e388257c71ef17a628647d0dad339
Review date: 2026-10-07

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The recorded retraction mechanism is supported. The diagnosis's stronger necessity claim, explanation of the successful seeded start, and exclusion of growth alternatives are not. Correct those before using this report to choose the next design. This review does not change the recorded FIXTURES_FAIL result or authorize execution.

## Scope and identity

Read AGENTS.md first, current source guidance, DESIGN_0H_REV7.md, the diagnosis, all named scripts/logs, the native and Python implementation, fixture report/compact evidence/birth events, and stored traces. Used only standard-library reads, hashing and arithmetic on existing data. No project imports, simulations, builds, tests or long jobs. Existing files were not edited. Reviewed target files match commit 15cda3e despite the workspace's later HEAD.

| Input | SHA256 |
|---|---|
| REV711_F5I_DIAGNOSIS.md | `9157be3622dca17a0d87a479bc3ba7ae179a89855afb0a7719d8bf694398143a` |
| trace.json.gz | `5fe47b035ac20ea8f258daa5f931833138217fe23230c4bcc504ab59d93c6435` |
| rev7_design.py | `d4bb361086ef76a9ab80fc9ac4ba5145d5536d8b45af2197cc78a6982f4465ef` |
| rev7_medium.cpp | `93fb9973ca14fd88b1fcbcf204cf01df41b65bdbd0c9bba21134a883d4744ec1` |
| rev711_fixture_run_20261006/F5.json.gz | `7a01b8add5d2f3287afa0e3690959d948704dccee61c8eada0722ed39628049e` |

All nine raw pilot files listed in RAW_FILES_OUTSIDE_GIT.json were available locally; every byte count and SHA256 matched, including the two kernel files in the listed scratch directory. These local files remain outside Git. The receipt's baseline pin is not an identity of the in-process patched behavior; the script and raw-file identities supply that distinction.

## Findings and concrete fixes

### R1 — High: the successful fixture contradicts “O must be surrounded”

Diagnosis lines 38–40 and 60 generalize sampled tip retraction into a size-independent impossibility, then explain F5(ii) as six angular sectors surrounding O. The actual seeded start is six points around **(3.1, 0)**, with O at **(−0.5, 0)**; that hexagon is not around O (`rev7_fixtures.py:41`).

Independently extracted the two world-index-7200 frame objects from the stored fixture F5.json.gz. In start (ii), **all 44 ordinary elements have x > −0.5**: minimum x = −0.3670105160. Their angles about O span only **−17.3161° to +76.7164°**. The nearest four distances are **0.439048, 0.542608, 0.563816, 0.784586** m.u. Thus the successful fixture has a one-sided configuration with strong O links. The stored seeded formation pilot reproduces this exact frame, and its complete 354-entry B-path event subset matches F5ii_BIRTH_EVENTS.json.

The diagnosis's “four nearest end at 0.41–0.48” also mixes evidence: the formation pilot ends at `[0.448, 0.556, 0.568, 0.793]`; the service pilot ends at `[0.411, 0.440, 0.483, 0.771]`. Neither has all four in that interval. Different local spacing, repulsive contacts and neighbour membership can balance motion without placing bodies around O on all sides. The passing one-sided F1c scaffold is another reason to avoid a universal impossibility claim.

**Fix, drafter:** replace “only if surrounded,” “whatever its size,” and the six-sector account with the observed local force imbalance. Describe seeded geometry from its own stored state. Keep C as a hypothesis, not a demonstrated requirement or an explanation of F5(ii). Narrow the title/conclusion to failure of the current empty-start growth trajectory under this motion law. Growth history, initial scaffold and O placement remain possible contributors; these pilots do not isolate them.

### R2 — Medium: the pilots support bounded connectivity observations, not exclusion of growth rules or F5 verdicts

The reported late active-path fractions independently reproduce: budget 96 = **0.002875**, budget 128 = **0.0152172619**, formation (ii) = **0.3227380952**, service (ii) = **0.4328571429**, kernel (i) = **0.0029166667**. The other listed late zeros reproduce. Their interpretation needs tightening:

- **Formation patch is active but tests graph pruning.** `_b_path_attempt` calls the replaced module-global `geometric_trial`. Filtering removes sub-margin edges incident to the new element from the trial graph; it does not reject every birth having such an edge. A birth can still reduce the deficit without closing a robust O edge. The margin-1 and margin-2 empty-start traces **and events are identical**. This is consistent with the patch's predicates, not evidence that every formation-margin policy is ineffective.
- **Service patch is active.** During `b_path`, the wrapper replaces the instance's graph query with Python geometry and raises the module-global rate. Ordering, service tests and geometric trials therefore use 1.0/s. `finally` restores the rate and removes the temporary override; the subsequent native graph, B1 and measurements use 0.5/s. Changed births/deaths support that intervention. It records an any-active-path interval **440.1–484.2 s (442 samples, 44.2 s)**. Late connectivity still vanishes, but “margins do not make a bridge hold” is too broad.
- **Budget patch really changes D3 too.** Admission uses the new ordinary-body cap and unscaled cost limit; `cost()` is multiplied by 64/budget, so the inherited `while cost()>64` removes bodies only above the new limit. Reported event costs are scaled. In the 128 pilot there are **zero cost/cap refusals and zero D3 removals**, and 81 total bodies at 800 s. This shows failure to sustain late connectivity within that horizon despite available resources; it does not exhaust or rule out the larger budget with a different scheduler/horizon.
- **Kernel patch is implemented in the scratch native build and broader than “weaker distant element attraction.”** The one-line change is inside the common element/site motion loop. It multiplies **both attraction and repulsion**, including active site bodies, by `exp(−rr²)`; sites use regularized rr. Neighbour selection and normalization remain unchanged. Scratch Python files match production, its C++ differs only at that line, and its build manifest verifies every listed source and the image selected by the scratch loader (`aa5662fd562d5778c4d45a65b6283cd388c3212baf8e00f9d06552a6b13e1122`). The changed traces are consistent with that intervention. No launch/import-path receipt cryptographically binds the historical process to this scratch build; retain that provenance limit. Nothing here supports generalizing from this kernel variant to all local/bonded laws.

The proxy is fair for comparing **late training connectivity on the same drives**. It is not normalized like E: it averages `number of connected active sites / number of active sites` per training step. F5 E is an eight-component, unconditional per-site path frequency averaged over fresh, growth-frozen assay copies from checkpoints 40/45/50, on validation recipients; the gate takes **max(E)**. For example, seeded formation's training proxy is 0.323 while its unconditional late training site-0 frequency is 0.700 and fixture max(E) is 0.800. Comparing 0.323 to the 0.5 E gate would be wrong. Zero training connectivity also does not prove zero connectivity after new assay drives move the copied geometry. Pilots do not measure A/B.

**Fix, drafter:** retain the numbers and explicit no-verdict labels; call the metric a late training connectivity diagnostic. Report any-path durations and per-site denominators beside it. Replace “both starts fail” for the kernel with “both lose late training connectivity,” and replace “not the growth rules” with “these specific interventions did not sustain late connectivity.” Relabel formation as a stricter trial graph, or specify a future test that actually requires a robust closing edge. No rerun is required to correct these statements.

### R3 — Medium: option A needs a coherent seeded protocol before F6–F9 can proceed

A is a reasonable owner-controlled narrowing, but the current code cannot simply continue the remaining fixtures on the passing seeded arm. `Harness.run_all` stops on the combined F5 failure. F6 takes its baseline from `checkpoints['i',40]`; F7 creates an empty M run matched against `self.intact`, retained from start (i); F8 starts from `self.live`, also retained from (i). Production's no-initial-state path starts empty. A changes initialization and comparator treatment as well as the sentence describing the claim.

**Fix, drafter:** describe A as a new seeded protocol revision. Specify common initial structure, roles/gains/phases/pin, RNG treatment and cost accounting for intact/M/U; revise dependent fixture targets and stop rows before implementation. Do not bypass the present F5 stop. Distinguish formation from seed-assisted growth and subsequent qualification: F5(ii) transmission does not establish learning, resonator qualification, recursive background generation, or superiority to scripted AI. No measured schedule establishes that A is necessarily the fastest complete route.

### R4 — Low: the force table omits a positive rear-neighbour term

The reported net velocities are correct, but “all seven pull back” and their listed ranges are not. At each sampled state the nearest rear element is closer than the approximately 0.556 equilibrium spacing, so its repulsion contributes **toward O**. Correct the table rather than discarding the valid retraction diagnosis.

**Fix, drafter:** include all eight signed contributions or O/other-element/site sums, label these as instantaneous RHS projections, and distinguish them from a 0.1-second displacement.

## Independent mechanism check

For unit vector u from tip to O, reconstructed the instantaneous velocity directly from the native equation:

`v·u = geometry_rate / |Nx| * Σ [(A(1+J cos Δφ) − B/rr) * (displacement·u)/rr] + wall·u`.

Used unrounded element/site records and actual motion lists in the stored baseline recovery-check frames; cross-checked the committed rounded trace. No integration was performed.

| Tip / time | O contribution | Other seven, summed | Sites | Total toward O | Nearest rear contribution |
|---|---:|---:|---:|---:|---:|
| 43 / 440.1 | +0.093458 | −0.397610 | 0 | −0.304152 | +0.015534 (37) |
| 35 / 360.1 | +0.114615 | −0.454985 | 0 | −0.340370 | +0.018907 (33) |
| 27 / 260.1 | +0.092352 | −0.727211 | 0 | −0.634859 | +0.008376 (26) |

**Site bodies were not missing force terms in these examples.** The actual Nx lists contain eight elements, including O, and no sites. Even the nearest site among all eight possible sites is 3.0523, 2.8629 and 3.0023 m.u. away respectively, versus eighth-selected-element distances 1.1255, 1.1412 and 1.5306. Activity cannot change that exclusion. The sampled tips are inside the wall radius and are free; neither the wall nor pin suppression adds an omitted term. Active site bodies do matter elsewhere and for the kernel intervention; their zero contribution at these tips does not establish that they are causally irrelevant to the whole trajectory.

The committed 4,800-step trace contains **12 observed path intervals and 365 path-present samples**. At every interval's first absent sample, the closing element remains in O's held phase list, its distance has crossed `sqrt(log(8)) = 1.442026887`, and its coefficient is below 0.5/s. O's phase degree remains eight. There are no D1/D3/D4 removals in that replay. Thus these observed breaks are geometric coefficient loss, not deletion, root loss alone, or loss from O's nearest-eight list. The graph criterion itself does not use phase difference; phase still affects motion through its cosine and affects actual transmission. “Phase is not the direct strong-edge-loss test” is more precise than excluding phase from the full causal story.

The negative sign comes from the **sum of projected pair terms and selected geometry**. Dividing by eight changes speed, not that sign; removing mean normalization alone would accelerate this retraction. The 0.1-second recording also cannot inventory paths born and lost entirely between samples.

## Better options and recommendation

**Refine B around mechanical support, not around a failed distance kernel.** A principled candidate is a locally formed, bounded-degree bond graph with reciprocal, phase-dependent spring stiffness and a rest length, plus short-range exclusion. Motion follows the gradient of that local interaction energy. For an aligned chain between two fixed ends, equal spacing with positive tensile prestrain gives balanced interior tensions and positive longitudinal/transverse restoring stiffness; require the resulting phase links to retain adequate coupling coefficients. This supplies a specific stability argument that multiplying the existing all-neighbour attraction/repulsion by a kernel does not. Define how bonds form, break and remodel from local state, how active site anchors behave, and how geometry feeds back into modes. Do not assume arbitrary bonded attraction plus repulsion from all neighbours is sufficient, or call this new law accepted C4/RRG evidence. A changed law needs its own design, normalization ledger and numerical/fixture checks.

**Add a narrower growth alternative before assuming the medium must change:** let missing-path demand grow the output-side component outward as well as the source-side component inward, with bounded support births near O and acceptance based on connection to either frontier, preserved existing paths and reduced separation. Current `_b_path_attempt` only places from the source-forward frontier and requires the newborn to be source-reached. Two-ended growth could construct the mechanically supported local geometry that the successful seeded trajectory already demonstrates. It changes the acceptance rule and may still fail; it is an untested design hypothesis, not a repair established here.

**Add an O-placement alternative:** choose and freeze O once from initial observed root geometry, under a declared rule shared fairly across policies. For example, restricting O to the radius-1 central disk keeps it at least 3 m.u. from every radius-4 site while allowing a shorter bridge toward the first root. Preserve O's no-direct-drive/non-root role, copy the stored pin into assays, and forbid later relocation based on assay results. This changes the origin-pin contract and geometric neutrality, so disclose the positional prior and obtain owner approval. It cannot guarantee success, but the different pins in F5(i)/(ii) are an unresolved confound worth separating from the initial scaffold.

A remains available if the owner prefers seed-assisted growth. C remains a possible placement policy, with no necessity established. I would first correct the diagnosis and compare a narrowly specified growth/placement alternative with the mechanically supported B design; the evidence does not compel immediate claim narrowing or an assumed major rewrite.

The drafter should record this recheck and dispositions in docs/PLAN_CURRENT.md. This review leaves that existing file untouched as requested. Git is not writable in this session, so the review is left uncommitted.
