# 0040: 0g B2 batch: fair neighbour-bonus controls, a candidate-pick audit, readiness criteria up front, and approvals in a config file

**Date:** 2026-10-09 (~15:45). **Decided by:** the owner ("agree with your ideas/suggestion feel free to do it"), on Claude's five suggestions. **Recorded by:** Claude (claude-opus-5-5).

## Decision

1. **Candidate-pick audit.** B2 readouts report which candidate families the trained networks actually choose, per role and arm. If one teacher-formula family dominates (for example the P16 escort point), the script is still doing the thinking in disguise, and that tool is the first to replace (0039 addendum).
2. **Fairness rule.** Any helpful input that only one arm receives is also given to the other arms.
   - **Concretely:** N1 and N1r get the neighbour-target bonus (+2 toward enemies that nearby allies currently target; unweighted, since they have no phase) as new arms N1b and N1rb, trained in the same B2 run.
   - **Why:** the RRG ablation controls (`da0d4c97`) showed that about half to 60% of N2's target gain comes from that bonus, with about 6–8 points from phase-gated selection.
   - **The RRG claim** needs N2 to beat N1b and N1rb.
3. **Readiness criteria are declared before the fights.** "Fights at teacher level" is written into the B2 protocol before any outcome is read (for example a win share against T and own deaths within a margin of T over paired fights). It is not adjusted afterwards.
4. **Owner approvals live in a config file.** Owner-approved caps and thresholds (training cap, coverage time bound, structurally empty strata, parity bounds) live in an owner-approved config file that code reads. A change in that file is recorded but is not source drift; real code changes still lock.
5. **More DAgger.** After B2 trains: 5–10 DAgger rounds as measured cost allows, with DART noise considered, each round checked in real fights.
6. **Arms trimmed.** The plain + history-features arm (N1h) is dropped from B2; it never clearly beat N1. B2 arms: N1, N1b, N1r, N1rb, N2 (all with tools).
