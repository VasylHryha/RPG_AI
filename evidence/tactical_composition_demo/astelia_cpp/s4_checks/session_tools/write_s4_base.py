from pathlib import Path
p=Path('evidence/tactical_composition_demo/astelia_cpp/s3_runner.py')
s=p.read_text().replace("ARMS = ('resonator', 'morale', 'pushpull', 'nearest')", """ARMS = ('resonator', 'morale', 'pushpull', 'nearest')
# Fixed development profiles, never controller tuning knobs.
ELITE_NO_ROLLOUT = {'artyFire': 'plan', 'lockedDodge': True,
    'dodgeShells': 'smart', 'castDodge': True, 'weaponsFree': True,
    'saveWounded': .3, 'artyBattery': True, 'artyRollout': None}
SETTINGS = ('s3_full_pool', 's4_melee10', 's4_full_head', 's4_p23',
            's4_anomaly_novice_line', 's4_anomaly_regular_alone')""")
s=s.replace("'opponent', 'diagnostics'}", "'opponent', 'diagnostics', 'setting', 'trace'}")
s=s.replace("('swapSides', 'diagnostics')", "('swapSides', 'diagnostics', 'trace')")
s=s.replace("    ai = [{}, {}]", """    setting = spec.get('setting', 's3_full_pool')
    if setting not in SETTINGS:
        raise ValueError('unknown development setting')
    if setting == 's4_p23' and opponent not in POOL:
        raise ValueError('P2/P3 requires a doctrine')
    if setting in ('s4_full_head', 's4_melee10') and opponent not in ('novice', 'regular'):
        raise ValueError('head-to-head requires novice or regular')
    if setting == 's4_melee10' and opponent != 'novice':
        raise ValueError('stage A requires novice')
    if setting.startswith('s4_anomaly_') and opponent not in ('novice', 'regular'):
        raise ValueError('anomaly requires a level')
    ai = [{}, {}]""")
s=s.replace("    return {'mode':", """    if setting == 's4_p23':
        ai[1-side]['skills'] = dict(ELITE_NO_ROLLOUT)
        ai[1-side]['lookahead'] = None
    if setting == 's4_anomaly_novice_line':
        if opponent != 'novice':
            raise ValueError('anomaly novice mismatch')
        ai[1-side].update(brain='formation', formation={'preset': 'line'})
    if setting == 's4_anomaly_regular_alone':
        if opponent != 'regular':
            raise ValueError('anomaly regular mismatch')
        ai[1-side].update(brain='alone')
    return {'trace': spec.get('trace', False), 'debug': spec.get('trace', False), 'mode':""")
s=s.replace("'army': {'melee': 10, 'ranged': 30, 'artillery': 10}", "'army': {'melee': 10, 'ranged': 0 if setting == 's4_melee10' else 30, 'artillery': 0 if setting == 's4_melee10' else 10}")
p.write_text(s)
