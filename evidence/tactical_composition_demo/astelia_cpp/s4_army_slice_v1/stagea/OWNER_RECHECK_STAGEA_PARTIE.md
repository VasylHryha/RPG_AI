APPROVE_FOR_PRODUCTION_PARITY_RERUN
Reviewer family: Codex
Review type: separate quick owner recheck, read-only code and real-host evidence review; not cross-family scientific acceptance

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The independent reviewer found and rechecked these dispositions:

- Recovery dispatch initially used a module-global actual path during mocked fixtures. Deriving dispatch from the recovery module's HERE isolates the fixtures. Fixed before the test batch.
- Cached certification validation trusted the aggregate uncertified count. It now independently checks each mismatch's certified flag and gap/selected-class deficit against its bound. An inconsistent-summary regression was added and passed.
- The changed readout branch needed focused coverage. Tests now reject old-rule, missing-arm, duplicate-arm, uncertified and native-flip proofs. They passed.
- The first actual batch stopped before host replay because importing the recovery module while legacy paths were mocked retained a fixture alias. Importing during collection captures the durable path before fixture mutation; teardown then restores it correctly. Fixed, with the failed batch and registration retained.

The reviewer confirmed that strict native float64 parity is unchanged; capped per-head measured error bounds and the selected-class deficit reject material flips. The rebuild adjustment permits only declared Python source-hash changes and requires an identical native binary hash and admission properties. Historical failures remain tied to their original identity. Recovery preserves prior receipts and requires every arm to rerun under the new rule.

Final evidence recheck confirmed PASS on 1,517 frames / 47,963 rows for the full failing N2J0 fight. Its single fire flip has float64 top-two gap and selected-class deficit 1.9220437083244946e-5 <= the declared 1e-4 bound. Native categorical mismatches remain zero with maximum error 1.0658141036401503e-14. The test log confirms 47 passed in 24.09 s; measured wall is 24.712 s. All 22 registration-preserved files and all host fixed artifact hashes match. The reviewer found no remaining blocking issue.

Disposition: ready for production all-arm parity rerun. Full all-arm parity and readout/outcome acceptance remain pending their normal host commands. No numeric quality score was assigned. This local record follows the owner's explicit instruction to leave docs/PLAN_CURRENT.md untouched.
