"""Prospective R4 analysis contracts, independent of any new experimental runner.

This is a tested repair component, not qualification of an experimental model.
R3 recorded settings/results are not reinterpreted. Effects are paired by actual
world/episode identities, and recursive effects use the same complete chains.
"""
import numpy as np

from geomind import c4_detect as D
from geomind import c6_r3_assay as A, c6_r3_protocol as P
from geomind.c6_r4_integrity import finite, ordered_worlds

CONDITIONS = ('intact', 'no_r', 'no_backreaction')
CONTROLS = CONDITIONS[1:]
CHAIN_ENDPOINTS = tuple(f'b_chain_{kind}_vs_{control}_turn{turn}'
    for turn in (1, 2) for kind in ('background_phase', 'later_formation') for control in CONTROLS)
ENDPOINTS = P.ENDPOINTS + CHAIN_ENDPOINTS
PRIMARY_COUNT = 16
STABILITY_KEYS = frozenset(('membership_jaccard', 'shape_cv', 'lock_std', 'freq_change',
    'pattern_change', 'recovery_jaccard', 'recovery_original_to_control',
    'recovery_original_to_kicked', 'recovery_control_to_kicked', 'recovery_pattern_error',
    'state_error_position', 'state_error_size', 'state_error_frequency'))


def closure_valid(effects, settings):
    if effects is None:
        return False
    q = settings['qualification']
    expected_dt = [settings['integration']['dt'] / factor for factor in (1, 2, 4)]
    qualified = A.source_qualifies(effects, settings)
    for direction in ('g_to_m', 'm_to_g'):
        values = effects[direction]
        intact = values['intact_by_dt']
        ablated = values['ablated_by_dt']
        if (len(intact) != 3 or len(ablated) != 3 or values['dt_values'] != expected_dt
                or not finite((intact, ablated))
                or values['intact'] != intact[0] or values['ablated'] != ablated[0]):
            raise ValueError('causal evidence does not match its recorded numerical grids')
        smallest = min(intact)
        if (smallest <= q['causal_floor']
                or max(intact) - smallest > q['causal_numerical_relative_tolerance'] * smallest
                or max(abs(v) for v in ablated) > max(q['vanish_absolute_tolerance'], q['vanish_fraction'] * smallest)):
            qualified = False
    return qualified


def validate_numerics(cell, settings):
    summary = cell['numerics']
    if type(summary.get('passed')) is not bool:
        raise ValueError('numerical gate must be a boolean')
    i, q = settings['integration'], settings['qualification']
    required = {'qualification': i['formation']}
    if cell['qualified']:
        required.update({f'operation/{c}': i.get('exposure', i['formation']) for c in CONDITIONS})
        required.update(probes=i['descriptor'], causality=max(settings['interventions']['gm_window'], settings['interventions']['mg_window']))
        if cell['episodes'] is not None:
            required.update({f'candidates/{c}': i['formation'] + i['recovery'] for c in CONDITIONS})
    checks = summary['checks']
    if not set(required) <= set(checks):
        raise ValueError('numerical check omits a reached assay scope')
    passed = True
    for scope, values in checks.items():
        if scope not in required:
            continue
        if (values['duration'] < required[scope] or values['integration_dt'] != i['dt']
                or values['fine_dt'] != i['dt']/4 or values['fine_replay_dt'] > values['fine_dt']):
            raise ValueError('numerical check does not cover the full scope or independently refined replay')
        for name, tolerance in (
            ('position_error_over_L', q['dt_tolerance']), ('phase_error_rad', q['dt_tolerance']),
            ('native_reference_error', q['native_reference_tolerance']),
            ('equivariance_position_over_L', q['equivariance_tolerance']),
            ('equivariance_phase_rad', q['equivariance_tolerance']),
        ):
            value = values[name]
            if not np.isfinite(value) or value < 0:
                raise ValueError('invalid recorded numerical error')
            passed &= value <= tolerance
    if summary['passed'] != bool(passed):
        raise ValueError('numerical flag differs from the recorded full-scope errors')


def formation_valid(formation, settings):
    """A qualified flag needs a candidate, persistence criteria AND causal paths."""
    if type(formation.get('qualified')) is not bool:
        raise ValueError('formation qualified flag must be a boolean')
    selected = [candidate for candidate in formation['candidates']
                if candidate.get('digest') == formation['selected_digest']]
    if formation['selected_digest'] is None:
        if formation['qualified'] or formation.get('causal') is not None or selected:
            raise ValueError('qualification without a selected candidate')
        return False
    if len(selected) != 1:
        raise ValueError('selected candidate is missing or duplicated')
    candidate = selected[0]
    members = candidate['members']
    if (not members or any(type(i) is not int or i < 0 for i in members)
            or len(set(members)) != len(members)
            or formation.get('selected_members') != members
            or candidate['digest'] != A.member_digest(members)):
        raise ValueError('candidate/member identity mismatch')
    structural = all(D.criteria_checks(candidate['stats'], settings['detector']).values())
    if type(candidate.get('accepted')) is not bool or candidate['accepted'] != structural:
        raise ValueError('candidate acceptance differs from persistence criteria')
    causal = closure_valid(formation.get('causal'), settings)
    valid = structural and causal
    if formation['qualified'] != valid:
        raise ValueError('qualification flag differs from candidate causal evidence')
    return valid


def validate_episodes(cell, settings):
    episodes = cell['episodes']
    if episodes is None:
        return
    if set(episodes) != set(CONDITIONS):
        raise ValueError('missing or extra paired condition')
    expected = settings['episodes']
    for condition in CONDITIONS:
        group = episodes[condition]
        if len(group) != expected:
            raise ValueError('incomplete paired episode inventory')
        for index, episode in enumerate(group):
            if type(episode.get('episode')) is not int or episode['episode'] != index:
                raise ValueError('episode identity/order mismatch')
            if (type(episode.get('persistent_unit')) is not bool
                    or episode['persistent_unit'] != formation_valid(episode['formation'], settings)):
                raise ValueError('episode persistence flag differs from causal qualification')
            counterpart = episodes['intact'][index]
            if not episode.get('candidate_initial_digest') or episode['candidate_initial_digest'] != counterpart['candidate_initial_digest']:
                raise ValueError('paired candidate initial states differ')


def validate_cell(cell, settings):
    if type(cell.get('qualified')) is not bool:
        raise ValueError('turn qualification must be a boolean')
    forms = cell['formation']
    if set(forms) != set(CONDITIONS):
        raise ValueError('missing source control formation')
    for form in forms.values():
        formation_valid(form, settings)
    if cell['qualified'] != forms['intact']['qualified']:
        raise ValueError('turn qualification differs from intact source evidence')
    controls = cell['controls']
    expected_sham = (np.isfinite(controls['sham_source_error'])
        and controls['sham_source_error'] <= settings['qualification']['sham_source_tolerance']
        and controls['sham_outgoing_mask'] == 0.)
    if (type(controls.get('sham_preserved')) is not bool
            or controls['sham_preserved'] != bool(expected_sham)
            or controls['no_r_qualifies'] != forms['no_r']['qualified']):
        raise ValueError('control flags differ from control evidence')
    validate_numerics(cell, settings)
    pub = cell.get('publication')
    if cell['qualified']:
        if (not pub or pub.get('member_digest') != forms['intact']['selected_digest']
                or pub.get('qualification') != forms['intact']['causal'] or not finite(pub)):
            raise ValueError('publication missing, nonfinite or linked to another candidate')
        selected = next(candidate for candidate in forms['intact']['candidates'] if candidate['digest'] == pub['member_digest'])
        if (pub['characteristic_size'] <= 0 or len(pub['effective_position']) != 2
                or set(pub['stability']) != STABILITY_KEYS
                or pub['mode_signature']['collective_frequency'] != selected['stats']['collective_frequency']
                or not 0 <= pub['mode_signature']['coherence'] <= 1
                or len(pub['mode_signature']['phase_offsets_sorted']) != len(selected['members'])
                or any(pub['stability'].get(key) != selected['stats'].get(key) for key in pub['stability'])):
            raise ValueError('invalid candidate-linked publication fields')
        timeline = cell['timeline']
        if (timeline['qualification_completed_at'] < 0
                or not timeline['qualification_snapshot_digest']
                or timeline['treatment_started_at'] < timeline['qualification_completed_at']
                or timeline['qualification_snapshot_digest'] != timeline['treatment_initial_snapshot_digest']):
            raise ValueError('treatment preceded qualification or changed the qualified snapshot')
    elif pub is not None:
        raise ValueError('publication without a qualifying source')
    background = cell['background']
    if background is not None:
        if set(background) != {'before', *CONDITIONS}:
            raise ValueError('background descriptor missing a paired branch')
        for descriptor in background.values():
            if not finite(descriptor) or descriptor['b_phase'] < 0 or descriptor['b_position'] < 0:
                raise ValueError('invalid measured background response')
    validate_episodes(cell, settings)


def chain_problems(row):
    """Check link fields against the actual episode, inputs, and inherited states."""
    if len(row['turns']) != 2:
        return [] if row.get('chain_link') is None else ['link without two turns']
    first, second = row['turns']
    link = row.get('chain_link')
    if link is None:
        return ['two turns without a retained inheritance link']
    if first['episodes'] is None:
        return ['second turn without recorded first-turn episodes']
    episode = first['episodes']['intact'][0]
    if not episode['persistent_unit'] or not episode['formation']['qualified']:
        return ['predefined episode zero did not qualify; continuation cannot be substituted']
    if second['formation']['intact']['selected_digest'] != episode['formation']['selected_digest']:
        return ['next turn source identity differs from the qualified episode-zero unit']
    expected = {
        'first_after': first['bath_after_digest'],
        'second_before': second['inherited_bath_digest'],
        'first_episode_source': episode['candidate_initial_digest'],
        'second_source_input': second['source_input_digest'],
    }
    problems = [name + ' is not bound to its actual record' for name, value in expected.items()
                if not value or link.get(name) != value]
    if expected['first_after'] != expected['second_before']:
        problems.append('next turn did not inherit the preceding bath')
    if expected['first_episode_source'] != expected['second_source_input']:
        problems.append('next source is not predefined episode zero')
    for episode_key, second_key in (
        ('reference_digest', 'qualification_reference_digest'),
        ('prior_digest', 'qualification_prior_digest'),
        ('qualification_flow_digest', 'qualification_flow_digest'),
        ('qualification_bath_after_digest', 'bath_before_digest'),
    ):
        if episode_key not in episode or second_key not in second or episode[episode_key] != second[second_key]:
            problems.append('next turn did not retain episode zero ' + episode_key)
    if link.get('intact_episode_reused') is not True:
        problems.append('episode-zero qualification prefix was restaged')
    return problems


def change_verdict(ci, margin, n, minimum):
    """A registered two-sided CHANGE, with equality and missing quorum inconclusive."""
    if ci is None or n < minimum:
        return 'INCONCLUSIVE'
    if not finite(ci) or len(ci) != 2 or ci[0] > ci[1] or not np.isfinite(margin) or margin < 0:
        raise ValueError('invalid contrast interval or practical margin')
    if ci[0] > margin or ci[1] < -margin:
        return 'PASS'
    if ci[0] > -margin and ci[1] < margin:
        return 'FAIL'
    return 'INCONCLUSIVE'


def cell_valid(cell):
    return bool(cell and cell['qualified'] and cell['controls']['sham_preserved']
                and not cell['controls']['no_r_qualifies'] and cell['numerics']['passed'])


def evaluate(records, settings, expected_world_ids, bootstrap_entropy, source_pin=None):
    """Validated world-paired effects; no file I/O, seeds generated, or model runs."""
    records = ordered_worlds(records, expected_world_ids)
    st = settings['statistics']
    if (not finite(settings) or type(st['bootstrap_resamples']) is not int or st['bootstrap_resamples'] < 1
            or type(st['minimum_qualified_worlds']) is not int or st['minimum_qualified_worlds'] < 1
            or not 0 < st['nominal_ci_level'] < 1 or not 0 < st['primary_ci_level'] < 1
            or st['phase_margin'] < 0 or st['formation_margin'] < 0
            or type(settings['episodes']) is not int or settings['episodes'] < 1
            or not 0 < settings['qualification']['causal_numerical_relative_tolerance'] < 1):
        raise ValueError('invalid registered analysis settings')
    required_level = 1 - (1 - st['nominal_ci_level']) / PRIMARY_COUNT
    if st['primary_ci_level'] < required_level - 1e-12:
        raise ValueError('CI does not cover all sixteen registered primary contrasts')
    for row in records:
        if len(row['turns']) not in (1, 2):
            raise ValueError('invalid reached-turn inventory')
        for cell in row['turns']:
            try:
                validate_cell(cell, settings)
            except (KeyError, TypeError, IndexError) as exc:
                raise ValueError('incomplete or malformed turn evidence') from exc
    n = len(records)
    draws = np.random.default_rng(bootstrap_entropy).integers(0, n, (st['bootstrap_resamples'], n))
    evaluated, not_run, hypotheses = {}, {}, {}
    gates = {'finite_records': True, 'world_inventory': True, 'source_controls': True,
             'numerical_checks': True, 'chain_provenance': True}
    for name in P.ARM_A_ENDPOINTS:
        not_run[name] = {'reason': settings['arm_a']}
    cells = {turn: [row['turns'][turn-1] if len(row['turns']) >= turn else None for row in records]
             for turn in (1, 2)}
    link_issues = {}
    for row in records:
        try:
            link_issues[row['world']] = chain_problems(row)
        except (KeyError, TypeError, IndexError) as exc:
            link_issues[row['world']] = ['missing or malformed continuation evidence: ' + str(exc)]
    gates['chain_provenance'] = not any(link_issues.values())
    complete = [not link_issues[row['world']] and len(row['turns']) == 2
                and all(cell_valid(c) and c['background'] is not None and c['episodes'] is not None
                        for c in row['turns']) for row in records]

    def contrast(turn, control, kind, scope):
        field, margin = ('b_phase', st['phase_margin']) if kind == 'background_phase' else ('persistent_unit', st['formation_margin'])
        values = []
        for index, cell in enumerate(cells[turn]):
            if not cell_valid(cell) or cell['background'] is None or (scope == 'chain' and not complete[index]):
                values.append(np.nan)
            elif kind == 'later_formation' and cell['episodes'] is None:
                values.append(np.nan)
            elif kind == 'background_phase':
                values.append(cell['background']['intact'][field] - cell['background'][control][field])
            else:
                values.append(float(np.mean([e[field] for e in cell['episodes']['intact']]))
                              - float(np.mean([e[field] for e in cell['episodes'][control]])))
        name = f'b_{"chain_" if scope == "chain" else ""}{kind}_vs_{control}_turn{turn}'
        valid = [v for v in values if np.isfinite(v)]
        if not valid:
            not_run[name] = {'reason': 'no qualified paired worlds in this registered scope'}
            return 'INCONCLUSIVE'
        ci = P.interval(values, draws, st['primary_ci_level'])
        verdict = change_verdict(ci, margin, len(valid), st['minimum_qualified_worlds'])
        evaluated[name] = {'value': {'mean': float(np.mean(valid)), 'ci': ci,
            'nominal_ci': P.interval(values, draws, st['nominal_ci_level']),
            'n_worlds': len(valid), 'world_ids': [row['world'] for row, v in zip(records, values) if np.isfinite(v)],
            'per_world': [float(v) if np.isfinite(v) else None for v in values],
            'margin': margin, 'scope': scope, 'direction': 'change'}, 'verdict': verdict}
        return verdict

    chain_verdicts = []
    for turn in (1, 2):
        reached = [c for c in cells[turn] if c is not None]
        qualified = sum(c['qualified'] for c in reached)
        evaluated[f'b_source_qualification_turn{turn}'] = {'value': {'qualified': qualified, 'total_worlds': n}, 'verdict': 'DIAGNOSTIC'}
        sham = all(c['controls']['sham_preserved'] for c in reached)
        no_r = all(not c['controls']['no_r_qualifies'] for c in reached)
        numeric = all(c['numerics']['passed'] for c in reached)
        for name, passed in (('sham_preservation', sham), ('no_r_control', no_r)):
            endpoint = f'b_{name}_turn{turn}'
            if reached:
                evaluated[endpoint] = {'value': {'checked_worlds': len(reached), 'passed': passed}, 'verdict': 'PASS' if passed else 'FAIL'}
            else:
                not_run[endpoint] = {'reason': 'turn not reached'}
        gates['source_controls'] &= sham and no_r
        gates['numerical_checks'] &= numeric
        for scope in ('turn', 'chain'):
            bg = P.claim([contrast(turn, control, 'background_phase', scope) for control in CONTROLS])
            ps = P.claim([contrast(turn, control, 'later_formation', scope) for control in CONTROLS])
            if bg != 'SUPPORTED_WITHIN_SCOPE' and ps == 'SUPPORTED_WITHIN_SCOPE':
                ps = 'INCONCLUSIVE'
            if not sham or not no_r or not numeric:
                bg = ps = 'INCONCLUSIVE'
            if scope == 'turn':
                hypotheses[f'H-BG_turn{turn}'], hypotheses[f'H-PS_turn{turn}'] = bg, ps
            else:
                chain_verdicts.extend((bg, ps))
        for name, field in (('background_position', 'background'), ('before_and_control_formation', 'before_episodes'), ('later_diagnostics', 'episodes')):
            endpoint = f'b_{name}_turn{turn}'
            values = [None if c is None else c[field] for c in cells[turn]]
            if any(v is not None for v in values):
                evaluated[endpoint] = {'value': values, 'verdict': 'DIAGNOSTIC'}
            else:
                not_run[endpoint] = {'reason': 'measurement absent; source or turn did not qualify'}
    hypotheses['H-RBG'] = P.claim(['PASS' if v == 'SUPPORTED_WITHIN_SCOPE' else 'FAIL' if v == 'NOT_SUPPORTED' else 'INCONCLUSIVE' for v in chain_verdicts])
    if (sum(complete) < st['minimum_qualified_worlds'] or not gates['chain_provenance']
            or not gates['source_controls'] or not gates['numerical_checks']):
        hypotheses['H-RBG'] = 'INCONCLUSIVE'
    evaluated['b_chain_yield'] = {'value': {'complete_chains': sum(complete), 'total_worlds': n,
        'world_ids': [row['world'] for row, ok in zip(records, complete) if ok]}, 'verdict': 'DIAGNOSTIC'}
    evaluated['b_chain_provenance'] = {'value': {'issues': link_issues}, 'verdict': 'PASS' if gates['chain_provenance'] else 'FAIL'}
    evaluated['b_numerical_checks'] = {'value': [c['numerics'] for row in records for c in row['turns']], 'verdict': 'PASS' if gates['numerical_checks'] else 'FAIL'}
    evaluated['b_costs'] = {'value': {'per_world_seconds': [row['seconds'] for row in records]}, 'verdict': 'DIAGNOSTIC'}
    if source_pin is None:
        not_run['source_pin'] = {'reason': 'orchestrator has not validated the complete release'}
    else:
        if source_pin.get('status') != 'PASS' or source_pin.get('source_files_verified') != 25:
            raise ValueError('invalid source-pin validation result')
        evaluated['source_pin'] = {'value': source_pin, 'verdict': 'PASS'}
    for name in ('H-COMP', 'H-PRED', 'H-AI', 'H-EFF'):
        hypotheses[name] = 'NOT_TESTED'
    if set(evaluated) | set(not_run) != set(ENDPOINTS) or set(evaluated) & set(not_run):
        raise ValueError('R4 endpoint coverage mismatch')
    return {'claim_schema': 'geomind-r5', 'analysis_schema': 'geomind-c6-r4/1',
            'primary_contrasts': PRIMARY_COUNT, 'gates': gates, 'hypotheses': hypotheses,
            'endpoint_coverage': {'evaluated': evaluated, 'not_run': not_run}}
