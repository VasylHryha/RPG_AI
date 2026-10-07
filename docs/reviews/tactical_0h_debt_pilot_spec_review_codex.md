APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed HEAD/spec commit: d1e97a65b7122690b53e9d1a511143f66d3c7430
Scope: DEBT_PILOT_SPEC.md, FRONT_ALLOCATION_DIAGNOSTIC.md, COVERAGE_PILOT_SPEC.md including Amendment 1, coverage_kernel.py, execute_coverage_plan.py, run_coverage_pilot.py, write_coverage_report.py, execute_economy_plan.py and kernel_builder/.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

The arm is implementable as one scheduling intervention on reproduced RD3. Debt starts at zero for all eight physical sites in both starts. Once per completed 0.1-second integrate, before adaptation/timers/growth, increment only active-unserved sites by floating +0.1. Inactive or served sites retain debt. No birth or removal updates it. The kernel's deep clone copies this history; the observer cannot own or drive it. The key is (not finite directed deficit, descending debt, pointer-relative id). The initial order remains fixed through the check; existing live path checks skip sites connected by earlier births. Two accepted births, output-first repeat, resource-stop propagation, pointer advance, B1 timers/quota, D3 and admission budget remain unchanged. Graph, physical activity and kernel history make this task-blind; assays/teacher/task labels are unavailable to the law.

Findings (nonblocking for arm construction):

1. The diagnostic's offline debt key deliberately has no finite-deficit priority. DEBT explicitly retains that priority. Its claim to be exactly that diagnostic key is too broad. Implement the explicit arm key, and report finite-first RD3/COV-A comparisons separately from the pure-debt diagnostic order. Do not silently remove priority.
2. Zero integrated-versus-lagged first-choice differences in the stored diagnostic are retrospective, not a guarantee for a new trajectory or later choices. Use the specified completed-integrate debt; do not substitute observer debt.
3. The fairness reading does not say whether minimum/no-site-below-0.10 refers to pooled site fractions or all site/run fractions. Coverage Amendment 1 establishes pooled denominators for coverage, but cannot resolve this new fairness clause. Report the minimum of eight pooled site fractions plus each run's minimum and COV-A equivalents, label their denominators, and withhold the unqualified FAIRER_THAN_COVA reading until the drafter fixes this ambiguity. This does not change the DEBT arm. Missing/zero denominators or incomplete integrity cannot support a positive reading; missing runs are not failed gates.
4. The falsifier is descriptive: altered ordering/quota exposure alone cannot prove scheduling is not a bottleneck. Live connectivity, quota, output-first and cost refusals intervene between initial order and service. Retain per-check order and terminal outcomes, not only first-choice counts.

Stop decision: no defect requires changing the arm's meaning; Step 2 may proceed. Approval is scratch-tool construction, not pilot execution, experimental acceptance or A7 authorization. The owner expressly assigns execution to Claude.

Separate reviewer recheck: a read-only Codex reviewer received the owner request verbatim and independently returned APPROVE_WITH_NOTES, with the same finite-priority, retrospective-equivalence, minimum-scope and incomplete-integrity findings. Disposition: preserve the explicit arm; implement separate comparisons and suppress ambiguous fairness labels. Under the owner's prohibition, this artifact tracks the recheck instead of editing docs/PLAN_CURRENT.md. No simulator, pilot, assay, mutation probe or process listing ran during review.
