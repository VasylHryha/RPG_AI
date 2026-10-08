# Formation sandbox (JS experiment)

A standalone JS battle sandbox for designing the pack/formation tactical leader before any game
code changes. Two equal armies (10 melee, 30 direct fire, 10 artillery each) or our army against a
respawning hunter stream. Every unit shares the same individual skills; only coordination differs.

Nothing here is wired into the game. Results use invented unit stats.

## Files

| file | what |
|---|---|
| `formation_sim.js` | the simulator: units, shapes, presets, opponent pool, role rules, commanders, look-ahead |
| `formation_sandbox.html` | viewer: all formations side by side, focus view with slots/targets/states |
| `gauntlet.html` | viewer: 10 fights in a row, only survivors go on; fixed list or random opponents |
| `gauntlet.js` | headless gauntlet (`DRAW=any` / `DRAW=pool` random opponents, fixed list otherwise; `OUR_LEVEL`, `ENEMY_LEVEL`, `HEAL=none`) |
| `ai_lab.js` | AI profile tests: `pieces [level]` (each skill / brain / look-ahead changed alone), `ladder` (level vs level), `vs A B` |
| `cost.js` | health cost of one fight per opponent |
| `trace_gauntlet.js` | one gauntlet, fight by fight: composition, losses, plans |
| `fresh.js` | single fights vs named opponents: survivors, losses by cause, plan time |
| `look2.js` | look-ahead commander variants (oracle / honest / cheap) |
| `reactive.js`, `shapes.js`, `doctrines.js`, `compare.js`, `audit.js`, `tune.js` | earlier comparisons, sweeps and audits |
| `tune2.log` | random-search result behind the `wide line` preset |

Run any script with `node <file> [seed range] ...`; open the HTML files in a browser.

## AI architecture

World rules are the same for both sides (shots aimed/homing and their speed, abilities on/off, healing between
gauntlet fights). Everything a side *decides* is its **AI profile**, one per side, resolved once when a battle
is created (`buildProfile`), so a decision in the hot loop is one property read (`sk(w, team, name)`):

| part | values |
|---|---|
| `brain` | `alone` (every unit for itself), `formation` (a fixed formation), `rules` (commander that reads the fight and switches plans, `RULES` / `PLANS`), `storm`, `wolfpack` |
| `formation` | `{ preset, ...overrides }` — shape and tactic settings (`DEFAULT_F`, `PRESETS`) |
| `lookahead` | `null`, `'full'` (`LOOKAHEAD`), `'fast'` (shortlist network, `setNet`), or a settings object; any side can use it |
| `skills` | the registry `SKILLS`: each unit-level decision with its default, the alternative `ai_lab.js` tests, allowed values and a one-line doc |

Levels (`LEVELS`: novice, regular, veteran, elite) are complete profiles. A battle takes profiles with
`options.ai = [ours, enemy]`, each `{ level?, brain?, formation?, lookahead?, skills? }` (own fields override the
level). A gauntlet enemy keeps its opponent's brain and formation and takes only a level's skills.
The older options (`mode`, `reactiveBase`, `f`, `enemyF`, `lookahead`, `shotDodge`, `shellDodgeAll`, `smoothLead`,
`pursuit`, `kiteRadius`, `reactAim`, `coordAbilities`) still work: they are read into the profile first, and
give exactly the results they gave before the profile layer.

To add a decision: register it in `SKILLS` (def, alt, doc), read it with `sk(w, team, 'name')` where the unit
decides, then `node ai_lab.js pieces` shows what it is worth; the viewer shows a control for it automatically.

## Look-ahead commander (2026-10-01)

Every second the commander forks the fight once per plan, plays each 3 s ahead (0.1 s steps, enemy
assumed to keep doing what it does now), and keeps the best damage trade (dealt - 1.5 x taken).
Settings: `LOOKAHEAD` in `formation_sim.js`; `gauntlet.html` uses it by default.

| random gauntlet, 40 runs | avg fights won | runs >= 4 | >= 6 | >= 8 | worst |
|---|---|---|---|---|---|
| any, old rules | 5.5 | 31 | 21 | 7 | 1 |
| any, look-ahead | 6.3 | 30 | 24 | 18 | 2 |
| pool, old rules | 4.9 | 29 | 13 | 6 | 1 |
| pool, look-ahead | 6.1 | 32 | 21 | 12 | 2 |

(Look-ahead rows used the 7-plan set; 12 plans add +0.5 to +2 survivors per fight.)
Measured and rejected: longer horizon (6 s), higher loss weight (3, 6), knowing the enemy's real brain
(no gain over the honest model). Wolfpack still ends most failed runs: its dodging skirmishers turn the
fight into an even shooter trade that plan choice cannot fix.

## Status (2026-10-01)

- Fixed 10-formation gauntlet: about 37/40 runs win all 10.
- Random gauntlets (`DRAW=any|pool`): about 6.2 fights won on average with the look-ahead commander
  (5.5 / 4.9 with the old rules); Wolfpack and loose skirmish cost the most.
- Owner targets per run: minimum 4 not yet met (about a quarter of runs end before fight 4, mostly vs
  Wolfpack); 8+ reached in 12-18 of 40 runs.
- PROTECT pair, sortie lease, pivot plan and wounded pull-back were measured without gain and removed.
- Pure-tactic plateau (2026-10-01): any 6.4-6.5 avg, >=4 in 33-34/40 runs; pool 5.9-6.0, >=4 in 34-35/40.
  Wolfpack (wins about half its meetings, ~20 units lost per win) and loose skirmish block the minimum target.
- Targets set by the owner: every random gauntlet run wins at least 4 fights (minimum), 6 (mid), 8
  (ultimate). Abilities (melee charge, shields) are deferred until pure tactics reach these targets.

## Abilities (2026-10-01)

Option `abilities: true` gives both armies the same six abilities (`ABIL` in `formation_sim.js`):
melee charge and shield, shooter aimed shot and disengage, artillery barrage and slow field. Using one
locks the unit's other ability for 1.5 s. Armies without our brain use simple per-unit triggers; our pack
coordinates (`coordAbilities`). Balance (`balance.js`, even mirror): no ability above 20% of damage,
exchange 0.995.

| measured (paired duels, `duel.js`) | result |
|---|---|
| our coordinated use vs simple triggers, both sides with abilities | +1.3 survivors per fight; 3.2 -> 3.9 gauntlet fights |
| abilities off vs on (look-ahead commander) | -3.0 per fight; 7.0 -> 3.9 gauntlet fights |
| look-ahead choosing ability posture, counter-charge, charge reserve, charge-aware siege, counter-battery, smart dodge | no clear gain (options off) |

Owner direction: the abilities stay as they are for both sides; the work is to get the most out of them for
our AI in any condition, not to adjust them in our favour.

Testing: `duel.js` (paired, staged, early stop) for decisions; `gauntlet.js` (parallel, live progress,
`QUICK=1`) for milestones; `taken.js` and `balance.js` for damage breakdowns.

## Measurement and tuning (2026-10-01)

- Paired battles stay in sync (per-tick order stream), every seed is also played side-swapped, and
  `sprt.js` runs a sequential probability ratio test on fresh seeds. 64-128 pairs decide gains of about
  1 survivor per fight; +0.5 needs about 250+.
- Confirmed with it: react to enemy aim tells +0.93; aimed shot is worth keeping (removing it -0.64);
  imitation-network shortlist (`LOOK=fast`, `"PRUNE3"`) plays like the full look-ahead at 3x less CPU.
- Not confirmed: enemy-response look-ahead +0.35, two-step plan search +0.27, barrage fix +0.26, bait +0.22.
- Evolution-strategy tuning (`es_tune.js`) of the ability thresholds: +1.06 confirmed for the rules
  commander (`AB_TUNED_RULES`); with the look-ahead commander a 28-generation run gave +0.01 on new seeds
  (256 pairs): the defaults stay.

## Removed options (2026-10-01)

Measured without gain and deleted (results identical by the fingerprint, 1701 -> 1402 lines): lure,
artillery volley, orbit kiting, in-fight learning, PROTECT pair, sortie lease, wounded pull-back, pivot,
charge-aware and cooldown-aware siege, charge reserve, counter-charge, counter-battery, artillery-first
focus, avoid shielded targets, smart dodge, ability postures, per-group ability scripts, enemy-response
look-ahead, two-step plan search, imitation network playing alone. The git history keeps them.

## Baseline with abilities (2026-10-01, current code, shortlisted look-ahead, 40 runs per mode)

| random gauntlet | avg fights won | runs >= 4 | >= 6 | >= 8 | worst |
|---|---|---|---|---|---|
| any | 4.0 | 26 | 6 | 1 | 1 |
| pool | 3.9 | 22 | 7 | 1 | 2 |

Without abilities the same code reached 6.4 / 5.9. Wolfpack ends most failed runs (won 10 of 29 meetings,
21-24 units lost per win), then loose skirmish (~14 per win). The shortlist may cost up to ~0.4
survivors per fight against the full look-ahead (128 pairs: +0.42 for the full one, undecided).

## Our AI picks its own group (roster.js)

Pool 20 melee / 60 shooters / 20 artillery; our AI picks 50 (melee and artillery 0-20 in steps of 5) against the
enemy it sees (10/30/10), by trial fights; then picked group vs standard 10/30/10 on 6 fresh fights each.

- Picking with the cheap rules commander (2 trials): picks were no better, and vs Wolfpack (abilities off) worse
  (3/6 wins vs 6/6) — the rules commander is not the one that fights.
- Picking with the shortlisted look-ahead (4 trials, abilities on, 360 s): picked >= standard everywhere, +0.3 to
  +1.8 survivors (Wolfpack 15/25/10: 36.8 vs 35.0) — within noise at 6 fights. 10/30/10 is already close to best.
- Deploy count was not varied: every pick fields all 50.

## How many units to send (gauntlet.js DEPLOY)

Random gauntlet (DRAW=any, LOOK=fast, abilities on, QUICK), same 30 seeds: send all 3.97 average fights won;
send 80% (rest wait as reserves) 3.5 on 10 seeds; AI picks 60%/80%/all per fight by 2 trial fights: 3.7.
Holding back loses: a smaller group loses more units per fight (strength grows with the square of numbers), and
the AI, trusting 2 noisy trials, sent 14-24 units into Wolfpack and lost the run with reserves still waiting.
Default stays "send all"; the option is kept for later tests.

## The real ceiling: health lost per fight (cost.js)

Our units carry their wounds from fight to fight and nothing heals, so a 10-fight run is a health budget.
At full strength (abilities on) every opponent is beaten 4/4, but each fight costs on average ~27% of our army's
total health while only ~3.6 units die: column 15%, line anvil 12%, crescent 14% ... screen 43%, loose skirmish
45%, wolfpack 57%. At ~27% per fight the army is spent after ~4 fights, which is what the gauntlet shows (4.0);
group choice and reserves cannot change that. Reaching 8 fights needs roughly <=12% per fight on average; the
work is to cut the cost of the expensive opponents (wolfpack, loose skirmish, screen, wedge hold, alone, line, ring).

## Aimed shots, dodging, lead (new default rules, both armies)

`shots: 'aimed'` (default; `'homing'` = old): a shot flies straight at `shotSpeed` 350 (5x unit speed) to where
its target will be and hits the first body it crosses, so it can miss. `shotDodge` (default on): a unit that has
seen a shot for `shotReact` 0.12 s and is in its path sidesteps instead of acting that tick. `smoothLead`: shots,
shells, barrage and slow fields aim with movement smoothed over 0.3 s. `pursuit: 'cut'`: melee run to where the
target will be. Packs can override per side (`f.shotDodge` false/'soft', `f.smoothLead`, `f.pursuit`, `f.jink`).
Old rules (`{"shots":"homing","pursuit":"chase","smoothLead":false,"shotDodge":false}`) reproduce the earlier
numbers exactly.

- Health cost per fight (cost.js): average unchanged (28.1% -> 28.4%); wolfpack 57% -> 41%, screen 43% -> 23%,
  wedge hold 36% -> 27%; column, crescent, line anvil dearer. Random gauntlet (20 runs) 3.9 -> 3.6, within noise.
- Our side only, SPRT on margin vs the default: shot dodge off -4.8 (dodging is essential); dodge only shooters
  and artillery -0.91; raw lead -0.67; squads of 4 by default +0.34 and focus plans `focus`/`pushfocus` (always
  tried, `laExtra`) +0.20, both undecided — the default "spread" already finishes the weakest target first without
  overkill; jink 14 px +0.03, 24 px -0.55; melee chase instead of cut +0.15. Shortlist network retrained on the
  new rules: -0.23, the old one is kept.
- The skills raise both armies equally; none of our side's choices on them lowers the health cost enough to move
  the gauntlet ceiling.

## Full healing between fights (default) and fire control

Gauntlet survivors are now fully healed between fights; `HEAL=none` (gauntlet.js, trace_gauntlet.js) or the
viewer's "full healing" checkbox keeps the old rule. Baseline, abilities on, LOOK=fast, QUICK, 40 runs:

| mode | average fights won | runs >=4 | >=6 | >=8 | 10/10 |
|---|---|---|---|---|---|
| any | 5.3 | 34/40 | 19/40 | 4/40 | 2/40 |
| pool | 5.4 | 34/40 | 18/40 | 5/40 | 1/40 |

(No healing: 3.6-4.0.) Hardest now: wolfpack (10/15 any, 6/20 pool), swarm, loose skirmish.

Where our shot damage goes (stats.shotOut, "/sure" = target could not dodge that shot): ~16% hits its target,
~56% is dodged, ~14% hits our own units in the way, ~9% flies at a target already dead, ~5% hits another enemy,
~1% overkill. Shots at targets that cannot dodge hit ~half the time; at dodging targets ~7%.
Tested for our side (SPRT, margin): fire control (`fireControl`: shots count by chance to hit so just enough
shooters stay on a target, targets that cannot dodge first — close, slowed or locked in melee — aim lane kept
clear) +0.11; plus aiming for enemies behind the target (`fireDepth` 0.25) -0.19; holding fire at targets that
can dodge (`holdFire`) -2.03. Missed shots are not wasted: a dodging unit does nothing else that moment.

## Every army dodges shells (default) — and why we win (ablate.js, now `ai_lab.js pieces`)

`shellDodgeAll` (default on): every army steps out of predicted shell splashes, not only our commander and
Wolfpack (`ENEMY_DODGE=0` / viewer checkbox = old rule). It was a large hidden edge for us: random gauntlet
(healing on, 40 runs) any 5.3 -> 2.6, pool 5.4 -> 2.6 average fights won; >=4 now 10/40 and 12/40.

Why we win (ablate.js: our side with one piece removed at a time, 19 opponents x 2 seeds x both sides, same
battles; margin = our survivors - theirs):

| our side | won | margin |
|---|---|---|
| full: formation + rules commander + look-ahead | 95% | +43.3 |
| rules commander, no look-ahead | 93% | +32.6 |
| rules commander, no coordinated abilities | 100% | +35.0 |
| plain wide line, no commander | 71% | +13.6 |
| no formation (each unit alone) | 39% | -4.5 |
| fairness: plain wide line vs its own mirror (12 fights, mirror.js check) | — | -3.6, noise ~4 |

Formation (+18) and the commander's plan switching (+19) are the biggest pieces; look-ahead adds +11 and is what
wins against an equal enemy (vs a wide line enemy: plain -10.8, rules -8.8, look-ahead +35.8). Coordinated
abilities do not help the rules commander (-2.4). Mirror check under the old rules leans -3.7 against our side
(12 fights, SD 5): a small possible team-order bias, against us, not chased yet.

## AI levels and what each piece is worth (ai_lab.js)

Ladder (`node ai_lab.js ladder`, 16 battles per cell, margin of the row against the column):

| | novice | regular | veteran | elite |
|---|---|---|---|---|
| novice | 4.0 | -40.8 | -40.7 | -44.4 |
| regular | 40.9 | -1.7 | -38.7 | -45.2 |
| veteran | 45.6 | 39.3 | -9.7 | -13.1 |
| elite | 45.6 | 45.1 | -1.6 | -2.3 |

Each level beats the one below by ~40; elite vs veteran is close (+5.7 averaged both ways). Same level vs
itself is within noise.

Veteran's pieces against the opponent pool (`node ai_lab.js pieces veteran`, 76 paired battles; "as is" 93% won,
margin +32.6, the same as the older-option rules commander): shell dodging off -46.3, shot dodging off -18.9,
rules commander replaced by its plain formation -11.8, abilities off -5.0, holdFire -6.3, reactAim off -2.4,
shotReact 0.3 -2.3, kite off -1.3, no lead -0.9, chase -0.7, fireControl -0.5, jink 14 +2.2 (noise level ~2).
Dodging decides most of a fight; the commander is the next biggest piece.

## Recheck fixes (fairness and speed)

- `separate()` pushed overlapping pairs one at a time in unit order (our units first): a small team-order bias
  (old-rules mirror -3.7). Now neighbours come from a grid and all pushes apply at once: old-rules mirror -1.0
  +/- 0.7, current rules +0.6 +/- 1.5 (64 fresh battles), veteran vs veteran +0.4.
- `room` (space behind a side, a shortlist-network input) assumed our side starts on the left; wrong in every
  side-swapped battle. Now measured from the side's facing.
- Artillery scored every target against every enemy on every tick, also while reloading; now only when ready.
- Coordinated-ability thresholds are per side (`profile.ab`), not one global `w.o.ab` (still read as before).
- Speed: 1.24 -> 0.97 ms per step without look-ahead; bench 393 -> 576 steps per CPU-second.
- Baseline after the fixes (fair dodging, healing, abilities, LOOK=fast, 40 runs): any 2.5, pool 2.5 average
  fights won, >=4 in 8/40 each. Hardest: wide line (4/10 won, 22.8 units lost per win), wolfpack, alone.

## Artillery volleys and the escape model (skill artyFire)

`artyFire`: `single` (default: each gun on its own), `net` (centre + ring), `herd` (centre + behind and beside),
`plan` (for the 3 densest clusters x 5 shapes — focus, net, wide, herd, wall — expected value under an escape
model: an enemy may reach any spot within its speed x flight time, it is hit only if every spot is covered;
forced dodges and herding toward us count `artyDodgeValue` / `artyHerdValue`). `artyVolley` / `artyWait` set
how many guns wait for each other and how long.

10 battles (veteran): units hit per shell single 0.76, net 0.67, herd 0.72, plan 0.85 (+13% damage per shell),
but waiting for volleys fires 16% fewer shells. Paired vs single (76 battles, noise ~2): plan with no wait
+0.25, plan with 2-gun volleys and 0.3 s wait +1.26, plan with 4-gun volleys -0.47. Not confirmed; default stays
single. Single shells already hit 0.76 units each because units dodge a shell only once they stand inside its
future blast, and melee locked in a fight do not dodge.

## Artillery planner (step 3 of PLAN_TACTICAL_MIND.md; skill artyFire 'plan')

Every army dodges shells with one shared rule (`shellEscape`). The planner plays that rule forward for the enemy
(`predictVolley`, 0.1 s steps, every shell already in the air) and blends it with a smart-dodger model
(`smartVolley`, `artyRobust` 0.5). Attacks compared on the 3 densest clusters in reach: singles, focus, net, wall,
trap (ring with a gap in 4 directions + finisher 0.4 / 0.8 s later at the predicted escapers), sweep (0.3 s apart).
Value = threat removed (damage x target's damage per second per health, plus a kill bonus). It plans whenever
another gun is ready; unused guns fire singles; delayed shots wait in `pack.artyQueue` (copied by `fork`).

10 battles, veteran: prediction 21.6 vs actual 22.3 damage per shell; damage per shell 17.9 -> 21.9 (+22%), same
fire rate per gun, fights 17% shorter, CPU -3%..+3%. Paired vs single (76 battles): veteran +3.04, elite +0.64
(the look-ahead's forks fire singles, so it cannot see the planner yet). SPRT veteran: +1.64, accepted (192 pairs).
Chosen attacks: singles and focus most, then net; trap, sweep and wall rarely — damage alone rarely favours them;
their control value needs the combined plans of step 5.

## The tactical mind (step 4 of PLAN_TACTICAL_MIND.md) — built, not adopted

`lookahead: 'mind'`: screens the current combination and the shortlisted plans, then tweaks one role at a time
(artillery, shooters, melee, position; role order rotates each decision; 8 combinations), then plays the best 2
also against an all-in rush (0.7 x worst + 0.3 x mean). Options: `models` (add 'rules': their commander re-plans),
`tweakMargin`, `horizon`, `objective: 'deaths'` (also honoured by the plain look-ahead), `extends` for partial
settings. Shells still in the air count at expected damage. Forks run a light artillery planner. ~2x the CPU of
the plain look-ahead.

| test (paired, B - A margin) | result |
|---|---|
| mind vs elite, against the pool (76) | +1.30 (noise) |
| mind vs elite, against an elite enemy (32) | -3.97 |
| plans only + rush check (16) | -2.38 +/- 2.37 |
| tweaks, no rush check (16) | -7.81 +/- 2.68 |
| tweaks + 'rules' reply + tweakMargin 20 (16) | -7.75 +/- 2.58 |
| tweaks, fixed shortlist input (16) | -7.63 +/- 3.27 |
| tweaks, 6 s horizon (16) | -6.63 +/- 3.40 |

Role mixes beat no-mind enemies but a smart enemy punishes them; longer horizon, smarter replies and a tweak margin
do not fix it (a likely cause: forks at 0.1 s steps misjudge mixed tactics such as released melee). Gauntlet
(healing, 40 runs, elite + artillery planner): 2.4 average fights won; with objective 'deaths' 2.4 (>=4 in 3/40 vs
8/40). Neither is adopted. Shortlist input fixed: a mixed combination feeds its position tactic as the plan.

## What kills us (elite + artillery planner vs the pool, 38 battles) and two answers tested

Our deaths per fight 4.7: shooters to shells 1.82, melee to shots 1.16, melee to shells 0.82, shooters to shots 0.45,
artillery to shells 0.37. Damage taken: shells 37%, shots 24%, melee hits 15%, charges 12%, barrages 9%. About
3 survivors per fight end below 30% health (healed before the next fight), so rotating the wounded gains little.
- `dodgeShells: 'smart'` (go to the reachable spot under the fewest blasts, counting every shell in the air):
  veteran -0.68 +/- 1.02 (76 battles) — most shell deaths cannot be escaped (melee locked in fights, crowding).
- Counter-battery (`artilleryDoctrine: 'counter'`): veteran -1.55 +/- 1.10 — their artillery dodges our shells.
Decisions (artillery planner, smart dodge, look-ahead, mind) are ours only; default enemies keep plain rules.

## Finishing fights: position score and stall breaker (adopted into veteran / elite)

Half the gauntlet runs ended in timeouts with our army mostly alive: stalemates where, for example, only their
artillery is left and reaching inside its minimum range takes longer than the 3 s look-ahead sees.
- `lockedDodge` (melee locked in a fight also dodge shells): SPRT +1.53 accepted (veteran, 192 pairs).
- Look-ahead `terminal: 6`: at the end of each playout, the damage per second each side can deal from where it
  stands, counted for 6 more seconds (`reachRate`). `stall: 10`: when the enemy has lost no health for 10 s, our
  losses weigh a third and our damage double. `urgency` (clock-based) did not help and is not used.
- Elite + terminal + stall vs elite: pool +2.03 +/- 1.00 (76), elite enemy -4.94 +/- 3.63 (16, not significant).
- Gauntlet (any, healing, abilities on, 40 runs; the earlier OUR_LEVEL runs lacked abilities and are not comparable):

| our AI | avg fights won | >=4 | >=6 | timeouts |
|---|---|---|---|---|
| reactive + LOOK=fast (baseline before the plan) | 2.5 | 8/40 | 0/40 | — |
| elite with artillery planner + lockedDodge | 3.0 | 17/40 | 2/40 | 13 |
| + terminal 6 + stall 10 (now elite) | 3.4 | 18/40 | 4/40 | 10 |

Veteran and elite levels now include artyFire 'plan' and lockedDodge (decisions: ours; default enemies keep plain
rules). Elite also includes terminal 6 and stall 10.

## Optimization pass (2026-10-02)

Exact (results identical: 82 legacy cases, fingerprint, result signatures):
- Ability triggers are worked out only when that ability is ready (`ready()` is side-effect free, every `use*()`
  checks it first); per-tick melee lists (`teamMelee`) for nearest-melee checks.
- Lane checks: remembered while nothing moved, and a live spatial grid (`lgMoved`, cell 40 px) instead of scanning
  every unit; ties go to the lowest id, as the full scan did.
- Best shooter target found without sorting unless its lane is blocked; shape cached until counts / settings change;
  previous positions stored on units; forks get fresh telemetry instead of deep copies.
- CPU per step: veteran 1.07 -> 0.81 ms (-24%), elite 3.25 -> 2.31 ms (-29%).

Measured, not adopted (changes decisions): `everyStable` — after a decision that kept the plan, the look-ahead
waits longer. 2 s: elite -27% CPU, margin -0.83 +/- 0.58; 1.5 s: -1.22 +/- 0.94 (76 battles each). About one unit of
margin for a quarter of the CPU; available as an option (e.g. for packs far from the player in the game).

## Re-measured options (veteran with artillery planner + lockedDodge, 76 paired battles, +/- standard error)

| change | margin |
|---|---|
| jink 14 | +0.24 +/- 1.04 |
| holdFire | -5.50 +/- 0.95 |
| fireControl | -0.04 +/- 0.68 |
| fireControl + fireDepth 0.25 | -0.12 +/- 0.87 |
| lockedDodge off | -0.63 +/- 0.68 (was +1.53 by SPRT before the planner) |
| artyFire single (planner off) | -2.05 +/- 1.12 |
| elite + urgency, gauntlet 40 runs | 3.4 vs 3.4 average fights won |

`ai_lab.js pieces` now tests a skill's default when the level already uses its alternative, and prints the error.

## Fairness fixes (2026-10-02, later)

- A side's brain-dependent defaults (abilities 'coordinated' for a commander) came from the older options, before
  its profile / level: an enemy given `level: 'veteran'` over `enemy: 'formation'` kept per-unit 'auto' abilities.
  Every same-level comparison (ladder, elite-enemy tests) had a slightly handicapped enemy; veteran mirror -3.3 +/- 1.7.
  Now the final brain sets the defaults: veteran mirror +3.0 +/- 1.8 and -1.3 +/- 1.6 on fresh battles (96, 144).
- Both packs decide in a random order every tick (the second saw what the first just did); not the lean's cause.
- Wind-ups (`windUp` world option, default off): shots 0.5 s, shells 1.0 s of preparation once reloaded, instant
  release, the rate of fire unchanged; moving and dodge steps keep the preparation, a dodge ability breaks it.
  Leader fire control (`leaderFire`): the leader assigns shooters to targets and, with wind-ups, holds each group
  until all are ready (at most 0.5 s) so the shots arrive together.
- Quick tests (veteran, 76 paired battles): leader fire control with wind-ups -1.09 +/- 1.17 (before the bracket),
  without wind-ups -0.47 +/- 0.87. Shot damage landing on enemies (10 battles, wind-ups on): 14% without the
  leader, 14% with it, 15% with bracketing (`leaderBracket` 12 px: centre, left, right). Our shooters fire from one
  side, so one sidestep dodges a whole volley; a shot from 95+ px is seen (0.12 s) and stepped out of (~0.15 s)
  before it lands. While dodging stays this reliable, how shots are coordinated changes little.
- Recheck fixes: an aimed-shot release did not restart the wind-up (the next normal shot needed none); the leader
  counted shots in flight at full damage while ~64% miss, so it assigned too few shooters (pending now counts the
  chance to hit under leader fire control). Leader fire control with wind-ups: -1.24 -> +0.45 +/- 0.89 (76).

## Game rules mode (`rules: 'game'`) — the game's combat numbers, nothing invented

Roles = monster kinds: melee brute (maul), shooters spitter (ember_spit), artillery shaman / Voltfang (arc_bolt).
Sources are listed at `GAME` in formation_sim.js: kind and ability data, the native build (health, energy, damage),
the dash-dodge profiles, and the combat docs. Rules: windup -> release -> authored cooldown for every attack (melee
too); a cast commits when a target is in reach, pays its energy at commit and always runs to release; a shot flies
straight at the target's position at release; a lob's landing point locks at commit and it lands after distance /
300 px/s; projectiles hit the first body they cross, allies included, for full damage; a lob hits everyone in its
40 px circle except its caster; units dodge only by their kind's dash (spitter 60 px, 80%, 0.9 s; shaman 110 px,
90%, 1.0 s; brute never), never by stepping out of lobs; group decisions at 5 Hz; the sandbox's invented
abilities are off. Not modelled: mitigation by type, instance stat rolls (+/-15%).

| | health | damage | reach | windup / cooldown | speed |
|---|---|---|---|---|---|
| brute | 258 | 19.5 | 64 | 0.45 / 1.8 | 40 |
| spitter | 92 | 10.4 | 280, shot 240 px/s | 0.55 / 1.4 | 55 |
| shaman | 181 | 18 (lob r 40) | 320, lob 300 px/s | 0.7 / 1.2 | 55 |

Veteran vs veteran under game rules (60 battles): margin -0.3 +/- 0.8 (fair), fights 73 s on average, 10 of 60
time out. (The artillery planner was off under game rules here; it runs under them since 2026-10-02, see
"Artillery under game rules" below.)

## First measurement under game rules (veteran vs the pool, 38 paired battles)

71% won, margin +2.8 (sandbox rules: 99%, +37). Our commander replaced by its plain formation: +0.6 +/- 0.6 —
under the real rules our tactical mind adds about nothing yet; its earlier edge came from invented physics
(perfect dodging, harmless friendly fire). Leader fire control -0.9 +/- 0.8, fire control -0.6 +/- 0.9, jink
+0.1, kite +0.2; dodge reflexes, lead, sandbox abilities and the artillery planner do not apply under game rules.
Known errors in this first game mode (fixed next, see PLAN_GAME_RULES_TACTICS.md): cooldown counted after release
instead of from cast start; lobs locked at commit instead of re-targeted at release; dashes against monster shots.
- A.1 fixes to the game mode (each from the game's code / docs, sources at `GAME`): cooldown runs from cast start;
  a shot or lob re-checks its target at release and aims at its current position (a lob with no lawful target
  fizzles, no refund); no dashes against monster shots (the mind dodges only the player's); kiters back off to the
  game's standoff (spitter 151 px, shaman 173 px) at x0.5 while casting goes on; a shot cannot start while a
  pack-mate is in its lane; melee approach identity-phased points on a ring around the target; protection from
  traits (brute 0.2, casters 0.15), damage floored to whole health. The fumble offset applies only to confused
  units (EncounterAI::stage_action_fumble), so it is not modelled. Mirror (60): +0.9 +/- 1.2, fights 65 s,
  12 of 60 time out, 0 dashes, 2.2 units hit per lob (both sides counted).
- A.2: the game's pack AI as an opponent (`enemy: 'gamepack'`, reduced port, sources at `GAMEPACK_PLANS`):
  PRESSURE / DEFEND / WITHDRAW with the game's gates and hysteresis, threat responses by family and coverage,
  layouts screen_and_focus (line) / surround (ring) / withdraw (ring moving away). Left out: learned utility,
  Sense uncertainty, region planner, excursions, morph. First battle: 29 mode changes in 68 s (the game's
  tracker notes the same flip-rate issue).

## A.4 baseline under the corrected game rules (won %, margin; 150 s fight cap)

| our AI | vs pool (38) | vs the game pack AI (24) |
|---|---|---|
| novice (no formation) | 58%, +3.2 | 54%, +0.6 |
| regular (fixed formation) | 82%, +15.8 | 4%, +16.9 |
| veteran (rules commander) | 92%, +15.1 | 92%, +6.4 |
| elite (look-ahead) | 89%, +21.4 | 33%, +17.0 |

Paired: regular - novice +12.6 +/- 1.5 (pool); elite - veteran +6.3 +/- 1.6 (pool), +10.6 +/- 2.4 (game AI).
Against the game AI, regular and elite mostly end at the time cap well ahead: the game AI turtles (DEFEND),
our fixed formation and the look-ahead do not finish it; the rules commander finishes but trades closer.

Game encounter facts for pack vs player (A.3): a normal encounter is 8 bodies (overworld/sortie_stager.gd, about
two packs of 3-6, systems/arena/danger_zone_encounter_planner.gd); hordes 100 alive, 10 engaging
(balance.json horde); brute / spitter / shaman are lab kinds used by systems/dev/dev_presets.gd::SKIRMISH60_FIGHT
(18 total, 8 alive, attacker cap 6, with hound, runner, warden). Player kit: base_dash 3.5 m in 0.45 s, cooldown
0.3 s, 10 EP (data/deliveries/core.json, data/magic/catalog.json); fire_bolt 12 damage, 12 EP, 11.25 m/s, 11.25 m.

## A.3 pack vs player (skirmish.js): the game's Skirmish 60 field against a player bot

Field: systems/dev/dev_presets.gd::SKIRMISH60_FIGHT (18 monsters drawn from spitter, hound, brute, shaman, runner,
warden; 8 alive; attacker cap 6). Kinds derived from the native build (GAME.kinds); warden block, dash rules (only
the player's shots: manual, or chip for the runner's skittish profile, or at <= 35% health), the player's Evo1
combat_ready kit (GAME.player: 763 HP, 4 auto limbs fire_bolt -> fire_lance, ember_bolt, cinder_pulse, dash).
The player bot's behaviour (kite, cast, dash on threats) is the sandbox's design. The game pack AI port now has
its pressure station by action range and intercept runs (it stood off before: the formed-gate never opened).

| pack AI (24 seeds, 180 s cap) | player killed | time to kill | monsters lost |
|---|---|---|---|
| the game's pack AI | 29% | 96 s | 14.9 |
| novice (every unit alone) | 58% | 73 s | 14.5 |
| regular (fixed formation) | 8% | 107 s | 14.5 |
| veteran | 42% | 116 s | 13.6 |
| elite | 33% | 145 s | 14.7 |

Against one player, units acting alone kill best: our formation-based levels were built for army fights and hold
back. Calibration gap: the preset is meant to clear in about a minute of competent play; the bot rarely clears
(the player's temporal speed, ACC 6.62, is not modelled, and the bot is simple), so absolute numbers are not the
game's; the comparison between pack AIs on the same battles is the measure.
- Temporal speed (FM_520 ACC from each kind's stats, FM_530 the player as frame of reference, FM_156 launch
  factor): brute / warden / spitter ACC 2.62 (run at 0.40 of the player), hound / runner 3.31 (0.50), shaman 4.48
  (0.68), player 6.62 (the formula reproduces it from its stats); projectiles launch x1.32 / 1.46 / 1.70. Pack vs
  player then: the game's pack AI kills the player in 50% (72 s), novice 46% (54 s), regular 4%, veteran 0%,
  elite 4% (24 seeds). Still not the preset's "clear in about a minute": the bot is simple and the surround slow
  is not modelled.

## B1 pack vs player: encircle (96 seeds, Skirmish 60 field, game rules incl. temporal speed and surround slow)

| pack AI | player killed | time to kill | monsters lost |
|---|---|---|---|
| the game's pack AI | 50% | 74 s | 14.0 |
| novice (every unit alone) | 48% | 62 s | 14.9 |
| veteran, few targets -> engage (all roles released) | 43% | 62 s | 15.2 |
| veteran, few targets -> surround | 68% | 71 s | 13.1 |
| elite | 74% | 87 s | 12.1 |
| elite, few targets -> surround | 77% | 92 s | 11.1 |

`surround` (rules commander, game rules, 2 or fewer enemies; default `fewPlan`): melee spread on a ring around the
focus target with the first angle on its escape, shooters on a 200-degree arc at 0.8 of their reach, artillery
behind (surroundOrders). Leading lobs (`lobLead`) is wrong against this player: novice 46% -> 0% with it; it is
off in every level. Surround slow (FM_600) for the player is modelled: the bot is rarely mobbed.
- Encircle settings (DEFAULT_F surroundRing / surroundArc / surroundDist / surroundLanes). Sweep, elite, 48 seeds:
  default 83%, lanes off 75%, waves of 3 71%, arc 300 83%, dist 0.65 75%, ring 1.0 77%. Lane-aware arcs
  (shooters at the gaps between the melee ring angles), 96 seeds: elite 82% vs 77% without, veteran 67% vs 68%;
  kept. `waves` (start casts together) is worse and stays off. Pack vs pack under game rules is unaffected by
  the few-targets rule: veteran vs the pool -0.08 +/- 0.12, vs the game pack AI +0.08 +/- 0.08.

## Recheck of pack vs player (fresh seeds 3000+, held-out player styles; 96 seeds each)

| player style | game pack AI | novice | veteran | elite |
|---|---|---|---|---|
| kite (tuned on, fresh seeds) | 52% | 49% | 72% | 84% |
| orbit (held out: circles at ~400 px from the nearest monster) | 2% | 4% | 2% | 25% |
| press (held out: pushes in to ~250 px) | 75% | 65% | 64% | 84% |

Elite is robustly best (fresh seeds, both held-out styles). Veteran is not robust: below the game AI against a
pressing player. A player that keeps 400 px from every monster is out of all monster reach (280 / 320) and 2.5x
faster in its own time: no pack catches it on an open field; only cornering it against the walls could. Adaptive
lob lead (lead only when the target has moved steadily for ~1 s; `lobLead: 'adaptive'`) changes nothing (kite 83%,
orbit 25%, press 83% for elite) and stays off. skirmish.js: SEED0, STYLE (kite | orbit | press).

## Round after the recheck
- Cornering (`surroundCorner`: stand between the target and the arena centre): elite on seeds 3000+ kite 84 -> 94%,
  press 84 -> 88%, orbit 25 -> 24%; on fresh seeds 6000+ kite 88 -> 89%, press 85 -> 85%: no confirmed gain (the
  first set was luck), stays off.
- Veteran on fresh seeds 6000+: press 71% vs the game AI 73%, kite 79% vs 48% — the earlier "below the game AI vs
  press" (64 vs 75) was noise. Its few-target plan stays surround (hold 64 / 14%, skirmish 57 / 6%, siege and
  intercept 20 / 0% for press / kite).
- Player numbers checked: spell cost x2 is real (cost_coefficient defaults to 1.0, combat_content_store.h:587;
  magic_cost = 1 + coefficient x (scale - 1), .cpp:3443). Burn on every fire attack is now modelled: 20% of the
  landed hit over 4 s, independent stacks, cap 5, unmitigated ticks (FM_270; effect_application_policy.cpp:397-399:
  the seeded rate replaces the flat one). Pack vs player then (seeds 6000+): game AI 41%, novice 32%, veteran 66%,
  elite 78%.
- Gauntlet under game rules (healing, 40 runs, 150 s cap): veteran 1.6 average fights won (>=4 in 3/40), elite
  2.0 (6/40; 19 of its runs end in a timeout).

## Frozen rules (2026-10-02): game rules; from here only decision logic changes

Perception is **off** (since 2026-10-02 evening): the arena is small and everyone sees everyone. The earlier
default (one 768 px sight radius for every monster) was not the game's rule (in the game sense grows with
progression and some monsters sense differently), so it only added noise to formation tests. It stays as option
`perception: true` (then the pack searches forward when it knows no enemy). Terrain is not modelled (it would be
mirrored, so it is fair to leave out).
Ported because it changes decisions: timing (wind-up, cast, cooldown from cast start), projectiles (speed, travel,
range, straight / lob, first body hit incl. allies), area attacks, the six kinds and their reach / speed, the
relative speed (temporal ratio), dash and block reactions, the attacker cap, body collision.
Kept simple on purpose (numbers only, no decision changes): mitigation, damage scaling, pool derivation, regen,
burn, rarity, stat rolls.

## suite.js — the one test (frozen game rules, fresh seeds, PASS / FAIL per line)

`node suite.js '<profile>'` (default elite): fairness, vs the game's pack AI (mirror armies), units lost per won
fight, vs the pool, vs player (kite / press / orbit). Elite (48 per line, seeds 20000+):

| line | result | |
|---|---|---|
| fairness | margin -1.4 +/- 0.7 | PASS |
| vs game AI | won 100%, margin +16.5 (game AI vs itself -0.6) | PASS |
| units lost per won fight | 31.0 of 50 (target <= 5) | FAIL |
| vs pool | won 97%, margin +21.9 | PASS |
| vs player kite / press / orbit | 85% / 79% / 6% (game AI 38% / 60% / 0%) | PASS |

Veteran: 5 of 6 before the cost line (press 60% = the game AI's 60%). The gap to 9-10 fights in a row is the
cost of a win: about 31 of 50 units, where about 5 is needed. Recheck: the perception-off mirror lean is not a
side bias (it flips sign across variants: veteran +1.3, regular -1.0, novice -0.85 on the same 120 battles);
a shooter's step-back check used unperceived melee, now perceived only.

## Decision step 1: local superiority (`oblique`), adopted in elite
The pack faces the end of the enemy line with fewer enemies near it instead of its nearest unit (positionAnchor,
f.oblique). Elite, suite on seeds 20000+ and fresh 30000+: units lost per win against the game AI 33.5 -> 23.5 and
33.2 -> 23.8, margin +16.5 -> +26.3 and +17.0 -> +25.8; against the pool unchanged (27.6 / 27.4), wins 100 -> 95%
on the fresh set. As a plan the look-ahead may choose: the same (24.3). Veteran with it: pool wins 97 -> 76%, so
not adopted there.
- Step 2 kill-speed targeting (`killSpeed`: health left per damage per second): cost per win vs game AI 23.5 -> 27.1
  (seeds 20000+), 23.8 -> 23.7 (30000+), pool wins 95 -> 87%: not adopted.
- Where our losses come from (elite vs the game AI, 24 won fights): 20.9 deaths per win, of them shooters to
  enemy artillery 12.7 and melee to enemy artillery 5.7 — lobs cause about 88% of our losses.
- Step 3 spacing against lobs (front / rank 55/40, 70/55, 90/70): cost per win 29.8 / 30.4 / 32.6 vs 23.8, worse.
  Counter-battery (`artilleryDoctrine: 'counter'`): 23.8 -> 23.2 on 30000+, 25.4 -> 25.3 on 20000+: no confirmed
  gain. Artillery raid plan (`raidart`, melee wings strike the enemy artillery; look-ahead may choose it): 26.9,
  worse. None adopted.
- The size of the gap (square law): losing 5 of 50 in a win against an equal army needs about 2.3x the enemy's
  effectiveness per unit; elite now loses about 24 of 50 (about 1.2x). Only decisions may close that gap.

## Artillery under game rules (2026-10-02): the planner runs, attacks judged by outcome

The artillery planner had been switched off under game rules (its guns never started casts); every game-rules
result before this section used plain artillery (each gun lobs at its own target). It runs now, within the rules:
a gun releases when its own wind-up ends (it cannot hold a finished cast), so a delayed shot (trap finisher,
sweep shells) goes to a gun already mid-cast and releasing near that time, or is dropped; flight = distance /
(lob speed x launch factor). Measured per attack (`w.stats.atk`: shells, damage, kills, own units hit).

Elite vs the game's pack AI, 24 fresh fights (seeds 6000-6011, both sides), perception off:

| artillery | margin | won | lost per win |
|---|---|---|---|
| plain (each gun at its own target) | +26.7 | 24/24 | 23.3 |
| planner, attack with the most predicted shell damage | +32.0 | 21/24 | 18.0 |
| + outcome check (`artyRollout`), top 3, 2 s | +35.7 | 24/24 | 14.4 |
| + outcome check, top 5, 2 s | **+37.6** | 24/24 | **12.4** |
| + top 5, 3 s / top 3, 1.5 s | +31.9 / +33.8 | 22 / 22 | 18.2 / 15.9 |
| + top 5 + shaping (split, herd, wall) always tried | +35.0 | 23/24 | 14.6 |
| + top 5 + counter-battery and shaping (battery, split, herd) always tried — **elite** | +37.2 | 24/24 | 12.8 |
| + follow-up (`artyFollow`: melee and shooters / shooters only go for the cut-off) | +35.5 / +37.0 | 23 / 22 | 14.2 / 12.4 |
| elite + fixed holds at cast start: finisher 0.4 / group 0.4 / both (removed) | +35.8 / +33.6 / +30.8 | 24 / 22 / 24 | 14.2 / 15.6 / 19.3 |
| elite + fire control `holdFire` sync 0.5 / 0.3 (hold only when one volley leaves no escape) | +37.1 / +35.3 | 23 / 23 | 13.1 / 14.8 |
| + scoring where they end up (`artyHerd`: in our reach / cut off from friends) | worse / no gain (8 fights) | | |

The outcome check plays each shortlisted attack `horizon` s forward on a copy of the battle (every unit acting,
their real brain) and fires the one with the best result (their health + 100 per kill lost minus ours, shells in
the air at predicted damage); about 4-5x the CPU of a fight. Traps work: the finisher shell does the most damage
per shell (about 110 vs 82 plain). Our own lobs hitting our units is small (about 170 damage in 4 fights). The
Fire control (`holdFire`, every unit, not an artillery skill): a unit able to start its cast is asked by gamePrep
(fireGate) to start or hold, and holds only when holding pays. Fixed holds (always hold a finisher, always wait for
the group) cost fire rate and lost, so they were removed; a first salvo version decided after the casts had already
started and was a no-op. Sync (area attacks, hold only for a volley that leaves no escape) ties. Bait (hold while
one of ours is already casting at the player and its dash is ready, then land in its cooldown) vs the player, 16
fights per style: kite 11 -> 14, press 14 -> 11, orbit 4 -> 0 kills: worse, because the player's dash cooldown
(0.3 s, core.json base_dash) is shorter than any of our wind-ups (0.45-0.7 s): there is no cooldown to land in.
The dash's real limit is its travel (112 px in 0.45 s) away from the threat, a predictable end point. Shaping (split / cut-off) is
chosen about a quarter of the time when always tried, but so far does not add kills: the follow-up that would
turn a split into kills (`artyFollow`) did not help either. Open: lost per win 12.8 against the target of 5.

Suite, elite with the outcome check (seeds 30000+, 48 per line, perception off): fairness +0.1 +/- 0.8 PASS; vs game
AI won 92%, margin +35.1 (was +25.8) PASS; units lost per won fight 18.5 (vs game AI 14.5, was 23.8; vs pool 23.2)
FAIL; vs pool 97%, +26.0 PASS; vs player kite / press / orbit 73 / 75 / 8% (game AI 27 / 50 / 0) PASS. 1104 s.
Next: timing judged by outcome (start now vs hold, played forward) instead of fixed holds.

## Defence and finishing (2026-10-02, research-backed plan in PLAN_TACTICAL_MIND.md)

Under game rules no side stepped out of lobs (buildProfile turned shell dodging off: "units dodge only by their
kind's dash"). Stepping out is movement, a decision: a cast never roots its unit (COMBAT_DESIGN.md:348, 373).
Elite vs the game's pack AI, 24 fresh fights (seeds 6000-6011, both sides):

| elite, plus | margin | won | lost per win |
|---|---|---|---|
| (before) | +37.2 | 24/24 | 12.8 |
| step out of blasts (`dodgeShells: true`) | +43.1 | 22/24 | 7.0 |
| smart dodge (`'smart'`: reachable spot under the fewest blasts) | +43.6 | 23/24 | 6.6 |
| + early dodge (`castDodge`: an enemy gun winding up is a blast to come at its target; the units next to the target step out before the lob exists) | +45.5 | 23/24 | 4.5 |
| + LTD2 outcome score (sum of sqrt(health) x damage rate: finished kills outscore spread damage) | +44.1 | 22/24 | 4.5 |
| + both (elite) | **+45.7** | **24/24** | **4.4** |

Suite with smart dodge only: vs game AI won 88% (FAIL), margin +43.5, lost per win 6.4 vs game AI, 9.2 overall.
Every fight not won was a standoff: the last 1-5 enemy guns about 330 px from our nearest unit (outside every
reach) for 100+ s, our look-ahead holding `siege` (its 2 s horizon sees the lobs closing in costs, never the kill).
Fix: the `few` rule also fires at 4 to 1, and finishing beats the look-ahead; the 48 suite fights vs the game AI
then all end with no enemy left.

Final suite of this batch (elite = smart dodge + castDodge + LTD2 + finishing + `shootGuns`; seeds 30000+, 48 per
line): fairness -0.8 +/- 1.0 PASS; vs game AI won 100% (was 88%), margin +42.7 PASS; units lost per won fight 11.0
FAIL (vs game AI 7.3, vs pool 15.6; target <= 5); vs pool 100%, +34.4 PASS; vs player kite / press / orbit 71 / 75
/ 17% (game AI 27 / 50 / 0) PASS. The quick 20-fight check (seeds 6000+) read 4.2 vs the game AI: those seeds are
easier, so the quick check ranks variants but does not replace the suite. The finishing fix turns the standoffs
into wins at a small cost (7.3 vs 6.4 when they were left unfinished). The pool costs most now (15.6).

## After-action reports (aar.js, aar_sum.js) and what they taught (2026-10-02)

`node aar.js '{"seed":6000,"opp":"gamepack"|"elite"}' <dir>` records a fight (snapshots every 100 ms, every
death with the killing attack and the shell's flight time, plan changes, artillery choices), finds the moments
where 3+ of ours die within 2 s (and stalls), freezes the battle at each (checkpoints every 0.5 s) and plays our
alternative plans 4 s forward; `node aar_sum.js <dir> [opp]` adds up many fights.

- vs the game AI (10 fights): 3 of 4 critical moments were the forced finishing surround charging into their
  withdraw ring (best alternatives hunt / advance by 680-1390). Now the look-ahead chooses how to close in among
  the closing plans (FINISH_PLANS): our deaths 49 -> 27 on the same fights, all won.
- A game lob always hits the unit it is aimed at: shaman launch factor 1.7 -> 509 px/s, at most 0.63 s of flight
  at 320 px, while a shooter needs 0.96 s to leave a 40 px blast (all 213 lob deaths in 6 fights vs elite: flight
  under 0.8 s). Dodging saves only the neighbours (castDodge). Traps and nets therefore matter only for the
  units around the aim point.
- vs elite (a mirror, 2 of 10 won): 25% of our deaths happen while dodging, and at about half of the 55 critical
  moments another plan did clearly better (best: engage 10, siege 9, hunt 7, counter 6, advance 6, ...): the
  look-ahead's network shortlist (3 plans) often never tries the right one.
- Tried from the lessons, not adopted (removed): random choice among equally safe escapes (no gain: the enemy does
  not predict our dodge, the target cannot escape anyway); guns first (our guns x6 on their guns, their guns
  count double in the outcome: vs game AI 2.5 -> 3.2 lost per win, vs elite -9.2 margin: splash on packed
  shooters is worth more); shooters stepping out of gun reach (never possible: their guns stand less than 61 px
  behind their front, our shooters reach 259 vs 320).
Quick check now (20 fights vs the game AI, seeds 6000+): margin +47.5, 20/20, lost per win 2.5.

## Recheck of the artillery work (2026-10-03)

- Planner accuracy (predicted vs actual damage of planned shells): vs non-dodgers actual 0.82-0.90 of predicted
  (protection not modelled), vs elite 1.45 (the model let every dodger step straight out; elite moves only to a
  spot under fewer blasts, else stays). `artyModel: 'exact'` (each enemy by its own dodge rule, locked melee that
  still dodge, protection) brings it to 1.01 / 1.04. It does not win more: vs an elite on the old model -2.5 over
  6 fights (noise); vs the pool 6.1-6.5 lost per win against 4.8 with the old model (the protection-weighted
  shortlist moves shells to less armoured targets, which the outcome check then prefers less). Default stays
  'simple'; the outcome check (real copies) is what corrects the shortlist.
- Our own lobs kill few of ours (pool 3 of 94 deaths, game AI 0 of 27, elite 28 of 478). A penalty for our units
  caught in planned blasts (`artyOwn`) was no help (pool 6.1 with exact either way); off.
- Pool after-action reports (19 opponents, aar.js now takes any pool name): all won, 4.9 lost per fight; 71% of
  deaths at 20-40 s, enemy lobs on our melee the largest cause (46 of 94). One stall (wedge flank, 20 s, siege):
  closing plans on a stall (`closeOnStall`) ended it no sooner (45 vs 44 s) and was removed; all plans in the
  look-ahead instead of the network's 3 (5.1 vs 4.9) and shooters on guns (4.8 vs 4.9) were neutral, removed.
- aar.js: moments ranked by size (was by text), square pictures (were cut), output outside the repo, and the enemy
  keeps its look-ahead in the alternative copies (`thinkTeams`).

Final suite after the recheck (elite, seeds 30000+, 48 per line), 7 of 7 PASS: fairness -0.2 +/- 1.2; vs game AI
won 100%, margin +46.5; units lost per won fight 4.5 (vs game AI 3.5, vs pool 5.6; target <= 5); vs pool 100%,
+44.4; vs player kite / press / orbit 75 / 75 / 17% (game AI 27 / 50 / 0). Start of 2026-10-02: lost per win
25.4, margin vs game AI +25.8.

## Universal test (2026-10-03): unit sets the AI has never seen

`unitsets.js` generates unit sets: 2-8 kinds, each an attack type (contact, straight shot, lob) with its own
stats, 50 units split over them; both sides field the same set. Families: `tune` (moderate ranges, development),
`heldout` (wider ranges, heavier units slower: verdict only), `anchor` (5 hand-made sets: verdict only). The sim
takes them as option `unitSet` (per-unit lob speed, blast radius and shot speed). `node universal.js <family>
<a-b>`: a 10-fight gauntlet per set (survivors healed, the dead stay dead, opponents drawn from the game's pack AI
and the pool), reporting fights won in a row.

Baseline, elite of 2026-10-03, tune 1-10: average 2.8 in a row, median 3, >=4 in 20% of sets, >=8 0%; 10-24 of ours
lost per fight (today's units: 5.4 average). Goal: >=4 in 90%, median 8, judged on heldout + anchor only.

Step 2, budget (2026-10-03): elite's CPU is 80% the artillery outcome check (1.8 ms per tick plain, 7.6 with the
look-ahead, 48.9 full). Copies at 0.1 s steps + at most one check per 0.3 s: 10.3 ms (4.7x faster) but pool lost
per win 7.1 +/- 0.9 vs 5.6 +/- 0.7 (38 fights each); either part alone also cost (pool, 19 fights: 6.0, 7.4, at
1/15 s steps 6.1, vs 4.8). Elite keeps the full check; level `elite-fast` has the budget, for development runs and
a CPU-limited port. Noise note: one fight per pool opponent has a standard error of about 0.9 lost per win.

Step 3, unit features (2026-10-03): every per-role constant the AI read under game rules now comes from the unit
(threat = its own damage rate, each gun's lob speed / blast / minimum range, formation reach per role from our
army, pace = our median speed, the melee ring from its own reach, the planner's cluster radius = 2 x blast). For
today's units this changes nothing material (applyRules already filled the role table with the game's numbers;
game AI 2.3-3.0, pool 5.8-6.5 lost per win, within the noise of one fight per opponent, about +/-1.5). On new units
it gained little (1.9 -> 2.1 in a row). After-action reports on the two sets that lost their first fight (48 and
50 melee of 50): our melee stood next to an enemy without swinging 70% of the time (busy peeling / answering for
an out-of-reach target). `weaponsFree` (a melee unit fights an enemy in reach when its own target is out of reach):
the melee fight goes from lost 50-9 to won 8-0 (still 42 lost); tune 1-10: 2.3 in a row, worst 0 -> 1; today's
units: game AI 2.3, pool 5.9. Pattern: wins in a row fall with the melee share (mostly artillery 2-6, 22-35 melee
2-3, 48-50 melee 1): our edge comes from artillery and lob dodging; armies without much artillery get a fair fight.

## Without artillery (2026-10-03): 20 melee / 30 shooters on both sides

Baseline elite-fast: vs game AI 17/20 won, 23.0 lost per win; vs pool 14/19, 27.6 (with artillery: about 2-3 and 5).
- `meleeFocus` (swing at the enemy in reach with the least health left after our swings in flight): 22.8, no gain;
  kept off.
- `saveWounded` 0.3 (below 30% health, back away toward our side; in a gauntlet it is healed for the next fight):
  vs game AI 20/20, 13.8; vs pool lost per win 9.4 (formation AIs: line 22 -> 5, crescent 22 -> 4) but 10/19 won
  (chargers swarm / loose free / berserk / storm turn narrow wins into losses). Only when no faster enemy threatens
  it: 21.0 / 18.1; only when no faster enemy targets it: 17.9 / 15.3; both dropped. With artillery: game AI 2.3
  (2.3), pool 4.7 (5.9). Adopted (0.3) in elite and elite-fast.
- Chargers beat us without artillery with or without it (alone, wolfpack 0-16, 0-20). The shooter duel decides:
  ours fire as often as theirs (45 vs 36%, 39 vs 39% of the time), lanes blocked by our own units about the same,
  but they have more shooters in reach (38k vs 30k, 47k vs 33k unit-ticks; vs line we have more, 42k vs 36k, and
  win 28-0): a charger walks every shooter up to its target, our formation keeps ranks and flanks out of reach.
  Look-ahead off (16/19, 28.8) or a sticky plan (27.2) do not change it.
- Firing line (a shooter with no enemy in reach but one within 120 px more steps up until it is in reach): vs alone
  ours in reach 30.2k -> 31.8k, theirs 38.1k -> 45.4k, lost 0-26 (was 0-16); removed. With equal reach, stepping up
  puts us in their reach as much as them in ours: only geometry (a concave line around their group, or one flank
  so their far side is out of reach) gives more of ours on each of theirs.
- Which plan beats a charger (each plan held all fight, no artillery, margin vs alone / wolfpack / swarm): engage
  +2 / -9 / +39, siege +31 / -33 / +3, push +27 / -12 / -21, spread -18 / +15 / -6, surround -32 / -29 / -28 (worst
  vs all three); our look-ahead -16 / -20 / +5. A plan that beats each exists; the 3 s look-ahead does not find it.
  Pool without artillery: surround out of elite's always-tried list 10 -> 13 of 19 won, margin +21.5 -> +28.6; a
  6 s look-ahead 13 won, +30.3; both 13, +24.5 (not additive, within noise). Surround dropped from the list (the
  finishing plans still have it); with artillery pool 5.2 lost per win, vs player unchanged.
- saveWounded cost kills vs the player (kite 13/16 -> 7/16): the wounded now keep fighting when finishing (their
  last 2, or 4 to 1), so always vs a lone player. Back to kite 13/16, press 11/16, orbit 2/16; no artillery vs game
  AI 14.5 lost per win.

## Commanding by hand (2026-10-03): command.js, COMMAND_LESSONS.md

`node command.js '<options>' <dir>` pauses a fight, writes the state (groups, enemy guns casting, lobs in the air,
deaths) and a picture, and waits for an orders file: goals the AI carries out with its own handling (place,
engage, release, plan) or unit orders (which replace its handling and played worse). No artillery, seed 30007:
won by hand vs alone 30-0 (the AI alone lost 0-16) and vs wolfpack 25-0; vs swarm the hand game exposed a rout
(save-the-wounded sending a mostly wounded army into a corner), fixed: wounded back off only while fewer than half
of us are wounded. The principle behind the wins (strike enemies cut off from their shooters' cover, never follow
into it) as an automatic commander (`autoCmd`): on fresh seeds no gain (29/36 won with and without), so it is off.
`learn_plans.js` (situation -> plan by nearest neighbours) was never evaluated: its collection run hit the 60 min
limit. Universal test now (elite-fast, tune 1-10): 2.4 in a row, >=4 in 30% of sets.
Suite after this batch (elite: unit features, weapons-free melee, save-the-wounded with its finishing and rout
fixes, surround out of the look-ahead list; commander off), seeds 30000+, 48 per line: 7 of 7 PASS. Fairness
-0.8 +/- 1.0; vs game AI 100%, +46.3; lost per won fight 4.9 (game AI 3.7, pool 6.4; previous suite 4.5 = 3.5 /
5.6); vs pool 100%, +43.6; vs player kite / press / orbit 75 / 71 / 17% (game AI 23 / 38 / 2).

## Architecture audit (2026-10-03): copies leaked into the real battle
`fork` shared by reference what a copy changes in place: the player's limbs and manual cast (playerBrain), the
shots a unit has rolled a dash against (u._rolled) and the commander goals (pack.cmd). A look-ahead copy playing
the player advanced or interrupted the REAL player's casts, which helped us: after the fix, vs player kite 13 ->
10 of 16, press 11 -> 6 of 16, orbit 2 -> 1 of 16 (seeds 30000-30015). The game AI's player numbers never used
copies. Our vs-player results since the look-ahead was introduced were inflated by this.
Also checked: the shaman's lob (data/monster_abilities.json astelia:arc_bolt) targets a lawful actor, so its
release re-checks the target, as the sim does; the "point locks at windup start" rule (ENEMY_DESIGN.md:546,
COMBAT_DESIGN.md:80-81) is for point / area deliveries; the sim's header comment cited it wrongly (fixed).

## Rework, step 0 of PLAN_TACTICAL_COMBOS.md (2026-10-03)
Suite on the code before the rework (copy-leak fix included, elite, seeds 30000+, 48 per line): 7 of 7 PASS. Fairness
-0.8 +/- 1.0; vs game AI 100%, +46.3; lost per won fight 4.9 (game AI 3.7, pool 6.4); vs pool 100%, +43.6; vs player
kite / press / orbit 56 / 46 / 6% (game AI 23 / 38 / 2). The earlier 7/7 therefore survives the fix.

What changed in formation_sim.js:
- One writer per decision. A tick is: packs plan and propose (slots, goals, `u.assigned`) -> reflexes (dash, block) ->
  every unit `decide()`s (the only writer of `u.target`, `u.state`, `u.dec` = its one movement goal) -> fire control
  (`castPermit`: holdFire, waves) -> the rules start casts (`gamePrep`, rules only) -> artillery planner -> every unit
  `act()`s (walk, release). Casts now start on this tick's target and reach, not last tick's. The artillery
  follow-up of cut-off enemies moved from the planner into the melee decision. Exception: the sandbox rules'
  abilities (off under game rules) still name their own target.
- One plan source (`planFrom`: order, forced, look-ahead, rules) and one switching rule (`planSwitchable`, `setPlan`).
- One `finishing()` (was three copies). `autoCmd` and `learn_plans.js` removed.
- `fork` copies everything a step changes in place and remaps every unit reference (new: a piercing shot's hit set,
  burn list, `manual.target`, `fireOrder`, skirmish arrivals with their random state). Checked with a scratch script:
  no mutable state shared with the real battle, the real battle unchanged after playing a copy.
- `bench_fingerprint.json` re-recorded (sandbox rules; the tick order changed, all 19 fights differ).

Paired, same seeds 32000+, elite-fast, before -> after (lost per win +/- se; won):
| set | before | after |
|---|---|---|
| vs game AI (40) | 3.63 +/- 0.34, 40/40 | 3.59 +/- 0.56, 39/40 |
| pool (38) | 6.59 +/- 0.77, 37/38 | 4.74 +/- 0.69, 38/38 |
| no artillery vs game AI (20) | 14.55 +/- 1.15, 20/20 | 13.80 +/- 1.29, 20/20 |
| chargers, no artillery (36) | 32.27 +/- 1.62, 22/36 | 30.97 +/- 1.35, 29/36 (margin +6.2 +/- 2.6) |
Universal tune 1-10: 2.4 -> 3.0 in a row (median 3, >=4 in 30% -> 20%, >=8 0% -> 10%): within noise at 10 sets.
Suite after (elite, 48 per line): 7 of 7 PASS. Fairness -0.1 +/- 1.3; vs game AI 100%, +46.9; lost per won fight 3.6
(game AI 3.1, pool 4.3); vs pool 97%, +45.0; vs player kite / press / orbit 52 / 48 / 2% (game AI 21 / 44 / 0).
Reading: no regression. The pool and charger gains are beyond 2 standard errors but unexplained (likely the same-tick
cast start and the copies being faithful); not relied on. Next: step 1, the combo engine with no combos.

## Combo engine, step 1 of PLAN_TACTICAL_COMBOS.md (2026-10-03): the engine, no combos
`formation_sim.js`: `observe()` (features from our side's view: counts by role, centres, nearest gap, their column
shape and speed along it, chase share, wall distance, finishing), the combo director `directorStep()` and the
registry `COMBOS` (combo = data: entry, roles, phase graph with goals / done / abort / min / max, success signal,
cooldown). It speaks only through goals (place / engage / release / plan: `pack.dir.goals`, read by `cmdOf` after the
outside commander's `pack.cmd`), every 0.5 s; selection every 2 s, only between combos; roles locked for the combo's
life; abort / timeout / success all release the units and are logged (`pack.dir.log`, `pack.dir.stats`, and a
briefing line per start and phase change in the event log). Skill `combos`: null = off (default), `[]` = on with no
combo, `['name', ...]` = those may start. Copies keep the director's state but do not run it.
Check: 13 game-rules fights (elite-fast / veteran, with artillery, without, unit set, vs player) give exactly the same
results with `combos: []` as with the director off; a throwaway two-phase combo (release, then engage) started, switched
phase, finished and released as written. No real combo yet. Next: the lure -> cross the T -> envelop chain.

## Chain 2 -> 1 -> 3 (lure, cross the T, envelop): measured, not adopted (2026-10-03)
`COMBOS.tchain` (formation_sim.js): lure (anchor gives ground 200 px per step while a chasing column strings out) ->
cross (hold, `widehold`, facing the column) -> envelop (the outer half of the shooters released, engage on their
nearest 8 melee). Entry: column elongation > 2.2, approaching, 6+ melee, gap 250-700, room behind. No artillery
(20 melee / 30 shooters), chargers = alone, wolfpack, swarm x 12 fights. Elite-fast.
- Development seeds 30300+ (36 fights, off: 26 won, margin +11.4): full chain 25 won, -1.3 +/- 2.2 (28 starts, 0
  success signals: the lure never strung the column out, the trade at the end was about 1.3 : 1, not the 2 : 1 aimed
  for); cross + envelop without the lure 32 won, +4.0 +/- 1.9; envelop alone 28 won, +0.1 +/- 2.0.
- Judging seeds 32000+, cross + envelop vs off (paired): chargers 26 vs 29 won, margin -2.9 +/- 2.2; no artillery vs
  game AI (20) lost per win 13.8 -> 17.8, margin -4.0 +/- 1.2 (it fired in every fight: the armies are columns at the
  start); with artillery vs game AI 36 vs 39 of 40 won, -2.0 +/- 1.4; pool unchanged (+0.3 +/- 0.5).
- Verdict: the development gain was noise (about 2 standard errors on one set, none on fresh seeds) and the combo
  harms where it fires at the start of a fight. Not adopted; `combos` stays null. What this says for the next combos:
  the entry condition must see a real column that has left its shooters behind (cover map, gap between its melee and
  its shooters), not just "elongated and approaching"; a start-of-fight formation march looks the same. The success
  signal never fired, so the phase conditions were never validated: build the scenario harness (fights where it should
  and should not fire) before the next combo.

## Fix, then lob the clump (combo 4): the entry almost never holds, not adopted (2026-10-03)
`COMBOS.fixlob`: entry = 5+ of their melee in contact with ours, a clump of 4+ of theirs inside one blast, none of ours
within a blast + 50 px of it, 3+ guns able to reach it; phases fix (anchor gives 50 px) -> lob. Development seeds
30000+, with artillery, elite-fast, off vs on: vs game AI (40) it never started (0 starts), identical results; pool
(38) 3 starts (2 successes), lost per win 6.13 -> 5.71, margin +0.4 +/- 0.4. The planner (`artilleryVolley`) already
fires on the densest spot, and with artillery we win about 100% at 3.5-6 lost per win, so there is little room, and
the combo's condition is rare. Not adopted; judging seeds not spent. The weak spots are elsewhere: no artillery
(chargers 29/36), and unseen unit sets (universal 3.0 in a row).

## Hand command page (2026-10-03): hand.html + hand_server.js
`node hand_server.js` then http://127.0.0.1:8766/hand.html (own port, localhost only; a plain `python3 -m http.server 8765` for gauntlet.html can run beside it, but it cannot take commands). The AI (elite-fast) plays everything; you pause, select our
units (drag box, click, 1/2/3 = melee / shooters / guns, A = all), and order them: right-click ground = move (they fight
what is in reach on the way), right-click an enemy = attack it, shift + right-click = retreat, H = hold 6 s, C = give
them back to the AI now. A unit returns to the AI by itself when its order is done (arrived, target dead, time up:
`decideOrder`, logged in `w.orderEvents`). Every order, completion and a 2 s timeline are saved to `hand_logs/` at the
end of the fight (or with Save log). Unit orders replace the AI's handling for that unit only; the formation, anchor and
the other units are untouched (the thing the goal-level `command.js` could not do).
Abilities and kinds on the page (same day): the "abilities" box turns on the old sandbox abilities (option
`sandboxAbilities`, on top of the game's numbers, both armies; results with it on are a separate setting from the frozen
game rules): melee charge (Q) and barrier (W, blocks 80% of shots for 3 s), shooters aimed shot (E) and jump back (R),
guns barrage (T) and slow field (Y). A key or button fires it for the selected units that have it, at the enemy under the
mouse (else each unit's nearest; charge needs 50-200 px), sharing the AI's cooldowns; the AI keeps using them on its own.
Select all of a kind: buttons, 1 / 2 / 3 / A, or double-click a unit. Off, fights are identical to before (checked on 13 fights).
Manual abilities (same day): `abilities manual` (default) sets `u.abManual` on our units: the AI never fires their
abilities (`ready()` is false for it); only the commander's trigger does. G = the AI may use abilities for the selected
units (white dot), B = manual again. The enemy keeps AI use. Checked headless: manual, our AI used 0 abilities (theirs 128); a hand shield fired on all 13 melee.
