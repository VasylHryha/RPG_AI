# Process review: architecture, lifecycle and rules, compared with established practice

Date: 2026-10-01. Scope: how GeoMind milestones are registered, built, verified, reviewed, accepted and recorded (C0–C2, plus the C4 proposal). This is not a review of the science.

## 1. The current solution, as it is

**Artifacts.**
- The normative standard (`GEOMIND_…_R4.md`). It also carries an ever-growing execution log.
- Registration manifests in `experiments/`.
- Code (`geomind/`, `native/`) and focused tests (`tests/`).
- Tooling (`tools/`): gate, two per-milestone pipelines, two mutation probes and hooks.
- Per-revision evidence folders in `evidence/` (24 so far): receipts, archived source, states, reviews.
- Agent rules (`AGENTS.md`, plus `CLAUDE.md` importing it).

**Lifecycle.**
1. Propose, then register a manifest before any fitting.
2. Implement → REVIEW_READY.
3. Run the gated pipeline (preflight → tests → smoke → mutation → recorded panel), each stage stamped against a source fingerprint with artifact hashes.
4. Commit the evidence; pre-commit re-verifies it.
5. One independent review, with a time cap.
6. ACCEPTED (code frozen by hash), or CHANGES_REQUIRED → new revision on fresh seeds.

Research decisions (e.g. STOP_THIS_BRANCH) are separate from implementation acceptance.

**Enforcement layers.**
1. `tools/gate.py` stamps.
2. Self-guarding runners.
3. Claude Code and Codex PreToolUse hooks (shared `gate_hook.py`).
4. A git pre-commit hook.
5. Written rules in `AGENTS.md`.

**What works well, keep it.**
- Implementation acceptance is kept separate from hypothesis support.
- Negative results are reported and recorded as decisions.
- Evidence is never overwritten.
- Exact source snapshots travel with each receipt.
- Strong simple baselines exposed the C1 and C2 stop signals.
- Independent reviews caught real defects in four revisions.
- Gates fail fast: the R006 pipeline stopped in 2 s instead of failing deep in a long run.

## 2. Gaps found in this repository

| # | Gap | Evidence from this project |
|---|---|---|
| G1 | **Bespoke pipeline per milestone.** `verify_milestone.py` (C1) and `verify_c2.py` (C2), two mutation probes, and milestone names hard-coded in `gate.py` (`"c1"`, `"c2"`). | C2 tooling diverged in style and stage semantics; C4–C8 would add five more copies. |
| G2 | **One global fingerprint.** Any change in `tools/`, `tests/` or `geomind/` invalidates every milestone's stamps. | Codex's C2 tooling edits reset C1's verified stamps. |
| G3 | **Status written in five places** (README, standard, `AGENTS.md`, acceptance documents, handoffs). | Repeated edit failures on changed anchor text; a commit message claimed a standard update that never applied. |
| G4 | **The standard mixes rules with history.** The normative R4 text carries an append-only execution log. | It grows with every revision; agents must edit near normative text to record status. |
| G5 | **Registration timing is not provable.** Nothing proves a manifest was committed before its results existed. | "Registered before fitting" rests on trust. |
| G6 | **Agent provenance is invisible.** Every commit carries the owner's identity; which agent implemented and which reviewed is prose only. | The C2 author and reviewer are both "a Codex agent"; family independence cannot be checked by a machine. |
| G7 | **Registered endpoints can go silently unevaluated.** | C2's `gradient_direction_cosine_min` and `equilibrium_abs_tolerance` were never computed by the panel and not listed as not run; the first review missed it. |
| G8 | **No evidence index; inconsistent names** (`c1_review`, `c1_claude_review`, `c1_current_independent`, …). | Finding "the" current receipt takes reading prose. |
| G9 | **Local-only verification state.** Stamps live in git-ignored `.gate/`; there is no CI. | A fresh clone cannot see what was verified except via committed `PIPELINE.json`. |
| G10 | **The native toolchain is not pinned.** The compiler is recorded, not locked; the binary is not committed. | C2 results depend on the local clang. |
| G11 | **Invariant checks are ad hoc.** Randomized probes are one-off scripts in evidence folders. | Reviewers reinvented similar probes in each review. |

## 3. How established projects solve these

| Practice | What it does | Maps to |
|---|---|---|
| **DVC pipelines** ([running pipelines](https://dvc.org/doc/user-guide/pipelines/running-pipelines)) | `dvc.yaml` declares each stage's command, dependencies and outputs; `dvc.lock` stores their hashes and is committed; `dvc repro` reruns only stages whose own dependencies changed. | G1, G2, G9: our stamps are a hand-made `dvc.lock`, but with one global dependency set and an uncommitted lock. |
| **Pre-registration and registered reports** ([NeurIPS 2020](https://neurips.cc/virtual/2020/workshop/16158), [2021](https://nips.cc/virtual/2021/workshop/21885)) | The protocol is reviewed and accepted before results exist; evaluation then focuses on design quality, not numbers. | G5: commit order should prove registration came first; optionally review the registration itself. |
| **ML reproducibility checklist** ([Pineau et al., JMLR 2021](https://jmlr.org/papers/v22/20-303.html)) | A per-paper checklist of claims, settings, seeds, compute and statistics that every submission answers. | G7: a machine-checked "every registered item is evaluated or explicitly NOT_RUN" list. |
| **LLM self-preference bias** ([Panickssery et al., 2024](https://arxiv.org/html/2404.13076v1)) | LLM judges recognize and favor their own (and same-family) outputs; the bias is causally linked to self-recognition. | G6: same-family review is weaker evidence; cross-family review should be the default and recorded. |
| **Writer/reviewer separation with diverse models** ([OpenHands guide](https://www.openhands.dev/blog/claude-code-best-practices-agentic-coding)) | Separate agents and contexts for writing, reviewing and testing; a different model as reviewer improves results. | G6: matches our practice; make it a rule. |
| **AGENTS.md open standard** ([InfoQ](https://infoq.com/news/2025/08/agents-md/), [Linux Foundation portability](https://codex.danielvaughan.com/2026/04/07/agents-md-open-standard-cross-tool-portability)) | One tool-agnostic instruction file; nested files per directory for local rules. | Already adopted. Nested per-milestone `AGENTS.md` files can hold milestone-specific rules. |
| **`Assisted-by:` commit trailer** (Linux kernel AI policy; [summary](https://www.ssdnodes.com/learn/ai-assisted-code-open-source-policies)) | `Assisted-by: AGENT:MODEL` records the AI's involvement; the human stays responsible. | G6: machine-readable agent provenance. |
| **Architecture Decision Records** ([MADR](https://expertsystem.readthedocs.io/stable/adr.html)) | Short, numbered decision files: context, options, decision, consequences. | G4: STOP_THIS_BRANCH, the R002 reconciliation and the gating design become ADRs; the standard stays normative. |
| **in-toto / SLSA provenance** ([overview](https://blogs.eclipse.org/post/mika%C3%ABl-barbero/understanding-software-provenance-attestation-roles-slsa-and-toto)) | Signed statements binding artifacts (by digest) to source commit and build steps; verifiers re-hash. | G9, the forged-stamp gap: `PIPELINE.json` is already an unsigned attestation; signing is optional hardening. |
| **Mutation tools** ([mutmut/cosmic-ray comparison](https://pytest-gremlins.readthedocs.io/en/latest/guide/comparison/)) | Generate broad syntactic mutants automatically. | G11: complements our semantic mutants (which are better for numerical claims); not a replacement. |
| **Hypothesis property-based testing** ([SciPy proceedings](https://proceedings.scipy.org/articles/Majora-342d178e-016)) | States invariants over whole input domains and shrinks counterexamples; it has found real bugs in NumPy and Astropy. | G11: permutation, translation and rotation invariance and conservation laws become reusable tests instead of one-off probes. |
| **Codex hooks and execpolicy rules** ([Codex hooks](https://developers.openai.com/codex/hooks)) | PreToolUse hooks (exit 2 blocks) plus Starlark `.rules` (`forbidden`); both vendors call hooks a guardrail, not a boundary. | Already adopted; keep the self-guards as the real boundary. |

## 4. Recommendations, prioritized

**P0: before any C4 code** (estimate: one focused session; protects every later milestone)

1. **One generic, declarative pipeline (DVC-style).** Each milestone gets a file `milestones/cN.json`. It declares the dependency globs, the stage commands (tests, smoke, mutation, panel), the mutant list and the evidence folder. One runner, `tools/verify.py --milestone cN`, and one gate both read it. The fingerprint is computed **per milestone** from its own dependencies, so a C4 change no longer resets C1/C2. Committed `milestones/cN.lock.json` files replace the git-ignored stamps (`dvc.lock` pattern). C1/C2 keep their frozen runners as history; C4+ use the generic one.
2. **Endpoint coverage check (G7).** The receipt must list every manifest endpoint key under `evaluated` (with value and verdict) or `not_run` (with reason). The pre-commit hook refuses evidence where any registered key is missing.
3. **Registration order check (G5).** The pre-commit hook refuses panel evidence unless its manifest file was committed, unchanged, in an earlier commit than the evidence.
4. **One status source (G3).** A machine-readable `STATUS.json` (milestone → revision → implementation status, hypothesis verdicts, review link, frozen hashes). README and standard show a generated block, and a check fails on mismatch. Status edits become one-file edits.
5. **Agent provenance (G6).**
   - Commits carry `Assisted-by: Claude:claude-opus-5-5` or `Assisted-by: Codex:<model>` (kernel convention).
   - Manifests record `implementer_family`; review receipts record `reviewer_family`.
   - The review gate requires different families by default; a same-family review must say so.
   - Note: this harness also adds a `Co-Authored-By: Claude` trailer. Keep both unless the owner chooses otherwise.

**P0 implementation status (done, before any C4 code):**

- **P0-1, generic pipeline:**
  - Files: `milestones/c4.json`, `tools/milestones.py` (gate), `tools/verify.py` (runner) and `tools/milestone_mutation.py` (parallel probe).
  - The fingerprint is per milestone.
  - Deviation: the committed attestation is `evidence/cN_rNNN/PIPELINE.json`, which the pre-commit hook checks against the current fingerprint and re-verified stamps. Stamps stay local in `.gate/cN/` instead of a committed `.lock.json`, because they reference staging artifacts that are not evidence.
- **P0-2 and P0-3:** `tools/milestone_precommit.py` checks endpoint coverage and registration order (`tools/verify.py` also refuses incomplete coverage at the panel stage).
- **P0-4:** `STATUS.json` plus `tools/status.py`. The README block is generated, and the pre-commit hook runs `--check`. The standard's Current work row now points to `STATUS.json` instead of duplicating it.
- **P0-5:**
  - `tools/provenance.py` (git commit-msg) requires `Assisted-by:` or `Human-authored: yes`.
  - The review folder is named per family, and the pre-commit hook refuses a same-family review unless it is declared.
- **Agent hooks:** `tools/milestone_hook.py` is wired for Claude Code and Codex next to the frozen legacy hook.
- **Tests:** `tests/test_milestones.py` runs a fake milestone end to end in a temporary repo.
- C1/C2 tooling is unchanged (bound by the accepted receipts).

**P1: during C4**

6. **ADRs (G4).** Write `docs/decisions/NNNN-title.md` (MADR) for the gating design, the R002 reconciliation and the C1/C2 STOP decisions. Then move the execution log out of the standard into `docs/log/`, so the standard stays normative and stable.
7. **Evidence index (G8).** A generated `evidence/INDEX.json` (milestone, revision, kind, verdict, commit), with one naming scheme for new folders: `cN_rNNN`, `cN_rNNN_review_<family>`.
8. **Property-based invariants (G11).** Write C4's invariance and ablation checks as Hypothesis tests, so reviewers run them rather than rewrite probes.

**P2: when there is a remote**

9. **CI** runs `tools/verify.py --through tests` on each push. The recorded panel stays a deliberate, once-per-revision local run.
10. **Optional hardening:** sign `PIPELINE.json` as an in-toto statement; pin the native toolchain (container or Nix) for C++ milestones.

## 5. Effect on the C4 proposal

C4 should be the first milestone on the generic pipeline (P0-1), with endpoint coverage (P0-2), registration order (P0-3) and recorded family provenance (P0-5) enforced from the start. Its invariance checks fit property-based tests (P1-8). The proposal's science is unaffected.
