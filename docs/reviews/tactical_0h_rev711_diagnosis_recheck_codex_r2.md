CHANGES_REQUIRED

Reviewer family: Codex
Reviewed commit: 423591ccaf785e43a31eddeae86361181a0ede68 (revision 2, including 739b167)
Review date: 2026-10-07

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The sampled retraction mechanism is correct, and the original R1, R3 and R4 corrections are satisfactory. R2's metric correction is sound, but new pilot defects and causal overstatements prevent approval of revision 2 as a basis for choosing the next design. In particular, one pilot's instrumentation advances the live medium during supposed recovery-copy integration. The recorded FIXTURES_FAIL result remains unchanged; this review authorizes no execution or protocol change.

## Scope and identity

Read AGENTS.md first, research/rrg/CURRENT.md, the current plan, round-1 review, revision-2 diagnosis/self-audit, DESIGN_0H_REV7.md, the named Python/native code, every pilot script and log, RAW_FILES_OUTSIDE_GIT.json, the committed diagnostic trace, fixture report/compact evidence and stored F5 frames. Used standard-library reads, hashing and arithmetic only; no project imports, simulations, builds, tests or long jobs. Only this new review file was written.

| Input | SHA256 |
|---|---|
| REV711_F5I_DIAGNOSIS.md | `b400317931c13b8ffa1c6ebc1f3667c53c637652c2977643ccd4512cd86e02fb` |
| trace.json.gz | `5fe47b035ac20ea8f258daa5f931833138217fe23230c4bcc504ab59d93c6435` |
| rev7_design.py | `d4bb361086ef76a9ab80fc9ac4ba5145d5536d8b45af2197cc78a6982f4465ef` |
| rev7_medium.cpp | `93fb9973ca14fd88b1fcbcf204cf01df41b65bdbd0c9bba21134a883d4744ec1` |
| rev711_fixture_run_20261006/F5.json.gz | `7a01b8add5d2f3287afa0e3690959d948704dccee61c8eada0722ed39628049e` |

All **26** listed local raw pilot files were available and matched both byte count and SHA256. These files remain outside Git; a future checkout needs them to reproduce this audit. The current scratch C++ matches production except for the two 1.5 motion-cutoff changes; scratch rev7_design.py, rev7_run.py and rev7_fixtures.py match production. Its current build manifest verifies every listed source and binary (`e999e2048068d4a1b9fa7034ce57fa10a928e06f356e9269229dadf6ec69d271`). The earlier kernel build has been replaced in this scratch directory, so its historical image cannot be verified anew from the current build. The diagnosis correctly discloses the absence of a launch receipt binding the historical processes to their loaded images. Neither input pins nor raw hashes establish that binding.

## Round-1 dispositions

| Finding | Round-2 disposition |
|---|---|
| R1, universal one-sided impossibility / surrounding O | Fixed in section 2. Independently extracted the fixture's index-7200 seeded frame: 44 ordinary bodies, minimum x −0.367010516, O at x −0.5, angle span −17.3161° to +76.7164°, nearest distances 0.439048 / 0.542608 / 0.563816 / 0.784586. The successful state is one-sided. New scaffold necessity claims still need narrowing below. |
| R2, pilot scope and E comparison | Metric and old intervention descriptions corrected. All listed late fractions reproduce arithmetically, including 0.095859694 for the contaminated combined pilot; reproducing that number does not validate its experiment. New findings below remain blocking. |
| R3, seeded protocol | Fixed as a design requirement. A now explicitly requires a new protocol, common initial structure/accounting across intact/M/U, changed dependent fixtures and review. It does not bypass F5 or establish qualification. |
| R4, missing positive rear term | Fixed. Independent unrounded reconstruction below reproduces all three signed sums. |

## Findings and concrete fixes

### R2-F1 — High: the combined range/bidirectional seeded pilot mutates the live run through recovery clones

`kernel_pilot/kpilot2.py:71–80` assigns an **instance function** `integrate(drives)` closing over `m`, `orig` (the bound live method), and `trace`. `Rev7Medium.clone` (`rev7_design.py:148–154`) deep-copies the instance dictionary; Python functions retain their closure. `rev7_qualification.finish:156–163` then calls `control.integrate` and `kicked.integrate`. Both calls invoke the captured **live** `orig`, advancing `m`, instead of their clone's native state. They also append to the training trace. This defect exists in the other scripts' equivalent instrumentation too, but only this recorded pilot exercises it.

The stored `kpilot_r15bidir_ii.json.gz` contains **9,200 steps ending at 920 s**, rather than 8,000 ending at 800 s. Its one exercised recovery candidate is from check time 300 s; its recovery event occurs at live time **480 s**, instead of 360 s. Episode 22 starts at 352 s; episode 23 starts at **488 s**, a 136 s separation instead of 16 s. This is exactly the extra 600 control + 600 kicked integrations. No clock disorder is needed: the clock advances monotonically while the wrong object is integrated. The late denominator is **2,800**, and includes recovery drives and the shifted training schedule. Recovery-copy measurements are invalid as well.

**Fix, drafter/implementer:** preserve and mark this pilot invalid; withdraw its 0.096 seeded-arm comparison and the “all pilots are 800 s” statement. Future instrumentation must bind to the actual instance and keep a training-only sink outside cloned state, or record at the Run/world-step boundary. Add a bounded synthetic clone-isolation check before any future pilot: clone integration must leave the live state/clock/sink unchanged, and training must contain exactly 160 steps per episode. Do not try to repair this trajectory by filtering its trace: its live state was changed. A replacement run needs separate authorization and new evidence. The other 25 listed traces have 8,000 steps ending at 800 s and no recovery candidates; the committed 4,800-step replay has none either, so this defect does not invalidate their recorded trajectories.

### R2-F2 — Medium: the root-group pilot is misreported and does not isolate budget splitting as the cause

Diagnosis line 81 says seeded (ii) has “exactly one group.” Its recorded pilot creates **five additional B1 centres**, at sites 2/3/5/6/7 and times 240/260/280/280/340 s, plus **nine** extra members, in addition to the initial six-element scaffold. Empty group-3 creates six centres and eight members; empty group-6 creates three centres and fifteen members. Counts of B1 events include both the original accepted root and its removed/re-added centre; those events are not all net added bodies.

The wrapper (`pilot_rootgroup.py:34–53`) changes more than group multiplicity: it first accepts the original root, removes it, and adds a centre with **no clearance or cost feasibility check**. Only subsequent members are checked. In empty group-3, the centre at t=360, site 0, is added at cost **64.4**, above the 64 limit; D3 later removes two elements. A group can also be partial. Extra members bypass the original two-birth B1 quota. The group is a centre plus peripheral members, whereas the initial scaffold is six peripheral hexagon vertices. Timing, location, shape and admission behavior differ from the successful initial scaffold.

**Fix, drafter:** replace the incorrect counts with centres/members, removals and net additions; disclose quota/admission changes and partial groups. Replace “because groups split the budget” with “resource refusals occurred; this pilot does not identify why late connectivity disappeared.” Budget competition is plausible, but the successful seeded arm also builds multiple groups and no matched single-group arm was tested. A future group policy needs atomic feasibility (including the centre), explicit group/quota accounting and a declared geometry. The proposed single-group variant remains a useful untested candidate, not a demonstrated rescue.

### R2-F3 — Medium: the scaffold and O-swap observations do not establish the new necessity/exclusion claims

The ring, no-gain and random-phase pilots really change the intended initial inputs. Their late fractions reproduce as 0 / 0 / 0.397180060. They support sensitivity of this seeded trajectory to those interventions. They do **not** identify a uniquely sufficient embryo size, placement, gain or phase family. Random phases passing once shows that initial perfect coherence is unnecessary in that tested realization, not that “phase is free.” There is no initial-count ablation, gain/radius sweep or proof that any compact inward root mass succeeds. Seed initialization also changes O's birth time/phase/identity and growth history; the two starts use different growth/recovery keys. Those factors were not equalized by swapping positions.

The O swap is active, and its late fractions reproduce as **0** and **0.408690476**. It excludes the specific explanation that the difference between x=0 and x=−0.5 alone determines the observed late-connectivity contrast. It does not rule out an O placement **rule**, and it measures no revised F5 verdict. The two positions lie on the x-axis; the first empty-start B1 root is at **site 2**, on the positive y-axis. Neither pin tests shortening that bridge by moving toward its root. The swap changes the seeded site's connectivity distribution and raises its proxy from 0.323 to 0.409, so placement does affect dynamics.

**Fix, drafter:** narrow lines 76–79, 92–98, 107 and 110–112 to the tested inputs and training-connectivity observations. Retain A as an owner-controlled seed-assisted hypothesis; remove “the property is identified,” “must” and the broad deletion of placement alternatives. Keep a declared root/demand-relative O-placement option available. Describe the untested confounds explicitly before recommending claim narrowing as evidence-compelled.

### R2-F4 — Medium: the “longest continuous path” table mixes first appearance, recurrence and durations

The raw table fractions reproduce, but the duration descriptions do not consistently represent their column. Ring/no-gain say “never,” although they contain **5 / 12 path-present samples** (longest 0.4 / 0.6 s). Empty inward B1's longest interval is **380.1–418.3 s, 383 samples = 38.3 s exposure**, not a 20 s episode. Empty group-3 holds an any-active-site path for **330.2–564.4 s, 2,343 samples = 234.3 s**, then loses late connectivity. Seeded O-swap's longest interval is **320.1–624.0 s, 304.0 s exposure**, rather than an uninterrupted hold from 272 s. Range-1.5 empty start's longest interval is **461.6–704.0 s, 242.5 s exposure**. A path for *some* active site is not necessarily the same site's continuous path, and inactive episodes can interrupt the observed diagnostic without mechanical destruction of the same chain.

**Fix, drafter:** give a common definition, explicit first/last-present times and sample-count exposure, and distinguish any-active-site continuity from per-site continuity. Correct the rows from stored data without rerunning. Use “no late connectivity” rather than “never,” and preserve long transient successes as evidence relevant to scheduling/support alternatives.

## Independent mechanism and intervention checks

Reconstructed from unrounded recovery-check frames and the actual recorded motion lists:

`v·u = geometry_rate / |Nx| * sum[(1 + 0.8 cos(delta_phase) − 1/rr) * displacement·u/rr] + wall·u`,

where u points from the tip to O. Element rr uses eps; site rr uses the native 0.3 regularization. All sampled tips are free and inside the radius-6 wall.

| Tip / time | O | Rear elements summed | Nearest rear term | Sites | Net toward O |
|---|---:|---:|---:|---:|---:|
| 43 / 440.1 | +0.093458 | −0.397610 | +0.015534 (37) | 0 | −0.304152 |
| 35 / 360.1 | +0.114615 | −0.454985 | +0.018907 (33) | 0 | −0.340370 |
| 27 / 260.1 | +0.092352 | −0.727211 | +0.008376 (26) | 0 | −0.634859 |

No site term was omitted **at these tips**: each Nx consists of eight elements including O. The nearest site among all sites is 3.052293 / 2.862865 / 3.002282 m.u. away, versus farthest selected element 1.125492 / 1.141233 / 1.530605. Sites can affect other bodies and the trajectory; this table does not exclude that indirect influence. Mean normalization changes speed, not the negative sign. These are instantaneous endpoint RHS projections, not integrated displacements or proof about every possible chain.

Independently recounted the committed replay: **12 observed intervals, 365 present samples**, no D1/D3/D4 removals. Every first absent sample retains the closing body in O's eight-entry held list, with r above sqrt(log(8)) and coefficient below 0.5/s. Thus these breaks are geometric strong-coefficient loss; deletion, root loss alone and removal from O's nearest-eight phase list do not explain them. Phase influences motion and transmission even though the strong-edge predicate itself ignores phase. The three instantaneous force examples support the local mechanism; they do not prove necessity of a seed or rule out all other trajectories.

The formation patch is called through `_b_path_attempt`'s module-global `geometric_trial`; it prunes trial edges and does not require a robust closing edge. The service wrapper changes the module rate and overrides the graph only during B-path, with restoration in `finally`; B1/measurement retain 0.5/s. Budget admission uses the raised cap/cost, while the scaled `cost()` makes the inherited D3 comparison equivalent to the raised budget; event costs are scaled. Budget-128 has zero cost/cap refusals and zero D3. The exponential kernel's common RHS line weights **both attraction and repulsion, including sites**; the 1.5 patch instead changes element **and site** motion selection, degrees and normalization, while phase selection stays at radius 3. Neither pilot isolates element attraction alone or excludes all local laws.

The active-site fraction is a fair descriptive training comparison on matched drives/horizons, after excluding contaminated evidence. It weights each step equally, with that step's active-site count in its denominator. It is not F5's unconditional eight-component E on fresh frozen-growth assays, whose gate is max(E); zero training connectivity does not establish an assay FAIL. The diagnosis now states this distinction correctly. Comments/docstrings calling the proxy “what E averages,” or claiming every formation incident edge is required robust, remain inaccurate and should be corrected in a future unpinned script revision.

## Options and a better next design comparison

**A** is fairly described as a new seeded protocol with a narrower claim. Its exact embryo remains a design prior, not an experimentally established minimum. **B** is a principled candidate, but the table omitted the **positive tensile prestrain** condition from round 1: an aligned spring chain at its rest lengths need not have positive linear transverse stiffness. Specify reciprocal bonds, positive stiffness k, equal spacing d greater than rest length ell, fixed endpoints, and tension `T = k(d−ell) > 0`. Then interior forces balance and transverse perturbations have restoring stiffness proportional to T/d. Ensure phase-dependent stiffness stays positive over the declared operating region; define formation/breakage, degree/cost accounting, site anchors and geometry↔mode feedback. This is a new model requiring its own normalization and numerical/fixture checks, not accepted RRG/C4 evidence. **C** remains viable: unconditional alternation is only one implementation of two-ended growth, and its failure on (ii) does not exclude demand-conditioned support growth.

That spring argument establishes mechanical stability only for the specified chain with frozen phases and bonds. It does not establish stability of the coupled geometry–phase–bond-remodelling system; that needs separate analysis and authorized validation.

Two narrower candidates deserve a fair comparison before treating A or a medium rewrite as compelled:

1. **Supported output-side growth under the current law.** Keep forward growth when it is mechanically adequate; when a closing/frontier body has predicted motion away from O, prioritize a bounded local support structure on the output side rather than blindly alternating a lone birth. Use the actual Nx, site terms and full force balance in a declared geometry-level criterion, preserve existing strong paths, and require adequate closing coefficients. This targets the observed imbalance while allowing the seeded arm to retain its successful growth schedule. It is an untested rule, and instantaneous balance alone cannot guarantee dynamic stability.
2. **A declared root-relative O pin.** At a specified initialization event, choose O once in the radius-1 central disk toward the first eligible driven root/demand, then freeze it. That disk remains at least 3 m.u. from radius-4 sites; retain O's non-root/no-direct-drive role and copy its pin into assays. Apply the same causal rule and cost/RNG treatment to all comparison policies; disclose the positional prior. The present x-axis swap does not test this rule. No success or qualification follows without a reviewed protocol and authorized evidence.

The single-group C variant already mentioned by the drafter also merits retention, with corrected atomic admission and geometry. A valid future comparison should separate support, placement and seed initialization rather than changing them together. The drafter should record this round-2 recheck and each disposition in docs/PLAN_CURRENT.md; that existing file is intentionally untouched here.

Review-of-review disposition: a separate Codex reviewer received the owner's request verbatim and independently confirmed the recovery contamination, group counts/admission defect and qualified alternatives. Its sole low clarification, limiting the spring stability argument to frozen phases/bonds, is incorporated above. This supporting recheck is same-family; the present review is cross-family against Claude's diagnosis.
