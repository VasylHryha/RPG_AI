"""DEVELOPMENT record, not the experiment. Rules fixed before it ran (see the conversation record and SPECIFICATION.md):

A. Task meaningful: scripted teacher vs rush in [0.65, 0.95]; teacher vs kiter in [0.40, 0.85]; rush baseline at least 0.20 below the
   teacher against each opponent; rush vs rush in [0.40, 0.60]; random vs rush <= 0.20. (win score on seen mixes, 100 episodes per cell)
B. Piece size: smallest hidden size in {16, 32, 64} where, on held-out states, AIM top-1 >= 0.97, MOVE median angle <= 5 degrees and
   ABILITY balanced accuracy >= 0.95 (3,000 rows per piece, 4,000 steps); else 64.
C. Added after calibration run 1 (kept as dev_calibration_run1_burst_too_rare.json): the burst fired in 1.1% of mage states, so the ABILITY
   piece had no job. Rule: the teacher's burst must fire in 10% to 60% of mage states. One adjustment allowed: blast radius 2.0 -> 3.0 and
   burst range 4.5 -> 5.0. Calibration run 2 uses the adjusted sandbox and is the last.
D. Correction of rule C (my error, found after run 2, kept as dev_calibration_run2_burst_still_rare.json): the burst has a 15-tick cooldown, so
   it can fire in at most 1 of 15 mage decisions; the rule must apply to states where the burst is ready, and the piece's rows and fidelity
   use ready-mage states only. The rate was still only 3.9% there, so the teacher's rule gained a finisher clause (also burst when the blast
   hits one enemy at or below 35% health), measured on the task alone at 12.2% of ready-mage states before adoption. Run 3 is final.
Own development entropy (below), separate from the recorded run and the smoke. No composed or one-big controller is evaluated here."""
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
cells = {}
for name, policy_a, opponent in (('teacher_vs_rush', T.teacher_policy, T.rush_policy), ('teacher_vs_kiter', T.teacher_policy, T.kiter_policy),
                                 ('rush_vs_rush', T.rush_policy, T.rush_policy), ('rush_vs_kiter', T.rush_policy, T.kiter_policy),
                                 ('random_vs_rush', T.make_random_policy(rng(9)), T.rush_policy), ('kiter_vs_rush', T.kiter_policy, T.rush_policy)):
    cells[name] = T.win_score(policy_a, T.SEEN_MIXES, opponent, rng(1, len(cells)), 100)
out['win_scores'] = cells
out['seconds_for_600_episodes'] = time.time()-t0
checks = {'teacher_vs_rush_in_0.65_0.95': 0.65 <= cells['teacher_vs_rush'] <= 0.95,
          'teacher_vs_kiter_in_0.40_0.85': 0.40 <= cells['teacher_vs_kiter'] <= 0.85,
          'rush_below_teacher_by_0.20_vs_rush': cells['teacher_vs_rush']-cells['rush_vs_rush'] >= 0.20,
          'rush_below_teacher_by_0.20_vs_kiter': cells['teacher_vs_kiter']-cells['rush_vs_kiter'] >= 0.20,
          'rush_vs_rush_in_0.40_0.60': 0.40 <= cells['rush_vs_rush'] <= 0.60,
          'random_vs_rush_at_most_0.20': cells['random_vs_rush'] <= 0.20}
out['task_checks'] = checks
out['task_ok'] = all(checks.values())
print('A', {k: round(v, 3) for k, v in cells.items()}, '\n  ', checks, '\n   %.1f s for 600 episodes' % out['seconds_for_600_episodes'])

pool = T.collect(rng(2), 320, T.SEEN_MIXES)
lab = T.labels(pool)
test = T.collect(rng(3), 60, T.SEEN_MIXES)
tlab = T.labels(test)
out['rows'] = {'train_states': len(pool['own']), 'test_states': len(test['own'])}
data = T.piece_datasets(pool, lab, 3000, 3000, 3000, rng(4))
sizes = {}
chosen = None
for hidden in (16, 32, 64):
    models = {}
    for j, (name, d_in, d_out) in enumerate((('AIM', T.AIM_DIM, 1), ('MOVE', T.MOVE_DIM, 2), ('ABILITY', T.ABILITY_DIM, 1))):
        X, Y = data[name]
        models[name] = T.MLP(d_in, hidden, d_out, rng(5, hidden, j)).fit(X, Y, rng(6, hidden, j), 4000)
    f = T.fidelity(models, test, tlab)
    ok = f['aim_top1'] >= 0.97 and f['move_median_angle_deg'] <= 5.0 and f['ability_balanced_accuracy'] >= 0.95
    sizes[hidden] = {**f, 'meets_rule': bool(ok)}
    print('B hidden', hidden, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in f.items()}, ok)
    if ok and chosen is None:
        chosen = hidden
out['piece_sizes'] = sizes
out['ability_positive_rate_among_ready_mage_states_in_0.10_0.60'] = bool(0.10 <= sizes[16]['ability_positive_rate'] <= 0.60)
print('C ability positive rate (ready mage states)', sizes[16]['ability_positive_rate'], out['ability_positive_rate_among_ready_mage_states_in_0.10_0.60'])
out['chosen_hidden'] = chosen if chosen is not None else 64
total = sum(T.MLP.parameter_count(d, out['chosen_hidden'], o) for d, o in ((T.AIM_DIM, 1), (T.MOVE_DIM, 2), (T.ABILITY_DIM, 1)))
mono_hidden = min(range(8, 400), key=lambda h: abs(T.MLP.parameter_count(T.MONO_IN, h, T.MONO_OUT)-total))
out['pieces_total_parameters'] = total
out['monolith_hidden_for_equal_parameters'] = mono_hidden
out['monolith_parameters'] = T.MLP.parameter_count(T.MONO_IN, mono_hidden, T.MONO_OUT)
print('chosen piece hidden', out['chosen_hidden'], 'pieces params', total, 'monolith hidden', mono_hidden, out['monolith_parameters'])
(HERE/'dev_calibration.json').write_text(json.dumps(out, indent=1, sort_keys=True))
