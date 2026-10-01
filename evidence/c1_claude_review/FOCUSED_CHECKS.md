# Claude reviewer focused checks — C1 R002 and R003

These are reviewer-only diagnostics, kept separate from the original receipts, which were not modified. The C0 world experiment was not rerun. The registered R002 panel was not rerun.

| File | SHA256 |
|---|---|
| `review_checks.py` | `d6de2dd58280ab4d01617ca886880d050e4c733d5ea70e571fc153a7f160f902` |
| `focused_checks.json` | `5beb3667fbbf64c0d4215121d0c1f3d76c05a5df695de6f1eaa6a5a4bd3e8e74` |
| `review_checks.log` | `420c0b335accc6b49b1f6992bf03288abf2f1125d347fcfa279ebd8c052fb0a1` |
| `mutation_checks.py` (version used for the R003 probe; the final version is listed in the R004 section) | `ba9c4f137b2df537e90a875eb91bc613e665ebf19810b9cbd71236d16439c604` |
| `mutation_checks.json` (R002) | `97930c7fb296805c7ce6092c82477f698367c18e9d1faac9ec7474e05d17cf65` |
| `mutation_checks_r003.json` | `a747cacf021a2df00592fcf45b245fed9b13047319f8a05fecb9f975a857af33` |

`review_checks.py` ran once, in 228.5 s, against the R002 source while live source still matched the R002 receipt (`identity.receipt_matches_live: true`). The R003 edits came after its modules were imported, so every result below describes R002 code. `mutation_checks.json` was produced by an earlier version of `mutation_checks.py`. That earlier version had the same 15 R002 mutants. The final version only adds the `--live` mode and two mutants that apply to R003 only.

## R002 results (`focused_checks.json`)

| Check | Result |
|---|---|
| Identity | All 19 inputs: receipt = live = archived `source/`. All 48 saved states match the receipt hashes. The C0 acceptance hash is bound. |
| Seed isomorphism | For each size/intervention, R001 seeds, R002 seeds and an arbitrary seed produced identical position-space worlds: same nodes, edges, offsets and intervention. **16/16 identical up to relabeling.** |
| Mechanism used by commits | **12 of 13** commits ran **0** relaxation steps. Certificates were **97.4–99.98%** of their dynamic visits, from 10 passes over unchanged coordinates. `touched_edges` equals the full edge count in every commit. |
| Cost vs fresh recompute | **13/13** commits were slower end to end than both a fresh sparse LS and a fresh compiled solve. |
| R001/C0 artifact migration | All 48 real archived R001 artifacts (32 C1 v1, 16 C0 v2) migrate with identical sampled answers. There were 0 rejections. |
| Randomized differential | 300 chained random worlds produced 616 updates. They mixed new nodes, isolated nodes, bridges, reversed and duplicate edges, weights 0.25–3 and contradictions. Results: **616 PASS, 0 wrong commits, 0 broken rollbacks**; maximum error vs dense LS `3.56e-7`. |
| Unresolved replay (diagnostic budget 20M) | 128 nodes converged after **2,159,663** visits, 21.6× the cap and 64× the fresh sparse LS's 33,635 visits, with error `1.29e-7`. 512 and 2,048 nodes were **still NOT_CONVERGED at 20M**. The archived before-states regenerate byte-identically. |
| Probes | A no-op update at 512 nodes cost 9,460 visits (10 × E). An isolated new node gives PASS with UNIDENTIFIABLE answers. A tiny-weight (1e-6) contradiction was NOT_CONVERGED at 2M visits, while the reference solved it. After a refusal at 128 nodes, the state answered 60 queries `OK`, and **20 were wrong for the new observation**. The state exposes no refusal marker. |

## Mutation probe: does the test suite catch deliberate defects?

Each mutant ran `tests/test_c1.py` in a scratch copy. The live checkout was never touched.

| Mutant | R002 (10 checks) | R003 (12 checks) |
|---|---|---|
| Frame offset sign flipped | caught | caught |
| Re-gauge removed | caught | caught |
| Freed old anchor not queued | survived (the certificate compensates) | caught (exact accounting) |
| Local quiet check ignores step tolerance | caught | survived (the certificate plus forced step compensate) |
| Local force ignores weight | caught | caught |
| Ten certificates reduced to one | survived (R002 only) | n/a |
| Forced certificate step removed | n/a | survived (summation-order mismatch not constructible in tests) |
| Certificate visits not charged | **survived** | caught |
| Warm-start reads not charged | **survived** | caught |
| Budget never enforced | caught | caught |
| Removal of one duplicate copy allowed | **survived** | caught |
| Frozen update allowed | caught | caught |
| Local norm guard removed | survived (second guard compensates) | survived (second guard compensates) |
| Reference RHS sign flipped | caught | caught |
| Evaluator energy gate removed | **survived** | caught |
| Evaluator status equality ignored | **survived** | caught |

The R002 suite caught **7/15** mutants; the R003 suite catches **12/15** applicable mutants (two mutants target R002-only code). Every remaining survivor removes a backup guard that another tested guard compensates for.

## Self-recheck of R003 (the reviewer's own repair)

Asked to recheck my own work, I found R003 had these problems:

1. **Its update was global by construction.** Every update took the full observation, re-sorted and re-prepared all edges (`_prepare`), rebuilt edge Counters, re-gauged every node, ran a global O(E) certificate, and serialized and hashed the whole snapshot twice. At 2,048 nodes, about 0.26 s of preparation and about 0.18 s of persistence surrounded 1–3 ms of dynamics. Any H-L outcome was therefore fixed by the design, not measured.
2. **One comparison was unfair.** "0/36 commits faster than a fresh recompute" compared a transaction that included whole-snapshot export and hashing with an in-memory recompute that did not.
3. **Contradictions had no resolution path.** R4 permits a separately metered fallback arm, and R003 had none. It also had no registered endpoints, so no H-L verdict was decidable.
4. **Minor.** `touched_edges` was still saturated by the global certificate, saved states took 38 MB, and only three worlds were used per cell.

R004 replaces it; see the R004 sections below and `evidence/c1_r004/`.

## R004 mutation probe (`mutation_checks_r004.json`)

| File | SHA256 |
|---|---|
| `mutation_checks.py` (final; R002 list unchanged, R004 list added, per-mutant 180 s timeout) | `307f3301a1c78d7816b4f9dd2965d470e40db25dd7f084e4d76c08f331345c08` |
| `mutation_checks_r004.json` | `fc189dea3e46b2762bdc632b89ef2e8f736ad946ba4bb6a5783e0f188e68f10c` |

The probe ran against the R004 source and the fourteen-check suite. Afterwards only `run_c1.main()` changed, adding per-cell spread to the receipt; no test executes `main()`. The R004 suite catches **18 of 23** mutants.

**Caught:**
- frame shift sign;
- certificate missing neighbors of moved nodes;
- certificate missing freed anchors;
- rollback skipping coordinates;
- rollback skipping the journal;
- unsorted degree lists;
- anchor tie-break;
- uncharged translations;
- uncharged local reads;
- cap never enforced (timeout);
- fallback cap never enforced;
- query ignoring the anchor gauge;
- duplicate-copy removal;
- frozen apply;
- relation redefinition;
- reference RHS sign;
- evaluator energy gate;
- evaluator status equality.

**Survived** (each a backup guard that another tested guard compensates for):
- certificate margin;
- the fallback's final certificate (behind the CG true-gradient check);
- the forced certificate step (affects only budget use);
- the local step-tolerance quiet check (behind the certificate plus forced step);
- the local force-norm guard (behind the residual-energy check).

Two survivors from an earlier R004 probe run were genuine gaps, and both are now closed:

- **Missing neighbors of moved nodes.** A new invariant check asserts that every node whose global C0 force changed was certified.
- **Unsorted degree lists.** A bit-exact audit compares in-memory degrees with the C0 validator's.

That earlier run was stopped and discarded once the gaps were found, so the recorded result is the post-fix run.
