"""Certify the same calibrated fire decoder used for native live commands."""
import runtime as r
import os,json,subprocess,time,numpy as np,torch
import parity
from calibration import fire_classes
from data import frames
from common import BINARY

def check_live(pid=None):return parity.check_live(pid)
LOCAL=r.LOCAL
def _replay(weights,rows,timeout=600,profile=None,fixture_monitor=None,fire_classes=None):
    # Stream one frame per RPC; persistent native state, bounded JS heap per tick.
    import secrets
    directory=LOCAL/'parity';directory.mkdir(parents=True,exist_ok=True)
    token=secrets.token_hex(8);request_path=directory/(token+'.requests.jsonl');output_path=directory/(token+'.outputs.jsonl')
    if fixture_monitor is not None and (os.environ.get('STAGEA_HOST_TEST')!='1' or not getattr(fixture_monitor,'fixture_only',False)):
        raise RuntimeError('explicit fixture-only replay monitor required')
    count=0;first_time=None
    if fixture_monitor is not None and not 0<timeout<=300:raise RuntimeError('fixture replay cap')
    with request_path.open('w') as f:
        for i,row in enumerate(rows):
            if fixture_monitor is not None:
                first_time=row['t'] if first_time is None else first_time
                if i>=91 or row['t']-first_time>3 or not 0<row['dt']<=.2:raise RuntimeError('fixture replay envelope')
            check_live()
            request=dict(operation='stageaReplay',frames=[row])
            if i==0:request['weights']=weights
            f.write(json.dumps(request,allow_nan=False,separators=(',',':'))+'\n')
            count+=1
    if not count:raise RuntimeError('empty native replay sequence')
    with request_path.open('r') as src,output_path.open('w') as dst:
        errpath=directory/(token+'.stderr')
        with errpath.open('w') as err:
            child=subprocess.Popen([str(BINARY)],stdin=src,stdout=dst,stderr=err,start_new_session=True,env={**os.environ,'STAGEA_MEMORY_PROFILE':'1'})
            started=time.monotonic()
            try:
                while child.poll() is None:
                    if fixture_monitor is None:check_live(child.pid)
                    else:fixture_monitor.live_memory(child.pid)
                    if time.monotonic()-started>timeout:raise TimeoutError('native sequence replay timeout')
                    time.sleep(.1)
                if child.returncode or errpath.stat().st_size:raise RuntimeError('native parity host failed; inspect local stream/stderr')
            finally:
                if child.poll() is None:__import__('os').killpg(child.pid,9);child.wait()
    out=[];memory=[]
    with output_path.open() as f:
        for line in f:
            check_live()
            result=json.loads(line)
            if result.get('stageAMemory'):
                memory.append(result)
                if fixture_monitor is not None:fixture_monitor.memory_report(result)
                continue
            if 'error' in result or result.get('combat_steps')!=0:raise RuntimeError('bad native replay '+str(result))
            if len(result['outputs'])!=1:raise RuntimeError('stream replay tick count')
            out.append(np.asarray(result['outputs'][0],dtype=np.float64))
            if fire_classes is not None:fire_classes.append(np.asarray(result['fireClasses'][0],dtype=np.int64))
    if len(out)!=count or not memory or not memory[-1]['final'] or memory[-1]['tick']!=count:
        raise RuntimeError('incomplete native replay/profile')
    if profile is not None:profile.update(frames=count,peak_rss_bytes=max(r['peak_rss_bytes'] for r in memory),memory_profile=memory)
    request_path.unlink();output_path.unlink();errpath.unlink()
    return out

def replay(weights,rows,timeout=600,profile=None,fixture_monitor=None,fire_classes=None):
    if fixture_monitor is not None:
        from jobs import locked
        with locked():return _replay(weights,rows,min(timeout,300),profile,fixture_monitor,fire_classes)
    return _replay(weights,rows,timeout,profile,fixture_monitor,fire_classes)

def compare_calibrated(a,b,native,rows,thresholds):
    error=max((float(np.max(np.abs(x[:,3:6]-y[:,3:6]))) for x,y in zip(a,b)),default=0.)
    bound=min(2*error,1e-4);details=[];native_errors=0
    for at,(x,y,z,row) in enumerate(zip(a,b,native,rows)):
        own=sorted((u for u in row['units'] if u[1]==0),key=lambda u:u[0]);roles=[u[2] for u in own]
        c32=fire_classes(x[:,3:6],roles,thresholds);c64=fire_classes(y[:,3:6],roles,thresholds)
        native_errors+=int(np.sum(c64!=z))
        for i in np.flatnonzero(c32!=c64):
            score=float(max(y[i,3],y[i,5])-y[i,4]);gap=abs(score-thresholds[roles[i]])
            # Active subtype changes also require a measured automatic/release tie.
            subtype=c32[i]!=1 and c64[i]!=1
            relevant=abs(float(y[i,3]-y[i,5])) if subtype else gap
            details.append(dict(frame_index=at,time=row['t'],unit_id=own[i][0],role=roles[i],float32_class=int(c32[i]),float64_class=int(c64[i]),threshold_gap=gap,relevant_gap=relevant,bound=bound,certified=relevant<=bound))
    return dict(native_mismatches=native_errors,float32_mismatches=details,uncertified_mismatches=sum(not d['certified'] for d in details),measured_logit_max_abs_error=error,bound=bound)

# Stage B recurrent rule (Claude 2026-10-09, owner-approved Stage B; see STAGEB_PROTOCOL addendum):
# the deployed native float64 path must stay exact. Float32 (training copy) categorical flips are
# certified when the float64 top-2 gap is <= 2x the measured per-head float32 error and flips stay
# <= 1 per 10,000 rows. Head error is reported, not capped (N2 phase drift reaches ~0.33 with 0 flips). The stage A 1e-4 ceiling is not met by
# float32 drift accumulated through recurrent/phase state over long sequences.
STAGEB_F32_FLIP_RATE_MAX=1e-4

def stageb_float32_passes(export):
    errors=export.get('head_max_abs_error',{})
    if len(export['mismatches'])!=export['categorical_mismatches']:return False
    for d in export['mismatches']:
        bound=2*errors.get(d['head'],0.)
        if not (d['float64_top2_gap']<=bound and d['float64_selected_class_deficit']<=bound):return False
    return export['categorical_mismatches']<=STAGEB_F32_FLIP_RATE_MAX*max(1,export['rows'])

def passes(proof):
    c=proof['calibrated_fire'];native=proof['native_float64']
    native_ok=native['categorical_mismatches']==0 and native['max_abs_error']<=parity.PARITY_RULE['native_atol']
    return native_ok and stageb_float32_passes(proof['float32_export']) and c['native_mismatches']==0 and c['uncertified_mismatches']==0

def evaluate(arm,fight):
    global LOCAL
    LOCAL=parity.LOCAL;raw=LOCAL/fight['raw_file'];start=time.monotonic()
    if r.sha(raw)!=fight['raw_sha256']:raise RuntimeError('calibrated parity shard drift')
    m32,weights=parity.load_model(arm,torch.float32);m64,_=parity.load_model(arm,torch.float64)
    a=parity.sequence(m32,frames(raw));b=parity.sequence(m64,frames(raw));classes=[];profile={}
    c=replay(weights,frames(raw),timeout=max(1,float(parity.DEADLINE-time.monotonic())) if parity.DEADLINE is not None else 600,profile=profile,fire_classes=classes)
    proof=dict(arm=arm,fight=fight['tag'],raw_sha256=r.sha(raw),float32_export=parity.compare(a,b,near_ties=True),native_float64=parity.compare(b,c),calibrated_fire=compare_calibrated(a,b,classes,frames(raw),weights['fireThresholds']),frames=len(a),seconds=time.monotonic()-start,native_memory=profile,parity_rule=parity.PARITY_RULE)
    proof['status']='PASS' if passes(proof) else 'FAIL';return proof
