"""Dormant section-10 orchestration; this module never starts a run on import.

Only a later owner-authorized session may call execute_arm. No development
execution or 200-episode projection is part of this delivery. Calibration must
already be frozen and the follow-up must have independent Claude review.
"""
from .run import Run
from .readouts import seed_unit, aggregate


def execute_arm(seeds, frozen_rows, reward=False, *, library=None):
    """Eight seeds x 2000 episodes and paired controls, for future authorization.

    Exceptions preserve both partial reports and produce INVALID. Frozen usable
    calibration is passed identically into the intact and control policies.
    """
    if len(seeds) != 8 or len(set(seeds)) != 8:
        raise ValueError('exactly eight independent medium seeds required')
    if not any(row.usable for row in frozen_rows.values()):
        return {'readouts': {k: 'INVALID' for k in ('G0', "G0'", 'G1', 'G1c', 'G5')},
                'reason': 'zero usable tasks', 'runs': []}
    reports, units = [], []
    for seed in seeds:
        intact = Run(seed, frozen_rows, reward, library=library)
        control = Run(seed, frozen_rows, reward, control=True, library=intact.library)
        try:
            try:
                for episode in range(2000):
                    intact.episode(episode)
                    control.episode(episode, intact)
                intact.evaluate()
                control.evaluate()
            except (Exception, KeyboardInterrupt) as error:
                intact.invalid = control.invalid = f'{type(error).__name__}: {error}'
            units.append(seed_unit(intact, control))
            reports.append({'intact': intact.report(), 'control': control.report()})
            if intact.invalid:
                break  # retain raw partial runs and return INVALID, never resume silently
        finally:
            intact.close()
            control.close()
    result = aggregate(units)
    result['runs'] = reports
    result['stop_rows'] = {
        'G1_task_blind_failure': not reward and result['readouts']['G1'] == 'FAIL',
        'G0prime_failure': result['readouts']["G0'"] == 'FAIL',
        'invalid': any(v == 'INVALID' for v in result['readouts'].values())}
    result['next_responsible_role'] = 'drafter' if any(result['stop_rows'].values()) else 'owner'
    return result
