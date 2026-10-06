"""Owner-authorized section-10 launch harness; reviewed physics APIs unchanged.

Run cost first, inspect COST.json, then full. No retry/resume or judging API.
Each worker owns an intact/control pair. All protocol operations use Run.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import time
import traceback

from .run import Run
from .evaluator import freeze, copy_template
from .protocol import Calibration, rotation, permutation, bindings, action, oriented
from .readouts import seed_unit, aggregate
from ..world.world import World

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / 'development_20261006'
SEEDS = {'task_blind': list(range(106061, 106069)),
         'reward': list(range(106071, 106079))}
COST_SEED = 106060


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def identity():
    subprocess.run(['git', 'merge-base', '--is-ancestor', '6bdc82e', 'HEAD'], cwd=ROOT, check=True)
    manifest = json.loads((HERE/'_build/build.json').read_text())
    files = dict(manifest['source_sha256'])
    for folder in ('runner', 'medium', 'world'):
        for p in (HERE.parent/folder).glob('*.py'):
            if p.name != 'section10.py':
                rel = str(p.relative_to(ROOT))
                # Pin reviewed tracked sources, excluding this additive harness.
                if subprocess.run(['git','ls-files','--error-unmatch',rel], cwd=ROOT,
                                  capture_output=True).returncode == 0:
                    reviewed = subprocess.check_output(['git','show',f'6bdc82e:{rel}'], cwd=ROOT)
                    assert sha(p) == hashlib.sha256(reviewed).hexdigest(), rel
                    files[rel] = sha(p)
    for rel, expected in files.items():
        assert sha(ROOT/rel) == expected, rel
    rrg = json.loads((ROOT/'research/rrg/v0.2.1.import.json').read_text())
    for rel, expected in rrg['file_sha256'].items():
        assert sha(ROOT/'research/rrg/v0.2.1'/rel) == expected, rel
    assert sha(HERE.parents[1]/'DESIGN_0H.md') == '39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925'
    from .native import library
    library()  # Validates source, binary, dependencies, ABI and NumPy identity.
    return {'time': now(), 'head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'reviewed_runner_commit': '6bdc82e', 'source_sha256': files,
            'harness_sha256': sha(__file__), 'build': manifest,
            'rrg_files_verified': len(rrg['file_sha256']), 'design_revision':'5.1',
            'authorization':'owner request; decision 0028 items 17-19',
            'cost_seed':COST_SEED, 'seeds':SEEDS, 'worker_process_limit':8,
            'training_namespace':'dev; episode seeds 0..1999 (cost 0..199)',
            'medium_domains':'initial; kick:<world_step>; g0_control',
            'calibration_namespace':'validation 0..255',
            'evaluation_namespace':'validation 0..127', 'judging_used':False}


class LedgerView:
    """Give the reviewed seed_unit iterable ledgers instead of JSON receipts.

    Run.report uses file receipts with audit_dir; seed_unit expects event rows.
    This adapter changes only the transport representation, no measurement.
    """
    def __init__(self, run, report):
        self.run, self.value = run, dict(report, events=run.medium.events)

    def __getattr__(self, name):
        return getattr(self.run, name)

    def report(self):
        return self.value


def save_report(path, report):
    with gzip.open(path, 'wt') as stream:
        json.dump(report, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n')


def pair(seed, arm, calibration):
    start = time.perf_counter()
    rows = {t:Calibration(**c) for t,c in calibration.items()}
    directory = OUT/arm/str(seed)
    directory.mkdir(parents=True, exist_ok=False)
    intact = control = None
    try:
        intact = Run(seed, rows, arm=='reward', backend='native', audit_dir=directory/'intact')
        control = Run(seed, rows, arm=='reward', control=True, library=intact.library,
                      backend='native', audit_dir=directory/'control')
        try:
            for episode in range(2000):
                intact.episode(episode)
                control.episode(episode, intact)
                if (episode+1)%20 == 0:
                    write(directory/'PROGRESS.json', {'time':now(), 'stage':'training',
                        'episodes':episode+1, 'snapshots':len(intact.snapshots),
                        'intact_N':len(intact.medium.native), 'control_N':len(control.medium.native),
                        'elapsed_seconds':time.perf_counter()-start})
            write(directory/'PROGRESS.json', {'time':now(), 'stage':'evaluation', 'episodes':2000})
            intact.evaluate()
            control.evaluate()
        except (Exception, KeyboardInterrupt) as error:
            intact.invalid = control.invalid = f'{type(error).__name__}: {error}'
            (directory/'ERROR.txt').write_text(traceback.format_exc())
        a, b = intact.report(), control.report()
        unit = seed_unit(LedgerView(intact,a), LedgerView(control,b))
        save_report(directory/'REPORT.json.gz', {'intact':a,'control':b})
        write(directory/'UNIT.json', unit)
        write(directory/'PROGRESS.json', {'time':now(), 'stage':'INVALID' if unit['invalid'] else 'complete',
            'episodes':a['exposure']['training_episodes'], 'elapsed_seconds':time.perf_counter()-start})
        return unit
    except BaseException:
        (directory/'FATAL.txt').write_text(traceback.format_exc())
        raise
    finally:
        if control is not None:
            control.close()
        if intact is not None:
            intact.close()


def projection(report):
    timing = report['timing']
    steps = report['exposure']['training_steps']
    checks = report['exposure']['qualification_frames']/601
    evaluator = report['exposure']['evaluator_episodes']
    assert steps == 32000 and checks == 52 and evaluator >= 128
    parts = {'training':timing['training']/steps*10240000,
             'qualification':timing['qualification']/checks*8512,
             'recovery':timing['recovery']/checks*8512,
             'evaluation_at_20_snapshot_cap':timing['evaluation']/evaluator*344064}
    return {'stage_projected_seconds':parts, 'serial_hours':sum(parts.values())/3600,
            'training_seconds_per_step':timing['training']/steps,
            'qualification_seconds_per_check':timing['qualification']/checks,
            'recovery_seconds_per_check':timing['recovery']/checks,
            'evaluation_seconds_per_episode':timing['evaluation']/evaluator,
            'training_steps':10240000, 'intact_checks':8512, 'maximum_evaluator_episodes':344064,
            'method':'observed stage rates; evaluation projected at full fixed 20-snapshot cap',
            'limitations':'One task-blind development seed; later population, candidate mix, reward/control rates, disk and host load may differ. Recovery rate includes observed zero-candidate checks. Evaluation copy sizes may differ; no upper runtime bound claimed.',
            'reported_above_design_24h_line':sum(parts.values())>24*3600,
            'owner_60h_stop':sum(parts.values())>60*3600}


def cost():
    OUT.mkdir(exist_ok=False)
    write(OUT/'IDENTITY.json', identity())
    started = time.perf_counter()
    rows, frozen = freeze()
    write(OUT/'CALIBRATION.json', frozen)
    calibration_seconds = time.perf_counter()-started
    if not frozen['usable']:
        raise RuntimeError('INVALID: zero usable tasks')
    directory = OUT/'cost'/str(COST_SEED)
    run = Run(COST_SEED, rows, episodes=200, backend='native', audit_dir=directory)
    try:
        for episode in range(200):
            run.episode(episode)
            if (episode+1)%20 == 0:
                status = {'stage':'cost training','episodes':episode+1,'N':len(run.medium.native),
                          'snapshots':len(run.snapshots),'seconds':time.perf_counter()-started}
                write(OUT/'COST_PROGRESS.json',status)
                print(json.dumps(status),flush=True)
        write(OUT/'COST_PROGRESS.json',{'stage':'cost evaluation','snapshots':len(run.snapshots)})
        run.evaluate()
        report = run.report()
        save_report(OUT/'COST_RUN.json.gz',report)
        result = {'status':'COMPLETE','seed':COST_SEED, 'episodes':200,
                  'calibration_seconds':calibration_seconds, 'measured_stage_seconds':run.timing,
                  'exposure':run.exposure, 'snapshots':len(run.snapshots),
                  'wall_seconds':time.perf_counter()-started, 'projection':projection(report)}
        write(OUT/'COST.json', result)
        print(json.dumps(result),flush=True)
    except BaseException as error:
        run.invalid = f'{type(error).__name__}: {error}'
        save_report(OUT/'COST_PARTIAL.json.gz',run.report())
        (OUT/'COST_ERROR.txt').write_text(traceback.format_exc())
        raise
    finally:
        run.close()


def full():
    measured = json.loads((OUT/'COST.json').read_text())
    if measured['projection']['owner_60h_stop']:
        raise RuntimeError('STOP: measured projection exceeds owner 60h serial limit')
    prior = json.loads((OUT/'IDENTITY.json').read_text())
    current = identity()
    assert prior['source_sha256']==current['source_sha256']
    assert prior['harness_sha256']==current['harness_sha256']
    assert prior['build']==current['build']
    calibration = json.loads((OUT/'CALIBRATION.json').read_text())['calibration']
    started = time.perf_counter()
    units = {'task_blind':[], 'reward':[]}
    with ProcessPoolExecutor(max_workers=8,mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = {pool.submit(pair,SEEDS[arm][i],arm,calibration):arm
                   for i in range(8) for arm in SEEDS}
        for future in as_completed(futures):
            arm = futures[future]
            units[arm].append(future.result())
            print(json.dumps({'arm':arm,'completed':len(units[arm]),'seconds':time.perf_counter()-started}),flush=True)
    results = {arm:aggregate(sorted(rows,key=lambda r:r['seed'])) for arm,rows in units.items()}
    write(OUT/'RESULTS.json',{'time':now(),'wall_seconds':time.perf_counter()-started,'arms':results})
    summarize()


def export_replay(arm, seed, report):
    if not report['snapshots']:
        return None
    snapshot = report['snapshots'][0]
    task = report['evaluations'][0]['best_task']
    medium = copy_template(snapshot['template'])
    frames = []
    try:
        with World(task,0,'validation') as world:
            while not world.observe().done:
                observation = world.observe()
                drives = bindings(task,observation,permutation(0),medium.time)
                medium.integrate(drives)
                chosen = action(task,observation,medium.native,medium.time)
                frames.append({'time':medium.time,
                    'elements':[[e.id,e.x,e.y,e.phase,e.rate,medium.native.gain(e.id)] for e in medium.native.elements],
                    'drives':[[getattr(d,f) for f,_ in d._fields_] for d in drives],
                    'action':[chosen.angle,chosen.magnitude,chosen.choice]})
                world.step(chosen)
            score = oriented(task,world.score())
        filename = OUT/f'REPLAY_{arm}.json.gz'
        save_report(filename,{'label':'additional diagnostic export; no learning or read-out selection',
            'arm':arm,'source_seed':seed,'type_id':snapshot['type_id'],'snapshot':snapshot,
            'task':task,'namespace':'validation','episode_seed':0,'backend':'reference',
            'assignment':permutation(0),'frames':frames,'oriented_score':score,
            'additional_exposure':{'diagnostic_evaluator_episodes':1,'world_steps':len(frames)}})
        return filename.name
    finally:
        medium.close()


def summarize():
    cost_value = json.loads((OUT/'COST.json').read_text())
    lines = ['INCOMPLETE','', 'Owner-authorized exploratory development; DESIGN_0H revision 5.1, decision 0028 items 17–19.',
             'Implementer: Codex (GPT-6). Not milestone acceptance or scientific qualification.', '',
             'Expected cost announced before execution: 21–55 serial hours; ideal 3–7 wall hours at eight workers, subject to contention.',
             f"Measured cost seed {COST_SEED}: 200 episodes, {cost_value['wall_seconds']:.3f} wall seconds including calibration.",
             f"Measured serial projection: {cost_value['projection']['serial_hours']:.3f} hours at the full 20-snapshot evaluator cap.",
             'Stage rates, projection arithmetic, exposure and limitations: [COST.json](development_20261006/COST.json).',
             'The 24-hour report line is retained; owner authorized continuation through 60 serial hours.', '']
    results_path = OUT/'RESULTS.json'
    if not results_path.exists():
        lines += ['Full run NOT_RUN: measured projection exceeds 60 serial hours.' if cost_value['projection']['owner_60h_stop'] else 'Full run pending.',
                  "G0, G0', G1, G1c and G5: NOT_RUN for each arm; no development verdict inferred from the cost seed.",
                  'Qualified-atom replay per arm: NOT_RUN (no full arm executed).']
    else:
        results = json.loads(results_path.read_text())
        verdicts = [v for arm in results['arms'].values() for v in arm['readouts'].values() if v!='DESCRIPTIVE']
        lines[0] = next((v for v in ('INVALID','FAIL','INCONCLUSIVE') if v in verdicts),'PASS')
        lines += [f"Full-run wall time: {results['wall_seconds']/3600:.3f} hours; maximum eight worker processes.", '',
                  "| Arm | G0 | G0' | G1 | G1c | G5 |", '|---|---|---|---|---|---|']
        for arm,result in results['arms'].items():
            r = result['readouts']
            lines.append('| '+arm+' | '+' | '.join(r[k] for k in ('G0',"G0'",'G1','G1c','G5'))+' |')
        lines += ['', 'Ordered rules: execution/measurement failure, nonfinite data, zero usable tasks or incomplete protocol → INVALID first. G0 requires both coverage and competence superiority in ≥6 unflagged seeds; ≤ on both in ≥6 gives FAIL; drops prevent PASS. G0\' requires |slope|≤0.5 per 100 episodes and no late rejection/protected over-budget state in ≥6 seeds; ≥3 outside gives FAIL. G1 requires snapshots in ≥6 seeds for PASS, ≤2 for FAIL. G1c is descriptive. G5: INVALID first; <6 snapshot-bearing seeds → INCONCLUSIVE; fractions D≤0.1 of ≥0.8 in ≥6 bearing seeds → PASS; fractions <0.5 in ≥3 → FAIL; otherwise INCONCLUSIVE.', '',
                  'Seed units, G0 coverage denominators and paired competencies, flags, control additions/deaths/retries/drops, D3 removals, late turnover, snapshot counts, G1c per-task/best-task values and G5 differences: [RESULTS.json](development_20261006/RESULTS.json).', '',
                  '| Arm / seed / policy | Steps | Episodes | Qualification frames | Recovery simulated s | Evaluator episodes | Reward episodes | Training / qualification / recovery / evaluation measured s | Peak/final learned coefficients | Final/peak position-phase scalars | Copies |',
                  '|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|']
        totals = {k:0. for k in ('training','qualification','recovery','evaluation')}
        replays = {}
        for arm in SEEDS:
            for seed in SEEDS[arm]:
                with gzip.open(OUT/arm/str(seed)/'REPORT.json.gz','rt') as stream:
                    pair_report = json.load(stream)
                for policy,r in pair_report.items():
                    e,a,t = r['exposure'],r['accounting'],r['timing']
                    for key in totals:
                        totals[key] += t[key]
                    lines.append(f"| {arm}/{seed}/{policy} | {e['training_steps']} | {e['training_episodes']} | {e['qualification_frames']} | {e['recovery_simulated_seconds']:.3f} | {e['evaluator_episodes']} | {e['reward_episodes']} | "+' / '.join(f'{t[k]:.3f}' for k in totals)+f" | {a['peak_learned_coefficients']}/{a['final_learned_coefficients']} | {a['retained_position_phase_scalars']}/{a['peak_position_phase_scalars']} | {a['evaluation_copies']} |")
                if arm not in replays and pair_report['intact']['snapshots']:
                    replays[arm] = export_replay(arm,seed,pair_report['intact'])
        write(OUT/'STAGE_TOTALS.json',totals)
        lines += ['', 'Measured full-run summed stage costs: '+', '.join(f'{k} {v/3600:.3f} h' for k,v in totals.items())+'.',
                  'Template scalar storage per content hash, complete snapshots with recovery timescales and flags, final templates, evaluator-copy identities, episodes, pending state and raw ledger receipts are retained in each seed’s REPORT.json.gz. Coefficient accounting is not RAM usage or an efficiency comparison.']
        for arm in SEEDS:
            lines += [f"Qualified atom export ({arm}): [{replays[arm]}](development_20261006/{replays[arm]}); one additional diagnostic validation episode, excluded from read-outs." if arm in replays else f'Qualified atom export ({arm}): none; no qualified snapshot in this arm.']
        lines += ['Stop-row responsibility: drafter if task-blind G1 FAIL or any G0\' FAIL; report INVALID with raw evidence. Any protocol change requires a new design revision and fresh development seeds. Owner decides any next development step.']
    lines += ['', 'All event logs and drive schedules are retained losslessly as ordered JSONL. Recovery-complete events retain complete immutable check-time native state and 601 frames; drive schedules retain the 600-step replay. All admitted snapshots and templates are retained, including those beyond the evaluation cap. File hashes and sizes: [ARTIFACTS.json](development_20261006/ARTIFACTS.json).',
              'Calibration is frozen once on validation 0–255 and shared by cost, both arms and controls. Training uses dev episode seeds; control uses g0_control entropy. No judging namespace was used. Reviewed code, constants, schedules and receipt files were unchanged. The additive launch harness uses a ledger adapter to expose ordered event rows to the reviewed seed_unit function; receipts remain unchanged in stored reports.',
              'Driven/cohort-restricted structural snapshots do not establish autonomous persistence or internally maintained closure. G5 is numerical copy covariance. H-BG, H-PS and H-RBG are NOT_TESTED; combinations and efficiency yardsticks remain deferred.']
    (HERE/'DEVELOPMENT_REPORT.md').write_text('\n'.join(lines)+'\n')
    artifacts = {str(p.relative_to(HERE)):{'sha256':sha(p),'bytes':p.stat().st_size}
                 for p in OUT.rglob('*') if p.is_file() and p.name!='ARTIFACTS.json'}
    write(OUT/'ARTIFACTS.json', artifacts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('cost','full','identity','report'))
    arguments = parser.parse_args()
    if arguments.stage == 'identity':
        print(json.dumps(identity(),indent=2))
    elif arguments.stage == 'cost':
        cost()
    elif arguments.stage == 'report':
        summarize()
    else:
        full()
