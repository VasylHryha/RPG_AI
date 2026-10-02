CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: gpt-6
Rechecked proposal commit: da46a40
Proposal SHA-256: aadbd68aadb9df15386da66a9a7c79eb11ccf08a73639a378a881a45a6fd70ef
Third re-check SHA-256: 617d29e238cda943fc916d890fa5fa77b12ead6f1c0659476a620248cc5a6dbe

Date: 2026-10-02. Scope: R3-1 through R3-4 and the tenth-self-audit amendment only, compared with `git diff 6a99b18 da46a40 -- experiments/c6_proposal.md`. Both supplied hashes match the working files and their named commits. Proposal locations below refer to da46a40. No project code, simulations, dynamics, seeds or new numerical probes were run.

| Finding | Status | Proposal lines | Evidence |
|---|---|---|---|
| R3-1 | PARTIALLY_RESOLVED | 69, 310–326, 437 | The primary statistic now explicitly includes geometry, retains the positive two-clique witness and excludes the diagnostic from verdicts, but the unqualified flat-blob claims at 69 and 326 still exceed the demonstrated null property. |
| R3-2 | PARTIALLY_RESOLVED | 206, 312–316, 437 | The operator and censored/invalid-τ abstention are specified with implementer ownership, counts and no verdict effect, but the newly required ratio has no zero-denominator rule and the disconnected-graph explanation conflicts with the definition of λ₂. |
| R3-3 | RESOLVED | 597, 600–602 | The contracts now require one shared scored set within each pair and explicitly label the consensus contrasts uncorrected. |
| R3-4 | RESOLVED | 302, 945, 970 | The operative text preserves exact rigid whole-part initial-kick equality and restricts identical-phase nonuniform kicks to first-order equality, with the finite-kick counterexample stated. |

R3-1's central scoring defect is resolved. Specifically:

- **Primary meaning: yes.** Lines 310, 318 and 437 define predictive grouping advantage, geometry included.
- **Locked-core consistency: yes.** `00_LOCKED_CORE.md:26–41` defines R = (G, M), including geometry-supported modes; section 7, lines 84–96, defines effective units in further interactions without demanding geometry-independent advantage. This statistic is a compatible operational comparison, not by itself the locked definition or proof of closure.
- **Two-clique witness counts: yes.** Line 322 now requires it to be positive, and the primary contrast no longer subtracts its identical diffusion null. The positive value established in the committed third re-check, lines 33–35, is therefore retained; it was not recomputed here.
- **Diffusion has no verdict path: yes.** Lines 311, 316 and 437 explicitly exclude it, and line 628 specifies a mutant for violating that exclusion.
- **Residual overstatement: yes.** Lines 69 and 326 still assert that arbitrary contiguous groupings in a flat blob are equally predictive. The actual cancellation proof at 308 requires identical responses of all unprobed elements; a local medium with spatially varying responses need not satisfy it. Replace those claims with that restricted consensus-null property and describe specificity as one comparison alongside the other gates. Also replace “the locked core's own test” at 69 with “an operational test compatible with §7.” This remaining wording issue does not separately block the corrected scoring design. The ninth self-audit is historical and superseded by the tenth; it does not reintroduce subtraction into the operative rule.

R3-2's operator is now unambiguous for a connected nontrivial graph: L = D − A for the undirected union, unit weights, and generator −L/(τ_n λ₂). Its τ validity checks are binary. The complete diagnostic output is **not yet total**, for the reasons below.

## New amendment findings, ranked

### R4-1 — Medium: the reported diffusion ratio is undefined on allowed inputs

**Location:** lines 315–316; ledger 206. **Blocks registration: yes**, under stop rule 8 (line 733); it does not compromise the primary verdict.

**Defect and failure scenario:** `c^null / c` is newly required without a domain or aggregation rule. The required consensus fixtures allow c = 0 with a finite positive τ and a connected graph, so the group-level NOT_COMPUTED conditions need not fire. If the diagnostic contrast is also zero, the requested share is 0/0; otherwise it still divides by zero. Negative contrasts also show that this ratio is not generally a fraction of explained advantage or constrained to [0,1].

**Smallest fix:** retain the raw diagnostic contrast and either remove the ratio or specify its aggregation and a separate, counted, implementer-owned yes/no ratio abstention for a zero or non-finite denominator, with no imputation or verdict consequence. If retained, label it a signed contrast ratio rather than an explained share and add its dimensionless normalization to the ledger.

The new graph abstention also needs a wording correction: line 313 defines λ₂ as the *smallest positive* eigenvalue, which can exist in a disconnected graph (two disjoint edges have spectrum 0, 0, 2, 2). Line 316's “disconnected (no λ₂)” is therefore false, and ledger 206 only mentions absence. State disconnection and absence of a positive mode as separate abstention conditions consistently in both places, or define λ₂ as the second eigenvalue in sorted order. Skipping disconnected graphs is a valid binary policy; its present explanation is not.

### R4-2 — Low: the new compactness quantity is absent from the normalization ledger

**Location:** line 317 versus ledger 185–211 and evaluator-side list 213–219. **Blocks registration: yes**, as an explicit proposal-ledger requirement, not an endpoint-design failure.

**Defect and failure scenario:** compactness now measures level-(n−2) centroid geometry in element spacings, but neither its quantity nor this evaluator-only normalization is listed. An implementation computing it would contradict line 183's requirement and fail the promised missing-quantity contract. At transition 3 it also reads across levels, which must be declared on the evaluator side.

**Smallest fix:** add a compactness ledger row identifying the sub-part level, the fixed group-at-s₀ element-spacing denominator and the stated mean radius-of-gyration aggregation; include it in the evaluator-side `unit_specificity` entry. Keep it reported only. Alternatively remove this optional diagnostic.

The former blocking geometric-subtraction design issue is gone. Registration blockers remain only in the amended reporting specification and ledger, so this is not approval as written. The drafter owns these fixes and their self-audit. The owner will next decide **D8 and D1 (approval)**; D8's ordered response-floor/error-ceiling rule remains executable, and this review neither chooses its numerical ceiling nor authorizes implementation.

## Commands run

Read-only commands are grouped below; repeated `nl`, `sed` and `rg` reads used narrowed ranges/patterns of these same files.

```text
pwd
git status --short
git rev-parse HEAD
rg --files -g AGENTS.md -g '*c6_proposal*' -g '*QUALITY_STANDARD*' -g 'PROCESS_REVIEW.md'
rg --files --hidden docs experiments -g AGENTS.md
rg -n 'GeoMind|ai_RPG_test|C6 proposal|RRG' /Users/new/.codex/memories/MEMORY.md
cat AGENTS.md
cat GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
cat docs/PROCESS_REVIEW.md
cat /Users/new/RiderProjects/RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md
nl -ba docs/reviews/c6_proposal_recheck3_codex.md
nl -ba experiments/c6_proposal.md
nl -ba GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
nl -ba /Users/new/RiderProjects/RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md
sed -n '82,110p' docs/reviews/c6_proposal_recheck3_codex.md
sed -n '1,100p' docs/reviews/c6_proposal_recheck_codex.md
rg -n <heading/statistic/diagnostic patterns> experiments/c6_proposal.md
rg -n <invariant/H-C/recursive patterns> GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
git diff 6a99b18 da46a40 -- experiments/c6_proposal.md
shasum -a 256 experiments/c6_proposal.md docs/reviews/c6_proposal_recheck3_codex.md
git show a9e72b1:docs/reviews/c6_proposal_recheck3_codex.md | shasum -a 256
git show da46a40:experiments/c6_proposal.md | shasum -a 256
shasum -a 256 /Users/new/RiderProjects/RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md
git diff --check
git ls-files docs/reviews/c6_proposal_recheck4_codex.md
```

The nested-instruction search and memory search returned no matches; no memory-derived fact was used. `git diff --check` was run separately after the no-match search. The only write was `apply_patch` creating this review. Final read-only validation used `sed` on this review, `git status --short`, `git diff --check`, and the proposal/third-review hash command above. No `git add` or `git commit` was run.
