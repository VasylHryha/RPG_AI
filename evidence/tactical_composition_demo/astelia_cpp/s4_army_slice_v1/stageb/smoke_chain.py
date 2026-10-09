"""Tiny real-binary round-1 wiring chain. Every write is inside a new scratch root."""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import secrets
import sys
import time
from unittest.mock import patch

import runtime as r
import owner_approvals as approvals


@contextlib.contextmanager
def scratch_context(root, test_mode):
    import common, train, training, data, parity, calibrated_parity, jobs, execution, readout_run, dagger
    # Imported aliases must also follow the scratch directory. HERE/BINARY stay
    # authoritative: use the existing environment, source chain and actual host.
    with contextlib.ExitStack() as stack:
        for module in (r, common, training, data, parity, calibrated_parity, jobs, r.collect):
            stack.enter_context(patch.object(module, 'LOCAL', root))
        stack.enter_context(patch.object(train, 'ROOT', root))
        stack.enter_context(patch.object(parity, 'RECEIPT_DIRECTORY', root/'parity'))
        stack.enter_context(patch.object(jobs, 'locked', contextlib.nullcontext))
        stack.enter_context(patch.dict(os.environ, {'STAGEA_HOST_TEST':'1'} if test_mode else {}))
        stack.enter_context(patch.object(training, 'MONITOR', None))
        stack.enter_context(patch.object(parity, 'MONITOR', None))
        stack.enter_context(patch.object(parity, 'DEADLINE', None))
        stack.enter_context(patch.object(training, 'objective', training.objective))
        yield


@contextlib.contextmanager
def admission(root, seconds, test_mode):
    # Read-only open of the existing repository lock: no shared files written.
    with contextlib.ExitStack() as stack:
        if not test_mode:
            shared = r.CPP/'s4_net_slice_v1/_local/collection/RUN.lock'
            file = stack.enter_context(shared.open('rb'))
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        file = stack.enter_context((root/'RUN.lock').open('a'))
        fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not test_mode:
            gate = r.common.load('stageb_smoke_process_gate', r.CPP/'s4_net_slice_v1/process_gate.py')
            gate.GATE_PATH = root/'PROCESS_GATE.json'
            gate.process_gate(wait=False, deadline=time.monotonic()+seconds)
        monitor = approvals.Monitor(test_mode)
        monitor.live_memory(os.getpid())
        yield approvals.Deadline(seconds), monitor


def run(round, test_mode=False, scratch_root=None):
    if round != 1: raise ValueError('Stage B smoke supports round 1 only')
    allowed = (r.HERE/'_local/smoke').resolve()
    root = Path(scratch_root).resolve() if scratch_root else allowed/('test_' if test_mode else 'host_')/secrets.token_hex(8)
    if not root.is_relative_to(allowed) or root == allowed:
        raise ValueError('smoke scratch must be a new directory under stageb/_local/smoke')
    root.mkdir(parents=True, exist_ok=False)
    cfg = approvals.load()
    receipt = dict(schema=1, round=round, status='FAIL', mode='TEST_MODE' if test_mode else 'HOST_GATED',
        scope='fixture wiring only; no production budget, checkpoint, ledger, seeds or outcome claim',
        scratch_root=str(root), steps=[], resource_budget=cfg['resources'],
        time_budget_seconds=cfg['smoke']['cap_seconds'], process_gate=not test_mode)
    started = time.monotonic(); failure = None
    import train, training, parity, calibrated_parity, execution, readout_run, loss
    from models import export
    import torch
    # Capture real parent information before redirecting all output locations.
    parent = train.ROOT/'round0'
    parent_budget = None
    receipt['sources'] = r.sources()
    def step(name, action):
        start = time.monotonic(); disk_before = __import__('shutil').disk_usage(root).free
        record = dict(name=name, status='FAIL')
        try:
            approvals.check_disk(root)
            if monitor is not None: monitor.peak = 0
            result = action()
            if monitor is not None: monitor.live_memory(os.getpid())
            record = dict(name=name, status='PASS', result=result)
        except Exception as error:
            record = dict(name=name, status='FAIL', error=type(error).__name__+': '+str(error))
            raise
        finally:
            # Also persist failed steps; downstream steps become NOT_RUN.
            record.update(seconds=time.monotonic()-start, python_peak_rss_bytes=approvals.rss(),
                native_peak_rss_bytes=monitor.peak if monitor is not None else 0,
                disk_free_before_bytes=disk_before, disk_free_after_bytes=__import__('shutil').disk_usage(root).free,
                scratch_bytes=sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),
                owner_approvals=approvals.snapshot(root/'owner_approvals'))
            receipt['steps'].append(record)
            r.write(root/'SMOKE_STAGEB.json', receipt)
            print(f"{name}: {record['status']} ({record['seconds']:.3f}s; RSS {record['python_peak_rss_bytes']}; disk free {record['disk_free_after_bytes']})", flush=True)
        return result
    monitor = None
    with scratch_context(root, test_mode):
        try:
            def preflight():
                nonlocal parent_budget
                import eval_revision
                parent_budget = eval_revision.verify(parent)
                # Explicitly undo the ROOT redirection for provenance/index gates.
                return dict(chain_head=r.sha(eval_revision.chain(parent)[-1][0]),
                    binary=r.collect.identity(), training_sources_unchanged=True)
            # Provenance needs the real train.ROOT while every writer stays scratch.
            real_root = parent.parent
            with patch.object(train, 'ROOT', real_root): step('preflight', preflight)
            training.environment()
            # Install only evaluator authority locally; production install mutates
            # global writers, so this bounded chain binds its own scratch receipts.
            with patch.object(calibrated_parity, 'passes', approvals.passes), \
                 patch.object(calibrated_parity, 'compare_calibrated', approvals.compare_calibrated), \
                 patch.object(calibrated_parity, 'stageb_float32_passes', approvals.float32_passes), \
                 contextlib.ExitStack() as lifecycle:
                admission_values = []
                def enter_admission():
                    nonlocal monitor
                    admission_values.append(lifecycle.enter_context(admission(root, cfg['smoke']['cap_seconds'], test_mode)))
                    monitor = admission_values[0][1]
                    return dict(process_gate=not test_mode, ram_discovery=not test_mode, scratch_lock=True)
                step('admission', enter_admission)
                deadline, monitor = admission_values[0]
                training.MONITOR = monitor; parity.MONITOR = monitor; parity.DEADLINE = deadline
                seed = secrets.randbelow(2**32-1)+1
                receipt['fixture_seed'] = seed
                def fight(arm, weights=None, cell='regular'):
                    request = r.collect.a0().request('T' if arm == 'T' else 'O', cell, seed, 0)
                    request['options']['duration'] = cfg['smoke']['fight_seconds']
                    request['stageA'] = dict(collect=True, shadow=True)
                    request['decisionTrace'] = False
                    if weights is not None: request['stageA']['weights'] = weights
                    tag = 'host_fixture_'+secrets.token_hex(8)
                    path = root/'requests'/(tag+'.json'); r.write(path, request, exclusive=True)
                    job = dict(tag=tag, seed=seed, request_sha256=r.sha(path), split='integration', arm=arm)
                    return execution.execute(job, deadline, monitor, 'FIXTURE_ONLY' if test_mode else 'SMOKE_ONLY')
                collected = {}
                def collect():
                    collected['teacher'] = fight('O')
                    return collected['teacher']
                step('collect', collect)
                teacher = collected['teacher']
                tiny = dict(raw_file=str(root/teacher['raw_file']), frames=teacher['frames'])
                models = {}; timings = {}; balances = {}
                def measure():
                    for arm in r.ARMS:
                        balance = parent_budget['samples'][arm]['target_balance']; balances[arm] = balance; loss.install(balance)
                        model, optimizer = training.make(arm)
                        rows, saved, refresh = training.stored(model, tiny, 1, deadline)
                        context = saved[0]
                        timings[arm] = [training.step(model, optimizer, rows, context, None, deadline) for _ in range(2)]
                        models[arm] = model, optimizer
                    r.write(root/'SMOKE_MEASUREMENT.json', dict(samples=timings, steps_per_arm=2, smoke_only=True))
                    return dict(samples=timings, steps_per_arm=2, target_balance='sealed round-0 train-only weights')
                step('measure', measure)
                weights = {}
                def fit():
                    outputs = {}
                    for arm, (model, optimizer) in models.items():
                        loss.install(balances[arm])
                        rows, saved, _ = training.stored(model, tiny, 1, deadline)
                        stats = training.step(model, optimizer, rows, saved[0], None, deadline)
                        # Exercise actual validation calibration on a tiny fixture.
                        from calibration import fit as calibrate
                        calibration = calibrate(model, [tiny], deadline)
                        path = root/'training'/(arm+'.weights.json'); path.parent.mkdir(exist_ok=True)
                        value = export(model, path)
                        value['fireThresholds'] = [calibration[role]['threshold'] for role in ('melee','ranged','artillery')]
                        r.write(path, value); weights[arm] = value
                        torch.save(dict(model=model.state_dict(), optimizer=optimizer.state_dict(), smoke_only=True), root/'training'/(arm+'.pt'))
                        outputs[arm] = dict(step=stats, export_sha256=r.sha(path), calibration=calibration)
                    return dict(steps_per_arm=1, outputs=outputs, scratch_only=True)
                step('train', fit)
                def check_parity():
                    records = []
                    from calibration import fire_classes
                    for arm in r.ARMS:
                        m32, value = parity.load_model(arm, torch.float32); m64, _ = parity.load_model(arm, torch.float64)
                        rows = list(r.data.frames(tiny['raw_file']))
                        a = parity.sequence(m32, rows); b = parity.sequence(m64, rows); classes = []; profile = {}
                        c = calibrated_parity.replay(value, rows, timeout=max(.01, deadline-time.monotonic()), profile=profile,
                            fixture_monitor=monitor if test_mode else None, fire_classes=classes)
                        monitor.memory_report(dict(peak_rss_bytes=profile['peak_rss_bytes']))
                        proof = dict(arm=arm, float32_export=parity.compare(a,b,near_ties=True), native_float64=parity.compare(b,c),
                            calibrated_fire=approvals.compare_calibrated(a,b,classes,rows,value['fireThresholds']), native_memory=profile)
                        if not approvals.passes(proof): raise RuntimeError('smoke parity failed: '+arm)
                        records.append(proof)
                    r.write(root/'SMOKE_PARITY.json', dict(status='PASS', records=records))
                    return dict(sequences_per_arm=1, records=records)
                step('parity', check_parity)
                def readout():
                    # One paired seed per production panel, all six policies.
                    records = []
                    for panel, cell in (('regular','regular'), ('C3',r.collect.a0().CELLS[0])):
                        for arm in (*r.ARMS, 'O', 'T'):
                            completion = teacher if arm == 'O' and panel == 'regular' else fight(arm, weights.get(arm), cell)
                            mechanism = readout_run.mechanism(root/completion['raw_file'])
                            if sum(mechanism['per_role_deaths'].values()) != completion['stats']['own_deaths']:
                                raise RuntimeError('smoke death attribution gap')
                            records.append(dict(arm=arm, panel=panel, tactic=cell, pair_key='smoke_'+panel+'_0', seed=seed,
                                stats=completion['stats'], mechanism=mechanism))
                    import readout as outcome
                    # Original report exercises both O/T comparisons and N2 state summaries.
                    summary = outcome.report(records, 1)
                    summary.update(status='SMOKE_ONLY', interpretation='tiny wiring fixture; no outcome inference')
                    result = dict(pairs_per_arm_per_panel=1, records=records, report=summary, fixture_only=True)
                    r.write(root/'SMOKE_READOUT.json', result)
                    return result
                step('readout', readout)
                receipt['status'] = 'PASS'
        except Exception as error:
            failure = error
            receipt['error'] = type(error).__name__+': '+str(error)
        finally:
            completed = {v['name'] for v in receipt['steps']}
            for name in ('preflight','admission','collect','measure','train','parity','readout'):
                if name not in completed: receipt['steps'].append(dict(name=name, status='NOT_RUN', reason=receipt.get('error','upstream refusal')))
            receipt.update(seconds=time.monotonic()-started, owner_approvals=approvals.snapshot(root/'owner_approvals'))
            r.write(root/'SMOKE_STAGEB.json', receipt)
            print('Smoke '+receipt['status']+': '+str(root/'SMOKE_STAGEB.json'), flush=True)
    if failure is not None: raise RuntimeError('smoke failed; inspect '+str(root/'SMOKE_STAGEB.json')) from failure
    return receipt
