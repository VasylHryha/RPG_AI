# B2 hierarchical heads

Implemented family choice followed by bounded nonlinear member scoring and the
existing learned residual. Inference scores <=64 members per head/unit; training
additionally scores <=64 members within the label's true family. Loss is family
CE + true-family member CE + residual, with the original pointer/fire/multiplier
and executed movement geometry losses retained.

The original exact/native bank is preserved without pruning. There are 15 native
movement types, subdivided into 26 nearest-first pages; aim uses 5 pages. Both
family heads have 32 fixed masked slots. This explicit expansion beyond the
suggested 10–16 families is necessary to keep every original candidate reachable
with 64-member pages. Every generated candidate has a unique family/member pair;
coverage checks that the original nearest candidate remains reachable. Its
20 px tolerance, raw residuals, bounded representability, and N2 drift subtraction
are unchanged. Page order uses 1e-6 px distance bins and original ordinal ties;
member score ties use original ordinal. No teacher-dependent pruning or inputs.

All five arms and OWNER_APPROVALS caps remain unchanged. The native export
requires semantic_pages64_v1 and parity now checks both family logits as well as
candidate decisions. The semantic pick audit aggregates pages under its existing
type names. Full-bank feature tensors remain transient; loss retains small
true-family targets, and candidate inputs stream from the existing lazy chunks.
Peak worker RSS is checked against an exclusive 1.5 GiB ceiling during live
checks and after optimizer steps. Compute receipts now honestly label the
64-member dense arithmetic estimate as an upper bound.

56 focused tests passed in 20.40 s, including all-five-arm native/Python parity,
forced nonfirst-page selection, graph fairness controls, true-family gradients,
label isolation, source integrity, and maximum-envelope reachability. Existing
dirty fixture outputs were preserved by directing these tests to fresh local
hierarchy fixture directories. Only a comment and the compute receipt field's
upper-bound label changed after that behavioral test batch.

I attempted the actual test-mode timing command. The repository's process gate
refused before any optimizer sample: pgrep returned 3, "Cannot get process list"
(sysmond unavailable in this sandbox). The guard was not bypassed. There is no
measured per-step time, full training projection, or worker RSS qualification.
The 4.5 h / 20% margin target remains an unfulfilled host measurement gate.
B2HIER_VALIDATION.json records this limitation and the exact source hashes.

The separate recheck found and corrected the candidate audit's remapping of
native type IDs; it found no other material defect by inspection. See
OWNER_RECHECK_B2HIER.md. No PLAN_CURRENT edit was made. Stage A, Stage B and rev2
sources and receipts were left untouched. No production build, recorded
training, DAgger, or fight look ran here.

Use HOST_COMMANDS_B2HIER.md. Coverage **is needed again**, because this revision
changes source/model identity and adds reachability checking. Preserve the prior
receipt using --preserve-stale. The real measure must admit its lane projection
(including validation/prefix/tail costs and 1.2 margin) before fitting. Do not
infer admission from TEST_ONLY timing or focused tests. A paired look 20 requires
round 1 full-fight DAgger/refit, parity, and the baseline bridge; round 0 alone
cannot produce a look.
