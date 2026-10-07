DONE

P5 sanity first: {"status": "WITHIN_DECLARED_BOUNDS", "regular_mean_enemy_guns_destroyed": 3.4, "regular_mean_own_gun_losses": 10.0, "reported_before_other_arms": true, "control_completed": 40}

|Arm/head|Wins/timeouts|Mean S|Gun kills/own losses|All own losses|Victims/success own/enemy|Nearest own median/p10 px|Enemy/own artillery HP ratio|
|---|---|---|---|---|---|---|---|
|P5 regular|0/17|-19.95|3.4/10|42.9|1.1827027027027026/3.551797040169133|19.99999999999992/19.16059733599432|2.057758230386133|
|P5 novice|20/0|38.55|10/1.3|11.45|3.282828282828283/4.365853658536586|19.98283069576771/18.83272626352351|0.17693370165745856|
|P10 regular|0/17|-14.95|6.2/10|39.95|1.0689245395127749/1.001392757660167|62.79875403561791/25.89165929116989|0.7803066037735849|
|P10 novice|20/0|38.25|10/1.4|11.75|3.437830687830688/1.0|48.55274727903837/24.6572734747259|0.12342506631299735|
|P11 regular|2/12|-9.65|7.55/9.95|41.1|1.099591419816139/1.054481546572935|50.54412966870029/21.215834678362327|0.5935409457900808|
|P11 novice|20/0|38.7|10/1.3|11.3|3.3548387096774195/1.4210526315789473|35.0635824295143/20.845364822603848|0.0923756906077348|

P5 regular: dead-before-impact own/enemy [165, 124]; own gun killers {"1_artillery": 151, "1_ranged": 40, "1_melee": 7, "0_ranged": 2}; realization {}; gun-range fractions [0.3620929508886896, 0.06862893996976589].

P5 novice: dead-before-impact own/enemy [335, 11]; own gun killers {"1_ranged": 17, "1_artillery": 7, "1_melee": 1, "0_artillery": 1}; realization {}; gun-range fractions [0.3972155361630385, 0.275597137856481].

P10 regular: dead-before-impact own/enemy [140, 170]; own gun killers {"1_melee": 3, "1_artillery": 89, "1_ranged": 99, "0_ranged": 8, "0_artillery": 1}; realization {"prepare_gun_ticks": 143004, "clipped_goal_ticks": 1267, "shift_ticks": 122083, "zero_multiplier_shift_ticks": 267, "raw_goal_out_of_focus_band_ticks": 44958, "coincident_pair_terms": 0, "neighbour_terms": 450528, "clipped_action_reconciled_ticks": 143004}; gun-range fractions [0.46383854793983365, 0.18026701415853033].

P10 novice: dead-before-impact own/enemy [215, 16]; own gun killers {"1_artillery": 13, "1_ranged": 14, "0_ranged": 1}; realization {"prepare_gun_ticks": 98146, "clipped_goal_ticks": 0, "shift_ticks": 97752, "zero_multiplier_shift_ticks": 252, "raw_goal_out_of_focus_band_ticks": 40649, "coincident_pair_terms": 0, "neighbour_terms": 379188, "clipped_action_reconciled_ticks": 98146}; gun-range fractions [0.3326437648401594, 0.37357704215289356].

P11 regular: dead-before-impact own/enemy [279, 111]; own gun killers {"1_artillery": 64, "1_melee": 5, "0_ranged": 6, "1_ranged": 124}; realization {"prepare_gun_ticks": 152506, "clipped_goal_ticks": 70, "shift_ticks": 113839, "zero_multiplier_shift_ticks": 239, "raw_goal_out_of_focus_band_ticks": 31811, "coincident_pair_terms": 0, "neighbour_terms": 349502, "clipped_action_reconciled_ticks": 152506}; gun-range fractions [0.5279778356979195, 0.23301028894710107].

P11 novice: dead-before-impact own/enemy [270, 4]; own gun killers {"1_ranged": 21, "1_artillery": 4, "1_melee": 1}; realization {"prepare_gun_ticks": 93690, "clipped_goal_ticks": 0, "shift_ticks": 92074, "zero_multiplier_shift_ticks": 924, "raw_goal_out_of_focus_band_ticks": 27484, "coincident_pair_terms": 0, "neighbour_terms": 288808, "clipped_action_reconciled_ticks": 93690}; gun-range fractions [0.3633161108501644, 0.3282452393889233].

[{"arm": "P10", "distance_realization": "both_increased", "reading": "\u00a719.6 favorable splash/exchange but no eliminations; supports this setting, insufficient for elimination, necessity unproven"}, {"arm": "P11", "distance_realization": "both_increased", "reading": "Regular elimination and better-than-P5 candidate pattern; no resonator/causal claim"}]

P10 S=100px, P11 S=60px, from GAME splash40/body10; literal simultaneous Cartesian sum on P5, unchanged targets/multiplier/stop. The sum can oppose308px commitment and push guns outside320px reach; P5 multiplier0 remains0. These are soft repulsion thresholds, with no dynamic separation guarantee. Clipping and impact timing remain native. The complete precombat measurement definitions, pooling, singularity conventions, outcome comparisons and yes/no stops are in [POLICY.md](s4_spacing_probe_v1/POLICY.md) and [DECLARATION.json](s4_spacing_probe_v1/DECLARATION.json).

Implementation: new controller/host/factory, admitted native binary, bounded two-worker P5-first runner, stored-only analyzer, renderer and focused prepare-only fixtures. Combat-based historical contract/parity availability is recorded in ENGINEERING.json when present. Historical tracked inputs/outputs retain their recorded SHA256; PLAN_CURRENT and DESIGN_0G are unchanged. [VALIDATION.json](s4_spacing_probe_v1/VALIDATION.json) records final checks and limitations. [COMPACT.json](s4_spacing_probe_v1/COMPACT.json) lists every measurement with availability. [OWNER_RECHECK.md](s4_spacing_probe_v1/OWNER_RECHECK.md) records the verbatim request and dispositions. Raw is local/gitignored, hashed in [RAW_FILES_LOCAL.json](s4_spacing_probe_v1/RAW_FILES_LOCAL.json); completed and interrupted raw records remain local. No delivered file exceeds45MB.

Resume only where process-list access works: `python3 s4_spacing_probe_v1/engineering.py` then `python3 s4_spacing_probe_v1/run.py`, `python3 s4_spacing_probe_v1/analyze.py`, `python3 s4_spacing_probe_v1/render.py`, from astelia_cpp, with caffeinate as declared. Both combat entrypoints repeat the mandatory pgrep gate. Do not replay a claimed seed ledger; do not alter rules after a fight. Finish a fresh owner recheck and validation before delivery of any future run.
