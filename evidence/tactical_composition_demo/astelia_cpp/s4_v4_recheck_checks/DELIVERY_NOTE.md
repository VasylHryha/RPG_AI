# S4 v4 stored-evidence recheck delivery

Main artifact: `../S4_V4_RECHECK_REPORT.md` (CHANGES_REQUIRED for the v4 policy candidate). Supporting files: `analyze_stored.py`, `STORED_TRACE_ANALYSIS.json`, `PLAN_AND_REVIEW.md`, and `VERIFICATION.json`.

Only the six named task files under `evidence/tactical_composition_demo/astelia_cpp/` belong to this delivery. Existing development reports/receipts, raw fights, replay exports and controller code are preserved; this task does not edit the root plan. Concurrent C6/growing-shapes files are excluded. No new combat, optimizer call, replay export, build, recorded run or test suite was executed; the two B raw replays were read by one paced standard-library process.

While this task was running, a concurrent growing-shapes commit `588cf8c` included the initially staged analysis script. That commit already carries `Assisted-by: Codex:GPT-6`. It contains the intermediate analyzer bounds, not the final derived receipt. This task's final scoped commit completes that script correction and adds the report/derived evidence; it does not amend or rewrite the other session's history. The root plan also advanced concurrently outside this task.

The shared Git index accepted scoped staging in this session. Delivery uses the repository's normal commit hooks and the provenance trailer `Assisted-by: Codex:GPT-6`. The resulting commit can be identified by its subject `Recheck v4 stored evidence and specify v5 corrections`; its exact identity is reported to the owner after commit. No push is included. If Git rejects the final write, the fallback is a hash-verified archive of these six small files with this delivery note; no hook bypass or permission escalation is allowed.

Verification: final extraction reconciles eight original count fields for each B arm; its raw hashes match `s4_v4_development/LOCAL_ARTIFACTS.json`. `VERIFICATION.json` binds inspected summaries and preserved source identities, checks report facts/links and records zero new combat. `git diff --cached --check` and explicit staged-path inspection precede the normal commit. Every deliverable is under 50,000,000 bytes. No full raw log is added to Git; local raw files remain necessary for independent reconstruction.

The reviewer was a separate Codex agent; its exact request and findings/disposition are recorded in `PLAN_AND_REVIEW.md`. Claude cross-family development review and a reviewed/approved v5 proposal remain separate. The report completes the requested read-only analysis and does not authorize v5 implementation, development execution or S5 registration.
