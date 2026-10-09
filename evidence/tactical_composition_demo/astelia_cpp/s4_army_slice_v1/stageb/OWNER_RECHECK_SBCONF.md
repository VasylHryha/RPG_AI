PASS (bounded tooling and fixture delivery)
Reviewer family: Codex

Owner request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Separate reviewer: /root/sbconf_recheck. Read-only review of Stage B tooling/config/scratch behavior, followed by read-only final receipt and hash verification. No numeric quality score assigned. No cross-family scientific acceptance claimed; no new recorded experiment or long run executed.

Findings and disposition:

- **Disk/admission refusal reporting:** moved disk checks into an initialized step and added an explicit admission step. Failure records include elapsed time, Python/native RSS and disk; downstream stages become NOT_RUN.
- **Cached adjudication provenance:** archive hashes are verified; config metadata is excluded from exact immutable numeric comparison, preventing a cache from rejecting its own config-bound record.
- **Live calibrated-fire thresholds:** cached numeric error/gap measurements are certified against the current config instead of trusting old certification flags. Added a tightening regression.
- **RSS identity:** separated Python/process peak from native peak and checked final native parity profiles against the fixture RSS cap.
- **Historical tooling membership:** actual revision-3 admission exposed ancestor changed_sources derived from today's extra tooling. Recomputed all proof fields using each ancestor's source map; added a regression for tooling introduced only at revision 3. The refusal occurred before any head was written. The reviewer separately checked this fix.
- **Refused-budget host flow:** the reviewer checked byte-for-byte archive, early-failure restore, retained new refusals, admitted-budget reuse and checkpoint refusal. No remaining blocker found.

Verification reviewed:

- Initial complete planned batch: 84 tests passed in 4.60 s (5.57 s command).
- Actual historical-chain admission failure required the final source-proof fix; final affected batch: 85 tests passed in 4.03 s (4.95 s command). No routine per-edit test runs.
- Test-mode whole smoke: all seven steps PASS, 8.966 s total, four parity records and twelve readout policy/panel records. Production process gate was explicitly disabled for this fixture.
- Revision-3 seal and parent hash verified; all 59 training-relevant source hashes match the round-0 budget. Live tooling hashes and archived config hashes verified.

Final reviewer found no actionable issue. This proves tiny wiring with the actual native binary, not production process/RAM admission, a full fit, final outcomes or experiment acceptance. User explicitly prohibited PLAN_CURRENT.md edits; this file records recheck/disposition locally instead.

Bound artifacts:

- Chain head SHA256: e3a6626b2bb171b4a2529b8e2b446ff3482cf4c0952c167f6cabb7f9612e14f3
- Scratch smoke receipt SHA256: 40aa6b7e8d057bed92e1851ca1aadda5b3d345e5f21bb0fc38c495be1399b93f
- Focused test receipt SHA256: 7409065e6cf36e103fa5d95ad41bfd160de45dfa2840a3625ba0362ab393d0a4
- Owner config SHA256: 81cfe5740a0729e21ece15b4e465fb9d7b1fd6858dd6dc904faab4f4374c6c9a
