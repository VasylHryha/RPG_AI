"""Fidelity metrics on explicit populations, strata and teachers.

Repairs against the recorded `tactics.change_metrics` (which stays frozen):
- every reported quantity is computed on states with more than one living enemy (single-enemy states agree trivially);
- the registered teacher's movement function is passed explicitly (`teacher_move`), so a changed stepping rule is scored against the NEW rule, never the old one;
- the primary estimand is `joint_action`: the controller's chosen enemy is admissible (tied-best for the registered teacher) AND the step it takes toward that enemy
  matches the teacher's step for that enemy (hold where the teacher holds, a move within an angle tolerance where it moves). No forgiving tie-set is involved;
- the forgiving tie-set step diagnostic (`step_tiebest`) scores EVERY eligible state: a wrong hold, and a wrong move where the teacher holds, each count as 90 degrees
  (no valid direction) and are reported separately;
- undefined populations stop the computation (ValueError) instead of returning silent values: empty multi-enemy population, a chosen enemy that is not alive,
  non-finite input. A chance level of 1 makes the chance-corrected agreement None.
"""
import numpy as np

from . import PARENT  # noqa: F401  (puts the tactical folder on sys.path)

HOLD = 0.5          # the sandbox's own hold threshold (tactics.move_metrics)
ANGLE_OK_DEG = 10.0  # registered step tolerance for the joint action criterion
MIN_STRATUM = 30    # a stratum rate is reported only from at least this many states


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


def _validate(chosen, pred_step, pool):
    chosen = np.asarray(chosen)
    if len(chosen) != len(pool['own']) or (pred_step is not None and len(pred_step) != len(pool['own'])):
        raise ValueError('chosen, prediction and pool must describe the same states')
    if not np.isfinite(pool['own']).all() or not np.isfinite(pool['enemies']).all() or (pred_step is not None and not np.isfinite(np.asarray(pred_step, float)).all()):
        raise ValueError('non-finite input')
    alive = pool['enemies'][:, :, 0] > 0
    if not alive[np.arange(len(chosen)), chosen].all():
        raise ValueError('a chosen enemy is not alive: the selection is invalid')
    multi = multi_enemy(pool)
    if not multi.any():
        raise ValueError('no multi-enemy state: the primary population is empty')
    return chosen, multi


def agreement(chosen, pool, lab):
    """Tie-aware and strict agreement of the chosen enemy with the teacher's best, with the chance level of a uniform living pick."""
    chosen, multi = _validate(chosen, None, pool)
    n = len(pool['own'])
    tied, alive = tied_best(pool, lab)
    hit = tied[np.arange(n), chosen]
    chance = tied.sum(1)/np.maximum(alive.sum(1), 1)
    a, c = float(np.mean(hit[multi])), float(np.mean(chance[multi]))
    return {'n_multi': int(multi.sum()), 'n_all': n, 'agree_tie_aware_multi': a, 'agree_strict_multi': float(np.mean((chosen == lab['target'])[multi])),
            'chance_tie_aware_multi': c, 'agree_corrected_multi': None if c >= 1.0-1e-12 else (a-c)/(1.0-c),
            'tie_share_multi': float(np.mean((tied.sum(1) > 1)[multi]))}


def _angle(p, v):
    return float(np.degrees(np.arccos(np.clip(float(p@v)/(np.hypot(*p)*np.hypot(*v)+1e-9), -1, 1))))


def joint_action(chosen, pred_step, pool, lab, teacher_move=None, angle_deg=ANGLE_OK_DEG, min_stratum=MIN_STRATUM):
    """The primary estimand. A multi-enemy state succeeds when the chosen enemy is tied-best for the registered teacher AND the predicted step matches the
    teacher's step toward THAT enemy: a hold (|step| < 0.5) where the teacher holds, otherwise a move (|step| >= 0.5) within `angle_deg` of the teacher's step.
    `lab` must hold the registered teacher's scores and the teacher's own step toward its own target (`lab['move']`), which defines three strata independent of the
    controller: hold, moving, back-off (moving with the step pointing away from the target). `teacher_move(rel, pref)` is the registered movement rule."""
    T = _tactics(None)
    move_fn = T.teacher_move if teacher_move is None else teacher_move
    chosen, multi = _validate(chosen, pred_step, pool)
    pred = np.asarray(pred_step, float)
    tied, _ = tied_best(pool, lab)
    n_idx = np.flatnonzero(multi)
    ok_target = np.array([bool(tied[k, chosen[k]]) for k in n_idx])
    ok_step, angles = np.zeros(len(n_idx), bool), []
    for i, k in enumerate(n_idx):
        rel = pool['enemies'][k][chosen[k], 1:3]
        v = move_fn(rel, pool['own'][k][4])
        p = pred[k]
        if float(np.hypot(*v)) < HOLD:
            ok_step[i] = float(np.hypot(*p)) < HOLD
        else:
            ang = _angle(p, v) if float(np.hypot(*p)) >= HOLD else 90.0
            angles.append(ang)
            ok_step[i] = float(np.hypot(*p)) >= HOLD and ang <= angle_deg
    success = ok_target & ok_step
    truth = np.asarray(lab['move'])[n_idx]
    rel_t = np.array([pool['enemies'][k][lab['target'][k], 1:3] for k in n_idx])
    moving = np.hypot(truth[:, 0], truth[:, 1]) > HOLD
    strata = {'hold': ~moving, 'moving': moving, 'backoff': moving & ((truth*rel_t).sum(1) < 0)}
    out = {'n_multi': int(len(n_idx)), 'a_joint': float(success.mean()), 'a_target_admissible': float(ok_target.mean()),
           'a_step_given_admissible': float(ok_step[ok_target].mean()) if ok_target.any() else None,
           'step_angle_median_moving_deg': float(np.median(angles)) if angles else None}
    for name, mask in strata.items():
        out['n_stratum_'+name] = int(mask.sum())
        out['a_joint_stratum_'+name] = float(success[mask].mean()) if mask.sum() >= min_stratum else None
    out['strata_adequate'] = all(out['a_joint_stratum_'+s] is not None for s in strata)
    return out


def step_toward_chosen(pred_step, chosen, pool, T=None, teacher_move=None):
    """Angle where the teacher would move and hold agreement where it would hold, judged toward the enemy the controller chose (multi-enemy states)."""
    T = _tactics(T)
    move_fn = T.teacher_move if teacher_move is None else teacher_move
    chosen, multi = _validate(chosen, pred_step, pool)
    idx = np.flatnonzero(multi)
    rel = np.array([pool['enemies'][k][chosen[k], 1:3] for k in idx])
    label = np.array([move_fn(rel[i], pool['own'][k][4]) for i, k in enumerate(idx)])
    return {'step_chosen_'+k: v for k, v in T.move_metrics(np.asarray(pred_step)[idx], label, rel).items()}


def step_tiebest(pred_step, pool, lab, T=None, teacher_move=None):
    """Forgiving diagnostic: the step against the best-matching tied-best enemy (a step head cannot know which tied enemy the score head will pick),
    multi-enemy states. EVERY eligible state is scored: a hold where a move is required, and a move where only holds are required, count as 90 degrees."""
    T = _tactics(T)
    move_fn = T.teacher_move if teacher_move is None else teacher_move
    tied, _ = tied_best(pool, lab)
    multi = multi_enemy(pool)
    if not multi.any():
        raise ValueError('no multi-enemy state: the primary population is empty')
    angles, hold_ok, hold_n, wrong_hold, wrong_move = [], 0, 0, 0, 0
    for k in np.flatnonzero(multi):
        labels = [move_fn(pool['enemies'][k][j, 1:3], pool['own'][k][4]) for j in np.flatnonzero(tied[k])]
        moving = [v for v in labels if float(np.hypot(*v)) > HOLD]
        holds = len(moving) < len(labels)
        p = np.asarray(pred_step[k], float)
        predicts_hold = float(np.hypot(*p)) < HOLD
        if holds:
            hold_n += 1
            hold_ok += bool(predicts_hold)
        if predicts_hold and holds:
            angles.append(0.0)
        elif predicts_hold:                 # a move was required (no tied label holds)
            angles.append(90.0)
            wrong_hold += 1
        elif moving:
            angles.append(min(_angle(p, v) for v in moving))
        else:                               # only holds were acceptable and the step moves
            angles.append(90.0)
            wrong_move += 1
    n = len(angles)
    return {'step_tiebest_n': n, 'step_tiebest_wrong_hold_share': wrong_hold/n, 'step_tiebest_wrong_move_share': wrong_move/n,
            'step_tiebest_hold_agreement': float(hold_ok/hold_n) if hold_n else None,
            'step_tiebest_median_angle_deg': float(np.median(angles)), 'step_tiebest_p90_angle_deg': float(np.quantile(angles, 0.9))}


def change_metrics(chosen, pred_step, pool, lab, T=None, teacher_move=None):
    out = agreement(chosen, pool, lab)
    out.update(joint_action(chosen, pred_step, pool, lab, teacher_move))
    out.update(step_toward_chosen(pred_step, chosen, pool, T, teacher_move))
    out.update(step_tiebest(pred_step, pool, lab, T, teacher_move))
    return out
