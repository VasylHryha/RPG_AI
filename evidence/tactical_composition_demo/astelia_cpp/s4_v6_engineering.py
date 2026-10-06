"""Only the required default-knob captured-trajectory refinement check."""
import gzip,json,math,pathlib,subprocess,time
import s4_v6 as V
from s4_v6_numerics import reference

def _run():
    out=V.CHECKS/'engineering';out.mkdir(exist_ok=False)
    d=V.declaration();rows=[];started=time.monotonic()
    for name,setting,head in [('A','s4_melee10','novice'),('B_novice','s4_full_head','novice'),('B_regular','s4_full_head','regular')]:
        req=V.request(dict(arm='resonator',params=V.defaults('resonator'),skeleton='v6',setting=setting,
                           opponent=head,seed=d['engineering_seeds'][name],endCounts=True,diagnostics=True))
        raw=out/(name+'.jsonl');err=out/(name+'.stderr.txt')
        with raw.open('w') as f,err.open('w') as e:
            run=subprocess.run([str(V.BINARY),'--capture-s3','--metrics'],input=json.dumps(req)+'\n',text=True,
                               stdout=f,stderr=e,timeout=180)
        if run.returncode:raise RuntimeError('captured engineering process failed')
        maximum=0;ticks=0;unit_samples=0;summary=None
        with raw.open() as f:
            for line in f:
                row=json.loads(line)
                if row.get('captureV6'):
                    if type(row['n']) not in (int,float) or not 1<=row['n']<=64 or row['n']!=int(row['n']):raise RuntimeError('capture substep coverage')
                    if not row['units'] or any(not all(math.isfinite(u[k]) for k in ('x','y','rate','pressure','real','imag')) for u in row['units']):raise RuntimeError('capture nonfinite state/input')
                    case=dict(dt=row['dt'],mu=row['mu'],K=row['K'],K_t=row['K_t'],
                        units=[[u['id'],u['target'],u['x'],u['y'],u['rate'],u['pressure'],u['real'],u['imag']] for u in row['units']])
                    fine=reference(case,4*int(row['n']));values=dict(row['commitments'])
                    expected_ids={u[0] for u in case['units']}
                    if len(values)!=len(fine) or len(fine)!=len(case['units']) or len(values)!=len(row['commitments']) or set(values)!=expected_ids:raise RuntimeError('capture commitment coverage')
                    if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in fine) or any(not math.isfinite(c) for c in values.values()):raise RuntimeError('capture nonfinite reference/commitment')
                    for u,z in zip(case['units'],fine):
                        actual=values[u[0]];expected=max(-1,min(1,z.real));maximum=max(maximum,abs(actual-expected));unit_samples+=1
                    ticks+=1
                elif 'controllerStatus' in row:summary=row
        if ticks==0 or unit_samples==0 or summary is None or summary['controllerStatus']!='completed' or any(summary['controllerFailures']):
            raise RuntimeError('captured engineering numerical failure')
        with raw.open('rb') as src,gzip.open(raw.with_suffix('.jsonl.gz'),'wb') as dst:
            for chunk in iter(lambda:src.read(1024*1024),b''):dst.write(chunk)
        raw.unlink() # compressed byte-identical raw retained locally
        rows.append(dict(name=name,request=req,summary=summary,ticks=ticks,unit_samples=unit_samples,
                         max_commitment_refinement_error=maximum,threshold_strict=.02,status='PASS' if maximum<.02 else 'FAIL',
                         raw_path=str(raw.with_suffix('.jsonl.gz').relative_to(V.ROOT)),raw_sha256=V.sha(raw.with_suffix('.jsonl.gz')),
                         stderr_sha256=V.sha(err)))
        if maximum>=.02:break
    record=dict(status='PASS' if len(rows)==3 and all(r['status']=='PASS' for r in rows) else 'NOT_READY',
                default_knobs=V.defaults('resonator'),rows=rows,elapsed_seconds=time.monotonic()-started,
                purpose='required section8 captured-default-knob engineering accuracy; no tuning/selection',
                development_panel_fights=0,engineering_fights=len(rows))
    V.write(V.CHECKS/'ENGINEERING_REFINEMENT.json',record);return record

def run():
    try:return _run()
    except BaseException as error:
        V.write(V.CHECKS/'ENGINEERING_REFINEMENT.json',dict(status='NOT_READY',error=repr(error),
                reason='captured trajectory execution/coverage/finiteness/accuracy failed; no development authorized'))
        raise
