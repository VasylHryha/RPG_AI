"""Lossless delivery and read-only audit, after section-10 execution has ended."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import math
from pathlib import Path
import time
from .section10 import HERE, OUT, SEEDS, COST_SEED, sha, write
from .protocol import template_hash, readouts


def archive(path, receipt):
    target = path.with_suffix(path.suffix+'.gz')
    digest = hashlib.sha256()
    count = size = 0
    with path.open('rb') as raw, target.open('xb') as compressed:
        with gzip.GzipFile(filename=path.name,mode='wb',fileobj=compressed,compresslevel=1,mtime=0) as stream:
            for block in iter(lambda:raw.read(1024*1024),b''):
                digest.update(block); count += block.count(b'\n'); size += len(block)
                stream.write(block)
    assert digest.hexdigest()==receipt['sha256'] and count==receipt['records'] and size==receipt['bytes'], path
    decoded = hashlib.sha256()
    decoded_count = decoded_size = 0
    with gzip.open(target,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            decoded.update(block); decoded_count += block.count(b'\n'); decoded_size += len(block)
    assert decoded.hexdigest()==digest.hexdigest() and decoded_count==count and decoded_size==size, target
    result = {'logical_path':str(path.relative_to(HERE)),'original_receipt_path':receipt['path'],
              'retained_path':str(target.relative_to(HERE)),'format':'ordered-jsonl-v1; gzip lossless transport',
              'decoded_sha256':digest.hexdigest(),'decoded_bytes':size,'records':count,
              'archive_sha256':sha(target),'archive_bytes':target.stat().st_size}
    path.unlink()  # Bytes retained exactly in the verified archive; original identity is preserved above.
    return result


def main():
    start = time.perf_counter()
    prior = json.loads((OUT/'IDENTITY.json').read_text())
    post = json.loads((HERE/'DEVELOPMENT_POSTFLIGHT.json').read_text())
    assert prior['source_sha256']==post['source_sha256']
    assert prior['harness_sha256']==post['harness_sha256']
    assert prior['build']==post['build']
    results = json.loads((OUT/'RESULTS.json').read_text())
    frozen = json.loads((OUT/'CALIBRATION.json').read_text())
    receipts = {}
    totals = {k:0 for k in ('training_steps','training_episodes','qualification_frames',
                           'recovery_simulated_seconds','evaluator_episodes','reward_episodes')}
    details = []
    g1c_lines = ['', 'G1c descriptive summary: the following are means within each seed over its first 20 admitted snapshots, followed by the counts of snapshot best tasks in the fixed task order. They are not promotion cuts or evidence of superiority.', '',
                 '| Arm / seed | Snapshot mean n: perceive / move / remember_static / choose | Best-task counts in that order |',
                 '|---|---|---|']
    for arm in SEEDS:
        units = results['arms'][arm]['seed_units']
        assert [u['seed'] for u in units]==SEEDS[arm]
        assert readouts(units)==results['arms'][arm]['readouts']
        for seed,unit in zip(SEEDS[arm],units):
            assert not unit['invalid'] and unit['complete']
            with gzip.open(OUT/arm/str(seed)/'REPORT.json.gz','rt') as stream:
                pair = json.load(stream)
            for policy,r in pair.items():
                assert r['complete'] and r['invalid'] is None
                assert r['seed']==seed and r['arm']==arm and r['control']==(policy=='control')
                assert r['usable']==frozen['usable']
                assert r['exposure']['training_steps']==320000 and r['exposure']['training_episodes']==2000
                assert abs(r['clock']-32000)<1e-3 and not r['pending_qualification']
                assert r['exposure']['qualification_frames']==(0 if policy=='control' else 532*601)
                assert r['exposure']['reward_episodes']==(2000 if arm=='reward' else 0)
                evaluated = min(20,len(r['snapshots']))
                assert len(r['evaluations'])==evaluated
                assert r['exposure']['evaluator_episodes']==(2*evaluated+1)*len(frozen['usable'])*128
                assert len(r['copy_instances'])==r['exposure']['evaluator_episodes']
                assert r['accounting']['evaluation_copies']==len(r['copy_instances'])
                for snapshot in r['snapshots']:
                    assert template_hash(snapshot['template'])==snapshot['type_id']
                    assert len(snapshot['members'])>=3
                for k in totals:
                    totals[k] += r['exposure'][k]
                for key in ('events','drive_schedule'):
                    receipt = r[key]
                    path = Path(receipt['path'])
                    assert path.is_relative_to(OUT)
                    if key=='drive_schedule':
                        assert receipt['records']==320000
                    receipts[path]=receipt
            evaluations = pair['intact']['evaluations']
            taskmeans=[sum(e['per_task'][t] for e in evaluations)/len(evaluations) for t in frozen['usable']]
            bestcounts=[sum(e['best_task']==t for e in evaluations) for t in frozen['usable']]
            g1c_lines.append(f'| {arm}/{seed} | '+ ' / '.join(f'{x:.6f}' for x in taskmeans)+' | '+' / '.join(map(str,bestcounts))+' |')
        passing = sum(not u['dropped'] and u['coverage']>u['control_coverage'] and u['competence']>u['control_competence'] for u in units)
        failing = sum(u['coverage']<=u['control_coverage'] and u['competence']<=u['control_competence'] for u in units)
        settled = sum(abs(u['slope'])<=.5 and not u['rejected'] and not u['protected_over_budget'] for u in units)
        g5fractions = [sum(d<=.1 for d in u['g5'])/len(u['g5']) for u in units]
        details += [f"{arm}: G0 both-superior unflagged seeds {passing}/8; both-≤ seeds {failing}/8; dropped-request flags {sum(bool(u['dropped']) for u in units)}/8. G0' settled and unrejected seeds {settled}/8; late rejection seeds {sum(u['rejected'] for u in units)}/8. G1 bearing seeds {sum(u['snapshots']>0 for u in units)}/8; admitted snapshots {sum(u['snapshots'] for u in units)}; evaluated snapshots {sum(len(u['g5']) for u in units)}. G5 fractions D≤0.1: "+', '.join(f'{x:.3f}' for x in g5fractions)+'.']
    with gzip.open(OUT/'COST_RUN.json.gz','rt') as stream:
        cost = json.load(stream)
    for key in ('events','drive_schedule'):
        receipt = cost[key]; receipts[Path(receipt['path'])]=receipt
    replay_exposure = 0
    for arm in SEEDS:
        with gzip.open(OUT/f'REPLAY_{arm}.json.gz','rt') as stream:
            replay = json.load(stream)
        assert replay['namespace']=='validation' and len(replay['frames'])==160
        assert replay['type_id']==template_hash(replay['snapshot']['template'])
        replay_exposure += replay['additional_exposure']['diagnostic_evaluator_episodes']
    write(OUT/'PROTOCOL_AUDIT.json', {'status':'PASS','source_and_build_unchanged':True,'seed_pairs':16,
          'training_runs':32,'horizon_seconds_per_run':32000,'exposure_totals':totals,
          'cost_seed_exposure':cost['exposure'],'additional_replay_evaluator_episodes':replay_exposure,
          'registered_readouts_match_reviewed_aggregator':True,'judging_used':False,
          'snapshot_template_hashes_verified':sum(u['snapshots'] for a in results['arms'].values() for u in a['seed_units']),
          'receipt_count':len(receipts),'details':details})
    print(json.dumps({'protocol_audit':'PASS','exposure_totals':totals,'ledgers':len(receipts)}),flush=True)
    transport = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(archive,path,receipt) for path,receipt in receipts.items()]
        for future in as_completed(futures):
            transport.append(future.result())
            print(json.dumps({'archived':len(transport),'of':len(receipts),'seconds':time.perf_counter()-start}),flush=True)
    write(OUT/'AUDIT_TRANSPORT.json', {'status':'PASS','decoded_bytes':sum(r['decoded_bytes'] for r in transport),
          'archive_bytes':sum(r['archive_bytes'] for r in transport),'ledgers':sorted(transport,key=lambda r:r['logical_path']),
          'seconds':time.perf_counter()-start,'verification':'each archive decoded and compared byte-for-byte by SHA256, byte count and record count before removing the unpacked copy'})
    report = HERE/'DEVELOPMENT_REPORT.md'
    text = report.read_text()+'\n'+'\n\n'.join(details)+'\n'+'\n'.join(g1c_lines)+'\n\n'
    text += 'Retention verification: [PROTOCOL_AUDIT.json](development_20261006/PROTOCOL_AUDIT.json) confirms all 32 horizons, exposure totals, calibration identity, snapshot hashes and the reviewed ordered aggregation. The source/build closure was unchanged before and after execution.\n\n'
    text += 'Audit transport: every original event/drive ledger is retained in a verified gzip archive. [AUDIT_TRANSPORT.json](development_20261006/AUDIT_TRANSPORT.json) maps original receipt paths to archives, preserving the original decoded SHA256, byte count and record count. Stored Run receipts are unchanged; unpacking restores their exact bytes. No event, snapshot, template or replay was discarded.\n\n'
    text += 'Summed stage timings are worker elapsed time under parallel execution, not isolated serial CPU measurements. The measured cost seed projected 11.403 serial hours; summed full-run stage time was %.3f worker hours. Development stops under the G0\' failure row; no further development or outcome-informed protocol change was performed.\n' % (sum(json.loads((OUT/'STAGE_TOTALS.json').read_text()).values())/3600)
    report.write_text(text)
    artifacts = {str(p.relative_to(HERE)):{'sha256':sha(p),'bytes':p.stat().st_size}
                 for p in OUT.rglob('*') if p.is_file() and p.name!='ARTIFACTS.json'}
    write(OUT/'ARTIFACTS.json',artifacts)
    print(json.dumps({'status':'COMPLETE','archive_count':len(transport),'seconds':time.perf_counter()-start}),flush=True)


if __name__=='__main__':
    main()
