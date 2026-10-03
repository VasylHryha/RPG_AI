"""DEVELOPMENT record for revision 2 of the change-cost test, not the experiment. Rule fixed before it ran:

The changed doctrine must be learnable by the piece that has to learn it: an AIM piece trained FROM SCRATCH on 3,000 one-enemy rows of the new doctrine
(Stage 0 recipe: 16 hidden units, batch min(128, n), learning rate 0.003, 170 epochs at the batch actually used, at least 500 and at most 16,000 steps) must
reach median tie-aware agreement >= 0.95 with it on held-out multi-enemy states (5 seeds). The same measurement is recorded for every row count in the revision's grid, for the equal-size
big controller trained from scratch (information only), and for the first revision's fine-tuning protocol at 3,000 rows (information only: it stalled at 0.84
to 0.88 in the recorded first revision). Added after the independent review of revision 2: the same record also holds chance-corrected agreement, the step angle
judged against the best-matching tied-best enemy, and each design's own pre-change quality, all information only. This is the second run of this record (the
first, agreement only, is kept in history_ability_attempt/); its 0.95 rule had been written down in the first revision's report and a scratch look (0.994) preceded
it, which is stated here because the margin makes no difference. Own development entropy, separate from every recorded run. No comparison between designs is a rule here."""
import json
import secrets
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import copy  # noqa: E402
import tactics as T  # noqa: E402

GRID = [100, 300, 1000, 3000, 6000, 12000]
entropy = secrets.randbits(96)
rng = lambda *key: np.random.default_rng(np.random.SeedSequence([entropy, *key]))


def scratch_steps(n):
    return int(min(16000, max(500, np.ceil(170*n/min(128, n)))))


rows = []
for seed in range(5):
    pool = T.collect(rng(1, seed), 260, T.SEEN_MIXES)
    lab1, lab2 = T.labels(pool), T.labels(pool, T.teacher2_scores)
    test = T.collect(rng(2, seed), 40, T.SEEN_MIXES)
    tl2 = T.labels(test, T.teacher2_scores)
    data = T.piece_datasets(pool, lab1, 3000, 3000, rng(3, seed))
    aim1 = T.MLP(T.AIM_DIM, 16, 1, rng(4, seed, 0)).fit(*data['AIM'], rng(5, seed, 0), 4000, 128, 0.003)
    move = T.MLP(T.MOVE_DIM, 16, 2, rng(4, seed, 1)).fit(*data['MOVE'], rng(5, seed, 1), 4000, 128, 0.003)
    out = {'seed': seed}
    pre = T.change_fidelity_composed(aim1, move, test, T.labels(test))
    out['pre_composed_corrected'], out['pre_composed_step'] = pre['agree_corrected_multi'], pre['step_tiebest_median_angle_deg']
    Xp, Yp = T.mono_dataset(pool, lab1, 6000, rng(14, seed))
    mono1 = T.MLP(T.MONO_IN, 15, T.MONO_OUT, rng(15, seed)).fit(Xp, Yp, rng(16, seed), 8000, 128, 0.003)
    pre_m = T.change_fidelity_mono(mono1, test, T.labels(test))
    out['pre_mono_eq_corrected'], out['pre_mono_eq_step'] = pre_m['agree_corrected_multi'], pre_m['step_tiebest_median_angle_deg']
    for n in GRID:
        X, Y = T.aim_dataset(pool, lab2, n, rng(6, seed, n))
        aim = T.MLP(T.AIM_DIM, 16, 1, rng(7, seed, n)).fit(X, Y, rng(8, seed, n), scratch_steps(n), min(128, n), 0.003)
        fa = T.change_fidelity_composed(aim, move, test, tl2)
        out['aim_scratch_%d' % n], out['aim_scratch_corrected_%d' % n], out['aim_scratch_step_%d' % n] = fa['agree_tie_aware_multi'], fa['agree_corrected_multi'], fa['step_tiebest_median_angle_deg']
        Xm, Ym = T.mono_dataset(pool, lab2, n, rng(9, seed, n))
        mono = T.MLP(T.MONO_IN, 15, T.MONO_OUT, rng(10, seed, n)).fit(Xm, Ym, rng(11, seed, n), scratch_steps(n), min(128, n), 0.003)
        fm = T.change_fidelity_mono(mono, test, tl2)
        out['mono_eq_scratch_%d' % n], out['mono_eq_scratch_corrected_%d' % n], out['mono_eq_scratch_step_%d' % n] = fm['agree_tie_aware_multi'], fm['agree_corrected_multi'], fm['step_tiebest_median_angle_deg']
    X, Y = T.aim_dataset(pool, lab2, 3000, rng(12, seed))
    tuned = copy.deepcopy(aim1).fit(X, Y, rng(13, seed), 2000, 64, 0.002, keep_scaling=True)
    out['aim_finetune_3000'] = T.change_fidelity_composed(tuned, move, test, tl2)['agree_tie_aware_multi']
    rows.append(out)
    print(seed, {k: round(v, 3) for k, v in out.items() if k != 'seed'})
med = {k: float(np.median([r[k] for r in rows])) for k in rows[0] if k != 'seed'}
result = {'dev_entropy': entropy, 'rule': 'median AIM-from-scratch tie-aware agreement at 3,000 rows >= 0.95', 'medians': med,
          'learnable': bool(med['aim_scratch_3000'] >= 0.95), 'rows': rows}
print('medians', {k: round(v, 3) for k, v in med.items()}, '\nlearnable:', result['learnable'])
(HERE/'dev_learnability.json').write_text(json.dumps(result, indent=1, sort_keys=True))
