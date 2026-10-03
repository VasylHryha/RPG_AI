"""Change-cost and fidelity metrics on explicit populations.

Repairs against the recorded `tactics.change_metrics` (which stays frozen):
- every reported agreement and step quantity is computed on states with more than one living enemy (single-enemy states agree trivially);
- the step judged against the best-matching tied-best enemy accepts a hold when any tied-best enemy's label is a hold (a correct hold on an
  in-band tied enemy is no longer scored as an angle error against the other enemy);
- a hold where every tied-best label requires a move counts as 90 degrees (no direction), and is also counted separately.
"""
import numpy as np

from . import PARENT  # noqa: F401  (puts the tactical folder on sys.path)

HOLD = 0.5   # the sandbox's own hold threshold (tactics.move_metrics)


def _tactics(T):
    if T is not None:
        return T
    import tactics
    return tactics


def multi_enemy(pool):
    return np.array([(e[:, 0] > 0).sum() > 1 for e in pool['enemies']])


def tied_best(pool, lab):
    alive = pool['enemies'][:, :, 0] > 0
    scores = np.where(alive, lab['scores'], -np.inf)
    return (scores >= scores.max(1)[:, None]-1e-9) & alive, alive


def agreement(chosen, pool, lab):
    """Tie-aware and strict agreement of the chosen enemy with the teacher's best, with the chance level of a uniform living pick."""
    n = len(pool['own'])
    tied, alive = tied_best(pool, lab)
    multi = multi_enemy(pool)
    chosen = np.asarray(chosen)
    hit = tied[np.arange(n), chosen]
    chance = tied.sum(1)/np.maximum(alive.sum(1), 1)
    a, c = float(np.mean(hit[multi])), float(np.mean(chance[multi]))
    return {'n_multi': int(multi.sum()), 'n_all': n, 'agree_tie_aware_multi': a, 'agree_strict_multi': float(np.mean((chosen == lab['target'])[multi])),
            'chance_tie_aware_multi': c, 'agree_corrected_multi': (a-c)/(1.0-c), 'tie_share_multi': float(np.mean((tied.sum(1) > 1)[multi]))}


def step_toward_chosen(pred_step, chosen, pool, T=None):
    """Angle where the teacher would move and hold agreement where it would hold, judged toward the enemy the controller chose (multi-enemy states)."""
    T = _tactics(T)
    multi = multi_enemy(pool)
    idx = np.flatnonzero(multi)
    rel = np.array([pool['enemies'][k][chosen[k], 1:3] for k in idx])
    label = np.array([T.teacher_move(rel[i], pool['own'][k][4]) for i, k in enumerate(idx)])
    return {'step_chosen_'+k: v for k, v in T.move_metrics(np.asarray(pred_step)[idx], label, rel).items()}


def step_tiebest(pred_step, pool, lab, T=None):
    """Step against the best-matching tied-best enemy (a step head cannot know which tied enemy the score head will pick), multi-enemy states."""
    T = _tactics(T)
    tied, _ = tied_best(pool, lab)
    angles, hold_ok, hold_n, wrong_hold = [], 0, 0, 0
    for k in np.flatnonzero(multi_enemy(pool)):
        labels = [T.teacher_move(pool['enemies'][k][j, 1:3], pool['own'][k][4]) for j in np.flatnonzero(tied[k])]
        moving = [v for v in labels if float(np.hypot(*v)) > HOLD]
        holds = len(moving) < len(labels)
        p = np.asarray(pred_step[k])
        predicts_hold = float(np.hypot(*p)) < HOLD
        if holds:
            hold_n += 1
            hold_ok += bool(predicts_hold)
        if predicts_hold and holds:
            angles.append(0.0)
        elif moving and predicts_hold:
            angles.append(90.0)
            wrong_hold += 1
        elif moving:
            angles.append(min(float(np.degrees(np.arccos(np.clip(float(p@v)/(np.hypot(*p)*np.hypot(*v)+1e-9), -1, 1)))) for v in moving))
    out = {'step_tiebest_n': len(angles), 'step_tiebest_wrong_hold_share': float(wrong_hold/len(angles)) if angles else None,
           'step_tiebest_hold_agreement': float(hold_ok/hold_n) if hold_n else None}
    if angles:
        out['step_tiebest_median_angle_deg'], out['step_tiebest_p90_angle_deg'] = float(np.median(angles)), float(np.quantile(angles, 0.9))
    return out


def change_metrics(chosen, pred_step, pool, lab, T=None):
    out = agreement(chosen, pool, lab)
    out.update(step_toward_chosen(pred_step, chosen, pool, T))
    out.update(step_tiebest(pred_step, pool, lab, T))
    return out
