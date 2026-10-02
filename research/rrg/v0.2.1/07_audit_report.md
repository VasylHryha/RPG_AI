# 07 — Audit report: substantive corrections, source checks and remaining gaps

**RRG v0.2.1 · 2 October 2026**

## Verdict

The previous package was not yet at the requested quality level. Its weaknesses were substantive: inconsistent project priorities, mixed evidence categories, several inflated mathematical interpretations, a conflation of physical background formation with coarse-graining, and incomplete source provenance. Adding more pages or references would not fix those issues.

The revised package preserves the author’s source-direction idea and broader hypotheses. It makes the immediate publication an explanation plus an evidence map, with optional mathematics and open invitations. No numerical quality score is offered as though it were independent assessment; the checks and remaining limitations are listed below.

## Scope of the audit

The current 04, 05 and 06 were inspected and revised. The original README and foundation files 01–03 were retrieved and checked for definition continuity and major conflicts, not fully source-audited. Twenty-two primary case records were assembled or rechecked at the read depth specified in each card, with three separate further-reading records. Selected small calculations were checked with a deterministic script. The earlier research ZIPs were inspected for readable contents and archive integrity, but their simulations were not rerun.

The audit is not independent peer review, a systematic literature search, a full reproduction of paper methods or a retraction-database clearance. Some findings are verified at original-abstract level. That is adequate for the deliberately narrow abstract-level summaries, not for claims about experimental robustness that require the full methods and data.

## 1. Project direction and fidelity

| Finding | Consequence | Repair |
|---|---|---|
| 04 §40 and 05’s structure kept universal proof as the next mandatory task | Contradicted the user’s explicit publication-and-evidence-first plan | README, 04 §40 and 05 now make mathematics optional; existing examples need not be rediscovered. |
| Earlier revisions had reduced a long discussion to only background recursion | Risked losing persistence, competition, life, engineering and cosmological conjectures | Retained the full 04 and added 08 with 23 session-coverage entries. |
| Same abstract process and same mathematical equation family were treated as one claim | Quietly narrowed or replaced the author’s idea | Distinguished the core interpretation from stronger possible formalizations. |
| Older snapshots contained priorities inconsistent with current companions | Readers could treat incompatible files as simultaneously authoritative | Current README defines reading order; unchanged 01–03 live under `foundations/`, with explicit errata. |
| Prior claims about persistent/project saves exceeded what the current artifacts establish | Could create false confidence that the online source had changed | Deliver a versioned conversation package; no claim of external overwrite or publication. |

## 2. Conceptual and evidential corrections

| Finding | Why it matters | Repair |
|---|---|---|
| Physical background change and mathematical coarse-graining were merged | Changing a description alone is not the creation of a new physical level | 04 §11 and §24 explicitly separate physical evolution from reduction. |
| “White noise” could be read as a literally featureless source without dynamics | Noise statistics alone do not specify forces, stability or energy exchange | Retain noise-like starting intuition, distinguish correlated effective backgrounds, and state what models assume. |
| Stationary spatial modes and temporal resonators were blurred | A patterned equilibrium does not by itself establish oscillatory self-maintenance | Corrected 04 definitions, 05 and E05. |
| A higher level was described as adding new degrees of freedom without qualification | Effective coordinates and accessible configurations differ from microscopic dimensionality | Qualified the possibility-space discussion; monotonic growth remains an open conjecture. |
| “Previous level already created what it can” suggested complete exhaustion | A later organization need not wait for all possibilities at an earlier level | Retained the intuition as conditional accessibility, with coexistence and branching allowed. |
| Lifetime, resonance strength, influence and spatial dominance were too easily combined | Long-lived weakly coupled states need not spread; strong drive can destabilize | Added loss/saturation/coherence qualifications and comparison cases E17/E22. |
| Repetition, entrainment, domain growth, replication and hierarchy were merged in the conversation | Success at one operation does not establish the next | Current claim map separates them. |
| “Every arrow has evidence” suggested a demonstrated composed chain | Different mechanisms in different systems may not causally concatenate | Catalogue states what each case demonstrates and what full sequence is still missing. |
| “No separate growth law” could be read as “no assumptions or dynamics needed” | Positive feedback can be built into chosen couplings | Every case says what was supplied; 05 separates inserted laws from results. |
| Cosmic expansion and engineered “new laws” were rhetorically close to demonstrated results | Domain growth is not metric expansion; effective control is not arbitrary law replacement | Preserve both as open conjectures with narrower established components. |

## 3. Mathematics: specific corrections

The previous note contained valid pieces of algebra, but their interpretation was too strong. These are the main repairs, not a claim that all possible future models have been checked.

**Finite-domain spectrum.** The maximum of \(r-(q^2-k^2)^2\) equals \(r\) only if the relevant domain permits \(|k|=q\), or wavenumbers are continuous. A finite domain may exclude that value. Current 05 states the discrete maximum and the resulting shifted threshold.

**Spatial pattern versus oscillator.** The real first-order Swift–Hohenberg-type example does not establish a temporal resonator merely by having a stable spatial pattern or a nonzero scalar fixed point. The current note treats these as pattern/order-parameter examples.

**Signed coordinate versus radius.** Old 05 introduced a nonnegative radius \(a=|A|\), then used signed additive-noise formulas. The revision uses an explicitly signed scalar and records why a complex-amplitude radius needs an Itô and measure correction. Its bistable-range branch algebra is retained with its proper scope.

**Noise and permanence.** Noise can permit barrier crossing into and out of a basin. A stationary probability density is not a proof of permanently maintained organization. Finite-noise lifetimes require a specified stochastic problem.

**Background response.** \(\Delta B=\rho I_*\) was conditional on constant intensity. With feedback \(I_*(B)\), the fixed point is implicit and can be unstable. The updated note gives the appropriate derivative for a one-variable adiabatic reduction and warns that a coupled model needs its own stability analysis.

**Mode “creation.”** Negative linear growth means damping, not nonexistence. Crossing zero means instability, not proof that a stable new resonator appears. The next channel and its background sensitivity had been inserted into the example; the rewrite says so.

**Scale growth.** Choosing decreasing \(q(B)\) builds increasing preferred wavelength into the example. The old repeated-level growth plot is an assumption-driven illustration, not evidence that eight levels arose automatically. Wavelength is not the cosmological scale factor.

**Error bounds.** The old failure criteria treated an exponentially growing upper bound as making predictions meaningless. An upper bound does not establish actual error growth. Even zero error satisfies the assumed recurrence for \(K>1\). Conversely, a contracting bound is sufficient under its assumptions, not evidence that a real system satisfies them. The recurrence itself needs controlled reduction maps and comparable norms.

**Action notation.** The foundations and 04 compressed stationary action, potential energy, force and spectra into a common notation. For a general dynamical action that is not automatically valid. Current 04 requires a specified variational or dynamical setting; the foundation snapshot is retained with explicit errata.

These fixes are in current 05, rather than hidden in a footnote that leaves the old “proof” claims in the public reading path.

## 4. Source verification and classification

The A/B/C/D system mixed result type and interpretation. The replacement is two-dimensional: **experiment/simulation/theory** and **component/bridge/analogy/constraint**. Claims still open are not classified as evidence.

Concrete source repairs include:

| Earlier problem | Current disposition |
|---|---|
| Noise-order review had incomplete or incorrect author attribution | F01 records Sagués, Sancho and García-Ojalvo, DOI 10.1103/RevModPhys.79.829. It is orientation, not another independent experiment. |
| Self-organized resonance could be read as a laboratory result | E09 explicitly identifies the reacting-particle study as a simulation. |
| Engineered control in Chladni manipulation and colloidal swarmalators was understated | E02 and E08 specify the apparatus and feedback/control supplied. |
| General micro/nano manipulation was supported by loosely matched broad reviews | E03 uses a primary microparticle experiment and does not promote it to a nanoscale result. |
| A nonresonating-grain experiment was grouped as a resonant-mode demonstration | E22 is now a comparator/constraint. Its actual apparatus is part of the finding. |
| Kedia’s preprint and journal title were not cleanly distinguished | E17 links the 2019 preprint lineage to the 2023 journal paper; it is one study, not two confirmations. The journal report also includes experimental evidence, not separately method-audited here. |
| An RNA source had an update notice | E13 records the publisher’s 31 October 2012 minor Figure 1 correction; no summary depends on that figure. |
| Recent mathematics was treated too broadly | E21 states its assumed heterogeneous equation and near-onset scope. F03 records its future issue date separately from current online availability and its noise-regularity assumptions. |
| Chen & Cory 2026 lacked sufficient bibliographic detail | The article was verified, not labelled fabricated: DOI 10.1103/j65l-f8lf. It remains optional theory reading (F02). |

Not every older bibliography entry is repeated as an active source. Review-led entries were often replaced by primary examples for the same theme; the original lists remain in the archive. Omission from the active shortlist does not mean an older source is false. Detailed unverified legacy claims are not silently carried forward as checked facts.

## 5. Additional useful cases

Five new primary cards extend the 17-topic catalogue: E18 optical binding, E19 controlled random-light interactions, E20 self-replicating granular bands, E21 a controlled slow-amplitude mathematical description, and E22 nonresonant vibrational transport as a constraint. They add coverage, not five confirmations of the universal theory.

E19 is particularly relevant to the fluctuating-background intuition, but already contains particles and an externally generated optical field. E20 links vibration, organization and duplication in one material system, but not unlimited hierarchical levels. These qualifications strengthen the usefulness of the examples rather than erase the connection.

The report’s empirical statements are traceable to the DOI-linked case cards in [06](06_evidence_catalog.md) and the machine-readable [source register](sources.json).

## 6. Checks actually run

Nine deterministic groups in [checks/verify_small_results.py](checks/verify_small_results.py) pass. They check the limited calculations recorded in [verification_results.json](checks/verification_results.json), not the correctness of a universal theory.

The original numerical ZIPs have readable contents and passed ZIP integrity checks. The 05 document inside the earlier mathematics ZIP matches the mounted original. No claim is made that the earlier 32-cell results, convergence checks or literature references were independently rerun.

The release includes a source-ID/DOI duplicate check, active local-link checks, selected Markdown/LaTeX delimiter checks, original-file hash comparisons and a manifest. Results are in [package validation](checks/package_validation.json). Syntax and hashes are quality controls, not scientific validation.

## 7. Remaining gaps and publication boundary

The full source-to-repeated-level causal sequence is not established by this evidence map. No unique novelty claim, fundamental-force derivation, cosmological mechanism, AI benefit or arbitrary engineered rule set has been verified. Some primary papers were checked through their original abstracts rather than full methods. The foundations’ broader physics bibliography has not been comprehensively refreshed. Videos were not watched and datasets were not reanalysed.

Those limits do not block publishing a clearly labelled hypothesis. They do block presenting it as a verified universal theory or the catalogue as an exhaustive review. Author attribution and publication licences also remain project decisions; no external website or repository was created or modified.

**The improvement is a more faithful and inspectable publication package—not an invented numerical score and not a claim that uncertainty has disappeared.**
