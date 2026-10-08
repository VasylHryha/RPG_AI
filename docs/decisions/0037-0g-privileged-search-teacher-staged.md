# 0037: 0g privileged search teacher with staged student access

**Date:** 2026-10-08. **Decided by:** owner. **Recorded by:** Codex.
**Extends:** decisions 0035 and 0036; resolves N-H1 in the [revision-2 Claude design recheck](../reviews/network_units_and_leader_design_r2_recheck_claude.md).

Owner's words, verbatim:

> for training yes, but to be sure let make it see for now

The search teacher may use explicitly declared hidden enemy state, initially enemy dodge readiness and remaining cooldown, to produce training labels in S3a and S3b. This is privileged-teacher distillation. The precedent is [Learning by Cheating, Chen et al., 2019](https://arxiv.org/abs/1912.12294); [asymmetric actor-critic, Pinto et al., 2017](https://arxiv.org/abs/1710.06542), is a related full-state-training/partial-observation-policy method, not the exact algorithm adopted here. Future RNG and undeclared private fields remain excluded.

**For now, S3a students also see the declared state** in an explicit, flagged privileged input channel, identical for the plain and RRG leaders during fitting and evaluation. Every S3a result is labelled privileged-student timing learning. This confirms whether the pipeline can learn timing when readiness is visible. **S3a cannot support any RRG-state claim.**

**Later, S3b removes that channel** from student features, stored states and exports. Its students learn to infer the declared readiness from public observation history. The teacher may still use it for training labels, but privileged state must never enter evaluation of S3b students, directly or through a hidden state, engineered feature or search call. The design must check bounded-public-history recoverability rather than require snapshot labels to have zero conflicts.

S3b adds a trained memoryless leader **P0** with matched observations, labels, budget and command support. A stateful R versus P reading is allowed only in a cell where P0 is measurably worse than P on declared validation and paired closed-loop criteria. If that gate fails, the cell is Markov coordination imitation or memory necessity NOT_EXERCISED; R/P differences cannot establish RRG state. Passing it is necessary, not sufficient: useful R/P outcomes, geometry/mode/persistence interventions and independent evidence are still required. No full source-recursion claim follows from this slice.

The detailed thresholds, channel inventory, search limits, costs and yes/no stops are in [design revision 3](../../evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/DESIGN_UNITS_AND_LEADER.md). This record changes the prospective design only. It does not authorize implementation, fixtures, training or evaluation during the protected running job, and it leaves existing code, evidence, statuses and accepted measurements unchanged.
