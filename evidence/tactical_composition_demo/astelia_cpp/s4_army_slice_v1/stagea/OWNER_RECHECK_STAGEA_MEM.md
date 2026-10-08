# Quick owner recheck: Stage A memory fix

Reviewer family: Codex. Separate reviewer agent; preferred other-family reviewer was not available through the current agent tools. Read-only review, no tests or fights run by the reviewer.

Owner request sent verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

| Finding | Disposition |
|---|---|
| Previous fight results in a batch were not rooted during subsequent tick sweeps. | Fixed before tests: hold completed batch results in a host root bank until final serialization. Extended the native root-lifetime contract. Reviewer verified the seam. |
| Fixture receipt could say PASS based only on RSS, before duration/frame/profile assertions failed. | Fixed before tests: receipt status uses every fixture predicate, with an empty-profile guard. Reviewer verified it. |
| Implementer subsequently isolated permanent quadratic dynamic-key layouts despite tick collection. | Added flat, per-snapshot layout ownership and changing-key stress. Reviewer checked get/keys/stringify compatibility, shared clone ownership and sweep-before-release ordering. |
| Layout owners must not clear while flat objects escape into surviving GC roots. | Current use is restricted to consumed Stage A snapshot maps. Recorded this ownership restriction. |
| Inactive branch-pool controllers retain stale handles rather than being destroyed immediately. | Corrected explanation: pool entries are replaced before reuse; destructors do not read stale JSON handles. No changed engine lifecycle. |
| Copied allocation probes cannot qualify whole-host RSS. | Report explicitly separates the probes from the pending host-only 150-second, 512 MiB regression. |

Reviewer found no further blocker in streaming EOF/draining/deadline checks, failure retention or sealed-request recovery. Final focused checks passed once after the complete batch; host memory qualification remains pending because sandbox process discovery is unavailable.

The owner's explicit instruction prohibits editing the current plan; this record holds recheck dispositions instead. No acceptance or learned-policy quality claim is made.
