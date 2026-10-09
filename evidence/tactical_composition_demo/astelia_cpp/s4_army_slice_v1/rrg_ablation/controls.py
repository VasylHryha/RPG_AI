"""Same-checkpoint offline controls; never trains, launches fights or writes upstream."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check as c  # sets BLAS environment limits before numpy/torch imports
import hashlib
import json
import math
import os
import time
import numpy as np
import torch
from controls_model import ControlsPolicy
from controls_report import report

HERE = c.HERE
ORIGINAL = HERE/'RRG_ABLATION_STAGEB_R0.json'
ORIGINAL_SHA = '64c1c652fcca0c48d72eb05733abe4b8fc1eee1f8f63458c858d7540d781bc93'
SWITCHES = {
    'intact': 'Unchanged N2 checkpoint; reproduces original target/fire counts exactly.',
    'indicator_no_phase': 'K=0, original learned forcing and omega retained, including all phase head features and fire window; replace only the target bonus by +2 for any masked ally assigned to that living enemy.',
    'intact_no_bonus': 'Intact phase dynamics and head features; remove only the hand-wired target bonus. Output-only change: scored from exact pre-bonus intact logits, no extra state replay.',
    'forcing_only_cut': 'Set phase forcing to zero, retain learned K, omega and original forcing scalar in the head.',
    'role_shuffle': 'After every physical RK4 update, permute phases within public-role groups. Carry shuffled phases into next tick. Fixed PRNG seed 41002 reset per fight. Preserves each role marginal at that intervention instant, not intact future trajectory or equal disturbance size.',
    'forced_synchronous': 'After every physical RK4 update overwrite all phases with zero, across roles. Carry zero phases forward; retain K/forcing/omega, peer selection and all readouts. Constant common phase makes absolute fire/head features an additional intervention.',
    'intact_no_fire_window': 'Intact dynamics, target bonus and head features; remove only the N2-only [2 cos(theta), -2 cos(theta), 2 cos(theta)] fire-logit addition. Output-only change: use exact pre-window logits, no extra state replay.',
}
REPLAY = tuple(s for s in SWITCHES if s not in ('intact_no_bonus', 'intact_no_fire_window'))


def diagnostic_counts():
    return {r: dict(rows=0, oracle_non_none_rows=0, oracle_among_neighbor_targets=0,
                    rule_correct=0, rows_with_neighbor_living_target=0) for r in c.ROLES}


def neighbor_rule(pos, enemy_pos, assignments, order, mask, enemies):
    """Plurality of valid neighbour assignments; distance then ID break ties."""
    chosen = []; support = []
    for i in range(len(pos)):
        counts = {eid: int(np.sum(assignments[order[i]][mask[i]] == eid)) for eid in enemies}
        supported = {eid for eid, n in counts.items() if n}
        support.append(supported)
        if not enemies:
            chosen.append(0); continue
        distances = np.linalg.norm(enemy_pos-pos[i], axis=1)
        best = min(range(len(enemies)), key=lambda j: (-counts[enemies[j]], distances[j], enemies[j]))
        chosen.append(1+best)
    return np.asarray(chosen), support


def diagnose(row, ids, enemies, packed, diagnostic, counts):
    arrays, _, _ = packed.pack(row, 'N2')
    units = {u[0]: u for u in row['units']}
    enemy_pos = np.asarray([[units[e][3], units[e][4]] for e in enemies]).reshape(-1, 2)
    chosen, support = neighbor_rule(arrays['pos'], enemy_pos, arrays['assignments'],
                                    diagnostic['order'].numpy(), diagnostic['mask'].numpy(), enemies)
    for i, lab in enumerate(c.labels(row, ids, enemies)):
        v = counts[lab['role']]; target_id = enemies[lab['target']-1] if lab['target'] else None
        v['rows'] += 1; v['oracle_non_none_rows'] += int(target_id is not None)
        v['oracle_among_neighbor_targets'] += int(target_id in support[i])
        v['rows_with_neighbor_living_target'] += int(bool(support[i]))
        v['rule_correct'] += int(chosen[i] == lab['target'])


def finish_diagnostic(v):
    return dict(v, oracle_among_neighbor_targets_fraction=v['oracle_among_neighbor_targets']/v['rows'] if v['rows'] else None,
                oracle_among_neighbor_targets_fraction_non_none=v['oracle_among_neighbor_targets']/v['oracle_non_none_rows'] if v['oracle_non_none_rows'] else None,
                trivial_rule_accuracy=v['rule_correct']/v['rows'] if v['rows'] else None)


def validate_inputs(old):
    if c.sha(ORIGINAL) != ORIGINAL_SHA:
        raise RuntimeError('Original metrics JSON changed')
    provenance = c.read(HERE/'RUN_SOURCE_PROVENANCE.json')
    for name, digest in old['input_sha256'].items():
        path = c.ROOT/name
        if path == HERE/'check.py':
            if digest != provenance['executed_sha256'] or c.sha(HERE/'CHECK_RUN_SOURCE.py') != digest:
                raise RuntimeError('Original executed source snapshot mismatch')
            digest = provenance['final_runner_sha256']
        if c.sha(path) != digest:
            raise RuntimeError('Original replay input pin changed: '+name)
    index = c.read(c.BASE/'stageb/_local/round0/INDEX.json')
    fights = [f for f in index['fights'] if f['split'] == 'test']
    budget = c.read(c.BASE/'stageb/_local/round0/TRAIN_BUDGET.json')
    if budget['windows_per_fight'] != 4 or budget['window_ticks'] != c.WINDOW:
        raise RuntimeError('Window selection changed')
    if len(fights) != old['test']['fights'] or sum(f['frames'] for f in fights) != old['test']['full_prefix_frames']:
        raise RuntimeError('Test fight inventory changed')
    # Original input pins include indices, training sources, shards and all checkpoint artifacts.
    paths = [c.ROOT/name for name in old['input_sha256']]
    paths += [ORIGINAL, HERE/'RUN_SOURCE_PROVENANCE.json', HERE/'CHECK_RUN_SOURCE.py',
              HERE/'controls.py', HERE/'controls_model.py', HERE/'controls_report.py', HERE/'test_controls.py', HERE/'CONTROLS_PROTOCOL.md']
    return fights, {str(p.relative_to(c.ROOT)): c.sha(p) for p in set(paths)}


def run():
    if (HERE/'RRG_ABLATION_STAGEB_R0_CONTROLS.json').exists():
        raise RuntimeError('Completed control evidence exists; do not rerun or overwrite')
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 15: os.nice(15-priority)
    torch.set_num_threads(1); torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True); torch.manual_seed(41001)
    start = time.monotonic(); cpu = time.process_time()
    old = c.read(ORIGINAL); fights, hashes = validate_inputs(old)
    intact, weights, outcome = c.load('N2')
    models = {}
    for switch in REPLAY:
        m = ControlsPolicy('N2', switch).float().eval(); m.load_state_dict(intact.state_dict()); models['N2_'+switch] = m
    if outcome['budget_sha256'] != c.sha(c.BASE/'stageb/_local/round0/TRAIN_BUDGET.json'):
        raise RuntimeError('N2 budget mismatch')
    thresholds = weights['fireThresholds']
    packed = c.PackedInputs(); c.training.pack = packed.pack; c.training.tensor = packed.tensor
    names = ['N2_'+s for s in SWITCHES]
    counts = {n: c.counters() for n in names}
    phases = {n: {r: c.PhaseStats() for r in c.ROLES} for n in models}
    diagnostics = diagnostic_counts(); sequences = []; row_hash = hashlib.sha256()
    with torch.inference_mode():
        for number, fight in enumerate(fights):
            contexts = {n: (c.initial('N2', []), [], None, (0, [])) for n in models}
            for m in models.values(): m.shuffle_rng.manual_seed(41002)
            starts = c.selected_starts(fight['frames'], 4)
            selected = set(i for at in starts for i in range(at, min(at+c.WINDOW, fight['frames'])))
            previous = old['sequences'][number]
            if previous['tag'] != fight['tag'] or previous['starts'] != starts or previous['scored_ticks'] != len(selected):
                raise RuntimeError('Original sequence/window identity mismatch')
            local = {n: c.counters() for n in names}; local_diag = diagnostic_counts(); nframes = 0
            for tick, row in enumerate(c.frames(fight['raw_file'])):
                nframes += 1
                if 'shadowLabels' in row: raise RuntimeError('Unexpected DAgger labels')
                for name, model in models.items():
                    state, ids, cache, next_frame = contexts[name]
                    y, state, ids, enemies, cache, next_frame, _ = c.forward(model, row, state, ids, cache, next_frame)
                    contexts[name] = state, ids, cache, next_frame
                    if tick not in selected: continue
                    c.score(y, row, ids, enemies, thresholds, local[name])
                    d = model.last_diagnostics
                    roles = np.asarray([lab['role'] for lab in c.labels(row, ids, enemies)])
                    for r in c.ROLES:
                        mask = roles == r
                        phases[name][r].add(state[:, 0].numpy()[mask], d['forcing'].numpy()[mask],
                                            d['coupling'].numpy()[mask], tick/max(1, fight['frames']-1), d['phase_forcing'].numpy()[mask])
                    if name == 'N2_intact':
                        c.score(dict(y, target=d['target_without_bonus']), row, ids, enemies, thresholds, local['N2_intact_no_bonus'])
                        c.score(dict(y, fire=d['fire_without_window']), row, ids, enemies, thresholds, local['N2_intact_no_fire_window'])
                        diagnose(row, ids, enemies, packed, d, local_diag)
                        for uid, lab in zip(ids, c.labels(row, ids, enemies)):
                            row_hash.update(json.dumps([fight['tag'], tick, uid, lab], sort_keys=True, separators=(',', ':')).encode()+b'\n')
            if nframes != fight['frames']: raise RuntimeError('Incomplete sequence '+fight['tag'])
            for n in names:
                for r in c.ROLES:
                    if local[n][r]['rows'] != previous['metrics']['N2_intact'][r]['rows']:
                        raise RuntimeError('Per-fight row mismatch')
                    for key, value in local[n][r].items(): counts[n][r][key] += value
            for r in c.ROLES:
                for key, value in local_diag[r].items(): diagnostics[r][key] += value
                for key in ('rows', 'target_correct', 'fire_correct'):
                    if local['N2_intact'][r][key] != previous['metrics']['N2_intact'][r][key]:
                        raise RuntimeError('Per-fight intact reproduction failed')
            sequences.append(dict(tag=fight['tag'], frames=nframes, scored_ticks=len(selected), starts=starts,
                                  metrics={n: {r: c.finish(v) for r, v in roles.items()} for n, roles in local.items()},
                                  neighbor_diagnostic={r: finish_diagnostic(v) for r, v in local_diag.items()}))
            print(f'{number+1}/{len(fights)} controls sequences; elapsed {time.monotonic()-start:.1f}s', flush=True)
    if row_hash.hexdigest() != old['test']['row_identity_sha256']:
        raise RuntimeError('Original scored row identity mismatch')
    for name, digest in hashes.items():
        if c.sha(c.ROOT/name) != digest: raise RuntimeError('Input changed during inference: '+name)
    result = dict(schema=1, scope='Owner-requested exploratory same-checkpoint offline controls; no retraining, fights, threshold tuning or source qualification.',
                  original_metrics_sha256=ORIGINAL_SHA, input_sha256=hashes,
                  execution=dict(seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu,
                                 nice=os.getpriority(os.PRIO_PROCESS, 0), torch_threads=1, torch_interop_threads=1,
                                 torch_version=torch.__version__, dtype='float32', shuffle_seed=41002),
                  test=dict(old['test'], selection='Same four 90-tick windows, full-prefix separate state replay for each dynamic arm. No-bonus and no-fire-window reuse intact state with exact captured pre-addition logits.'),
                  interventions=SWITCHES, definitions=dict(old['definitions'],
                      forcing='Learned tanh forcing scalar remains in the head for every control. effective_phase_forcing is zero only in forcing_only_cut; indicator_no_phase instead zeros K.',
                      neighbor_diagnostic='Up to eight living own allies strictly within 300 px, same graph as intact; all roles. Exact current pre-decision assignment IDs, no oracle input. Ignore assignments to None/dead enemies. Oracle support excludes None from numerator; report all-row and non-None-label denominators.',
                      trivial_rule='Pick living enemy with largest masked-neighbour assignment count; break ties by nearest Euclidean distance then smallest persistent ID; absent valid assignments pick nearest; no living enemy => None.',
                      disturbance='Shuffle preserves the within-role updated phase multiset each tick of its own perturbed trajectory. Forced synchrony sets common absolute phase 0. Neither guarantees equal disturbance amplitude or preservation of learned head distribution.',
                      coupling_rate='Post-intervention hypothetical instantaneous original RHS term, not actual whole-step rate under shuffle or forced synchrony.'),
                  metrics={n: {r: c.finish(v) for r, v in roles.items()} for n, roles in counts.items()},
                  neighbor_diagnostic={r: finish_diagnostic(v) for r, v in diagnostics.items()},
                  phase_diagnostics={n: {r: v.result() for r, v in roles.items()} for n, roles in phases.items()},
                  original_intact_reproduction='Exact per-fight rows/target_correct/fire_correct and scored row hash match.',
                  sequences=sequences)
    # Report derives comparisons and bounded verdict before the new evidence is sealed.
    text = report(result, old)
    c.write('RRG_ABLATION_STAGEB_R0_CONTROLS.json', result)
    (HERE/'RRG_ABLATION_STAGEB_R0_CONTROLS.md').write_text(text)
    print(result['verdict'], flush=True)
    return result


if __name__ == '__main__': run()
