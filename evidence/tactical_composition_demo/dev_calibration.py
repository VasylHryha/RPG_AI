"""DEVELOPMENT record for the Stage 0 design (AIM + MOVE), not the experiment. Rules fixed before it ran:

A. Task meaningful (win score of our team; seen mixes, 300 episodes per gap-check cell for power (100 was too noisy for a 0.20 margin, found when a
   rerun missed by 0.011 with the task unchanged), the symmetry check 500, random 100):
   teacher vs rush in [0.65, 0.95]; teacher vs kiter in [0.40, 0.85]; rush baseline at least 0.20 below the teacher against each opponent;
   rush vs rush in [0.43, 0.57]; random vs rush <= 0.20.
   Unseen type (our team from the skirmisher mixes, 300 episodes): teacher vs rush in [0.55, 0.95]; rush baseline at least 0.15 below
   the teacher against each opponent.
B. Piece size: smallest hidden size in {16, 32, 64} where, on held-out states, AIM top-1 >= 0.97, MOVE median angle <= 5 degrees and MOVE
   hold agreement >= 0.90 (3,000 rows per piece, 4,000 steps, batch 128); else 64. The one big controller gets the hidden size whose parameter
   count is closest to the pieces' total; scaled rows use 2x and 4x that width with 4x and 16x the data.
Own development entropy (below), separate from the recorded run and the smoke. No composed or one-big controller is evaluated here.
Unseen type revised twice: (1) after the independent review the first skirmisher (speed 0.45, outside the trained range, an input the pieces never
see) was replaced by an unseen combination of in-range inputs; (2) that version was overpowered (hp 70, cooldown 3: teacher 0.98 against rush, rush
against rush 0.77, no headroom) and became an archer with a short preferred range (hp 60, range 6.0, damage 7, cooldown 4, preferred range 2.5,
speed 0.30). Earlier calibration files are kept in history_ability_attempt/.
History: an earlier design with the mage's burst piece (ABILITY) is kept in history_ability_attempt/; its calibration found the burst
decision too rare to teach fairly, and Stage 0 was narrowed to AIM + MOVE (ABILITY becomes Stage 0b)."""
import json
import secrets
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402

entropy = secrets.randbits(96)
rng = lambda *key: np.random.default_rng(np.random.SeedSequence([entropy, *key]))
out = {'dev_entropy': entropy}
t0 = time.time()
cells, k = {}, 0
for name, policy_a, opponent, mixes, episodes in (
        ('teacher_vs_rush', T.teacher_policy, T.rush_policy, T.SEEN_MIXES, 300), ('teacher_vs_kiter', T.teacher_policy, T.kiter_policy, T.SEEN_MIXES, 300),
        ('rush_vs_rush', T.rush_policy, T.rush_policy, T.SEEN_MIXES, 500), ('rush_vs_kiter', T.rush_policy, T.kiter_policy, T.SEEN_MIXES, 300),
        ('random_vs_rush', T.make_random_policy(rng(9)), T.rush_policy, T.SEEN_MIXES, 100),
        ('unseen_teacher_vs_rush', T.teacher_policy, T.rush_policy, T.UNSEEN_MIXES, 300), ('unseen_teacher_vs_kiter', T.teacher_policy, T.kiter_policy, T.UNSEEN_MIXES, 300),
        ('unseen_rush_vs_rush', T.rush_policy, T.rush_policy, T.UNSEEN_MIXES, 300), ('unseen_rush_vs_kiter', T.rush_policy, T.kiter_policy, T.UNSEEN_MIXES, 300)):
    k += 1
    cells[name] = T.win_score(policy_a, mixes, opponent, rng(1, k), episodes)
out['win_scores'] = cells
out['seconds'] = time.time()-t0
checks = {'teacher_vs_rush_in_0.65_0.95': 0.65 <= cells['teacher_vs_rush'] <= 0.95,
          'teacher_vs_kiter_in_0.40_0.85': 0.40 <= cells['teacher_vs_kiter'] <= 0.85,
          'rush_below_teacher_by_0.20_vs_rush': cells['teacher_vs_rush']-cells['rush_vs_rush'] >= 0.20,
          'rush_below_teacher_by_0.20_vs_kiter': cells['teacher_vs_kiter']-cells['rush_vs_kiter'] >= 0.20,
          'rush_vs_rush_in_0.43_0.57': 0.43 <= cells['rush_vs_rush'] <= 0.57,
          'random_vs_rush_at_most_0.20': cells['random_vs_rush'] <= 0.20,
          'unseen_teacher_vs_rush_in_0.55_0.95': 0.55 <= cells['unseen_teacher_vs_rush'] <= 0.95,
          'unseen_rush_below_teacher_by_0.15_vs_rush': cells['unseen_teacher_vs_rush']-cells['unseen_rush_vs_rush'] >= 0.15,
          'unseen_rush_below_teacher_by_0.15_vs_kiter': cells['unseen_teacher_vs_kiter']-cells['unseen_rush_vs_kiter'] >= 0.15}
out['task_checks'], out['task_ok'] = checks, all(checks.values())
print('A', {n: round(v, 3) for n, v in cells.items()}, '\n  failed:', [n for n, ok in checks.items() if not ok], '\n  %.1f s' % out['seconds'])

pool = T.collect(rng(2), 240, T.SEEN_MIXES)
lab = T.labels(pool)
test = T.collect(rng(3), 60, T.SEEN_MIXES)
tlab = T.labels(test)
out['rows'] = {'train_states': len(pool['own']), 'test_states': len(test['own'])}
data = T.piece_datasets(pool, lab, 3000, 3000, rng(4))
sizes, chosen = {}, None
for hidden in (16, 32, 64):
    models = {name: T.MLP(d_in, hidden, d_out, rng(5, hidden, j)).fit(*data[name], rng(6, hidden, j), 4000)
              for j, (name, d_in, d_out) in enumerate((('AIM', T.AIM_DIM, 1), ('MOVE', T.MOVE_DIM, 2)))}
    f = T.fidelity(models, test, tlab)
    ok = f['aim_top1'] >= 0.97 and f['move_median_angle_deg'] <= 5.0 and f['move_hold_agreement'] >= 0.90
    sizes[hidden] = {**f, 'meets_rule': bool(ok)}
    print('B hidden', hidden, {n: (round(v, 3) if isinstance(v, float) else v) for n, v in f.items()}, ok)
    chosen = hidden if (ok and chosen is None) else chosen
out['piece_sizes'] = sizes
out['chosen_hidden'] = chosen if chosen is not None else 64
total = sum(T.MLP.parameter_count(d, out['chosen_hidden'], o) for d, o in ((T.AIM_DIM, 1), (T.MOVE_DIM, 2)))
mono = min(range(4, 400), key=lambda h: abs(T.MLP.parameter_count(T.MONO_IN, h, T.MONO_OUT)-total))
out['pieces_total_parameters'], out['monolith_hidden_equal_parameters'] = total, mono
out['monolith_scaled_hidden'] = [mono, 2*mono, 4*mono]
out['monolith_parameters'] = [T.MLP.parameter_count(T.MONO_IN, h, T.MONO_OUT) for h in out['monolith_scaled_hidden']]
print('chosen piece hidden', out['chosen_hidden'], 'pieces params', total, 'monolith hidden', out['monolith_scaled_hidden'], out['monolith_parameters'])
(HERE/'dev_calibration.json').write_text(json.dumps(out, indent=1, sort_keys=True))
