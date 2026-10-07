APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewed commit: `59c5569e9ee80df708be067e4df13b2ae30a2c8e`
ECONOMY_PILOT_SPEC.md SHA256: `9ab8366447412c3d27c8fda6cdef6f04dc34deedb355ea903604267e7909636d`

Round-2 static review of AGENTS.md, Amendment 1, the round-1 review, mass and coverage diagnostics/report, telemetry report/recheck, coverage and service graph/observer/worker/scheduler/report pipelines, both kernel builders and retained fd21826 RD3 source. Also checked scheduler history at eea6276 and de89074. No pilot, medium step, assay, process enumeration, or project test ran during this review. Historical raw inventories are not independently reverified by this specification review.

Amendment 1 resolves the round-1 meaning-changing blocker. Step 2 is unblocked within the owner's build-and-synthetic-only scope.

| Round-1 issue | Disposition |
|---|---|
| Deficit snapshots and active-only mismatch | Consecutive end-of-growth-check all-physical-site directed deficits, after removals and births; not observer spring gaps. Missing roots/O give infinity; history is kernel-owned and clone-copied. |
| Clock update and reset persistence | Only growth-end updates, in fixed 20-second increments; served/progress resets, finite stagnation accumulates, rootlessness pauses. Regained roots reset the comparison history. |
| Removal boundary | ECO-F follows measured locks and D1/D4, precedes D3 and all births. ECO-R follows D1/D4/D3 and precedes births. |
| Front/tip/no-donor/shared fronts | All-site strong route exclusion; tip chosen from entire current site front by distance then id; all sites' roots excluded; measured lock/id rank and age >=200; ascending site order, fresh classification after removal, D5f_none and reset. No O means no removal. |
| ECO-R safety and cost | Pure geometry rebuild with fresh nearest neighbors and full held receiver degrees; preserve the original served set including idle sites; first passing donor, at most one. Record trials, failures, no-candidate/no-passing checks and elapsed/CPU check time. |
| Reserve/reading/cap | 56 is a heuristic trigger, not promised headroom. Exact doubling threshold 0.17202754532775452; completeness and both integrity pairs gate positive/regression readings. Cap3600 and workers<=10; projection stop requires executor/owner disposition. |

**N1 — finite-current guard on the newly-gained-roots clause.** Read line66's parenthetical "roots newly gained" with line68's explicit rootless pause: implement rule2 as `finite_now and (first_finite or not finite_previous or now < previous - 1e-9)`. Consecutive infinity is not newly gained roots. Initialize history to infinity and clocks to zero; no-O deficits remain infinity. A literal unguarded previous-infinity test would contradict rule4, so record this reading and test finite->infinity->infinity->finite plus no-O histories. This makes the declared pause/progress cases consistent; it does not add a new mechanism.

**N2 — preserve the ordered clock/removal stages.** D5f reads the stored clock from the preceding check. Its reset happens before D3/births; if the current end deficit remains finite and stagnant, the ordered growth-end update can make that clock20 again. Do not add a live-served veto or prospective service veto to ECO-F, reset deficit history upon deletion, or suppress that end update. Service gained/lost between growth checks does not change its clock until the specified growth-end sample. Retraction excludes route bodies in the current graph but may break service by rewiring; this is the recorded trade-off.

Both economy arms remain single changes on reproduced RD3, using physical sites, geometry, measured locks and age, without task/assay inputs. COV-A's ordering and COV-B's recycle are contextual comparisons only. D3 retains its class priority, ordinary eligibility and measured locks. Output-first, pointer, two-birth B-path quota, B1 admission/timers/quota and cap/cost resource-stop propagation stay inherited. Removal can change their live inputs without changing their laws.

The coverage amendment remains precisely computable: COV-A zero-initialized active-unserved accumulated time, idle-service reset, inactive pause, finite-before-rootless ordering and pointer tie; COV-B one age-eligible non-service donor excluding anchors, same fixed-point full retry, persistent removal on recycle_failed, one shared recycle/check. B1 has no B-path trial. A propagated resource-stop has no candidate. No coverage law enters ECO-F/ECO-R.

Observer requirements are adopted: preserve pre-transition outages, post-birth gaps, exclude repairing terminals/restoring samples from B, retain restoration with zero duration weight, and prevent new outages inheriting preceding births. Historical RD3 B remains legacy_B in new outputs unless complete boundary facts exist; never rewrite old receipts. Add explicit D5f/D5r removal attribution including rewiring loss, without treating a coincident label as causal proof. Class-cost allocations conserve ordinary N+.1 per ordinary held pair, splitting each pair charge equally; allocations do not measure marginal deletion savings. Record actual candidate cost/time at the first refusal, before later births/removals.

All eight sites, both starts, per-run A/B/E and active-step pooled coverage remain visible. Missing/bad jobs or an unverified integrity pair make that arm INCOMPLETE for both improvement and regression; no missing job counts as a failure. These are exploratory descriptive readings, not acceptance, A7 authorization or a recursion claim.

Owner recheck request sent verbatim to separate read-only reviewer `/root/economy_r2_recheck`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Disposition: separate Codex reviewer returned APPROVE_WITH_NOTES, independently confirmed original-blocker resolution and the finite-current/pause reading, and checked reachable RD3 output permanence before distinguishing a wording clarification from a meaning-changing blocker. Notes N1/N2 above incorporate its findings. This is a same-family supporting pass, not Claude acceptance. Tracking stays here under the owner's prohibition on editing docs/PLAN_CURRENT.md.

| Stop condition | Yes/no | Action | Responsible role |
|---|---|---|---|
| Does a remaining specification defect change an arm's meaning? | No | Proceed with scratch implementation and synthetic checks only. | Implementer |
| Does implementation reveal a new arm-meaning defect? | Pending | Stop and return the defect to the drafter. | Implementer |
| Does the complete plan project above3600s? | Yes on historical RD3 maximum (3987.979s at10 workers) | Preserve the cap and stop before launch; resolve with owner. | Executor |

No plan, design, committed evidence receipt or accepted source was changed by this review. No pilot execution is authorized for Codex.
