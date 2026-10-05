STOP

# S4 v2 development report

Implementer family: Codex (GPT-6). Exploratory scope: decision 0028 items 15-17 and the owner's explicit v2 request. Contract review stopped before implementation under the instruction: "If anything in section 13 is ambiguous, write the question in the report and stop instead of choosing silently."

Source snapshot: repository HEAD `2edac7fcad8a7a933fe8707544c884934719ca23`; `DESIGN_0G.md` section 13 (revision 5), Claude's `astelia_cpp_review_claude/S4_V1_REVIEW.md`, the native S3 controller/bridge, and `S4_AMENDED_PROTOCOL.md`. The drafter must resolve the questions below in the design before implementation resumes. No equation, bound, parameter count or selection policy was chosen implicitly.

## Questions for the drafter

1. **Which additional knob is fixed/removed, or is the cap increased to 11?** Section 13 item 5 replaces f with f_c and m_k, adds lambda_th, and fixes gamma at 1, while requiring the cap of 10 for resonator and morale. The resulting independent knobs are K, K_t, kappa, beta, the two role rates, G, w, f_c, m_k and lambda_th: **11**, not 10. The two rates are omega_melee/omega_ranged for resonator and lambda_melee/lambda_ranged for morale. The original section 5 table and `s4_development.py` BOUNDS both have ten. Starting an optimizer with eleven, tying the role rates, or fixing another knob would each change the requested contract. Push-pull's G/f_c/m_k count of three is unambiguous.

2. **How is the union reduced when it contains more than 16 enemies?** Section 13 item 4 specifies the eight nearest living enemies union all threats, capped at sixteen, without a selection priority for overflow. Eight nearby non-threats plus ten more distant active artillery threats can give eighteen distinct enemies. Keeping all eight nearest and choosing eight threats, prioritizing threats, or taking the sixteen nearest from the union yields different movement. Please specify which entries survive, their ranking and deterministic tie rule. Also confirm that the unanswered label uses the full threat set, independently of any movement cap.

3. **How is the enemy's reach expressed in the own unit's distance coordinate for mixed artillery/direct or artillery/melee pairs?** Section 2 defines rho as surface gap for melee/direct and centre distance for artillery; the bridge uses the same distinction. Section 13 item 3 compares/interpolates R_i and R_e without specifying the conversion between those coordinates. If h is the sum of radii, a direct enemy's centre reach is range_e+h, while an artillery enemy's centre reach is range_e. For an own artillery unit facing a direct enemy, using raw range_e in the centre-distance escape formula can leave it inside the enemy's reach (notably at w=0); converting adds h. For an own direct unit facing artillery, converting the artillery's reach to the own gap coordinate subtracts h. Please specify whether R_e is converted to the own coordinate before the comparison and distance law, including handling of a non-positive converted reach. Also clarify how an own artillery unit's minRange interacts with f_c*R_i or the kite-band distance: a preferred distance below minRange is below maximum reach but outside its legal firing set.

## Execution state

| Work | State | Reason |
|---|---|---|
| Part 1 v2 controller and contract tests | not_run | Questions above require design clarification |
| Rebuild and affected test batch | not_run | No implementation changes |
| v0/v1 fixture replay verification | not_run | Sources unchanged; no new parity claim |
| Part 1 implementation commit | not_run | Only this contract-stop report is delivered |
| Fresh development seed ledger | not_created | Development cannot start before committed Part 1 |
| Stages A/B/C tuning and validation | not_run | Contract stop before implementation |
| Novice A/B stop gates | not_evaluated | No validation fights |
| Timeouts and enemy guns alive, every arm/setting | not_measured | No development fights |
| Viewer replays per arm/stage | not_exported | No development fights |
| Fresh P2/P3 spread, delta and n proposal | not_run | No Stage C data |

No `s4_v2_development/` output directory was created. No judging roots were read and no judging or development seeds were generated. No registration, recorded run, frozen GeoMind changes, committed receipt changes, milestone status changes or `growing_shapes/` changes occurred. Existing v0/v1 sources and fixtures were left unchanged.

The unchanged amended protocol estimates 90-120 minutes for all stages with ten workers; this is a protocol estimate, not a measured v2 estimate. No long run was started. After clarification, finish the entire implementation/test batch, rebuild and run affected tests once, commit Part 1, then announce the duration and execute the fresh-seed development protocol. Claude's independent review remains a separate gate; this STOP is a contract stop, not the novice performance stop observed in v1.

The workspace's Git metadata is read-only under this session's permission profile. This report is committed with repository hooks in an isolated checkout and delivered with a verified bundle and `s4_v2_checks/WORKSPACE_DELIVERY.md`; Claude integrates the scoped branch.
