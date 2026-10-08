# Shape lab v5: V1 battery timing

PREPARE ONLY. Development tooling under decision 0033 and SHAPE_LAB_SPEC §14.
No fights, pick, superiority reading, registration or acceptance at delivery.

Three arms: (a) forcedP16+react (script); (b) forcedP16+react+central_sync
(script); (c) forcedP16+react+battery_oscillator (RRG mechanism: local battery
phase law only; no claim of source recursion). All P16 target/aim and REACT
policies are unchanged. V1–v4 and adapter v1 remain read-only inputs.

Central sync copies `artillery.cpp::fireGate` (including `smartVolley` scoring
of waiting versus separate shells) and the `combat.cpp::coreStep` waves block.
Declared sync window 0.5 s, waves=3, waves timeout 1 s, holdWave=0. The copied
holdSync predicate enables the gate for our external controller; the native
formation/planner stays disabled. It gates preparation, as the engine does.
Central volley membership is the common preparation tick; no V2 aim patterns
or planner rollout is enabled. Native fixtures compare copied gates against
engine predicates on persisted synthetic state records, without coreStep.

Oscillator: phi in radians, T_i = catalog cooldownMax + windup (seconds),
omega_i=2*pi/T_i, K_i=k/T_i (1/s), coupling sum averaged over living own gun
neighbours within R_c (pixels), excluding self. All living guns evolve even
when unready, reacting or without targets. Synchronous explicit Euler with
substeps <=1/120 s; positive wrap crossing is remembered during a tick.
Initial phases are deterministic ID-hash fractions of 2*pi, independent of
controller RNG and knobs. Release only when cast fully ready, legal and a
crossing occurred this tick, or the ready hold has reached T_i. No release is
queued from an unready crossing. Illegal/body/react states veto release; a
ready timer remains running while illegal, so it fires at first legal tick
once overdue. Phase resets to zero only on actual normal shell launch. Prep
runs normally before oscillator arbitration; timing holds the completed cast,
not the windup. Base fires as soon as its cast is ready.

Grid declared before fights: k={0.5,1,2}, R_c={200,400,infinity} (JSON/CLI -1
represents infinity). One development pick only, based on mechanism summaries;
PICK.json is immutable and bound to the complete mechanism/declaration hashes.
Selection rationale belongs to Claude: compare landing spread, dodges, hits,
shells/kill and firepower loss together; no outcome or win-rate tuning. Null
ratios never count as benefit. Review continue requires a pick; stop blocks
later stages without requiring a pick. No automatic numerical verdict is added.

Mechanism uses **20 common draws for every grid candidate**: 10 D1 guns versus
static dummy guns and ranged targets; 10 V1D2 guns versus dodging ranged dummies
(the admitted REACT primitive, no attack/planner). Each drill includes eight
10-gun draws, one 1-gun draw and one 2-gun draw. The two base/script arms run once
per draw; each of nine oscillator candidates runs those same 20 draws. Thus
20 paired comparisons per candidate, 220 actual development fights, not 20
fights total including grid search. This declared grid cost is projected from
calibration before the remainder runs. Baseline receipts are shared, not rerun.
Mechanism abilities are off for all arms to isolate the timing primitive.
C3 is 50/100/200 total paired draws across regular plus 19 tactics, three arms;
S10X is ten paired series of up to ten fights per arm, abilities off. Map/tactic
schedules are persisted and controller-RNG independent. Survivors heal, dead
cohort IDs do not return; first non-win stops each series arm. Streak primary,
reach and won/non-win losses secondary, with explicit denominators.

Mechanism metrics: landing-time spread in multi-shell volleys; launch-exposed
enemy escape fraction (all launch-exposed units of resolved shells in denominator; pre-landing deaths disclosed as non-escapes); hits per landed own
shell (including zero hits); landed shells per artillery kill; legal timing-induced
hold seconds per initial gun; fired shells per living gun-minute; 1/2-gun
intervals. Launch/landing exposure is captured at the native event seam, not
inferred from tick-end positions. Volley labels are metadata, never release
authority: central common prep tick, oscillator/base common release tick.
Singletons, unresolved shells, pre-landing deaths and unmatched damage are shown.
Null multi-shell spread cannot support a positive synchrony reading. Central idle
starts at engine preparation readiness; oscillator idle starts when fully prepared.
These are descriptive development measurements, not causal dodge attribution.

Reading after the declared outcomes: "RRG earns this job" if (c) is clearly
better than (a) on mechanism and outcome at decision-0033 size (about 10 pp
wins, about 2 units saved, or a clear streak difference), and not clearly worse
than (b). "The script is better" if (b) clearly beats (c). Otherwise park;
never expand past 200 pairs to chase a small effect.

Heavy diagnostics are off. Light observer damage/dodge/launch/units and small
battery/launch exposure rows are on. Replays only C3 pairs 0/1 per arm and
series 0 per arm, deterministic FPS reduction to 8 MB/file. Same mutable
`../s4_shape_lab_v1/raw/LAB_CAP.json` (missing=3600 s), repository-scoped process
gate, six workers, caffeinate, immutable completions, cap pause/resume and
measured cost projection as v4. Gate unavailable means no fights. Calibration
reuses allocated fights; no rehearsal. Sources/native/input identities seal at
prepare. Never rebuild or edit sealed sources after preparation.

Claude commands from repository root (preparation already complete):

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v5/lab.py
.venv/bin/python -B "$LAB" calibrate --stage mechanism
.venv/bin/python -B "$LAB" run --stage mechanism
.venv/bin/python -B "$LAB" report
# Read MECHANISM_SUMMARY.json, then choose actual grid values/rationale:
.venv/bin/python -B "$LAB" pick --k 1 --radius 400 --note "<actual mechanism-only rationale; change values to chosen grid point>"
.venv/bin/python -B "$LAB" review --stage mechanism --decision continue --note "<actual mechanism observation>"
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50
.venv/bin/python -B "$LAB" run --stage outcome --look 50
# Read each completed look. Continue only if unclear; stop if clear:
.venv/bin/python -B "$LAB" review --stage outcome --look 50 --decision continue --note "<actual reading at 50>"
.venv/bin/python -B "$LAB" run --stage outcome --look 100
.venv/bin/python -B "$LAB" review --stage outcome --look 100 --decision continue --note "<actual reading at 100>"
.venv/bin/python -B "$LAB" run --stage outcome --look 200
.venv/bin/python -B "$LAB" review --stage outcome --look 200 --decision stop --note "<actual reading at 200; keep script / RRG earns job / park>"
.venv/bin/python -B "$LAB" calibrate --stage series
.venv/bin/python -B "$LAB" run --stage series
.venv/bin/python -B "$LAB" report
```

At an earlier clear look, record `stop` and omit later C3 commands. Series still
runs once that C3 look is read/finished. Mechanism `stop` blocks outcome/series.
Repeat the same command only for PAUSED_CAP; successful cells are verified/reused.

| Stop question | Action | Role |
|---|---|---|
| Is mechanism complete/read and a one-time grid pick fixed? No | Block C3 | implementer |
| Did mechanism reader stop? Yes | Block later stages | implementer |
| Is the previous outcome look read? No | Block next look | implementer |
| Is effect clear at a look? Yes | Record stop | reviewer |
| Have 200 pairs failed to show a clear effect? Yes | Park | reviewer |
| Is C3 finished/read? No | Block series | implementer |
| Does projection exceed owner cap? Yes | Request owner resource decision | implementer |
| Is process discovery unavailable or identity inconsistent? Yes | Stop and investigate | implementer |
