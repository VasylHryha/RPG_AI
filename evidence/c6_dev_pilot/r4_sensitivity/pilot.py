"""Single-use exploratory Q/H pilot. Scientific helpers are read-only imports."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC = HERE / 'SPEC.json'
sys.path.insert(0, str(ROOT))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path, value):
    raw = (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    return len(raw)


def guard(spec):
    for name, expected in spec['file_hashes'].items():
        path = ROOT / name
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError('missing/mismatched dependency: ' + name)
    record = json.loads((ROOT / 'build/c6_r4/BUILD.json').read_text())
    if record != spec['native_build']:
        raise RuntimeError('native build record changed')
    if record['source_sha256'] != digest(ROOT / 'native/c6_r4/field.cpp') or record['binary_sha256'] != digest(ROOT / 'build/c6_r4/field.dylib'):
        raise RuntimeError('native identity mismatch')


def failures(stats, detector):
    checks = {
        'membership': stats['size'] >= detector['min_size'] and stats['membership_jaccard'] >= detector['membership_jaccard'],
        'shape': stats['shape_cv'] <= detector['shape_cv'],
        'mode_lock': stats['lock_std'] <= detector['lock_std'],
        'frequency_stationarity': stats['freq_change'] <= detector['freq_tol'],
        'phase_pattern': stats['pattern_change'] <= detector['pattern_tol'],
    }
    return [name for name, passed in checks.items() if not passed]


def native_without_build(spec):
    # Check before the original loader, then pin its existing handle. No loader
    # replacement or build fallback is called. Drift is checked at checkpoints.
    guard(spec)
    from geomind import c6_r4_field as F
    lib, record = F.native()
    if record != spec['native_build']:
        raise RuntimeError('unexpected native identity after loader')
    return lib


def worker(pair, arm, output, spec):
    started = time.monotonic()
    cpu = time.process_time()
    row = {'pair': pair, 'arm': arm, 'status': 'INCOMPLETE', 'stage': 'setup', 'checks': [], 'timings': {}}
    path = output / f'pair_{pair:02d}_{arm}.json'

    def save():
        row['seconds'] = time.monotonic() - started
        row['cpu_seconds'] = time.process_time() - cpu
        raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        row['peak_rss_bytes'] = int(raw if sys.platform == 'darwin' else raw * 1024)
        row['serialization_started_after_seconds'] = row['seconds']
        at = time.monotonic()
        row['serialized_bytes'] = 0
        for _ in range(3):
            row['serialized_bytes'] = atomic(path, row)
        row['last_serialization_seconds'] = time.monotonic() - at

    def stop(_sig, _frame):
        raise InterruptedError('parent cancellation')

    signal.signal(signal.SIGTERM, stop)
    save()
    try:
        native_without_build(spec)
        import numpy as np
        from geomind import c6_r4_field as F, c6_r4_field_assay as A, c6_r4_field_protocol as P
        from geomind.c6_r4_integrity import validate_pin
        row['source_pin'] = validate_pin(ROOT)
        s = P.load_settings()
        if s != spec['settings']:
            raise RuntimeError('settings mismatch')
        row['native_build'] = spec['native_build']
        row['timings']['setup'] = {'wall':time.monotonic()-started,'cpu':time.process_time()-cpu}
        entropy = spec['pilot_entropy']
        # An external checkpointing subclass observes completed original calls.
        # It does not change the loader, equations, assays or their inner loops.
        class ObservedGrid(A.GridSet):
            def clone(self):
                return ObservedGrid(self.owners, self.s, self.checks)

            def run(self, duration, scope, sample_dt=None):
                try:
                    return super().run(duration, scope, sample_dt)
                finally:
                    guard(spec)
                    row['last_scope'] = scope
                    save()

        background = ObservedGrid([F.medium(P.rng(entropy, pair, 1), s['model'])] * 3, s, row['checks'])
        row['background_before_quiet'] = [P.snapshot(o) for o in background.owners]
        row['stage'] = 'quiet_background'
        at = time.monotonic(); acpu = time.process_time()
        quiet_flow = background.run(spec['quiet_duration'], 'quiet')
        row['quiet_prefix_by_dt'] = [f.tolist() for f in quiet_flow]
        row['quiet_end_states'] = [P.snapshot(o) for o in background.owners]
        row['timings']['quiet'] = {'wall': time.monotonic()-at, 'cpu': time.process_time()-acpu}
        q = background.owners[0].q
        indices = sorted(range(len(q)), key=lambda i: (float(np.linalg.norm(q[i] - [2., 0.])), background.owners[0].site_ids[i]))[:8]
        phases = P.rng(entropy, pair, 90).uniform(-np.pi, np.pi, 8)
        row['patch_site_ids'] = [background.owners[0].site_ids[i] for i in indices]
        row['patch_phases'] = phases.tolist()
        if arm == 'H':
            for o in background.owners:
                o.z[indices] = spec['patch_radius'] * np.exp(1j*phases)
        boundary = spec['amplitude_boundary']
        if any(int(np.sum(np.abs(o.z) > boundary)) != (0 if arm == 'Q' else 8) for o in background.owners):
            raise RuntimeError('background construction high-site count mismatch')
        row['initial_background'] = [P.snapshot(o) for o in background.owners]
        states = [F.population(P.rng(entropy, pair, 10, 1, 0), o, 1, 0, s['elements']) for o in background.owners]
        grid = ObservedGrid(states, s, row['checks'])
        c = grid.owners[0].cohorts[-1]
        row['paired_material'] = {'x': c.x.tolist(), 'theta': c.theta.tolist(), 'rates': c.rates.tolist(), 'ids': list(c.ids), 'tokens': list(c.tokens)}
        row['perturbations'] = {k:v.tolist() for k,v in P.physical_perturbations(P.rng(entropy,pair,20,1,0), grid.owners[0]).items()}
        pert = {k:np.array(v) for k,v in row['perturbations'].items()}
        row['introduced_states'] = [P.snapshot(o) for o in grid.owners]
        row['stage'] = 'formation'; at = time.monotonic(); acpu = time.process_time(); save()
        prefix = grid.run(s['formation'], arm+'/formation')
        row['formation_prefix_by_dt'] = [f.tolist() for f in prefix]
        row['formation_end_states'] = [P.snapshot(o) for o in grid.owners]
        row['timings']['formation'] = {'wall':time.monotonic()-at,'cpu':time.process_time()-acpu}
        row['stage'] = 'qualification'; save(); at = time.monotonic(); acpu = time.process_time()
        qualification = A.qualification(grid, prefix, pert, arm+'/qualification')
        row['qualification'] = qualification
        for candidate in qualification['candidates']:
            candidate['structural_failures'] = failures(candidate['stats'], s['detector'])
        row['finer_structural_rows'] = 'not emitted by existing qualification helper; raw finer prefixes retained'
        row['timings']['qualification'] = {'wall':time.monotonic()-at,'cpu':time.process_time()-acpu}
        row['retention'] = {'applicable': False, 'retained': False}
        continuation = None
        if qualification['qualified']:
            row['stage'] = 'continuation'; save(); at = time.monotonic(); acpu = time.process_time()
            retained = grid.clone()
            members = qualification['selected_members']
            for o in retained.owners:
                o.cohorts[-1].selected = tuple(members)
                o.cohorts[-1].output = 0.
            continuation = retained.run(spec['continuation_duration'], arm+'/structural-continuation')
            row['continuation_by_dt'] = [f.tolist() for f in continuation]
            row['continuation_end_states'] = [P.snapshot(o) for o in retained.owners]
            rolling = [P.rolling_persistence(prefix[k], continuation[k], retained.owners[k], members, s) for k in range(3)]
            for rows in rolling:
                for entry in rows:
                    entry['structural_failures'] = failures(entry['stats'], s['detector'])
            masks = [[r['passed'] for r in rows] for rows in rolling]
            if masks[1:] != [masks[0], masks[0]]:
                raise A.NumericalFailure('grid-dependent structural retention')
            row['retention'] = {'applicable':True, 'retained':all(masks[0]), 'rolling_by_dt':rolling,
                                'first_loss_by_dt':[next((r for r in rows if not r['passed']),None) for rows in rolling]}
            row['timings']['continuation'] = {'wall':time.monotonic()-at,'cpu':time.process_time()-acpu}
        row['carrier_actual_amplitudes_by_stage'] = {}
        patch_ok = True
        for label, flows in [('formation',prefix), ('continuation',continuation)]:
            if flows is None:
                continue
            records = []
            for f in flows:
                ns = len(q); offset = 2*ns + 3*s['elements']
                actual = np.abs(f[:,:2*ns].copy().view('c16'))
                carrier = np.abs(f[:,offset:offset+2*ns].copy().view('c16'))
                good = bool(np.all(carrier < boundary)) if arm == 'Q' else bool(np.all(carrier[:,indices] > boundary))
                patch_ok = patch_ok and good
                records.append({'actual':actual.tolist(),'carrier':carrier.tolist(),'condition_held':good})
            row['carrier_actual_amplitudes_by_stage'][label] = records
        row['background_condition_held'] = patch_ok
        row['status'] = 'COMPLETE'
        row['stage'] = 'complete'
        guard(spec)
    except (Exception, KeyboardInterrupt) as exc:
        row['status'] = 'INCOMPLETE'
        row['error'] = {'type':type(exc).__name__,'message':str(exc)}
    finally:
        save()
    return 0 if row['status'] == 'COMPLETE' else 2


def process_usage(groups):
    """Sample every process in owned groups, including descendants."""
    listing = subprocess.check_output(['ps','-axo','pid=,pgid=,rss=,time='], text=True, timeout=2)
    result = {g:{'cpu':0.,'rss':0,'pids':[]} for g in groups}
    for line in listing.splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        pid, group, rss = map(int, fields[:3])
        if group in result:
            parts = fields[3].split(':')
            seconds = sum(float(v)*60**i for i,v in enumerate(reversed(parts)))
            result[group]['cpu'] += seconds
            result[group]['rss'] += rss*1024
            if rss > 0: result[group]['pids'].append(pid)
    return result


def signal_owned(pid, sig):
    try:
        os.killpg(pid, sig)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS can return EPERM for an exited/zombie-only group. Never
        # suppress a permission failure while an owned process is alive.
        if process_usage([pid])[pid]['pids']:
            raise


def cancel(active, grace=5.):
    for pid in active:
        got, status, usage = os.wait4(pid, os.WNOHANG)
        if got: active[pid]['reaped'] = (status,usage)
        signal_owned(pid, signal.SIGTERM)
    deadline = time.monotonic()+grace
    while active and time.monotonic()<deadline:
        for pid in list(active):
            if 'reaped' in active[pid]:
                continue
            got, status, usage = os.wait4(pid, os.WNOHANG)
            if got:
                active[pid]['reaped'] = (status,usage)
        if all('reaped' in info for info in active.values()):
            break
        time.sleep(.05)
    # Kill surviving group descendants even when the direct child exited.
    for pid in active:
        signal_owned(pid, signal.SIGKILL)
    for pid, info in active.items():
        if 'reaped' not in info:
            _, status, usage = os.wait4(pid, 0)
            info['reaped'] = (status,usage)


def interpret(rows):
    by = {(r['pair'],r['arm']):r for r in rows}
    raw = []
    for pair in range(16):
        q, h = by.get((pair,'Q')), by.get((pair,'H'))
        raw.append({'pair':pair,'Q':None if not q or q['status']!='COMPLETE' else q['qualification']['qualified'],
                    'H':None if not h or h['status']!='COMPLETE' else h['qualification']['qualified'],
                    'Q_retained':None if not q or q['status']!='COMPLETE' else q['retention']['retained'],
                    'H_retained':None if not h or h['status']!='COMPLETE' else h['retention']['retained']})
    out = {'paired_outcomes':raw,'status':'INCOMPLETE','denominator_per_arm':16}
    if len(by)!=32 or any(r['status']!='COMPLETE' for r in rows):
        return out
    for pair in range(16):
        q, h = by[pair,'Q'], by[pair,'H']
        if q['paired_material'] != h['paired_material'] or q['perturbations'] != h['perturbations']:
            out['pairing_error'] = pair
            return out
    qcount = sum(r['Q'] for r in raw); hcount = sum(r['H'] for r in raw)
    out.update(status='COMPLETE', Q_qualified=qcount,H_qualified=hcount,
               quiet_ceiling='STRENGTHENED' if qcount>=14 else 'WEAKENED' if qcount<=8 else 'INDETERMINATE',
               patch_held=all(r['background_condition_held'] for r in rows))
    for label,qkey,hkey in [('qualification','Q','H'),('structural_retention','Q_retained','H_retained')]:
        forward = [r['pair'] for r in raw if r[qkey] and not r[hkey]]
        reverse = [r['pair'] for r in raw if r[hkey] and not r[qkey]]
        association = []
        for pair in forward:
            h = by[pair,'H']
            if label == 'qualification':
                candidates = h['qualification']['candidates']
                linked = not any(c['structural'] for c in candidates) and any(c['structural_failures']==['frequency_stationarity'] for c in candidates)
            else:
                loss = h['retention'].get('first_loss_by_dt',[])
                linked = h['qualification']['qualified'] and len(loss)==3 and all(r and r['structural_failures']==['frequency_stationarity'] for r in loss)
            if linked: association.append(pair)
        delta = sum(r[qkey] for r in raw)-sum(r[hkey] for r in raw)
        out[label] = {'Q_successes':sum(r[qkey] for r in raw),'H_successes':sum(r[hkey] for r in raw),
                      'difference':delta,'Q_success_H_failure':forward,'H_success_Q_failure':reverse,
                      'stationarity_associated_pairs':association,
                      'suppression_signal':out['patch_held'] and delta>=4 and len(forward)>=4}
    out['apparatus_mechanism'] = 'INDETERMINATE' if not out['patch_held'] else 'SUPPLIED_BACKGROUND_CONTRAST_ONLY'
    return out


def supervisor_cpu():
    children=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.process_time()+children.ru_utime+children.ru_stime


def supervise(spec, output, fake=None):
    start = time.monotonic(); cpu_start = supervisor_cpu()
    caps = spec['caps']; active = {}; accounting = []; pending = list(spec['schedule']); stopped = None
    summary = {'kind':'EXPLORATORY_NOT_C6_EVIDENCE','status':'INCOMPLETE','accounting':accounting,'stop_reason':None,
               'spec_sha256':digest(SPEC),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    try:
        if fake is None: guard(spec)
        while pending or active:
            if supervisor_cpu()-cpu_start >= caps['cpu_seconds']:
                stopped = 'AGGREGATE_CPU_CAP'; break
            if time.monotonic()-start >= caps['cancel_wall_seconds']:
                stopped = 'GLOBAL_WALL_CANCELLATION'; break
            while pending and len(active)<caps['workers']:
                pair,arm = pending.pop(0)
                if fake is None:
                    command = [sys.executable,str(Path(__file__).resolve()),'--worker',str(pair),arm,'--output',str(output)]
                else:
                    command = [sys.executable,'-c',fake,str(output),str(pair),arm]
                log = (output/f'pair_{pair:02d}_{arm}.log').open('wb')
                child = subprocess.Popen(command, cwd=ROOT, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
                active[child.pid] = {'pair':pair,'arm':arm,'start':time.monotonic(),'log':log,'child':child,'peak_group_rss_bytes':0}
            usage = process_usage(active)
            cpu_total = supervisor_cpu()-cpu_start+sum(v['cpu'] for v in usage.values())
            if cpu_total>=caps['cpu_seconds']:
                stopped = 'AGGREGATE_CPU_CAP'; break
            for pid,info in list(active.items()):
                measured = usage[pid]; info['peak_group_rss_bytes']=max(info['peak_group_rss_bytes'],measured['rss'])
                if measured['rss']>caps['worker_rss_bytes']:
                    stopped = 'WORKER_RSS_CAP'; break
                if time.monotonic()-info['start']>=caps['arm_wall_seconds']:
                    stopped = 'ARM_WALL_CAP'; break
                got,status,rusage = os.wait4(pid,os.WNOHANG)
                if got:
                    info['child'].returncode = os.waitstatus_to_exitcode(status)
                    info['log'].close()
                    raw_rss = int(rusage.ru_maxrss)*(1 if sys.platform=='darwin' else 1024)
                    receipt = {'pair':info['pair'],'arm':info['arm'],'exit_code':info['child'].returncode,
                               'seconds':time.monotonic()-info['start'],'cpu_seconds':rusage.ru_utime+rusage.ru_stime,
                               'peak_rss_bytes':max(raw_rss,info['peak_group_rss_bytes'])}
                    accounting.append(receipt); del active[pid]
                    path = output/f"pair_{info['pair']:02d}_{info['arm']}.json"
                    if receipt['exit_code']!=0 or not path.is_file() or json.loads(path.read_text()).get('status')!='COMPLETE':
                        stopped = 'INCOMPLETE_WORKER'; break
                    if fake is None:
                        other_arm='H' if info['arm']=='Q' else 'Q'
                        other_path=output/f"pair_{info['pair']:02d}_{other_arm}.json"
                        if other_path.is_file():
                            this=json.loads(path.read_text());other=json.loads(other_path.read_text())
                            if other['status']=='COMPLETE' and (this['paired_material']!=other['paired_material'] or this['perturbations']!=other['perturbations']):
                                stopped='PAIRED_INPUT_MISMATCH';break
                    if receipt['peak_rss_bytes']>caps['worker_rss_bytes']:
                        stopped = 'WORKER_PEAK_RSS_CAP'; break
            if stopped: break
            atomic(output/'PROGRESS.json', {'elapsed_seconds':time.monotonic()-start,'cpu_seconds':cpu_total,
                                          'accounting':accounting,'active':[{k:v for k,v in i.items() if k in ('pair','arm','start','peak_group_rss_bytes')} for i in active.values()],
                                          'pending':pending})
            time.sleep(.1)
    except (Exception, KeyboardInterrupt) as exc:
        stopped = type(exc).__name__+': '+str(exc)
    finally:
        cancel(active)
        for info in active.values():
            status,ru = info['reaped']; info['child'].returncode=os.waitstatus_to_exitcode(status);info['log'].close()
            accounting.append({'pair':info['pair'],'arm':info['arm'],'exit_code':info['child'].returncode,
                               'seconds':time.monotonic()-info['start'],'cpu_seconds':ru.ru_utime+ru.ru_stime,
                               'peak_rss_bytes':max(int(ru.ru_maxrss)*(1 if sys.platform=='darwin' else 1024),info['peak_group_rss_bytes']), 'cancelled':True})
        rows = [json.loads(p.read_text()) for p in sorted(output.glob('pair_*.json'))]
        summary['interpretation'] = interpret(rows) if fake is None else {'status':'HARNESS_ONLY'}
        if fake is None:
            try: guard(spec)
            except Exception as exc: stopped='DEPENDENCY_DRIFT: '+str(exc)
        summary['stop_reason']=stopped
        summary['unsubmitted']=pending
        summary['missing_arms']=[entry for entry in spec['schedule'] if not any(r.get('pair')==entry[0] and r.get('arm')==entry[1] and r.get('status')=='COMPLETE' for r in rows)]
        summary['status']='COMPLETE' if not stopped and len(accounting)==len(spec['schedule']) and summary['interpretation']['status']=='COMPLETE' else 'INCOMPLETE'
        summary['seconds']=time.monotonic()-start
        summary['cpu_seconds']=supervisor_cpu()-cpu_start
        summary['artifact_hashes']={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='SUMMARY.json'}
        summary['serialized_artifact_bytes']=sum(p.stat().st_size for p in output.iterdir() if p.is_file())
        atomic(output/'SUMMARY.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--worker',nargs=2)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    spec=json.loads(SPEC.read_text())
    if args.worker:
        return worker(int(args.worker[0]),args.worker[1],args.output,spec)
    if not args.run: parser.error('use --run for the single authorized execution')
    # An exclusive directory is the durable one-shot latch; never resume/retry.
    output=HERE/'run'
    output.mkdir()
    atomic(output/'RUN_STARTED.json', {'spec_sha256':digest(SPEC),'pid':os.getpid(),'no_retry':True})
    def parent_stop(_sig,_frame):
        raise InterruptedError('external parent cancellation')
    signal.signal(signal.SIGTERM,parent_stop)
    result=supervise(spec,output)
    print(json.dumps({'status':result['status'],'seconds':result['seconds'],'stop_reason':result['stop_reason'],'interpretation':result['interpretation']}),flush=True)
    return 0 if result['status']=='COMPLETE' else 2

if __name__=='__main__':
    sys.exit(main())
