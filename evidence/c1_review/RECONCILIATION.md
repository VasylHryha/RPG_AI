# C1 R002 verdict reconciliation

Two receipts disagree about C1 R002 (`geomind-c1-r4-002`):

| Receipt | SHA256 | Verdict |
|---|---|---|
| `ACCEPTANCE.md` (separate agent, 13:15) | `5b008dac4fa986e139d487a2b9d1c3da633ff462098cd4411dbc1c12c16b364c` | ACCEPTED |
| `CLAUDE_ACCEPTANCE.md` (Claude review) | see the current file | CHANGES_REQUIRED |

The owner delegated the decision ("do them"). **Decision: CHANGES_REQUIRED stands for R002.** `ACCEPTANCE.md` is kept byte-identical as the historical record of a superseded verdict; neither file has been edited to agree with the other.

## Why

The two receipts agree on the transaction facts. Every R002 commit was reference-correct, every refusal kept byte-identical prior state, and the 19 inputs and 48 saved states matched. They disagree on whether the evidence supports acceptance. The earlier acceptance missed, or stated incorrectly, points that were each verified by a reproducible check:

1. **Not fresh data (§5.2).** "Fresh seeds" generated the same 16 worlds as R001 up to node relabeling (`evidence/c1_claude_review/focused_checks.json` → `seed_isomorphism`: 16/16 identical). The R002 redesign was made after inspecting R001 failures on those geometries, so "13/16" was not held-out evidence. On seed-varied worlds, the local queue resolved 0 contradictions (R003 0/12, R004 0/20), including at 32 nodes.
2. **Misattributed mechanism.** 12/13 commits used zero relaxation steps, so frame placement produced them, not the specified dynamics.
3. **Incorrect claim.** `ACCEPTANCE.md` states that "ten metered certificates prevent an empty queue from qualifying a bad equilibrium". The ten passes recomputed an unchanged state; one certificate does that. They made up 97.4–99.98% of the charged visits in no-relaxation commits.
4. **Test evidence weaker than presented.** Its "10 PASS" relied on checks that caught 7/15 deliberate defects (`mutation_checks.json`), including no test of duplicate-copy removal, budget charging, or the evaluator's energy and status gates.

## Effect on the C2 gate

Neither R002 receipt is the C2 prerequisite any longer. R002 → R003 → R004 is the repair chain, and **the C2 gate is the independent acceptance decision on R004**. That decision is recorded separately in `evidence/c1_r004_independent/INDEPENDENT_REVIEW.md`. No code reads the C1 acceptance files; `run_c1` binds only to the C0 acceptance.
