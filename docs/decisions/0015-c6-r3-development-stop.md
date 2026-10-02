# 0015: C6 R3 stops at development qualification

2026-10-02. Codex completed the approved Arm B implementation (`560ecdb`),
passed 418 everyday tests, and ran the ten fixed development worlds once.
The immutable [receipt](../../evidence/c6_r3_design_gate/results.json) reports
STOP with no infrastructure errors. Source qualification was 0/10 versus the
fixed 5/10 target. World 4 initial dt comparison also exceeded the fixed .05
tolerance (.0742828780 at dt=.02 versus dt=.005). Both matched causal controls
passed all ten worlds; native/reference agreement stayed near machine precision.

These are development readiness failures, not final scientific hypothesis
verdicts. Predominantly mixed bath/source formations cannot be silently relabeled
as the registered source, and thresholds/time steps cannot be changed to pass
this recorded revision. Second-turn workload was not reached, so full panel
runtime remains unknown.

Retain every raw world, receipt, hashes and build identity unchanged. Mark C6
BLOCKED in STATUS.json and regenerate README. Do not generate final entropy,
register a final panel, probe mutants or run another development gate for this
protocol. A future redesign needs a new prospective proposal and owner approval
under the repository process. Arm A retains decision 0013 unchanged.

| Yes/no stop condition | Answer | One action | Responsible role |
|---|---|---|---|
| B source quorum below 5/10? | Yes | Return this recorded STOP | Implementer |
| B numerical tolerance exceeded? | Yes | Preserve the recorded failure | Implementer |
| Full second-turn runtime measured? | No | Keep final registration blocked | Implementer |
