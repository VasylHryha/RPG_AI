READY_TO_RUN

v5 Part 1 implements the amended section-17 A/B-only design (Codex design review: APPROVE_WITH_NOTES). Native v5 is byte-identical to historical v3 on synthetic controller fixtures; hold/focus are off, H/F/HF/v4 remain labelled variants. No development run was performed, and the fresh ledger remains unclaimed.

Build: one native build, exit 0, 6.052 seconds. Affected tests: 27 passed in 1.73 seconds (supervisor 1.906 seconds), zero combat. The first batch stopped after 8 passes because a fake fixture allowed only 60 minutes, below the runner's conservative workload floor. Only fixture allowance was repaired to 360 minutes, then rechecked before one successful retry. FAILED_FIRST_TEST_RESULT.json and logs preserve that attempt; no rebuild occurred.

Selection: A novice mean; B regular mean with novice tuning mean >=0 eligibility ahead of every negative-novice candidate. Same ordering in CMA and incumbent retention; stable earlier ties. After all-arm validation, resonator novice mean must exceed zero at A/B; B regular mean must strictly exceed -7.62 for PROGRESS. Equality stops. Report both predicates, eligibility and role omega diagnostics even on B stops; partial/failure reports retain the newest evaluated incumbent. The runner stops after B in every case; C is explicitly not_run. PROGRESS is not beating regular, statistical superiority, registration or READY_FOR_S5.

Exact command, from the repository root, for a separately authorized launch after tonight's C6 timing and when the laptop is free:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
v5_commit=$(.venv/bin/python -c 'import json; print(json.load(open("evidence/tactical_composition_demo/astelia_cpp/s4_v5_part1_checks/PART1_DELIVERY.json"))["implementation_commit"])')
/usr/bin/caffeinate -i -s .venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v5.py --implementation-commit "$v5_commit" --output evidence/tactical_composition_demo/astelia_cpp/s4_v5_development
```

Cost estimate: **4–6 hours with ten workers**, conservative section-17 allowance; v5 wall time and added identity-check overhead are unmeasured. Maximum 58,596 tuning + 2,400 validation = 60,996 fights, no extra replay fights. A stop reduces this workload. The .062-second/fight projection floor alone is about 63 minutes and is not an empirical duration prediction. Full **360-minute absolute monotonic allowance** starts at runner entry. Bounded submission, clamped subprocess timeouts, pending cancellation, active-child termination and failure timing are tested. A forecast beyond remaining allowance stops rather than extending the cap.

Fresh declaration: S4_V5_SEEDS.json, independent development entropy with prior-declaration hashes and inventory. Never judging. The exclusive permanent LEDGER_USED.json claim and existing-output refusal prevent reuse. Code/imports/optimizer/native sources/binary/build are pinned and checked before/after evaluation; worker identity checks precede cache publication. PART1_DELIVERY.json binds the normal-hook commit, verified bundle, admitted binary and runtime hashes. Run only after that sidecar exists and verifies; changing an input requires a new reviewed delivery.

Owner recheck: separate Codex reviewers approved the repaired design/implementation with notes. Claude CLI was attempted and returned Not logged in; the additional implementation review is same-family, not independent cross-family acceptance. See OWNER_RECHECK.md and PLAN_AND_REVIEW.md. DESIGN_0G.md and docs/PLAN_CURRENT.md were not edited. This engineering readiness delivery supplies no new scientific or execution approval and launches nothing.
