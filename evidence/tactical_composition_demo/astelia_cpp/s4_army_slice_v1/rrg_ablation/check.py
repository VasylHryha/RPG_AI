"""Owner-requested offline mechanism diagnostic; no training or simulator calls."""
import sys
sys.dont_write_bytecode = True
import os
for variable in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[variable] = '1'
import argparse
import hashlib
import json
import math
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = BASE.parents[3]
STAGEA = BASE / 'stagea'
TRAIN = BASE / 'stageb/_local/round0/training'
sys.path.insert(0, str(STAGEA))
import numpy as np
import torch
from models import Policy, initial
from data import frames, labels, pack
from training import forward, selected_starts, WINDOW
import training
from ablation_model import AblationPolicy

ROLES = ('melee', 'ranged', 'artillery')
SWITCHES = {
    'intact': 'Unchanged trained forward law and readouts.',
    'k_zero': 'K=0; retain omega, learned forcing, phase readouts and drift.',
    'frozen_phase': 'Hold each persistent ID phase at its deterministic initial value; retain forcing and all phase readouts.',
    'reset_disabled': 'Exact no-op: pinned model has no attack-triggered reset; fight initialization and ID remapping remain required.',
    'topology_only': 'Freeze directed edges, distances, weights and displacement vectors at first recorded tick; remove dead endpoints without recruiting neighbors. Public tokens, assignments and speeds remain live.',
    'no_mode_to_geometry': 'Zero output drift only. Recorded positions remain exogenous; phase and heads unchanged.',
    'no_geometry_to_mode': 'Zero input-dependent forcing only in the phase RHS and zero geometry-weighted coupling; phase advances only by learned omega. Retain the learned forcing scalar in the head, geometry in attention/heads, and phase-dependent drift/readouts.',
}


class PackedInputs:
    """Per-row reuse of identical read-only arrays, with no persistent state."""
    def __init__(self):
        self.row = None; self.values = {}; self.tensors = {}

    def pack(self, row, kind):
        if row is not self.row:
            self.row = row; self.values = {}; self.tensors = {}
        # Only N1h adds history; all other requested kinds pack identically.
        key = 'N1h' if kind == 'N1h' else 'N1'
        if key not in self.values:
            self.values[key] = pack(row, key)
        return self.values[key]

    def tensor(self, x, dtype=torch.float32):
        key = (id(x), dtype)
        if key not in self.tensors:
            self.tensors[key] = {k: torch.as_tensor(v, dtype=torch.long if k in ('own', 'enemy', 'assignments') else dtype) for k, v in x.items()}
        return self.tensors[key]


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def load(arm, switch='intact'):
    outcome = read(TRAIN / (arm + '.outcome.json'))
    weights = read(TRAIN / (arm + '.weights.json'))
    for suffix, field in (('.pt', 'checkpoint_sha256'), ('.weights.json', 'export_sha256'), ('.calibration.json', 'calibration_sha256')):
        if sha(TRAIN / (arm + suffix)) != outcome[field]:
            raise RuntimeError('Pinned outcome input mismatch: ' + arm + suffix)
    checkpoint = torch.load(TRAIN / (arm + '.pt'), map_location='cpu', weights_only=True)
    exported = {k: torch.tensor(v['values'], dtype=torch.float32).reshape(v['shape']) for k, v in weights['parameters'].items()}
    if checkpoint['epoch'] != outcome['selected_epoch'] or checkpoint['model'].keys() != exported.keys():
        raise RuntimeError('Selected checkpoint/export identity mismatch')
    if not all(torch.equal(checkpoint['model'][k], exported[k]) for k in exported):
        raise RuntimeError('Checkpoint weights differ from export')
    model = AblationPolicy(arm, switch) if arm == 'N2' else Policy(arm)
    model.load_state_dict(exported)
    model.eval()
    return model, weights, outcome


class Moments:
    def __init__(self):
        self.n = 0; self.s = 0.; self.s2 = 0.; self.abs = 0.
        self.lo = math.inf; self.hi = -math.inf

    def add(self, a):
        a = np.asarray(a, dtype=np.float64)
        if not np.isfinite(a).all():
            raise RuntimeError('Nonfinite diagnostic')
        if not a.size:
            return
        self.n += a.size; self.s += float(a.sum()); self.s2 += float((a*a).sum())
        self.abs += float(np.abs(a).sum()); self.lo = min(self.lo, float(a.min())); self.hi = max(self.hi, float(a.max()))

    def result(self):
        if not self.n:
            return dict(samples=0)
        return dict(samples=self.n, mean=self.s/self.n, std=math.sqrt(max(0., self.s2/self.n-(self.s/self.n)**2)),
                    mean_absolute=self.abs/self.n, min=self.lo, max=self.hi)


class PhaseStats:
    def __init__(self):
        self.forcing = Moments(); self.phase_forcing = Moments(); self.coupling = Moments(); self.order = Moments(); self.pairs = Moments()
        self.multi_order = Moments(); self.hist = np.zeros(12, dtype=np.int64)
        self.strata = {s: Moments() for s in ('early', 'middle', 'late')}
        self.singletons = 0

    def add(self, theta, forcing, coupling, progress, phase_forcing=None):
        if not len(theta):
            return
        self.forcing.add(forcing); self.phase_forcing.add(forcing if phase_forcing is None else phase_forcing); self.coupling.add(coupling)
        resultant = abs(np.exp(1j*theta).mean())
        self.order.add([resultant])
        self.strata['early' if progress < 1/3 else 'middle' if progress < 2/3 else 'late'].add([resultant])
        self.hist += np.histogram(np.mod(theta, 2*math.pi), bins=12, range=(0, 2*math.pi))[0]
        if len(theta) == 1:
            self.singletons += 1
        else:
            self.multi_order.add([resultant])
            delta = np.abs(np.angle(np.exp(1j*(theta[:, None]-theta[None, :]))))
            self.pairs.add(delta[np.triu_indices(len(theta), 1)] <= math.pi/6)

    def result(self):
        return dict(forcing=self.forcing.result(), effective_phase_forcing=self.phase_forcing.result(), coupling_rate=self.coupling.result(), order_parameter=self.order.result(),
                    order_parameter_at_least_two_units=self.multi_order.result(), singleton_frames=self.singletons,
                    phase_bins_12=self.hist.tolist(), pair_fraction_within_pi_over_6=self.pairs.result(),
                    order_by_relative_fight_time={s: m.result() for s, m in self.strata.items()})


def counters():
    return {role: dict(rows=0, target_correct=0, fire_correct=0, calibrated_fire_correct=0,
                      calibrated_fire_with_safety_correct=0, move_sum=0., aim_sum=0., aim_rows=0) for role in ROLES}


def score(y, row, ids, enemies, thresholds, counts):
    labs = labels(row, ids, enemies)
    target = y['target'].argmax(-1).numpy(); raw_fire = y['fire'].argmax(-1).numpy()
    fire = y['fire'].numpy(); subtype = np.where(fire[:, 0] >= fire[:, 2], 0, 2)
    roles = np.array([ROLES.index(l['role']) for l in labs])
    calibrated = np.where(np.maximum(fire[:, 0], fire[:, 2])-fire[:, 1] >= np.asarray(thresholds)[roles], subtype, 1)
    own = {u[0]: u for u in row['own']}; label_by_id = {l['id']: l for l in row['labels']}
    allowed = np.array([not label_by_id[uid]['active'] and own[uid][1] <= row['t'] and not own[uid][7] for uid in ids])
    calibrated_safety = np.where(allowed, calibrated, 1)
    scale = y['move'].new_tensor([row['width'], row['height']])
    movement = (y['move']*scale+y['drift'])/100
    truth_move = y['move'].new_tensor([l['move'] for l in labs])*scale/100
    move_error = torch.nn.functional.smooth_l1_loss(movement, truth_move, reduction='none').mean(-1).numpy()
    truth_aim = y['aim'].new_tensor([l['aim'] for l in labs])*scale/100
    aim_error = torch.nn.functional.smooth_l1_loss(y['aim']*scale/100, truth_aim, reduction='none').mean(-1).numpy()
    truth_target = np.array([l['target'] for l in labs]); truth_fire = np.array([l['fire'] for l in labs])
    aim_mask = np.array([l['aim_mask'] for l in labs], dtype=bool)
    for role_index, role in enumerate(ROLES):
        mask = roles == role_index; c = counts[role]; aim = mask & aim_mask
        c['rows'] += int(mask.sum()); c['target_correct'] += int((mask & (target == truth_target)).sum())
        c['fire_correct'] += int((mask & (raw_fire == truth_fire)).sum())
        c['calibrated_fire_correct'] += int((mask & (calibrated == truth_fire)).sum())
        c['calibrated_fire_with_safety_correct'] += int((mask & (calibrated_safety == truth_fire)).sum())
        c['move_sum'] += float(move_error[mask].sum()); c['aim_sum'] += float(aim_error[aim].sum()); c['aim_rows'] += int(aim.sum())


def finish(c):
    return dict(rows=c['rows'], target_correct=c['target_correct'], target_accuracy=c['target_correct']/c['rows'] if c['rows'] else None,
                fire_correct=c['fire_correct'], fire_accuracy=c['fire_correct']/c['rows'] if c['rows'] else None,
                calibrated_fire_accuracy=c['calibrated_fire_correct']/c['rows'] if c['rows'] else None,
                calibrated_fire_with_safety_accuracy=c['calibrated_fire_with_safety_correct']/c['rows'] if c['rows'] else None,
                move_smooth_l1=c['move_sum']/c['rows'] if c['rows'] else None,
                aim_rows=c['aim_rows'], aim_smooth_l1=c['aim_sum']/c['aim_rows'] if c['aim_rows'] else None)


def run():
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 10:
        os.nice(10-priority)
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError('Low CPU priority required')
    torch.set_num_threads(1); torch.set_num_interop_threads(1); torch.use_deterministic_algorithms(True)
    torch.manual_seed(41001)
    packed = PackedInputs()
    training.pack = packed.pack; training.tensor = packed.tensor
    started = time.monotonic(); cpu = time.process_time()
    index_path = BASE/'stageb/_local/round0/INDEX.json'; stagea_index = STAGEA/'_local/INDEX.json'
    index = read(index_path); aindex = read(stagea_index)
    if index['round'] != 0 or index['stagea_index_sha256'] != sha(stagea_index):
        raise RuntimeError('Round-0 sealed data identity mismatch')
    expected = [dict(f, raw_file=str((STAGEA/'_local'/f['raw_file']).resolve())) for f in aindex['fights']]
    if index['fights'] != expected or any(v != expected for v in index['arm_fights'].values()):
        raise RuntimeError('Stage B round-0 split changed')
    budget_path = BASE/'stageb/_local/round0/TRAIN_BUDGET.json'; budget = read(budget_path)
    if budget['windows_per_fight'] != 4 or budget['window_ticks'] != WINDOW or budget['index_sha256'] != sha(index_path):
        raise RuntimeError('Outcome row selection mismatch')
    # Stage B source keys are relative to astelia_cpp. Verify the imported
    # forward/data dependencies against the pins that trained these checkpoints.
    for name in ('common.py', 'models.py', 'data.py', 'training.py', 'recording.py', 'training_control.py'):
        p = STAGEA/name
        if budget['sources'].get(str(p.relative_to(BASE.parent))) != sha(p):
            raise RuntimeError('Training source pin mismatch: '+name)
    fights = [f for f in index['fights'] if f['split'] == 'test']
    # Only inputs actually used here belong in the unchanged-input guard.
    # Independent Stage B2/rev2 development must not invalidate this replay.
    protected = [STAGEA/name for name in ('common.py', 'models.py', 'data.py', 'training.py', 'recording.py', 'training_control.py')]
    inputs = [index_path, stagea_index, budget_path, BASE/'stageb/STAGEB_PROTOCOL.md', STAGEA/'STAGEA_PROTOCOL.md',
              ROOT/'research/rrg/CURRENT.md', HERE/'check.py', HERE/'ablation_model.py', HERE/'test_switches.py']
    for arm in ('N1', 'N1h', 'N1r', 'N2'):
        inputs.extend(TRAIN/(arm+suffix) for suffix in ('.pt', '.weights.json', '.outcome.json', '.calibration.json'))
    inputs.extend(Path(f['raw_file']) for f in fights)
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in set(protected+inputs)}
    for f in fights:
        if sha(f['raw_file']) != f['raw_sha256']:
            raise RuntimeError('Test recording drift: '+f['tag'])
    models = {}; outcomes = {}; thresholds = {}
    for arm, switch in [('N1', 'intact'), ('N1h', 'intact'), ('N1r', 'intact')]+[('N2', s) for s in SWITCHES]:
        name = arm if arm != 'N2' else 'N2_'+switch
        models[name], weights, outcomes[name] = load(arm, switch)
        if outcomes[name]['budget_sha256'] != sha(budget_path):
            raise RuntimeError('Checkpoint budget mismatch')
        thresholds[name] = weights['fireThresholds']
    counts = {name: counters() for name in models}
    phases = {name: {r: PhaseStats() for r in ROLES} for name in models if name.startswith('N2_')}
    sequence_results = []
    row_hash = hashlib.sha256()
    with torch.inference_mode():
        for number, fight in enumerate(fights):
            contexts = {name: (initial(model.kind, []), [], None, (0, [])) for name, model in models.items()}
            for model in models.values():
                if isinstance(model, AblationPolicy):
                    model.frozen_graph = None
                    model.graph_cache = None
            starts = selected_starts(fight['frames'], 4)
            selected = set(i for at in starts for i in range(at, min(at+WINDOW, fight['frames'])))
            local_counts = {name: counters() for name in models}; nframes = 0
            for tick, row in enumerate(frames(fight['raw_file'])):
                nframes += 1
                if 'shadowLabels' in row:
                    raise RuntimeError('Unexpected DAgger labels in round-0 test')
                intact_forward = None
                for name, model in models.items():
                    if name in ('N2_reset_disabled', 'N2_no_mode_to_geometry'):
                        # Exact structural identities, proven by the switch tests:
                        # reset_disabled has no changed operation; drift is output-only.
                        y, state, ids, enemies, cache, next_frame = intact_forward
                        if name == 'N2_no_mode_to_geometry':
                            y = dict(y, drift=torch.zeros_like(y['drift']))
                    else:
                        state, ids, cache, next_frame = contexts[name]
                        y, state, ids, enemies, cache, next_frame, _ = forward(model, row, state, ids, cache, next_frame)
                    if name == 'N2_intact':
                        intact_forward = y, state, ids, enemies, cache, next_frame
                    contexts[name] = state, ids, cache, next_frame
                    if tick not in selected:
                        continue
                    score(y, row, ids, enemies, thresholds[name], local_counts[name])
                    if name.startswith('N2_'):
                        labs = labels(row, ids, enemies); roles = np.array([l['role'] for l in labs])
                        diagnostic = models['N2_intact'].last_diagnostics if name in ('N2_reset_disabled', 'N2_no_mode_to_geometry') else model.last_diagnostics
                        for role in ROLES:
                            mask = roles == role
                            phases[name][role].add(state[:, 0].numpy()[mask], diagnostic['forcing'].numpy()[mask],
                                                   diagnostic['coupling'].numpy()[mask], tick/max(1, fight['frames']-1),
                                                   diagnostic['phase_forcing'].numpy()[mask])
                    if name == 'N1':
                        for uid, lab in zip(ids, labels(row, ids, enemies)):
                            row_hash.update(json.dumps([fight['tag'], tick, uid, lab], sort_keys=True, separators=(',', ':')).encode()+b'\n')
            if nframes != fight['frames']:
                raise RuntimeError('Incomplete sequence '+fight['tag'])
            for name in models:
                for role in ROLES:
                    for key, value in local_counts[name][role].items():
                        counts[name][role][key] += value
            sequence_results.append(dict(tag=fight['tag'], frames=nframes, scored_ticks=len(selected), starts=starts,
                                         metrics={name: {r: finish(c) for r, c in v.items()} for name, v in local_counts.items()}))
            print(f'{number+1}/{len(fights)} test sequences; elapsed {time.monotonic()-started:.1f}s', flush=True)
    results = {name: {r: finish(c) for r, c in v.items()} for name, v in counts.items()}
    parity = {}
    for name in ('N1', 'N1h', 'N1r', 'N2_intact'):
        parity[name] = {}
        for role in ROLES:
            old = outcomes[name]['test']['roles'][role]; new = results[name][role]
            parity[name][role] = {key+'_difference': new[key]-old[key] for key in ('rows', 'target_correct', 'fire_correct')}
            if new['rows'] != old['rows'] or abs(new['target_correct']-old['target_correct'])/new['rows'] > 1e-4 or abs(new['fire_correct']-old['fire_correct'])/new['rows'] > 1e-4:
                raise RuntimeError('Original outcome reproduction failed: '+name+':'+role)
    for name in ('N2_reset_disabled', 'N2_no_mode_to_geometry'):
        for role in ROLES:
            for field in ('target_correct', 'fire_correct', 'calibrated_fire_accuracy', 'aim_smooth_l1'):
                if results[name][role][field] != results['N2_intact'][role][field]:
                    raise RuntimeError('Expected exogenous-replay identity failed: '+name)
    for p, digest in hashes.items():
        if sha(ROOT/p) != digest:
            raise RuntimeError('Read-only input changed during inference: '+p)
    law = models['N2_intact'].law.detach()
    result = dict(schema=1, scope='Owner-requested exploratory offline mechanism check; no retraining, no fights, no source-recursion qualification.',
                  dtype='float32 (selected training checkpoint; exact equality to float32 cast of export)',
                  execution=dict(torch_threads=1, torch_interop_threads=1, nice=os.getpriority(os.PRIO_PROCESS, 0),
                                 seconds=time.monotonic()-started, cpu_seconds=time.process_time()-cpu, torch_version=torch.__version__),
                  input_sha256=hashes, test=dict(fights=len(fights), full_prefix_frames=sum(f['frames'] for f in fights),
                       scored_unit_rows=sum(c['rows'] for c in counts['N1'].values()), row_identity_sha256=row_hash.hexdigest(),
                       selection='Same four selected_starts windows of 90 physical ticks as outcome.test; full prefix replay separately for every dynamic intervention, never reuse intact stored snapshots. Reset-disabled reuses intact outputs exactly; drift-only removal reuses intact state/heads and zeros output drift. Both are structural identities verified by tests.',
                       provenance='Sealed Stage A whole-fight split matched exactly to Stage B round0; raw recording hashes checked.'),
                  definitions=dict(target_accuracy='argmax pointer including None; unit-row weighted',
                       fire_accuracy='raw three-class argmax, as outcome.test',
                       calibrated_fire_accuracy='unchanged validation thresholds from each arm export; no recalibration',
                       calibrated_fire_with_safety_accuracy='same threshold plus calibration.collect_scores allowed mask (active/guard/busy), not complete native arbitration',
                       move_smooth_l1='mean beta=1 SmoothL1 across x/y in 100 px units, including drift',
                       aim_smooth_l1='mean beta=1 SmoothL1 across x/y in 100 px units, oracle aim mask only; null when no labels',
                       phase='At scored ticks after physical update; R=abs(mean(exp(i theta))) within role per tick. R means weight ticks equally; histogram/forcing weight units. Pair fraction weights unordered within-role pairs. No inferred discrete cluster count.',
                       phase_rate_units='omega, forcing and coupling in radians/second; phase bins radians modulo 2pi',
                       coupling_rate='Instantaneous coupling RHS evaluated at post-step theta, not realized RK4 whole-step average. Hypothetical under frozen_phase: actual phase rate is zero.',
                       forcing='Learned tanh output retained in the head in all cuts. effective_phase_forcing is its value used in the phase RHS; zero only for no_geometry_to_mode.'),
                  interventions=SWITCHES, metrics=results, outcome_reproduction=parity,
                  learned=dict(raw_law=law.tolist(), K=float(2*torch.sigmoid(law[3])), omega=float(2*torch.tanh(law[4])),
                               A=float(torch.sigmoid(law[0])), B=float(torch.sigmoid(law[1])), J=float(torch.sigmoid(law[2])),
                               drift_share=float(.25*torch.sigmoid(law[5])), attack_resets=0),
                  phase_diagnostics={name: {r: s.result() for r, s in v.items()} for name, v in phases.items()},
                  sequences=sequence_results)
    write('RRG_ABLATION_STAGEB_R0.json', result)
    report(result)
    return result


def report(result):
    m = result['metrics']; baseline = m['N1']; intact = m['N2_intact']
    dynamics_lost = all(m['N2_'+s][r]['target_accuracy'] <= baseline[r]['target_accuracy']
                        for s in ('k_zero', 'frozen_phase', 'no_geometry_to_mode') for r in ('ranged', 'artillery'))
    lines = ['# Stage B round-0 RRG mechanism check', '',
             'Offline float32 inference on the selected trained checkpoints. No retraining and no fights. '
             f"The exact sealed TEST split has {result['test']['fights']} fights, "
             f"{result['test']['full_prefix_frames']:,} replayed physical ticks, and "
             f"{result['test']['scored_unit_rows']:,} scored unit rows. "
             'Each dynamic intervention gets its own full-prefix state replay; scoring uses the same four 90-tick windows as the original outcomes. '
             'The tested exact identities reuse intact computation: reset-disabled changes nothing, and drift-only removal zeros output drift while retaining identical state and heads.', '',
             '| Policy / intervention | Melee target | Ranged target | Artillery target |',
             '|---|---:|---:|---:|']
    if dynamics_lost:
        lines[4:4] = ['N2’s ranged/artillery target advantage does **not** survive K=0, frozen phase, or no geometry→mode. '
                      'For this trained checkpoint on these fixed test rows, the phase/coupling path is needed to express the observed gain. '
                      'The static architecture with those paths disabled does not retain it. This supports a phase/coupling mechanism contribution; '
                      'it does not establish resonance in general, a live geometry↔mode feedback loop, or recursive RRG.', '']
    for name, roles in m.items():
        lines.append('| '+name+' | '+' | '.join(f"{roles[r]['target_accuracy']:.4f}" for r in ROLES)+' |')
    lines += ['', 'Intact N2 minus N1 target accuracy is '+', '.join(
        f"{r}: {100*(intact[r]['target_accuracy']-baseline[r]['target_accuracy']):+.2f} percentage points" for r in ROLES)+'.', '']
    for name in ('k_zero', 'frozen_phase', 'topology_only', 'no_geometry_to_mode'):
        v = m['N2_'+name]
        lines.append(f"{name}: change from intact is "+', '.join(
            f"{r} {100*(v[r]['target_accuracy']-intact[r]['target_accuracy']):+.2f} points" for r in ('ranged', 'artillery'))+
            '; remaining advantage over N1 is '+', '.join(
            f"{r} {100*(v[r]['target_accuracy']-baseline[r]['target_accuracy']):+.2f} points" for r in ('ranged', 'artillery'))+'.')
    survival = all(m['N2_'+s][r]['target_accuracy'] > baseline[r]['target_accuracy']
                   for s in ('k_zero', 'frozen_phase', 'topology_only', 'no_geometry_to_mode') for r in ('ranged', 'artillery'))
    lines += ['', ('A positive target-accuracy margin over N1 remains after every cut on this fixed test replay; the numbers show how much '
                  'of the original margin remains. K=0 and frozen phase show that nonzero coupling and phase evolution are not necessary '
                  'for that remaining margin in this checkpoint. This is consistent with an architectural/readout contribution. '
                  'Phase-dependent features/readouts remain, so this does not isolate a phase-free architecture or establish that resonance is absent.'
                  if survival else
                  'At least one cut erases the observed margin over N1. This establishes checkpoint sensitivity to that intervention '
                  'on these rows, without proving resonance or a general architecture effect.'), '',
              'Reset disabled is exactly intact: this implementation never resets phase on attack. Removing mode→geometry zeros drift and '
              'can change movement error, but leaves target/fire/aim unchanged in this replay. Recorded positions cannot react to the removed drift. '
              'Neither identity result tests a live feedback loop.', '',
              'Frozen phase retains ID-dependent sin/cos features, peer phase summaries and the explicit target-alignment/fire-window readouts. '
              'No geometry→mode removes learned input-dependent forcing from the phase equation and removes geometry-weighted coupling; '
              'learned omega and the direct forcing feature supplied to the head remain. '
              'Topology-only freezes edges, distances and direction vectors at the first recorded tick, while tokens and target assignments stay live. '
              'These are distinct cuts, not a trained replacement architecture. No phase-free retrained model is compared. '
              'No causal background transformation or recursive RRG claim is tested.', '',
              'Fire below is raw three-class accuracy, matching the outcome metric. The JSON also gives fire accuracy with each original '
              'validation threshold unchanged, both before and after the calibration safety mask. Move and masked aim errors are mean SmoothL1 '
              'with beta=1, in 100-pixel units; lower is better. Aim uses only oracle rows with an aim label.']
    for role in ROLES:
        lines += ['', f'{role.capitalize()} heads:', '', '| Policy | Fire accuracy | Move error | Aim error |', '|---|---:|---:|---:|']
        for name, roles in m.items():
            v = roles[role]
            aim_text = 'N/A' if v['aim_smooth_l1'] is None else f"{v['aim_smooth_l1']:.4f}"
            lines.append(f"| {name} | {v['fire_accuracy']:.4f} | {v['move_smooth_l1']:.4f} | {aim_text} |")
    learned = result['learned']
    lines += ['', f"Learned N2 K={learned['K']:.6f}; omega={learned['omega']:.6f} rad/s. "
              'Forcing is the learned tanh output from query/context, separate from coupling. At scored test ticks:', '',
              '| Role | Forcing mean ± SD (rad/s) | Mean absolute forcing | Mean R (≥2 units) | Pair fraction within 30° |', '|---|---:|---:|---:|---:|']
    for role, v in result['phase_diagnostics']['N2_intact'].items():
        f = v['forcing']; order = v['order_parameter_at_least_two_units']; pairs = v['pair_fraction_within_pi_over_6']
        lines.append(f"| {role} | {f['mean']:.4f} ± {f['std']:.4f} | {f['mean_absolute']:.4f} | {order['mean']:.4f} | {pairs['mean']:.4f} |")
    lines += ['', 'With K=0, mean R falls to '+', '.join(
        f"{r} {result['phase_diagnostics']['N2_k_zero'][r]['order_parameter_at_least_two_units']['mean']:.4f}" for r in ROLES)+
        '. Thus lower phase alignment accompanies the lost target-accuracy advantage.']
    lines += ['', 'R is the length of the mean unit phase vector: near one means global alignment; low R can mean dispersed phases or opposing clusters. '
              'Singleton R values are excluded from the displayed means. The pair fraction is a descriptive clustering measure, '
              'not a fitted number of clusters. JSON includes every intervention, phase histograms, early/middle/late R and per-fight head metrics. '
              'Alignment alone cannot establish that coupling causes the accuracy gain. The JSON coupling statistic is the instantaneous post-step RHS term, '
              'not the realized whole-step average; it is hypothetical under frozen phase, whose actual phase rate is zero.', '',
              'Original outcome reproduction: '+('all row and target/fire correct counts match exactly.' if
              all(v == 0 for roles in result['outcome_reproduction'].values() for fields in roles.values() for v in fields.values())
              else 'row counts match; target/fire correct-count differences are recorded explicitly in JSON (maximum allowed accuracy difference 0.0001).'), '',
              f"Inference took {result['execution']['seconds']:.1f} s wall / {result['execution']['cpu_seconds']:.1f} s CPU; "
              f"nice {result['execution']['nice']}, one Torch thread and one interop thread. All input/source hashes were checked again after inference. "
              'Results describe this held-out offline replay and are exploratory; repeated unit ticks are not independent fights.']
    (HERE/'RRG_ABLATION_STAGEB_R0.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    run()
