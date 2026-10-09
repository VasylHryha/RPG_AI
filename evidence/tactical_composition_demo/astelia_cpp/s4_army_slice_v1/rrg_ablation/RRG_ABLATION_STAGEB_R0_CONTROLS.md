# Stage B round-0 controls

The hand-wired neighbour-target feature explains part of the target gain with coupling switched off; recovery differs by role or is incomplete. The remaining gap cannot be assigned uniquely to phase dynamics because the trained head also consumes phase features. This replay does not isolate a learned resonance mechanism.

Same N2 epoch-10 checkpoint, 50 original TEST fights, 63,897 full-prefix ticks, 592,992 scored unit rows, same four 90-tick windows and exact original row hash. No retraining, new fights, recalibration or changes to the original metrics JSON. Intact target/fire counts reproduce exactly in every fight.

| Control | Melee target | Ranged target | Artillery target |
|---|---:|---:|---:|
| Original N1 reference | 0.8839 | 0.6535 | 0.6383 |
| N2_intact | 0.9008 | 0.8015 | 0.7936 |
| N2_indicator_no_phase | 0.8989 | 0.7433 | 0.7147 |
| N2_intact_no_bonus | 0.8854 | 0.6558 | 0.6395 |
| N2_forcing_only_cut | 0.8982 | 0.7454 | 0.7206 |
| N2_role_shuffle | 0.8997 | 0.7978 | 0.7403 |
| N2_forced_synchronous | 0.8985 | 0.7453 | 0.7173 |
| N2_intact_no_fire_window | 0.9008 | 0.8015 | 0.7936 |

| Comparison | Ranged | Artillery |
|---|---:|---:|
| N2_indicator_no_phase change from intact (pp) | -5.82 | -7.88 |
| N2_intact_no_bonus change from intact (pp) | -14.58 | -15.41 |
| N2_forcing_only_cut change from intact (pp) | -5.61 | -7.30 |
| N2_role_shuffle change from intact (pp) | -0.37 | -5.33 |
| N2_forced_synchronous change from intact (pp) | -5.63 | -7.62 |
| N2_intact_no_fire_window change from intact (pp) | +0.00 | +0.00 |

The K=0 synchronised-indicator control retains ranged: 60.7% of the original N2-minus-N1 margin (+8.98 pp over N1), artillery: 49.2% of the original N2-minus-N1 margin (+7.64 pp over N1).

Intact phase dynamics without the target bonus lose ranged: 14.58 pp, artillery: 15.41 pp. This is removal from a head trained with the bonus, not a retrained feature-matched architecture comparison.

Forcing-only retains K and the original forcing feature in the head; it isolates forcing removal from coupling removal. The earlier K=0, frozen-phase and no-geometry-to-mode cuts largely share one alignment disruption; they are not three independent confirmations. In particular, frozen and omega-only phases share relative phases.

Same-role shuffle permutes phases after each physical update and carries the permutation forward. It preserves that tick’s role marginal, but later marginals evolve on the perturbed trajectory. Forced synchrony overwrites all phases with zero each tick. These are disturbance controls, not proof of equal disturbance magnitude or equally familiar joint inputs. The synchrony arm also changes absolute-phase head/fire inputs, so its difference from intact cannot uniquely identify target-alignment information.

| Role | Oracle target among neighbour targets / all rows | Among non-None oracle rows | Trivial plurality-else-nearest accuracy |
|---|---:|---:|---:|
| melee | 0.1226 | 0.7611 | 0.0541 |
| ranged | 0.4984 | 0.9367 | 0.3580 |
| artillery | 0.5230 | 0.8682 | 0.2710 |

The diagnostic uses the identical up-to-eight within-300-px graph, across all own roles. None/dead-target assignments are ignored. Plurality ties use nearest distance, then smallest enemy ID; no valid assigned target falls back to nearest, and no living enemy returns None. Oracle labels are used only to score the diagnostic. Support fraction is a descriptive overlap, not a bound on total model accuracy.

Fire-window contribution (raw three-class accuracy and unchanged original N2 validation thresholds; no recalibration):

| Role | Intact raw | No window raw | Raw change (pp) | Intact calibrated | No window calibrated | Calibrated change (pp) |
|---|---:|---:|---:|---:|---:|---:|
| melee | 0.8499 | 0.7650 | -8.50 | 0.8339 | 0.8221 | -1.18 |
| ranged | 0.7979 | 0.7199 | -7.79 | 0.7157 | 0.7403 | +2.46 |
| artillery | 0.8595 | 0.7477 | -11.18 | 0.8501 | 0.8553 | +0.52 |

No-bonus and no-fire-window arms reuse intact state but use exact logits captured before their respective additions. The additions never feed back into recurrent state on these fixed rows. Light multi-tick tests check the identities against separate switch forwards. All other interventions replay full prefixes independently. JSON includes per-fight metrics, head errors, safety-masked calibrated fire and phase diagnostics.

N2-specific readout inputs (protocol correction M3; Stage A protocol left untouched by owner scope):

| Readout | Extra input and fixed transformation |
|---|---|
| Target bonus | Up to 8 own allies within 300 px, their exact current engine target IDs, and unit/peer phases. Per enemy: +2 times cosine alignment with the normalized mean phase of peers assigned to that enemy; zero for absent or cancelling groups. None gets no bonus. |
| Fire window | Updated absolute unit phase. Add [2 cos(theta), -2 cos(theta), 2 cos(theta)] to automatic/hold/release logits. |

N1/N1h/N1r lack these hard-wired additions. Equal registered parameter counts and the shared 136-coordinate head input do not establish matched readout information. Public targets also appear as scalar IDs in tokens, but exact neighbour-ID matching is privileged in N2.

Limitations: one training seed/checkpoint per architecture; a matched epoch/budget comparison, not convergence. N1 lacks the exact peer-target readout, so it cannot serve as a feature-matched memory control. Phase is recurrent state. A retrained N1 plus the same neighbour-target feature would test the architecture question. Fixed recorded positions and assignments cannot respond to altered policy actions; neither live geometry-mode feedback nor recursive background transformation is tested. Per-fight deltas are descriptive; repeated unit ticks are not independent replications.

Execution: 749.6 s wall / 715.0 s CPU, nice 15, one Torch thread and one interop thread. All original input pins and new inference source hashes rechecked after replay. Original metrics JSON SHA256: `64c1c652fcca0c48d72eb05733abe4b8fc1eee1f8f63458c858d7540d781bc93`.
