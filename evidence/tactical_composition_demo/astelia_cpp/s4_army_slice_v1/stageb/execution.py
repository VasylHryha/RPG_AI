"""Bounded compact Stage B fights, immutable requests and resumable completions."""
import runtime as r
import secrets,time,shutil,os
from streaming import stream_host
from recording import rows

def _execute(job,deadline,monitor,digest):
    path=r.LOCAL/'raw'/(job['tag']+'_COMPLETE.json');request_path=r.LOCAL/'requests'/(job['tag']+'.json')
    if r.sha(request_path)!=job['request_sha256']:raise RuntimeError('request drift')
    request=r.read(request_path)
    if path.exists():
        receipt=r.read(path)
        if receipt['job']!=job or receipt['ledger_sha256']!=digest or receipt['status']!='DONE' or r.sha(r.LOCAL/receipt['raw_file'])!=receipt['raw_sha256']:raise RuntimeError('completed Stage B fight drift')
        return receipt
    if shutil.disk_usage(r.LOCAL).free<5_000_000_000:raise RuntimeError('5 GB disk reserve')
    token=secrets.token_hex(8);raw=r.LOCAL/'raw'/(job['tag']+'_'+token+'.slim.xz');raw.parent.mkdir(parents=True,exist_ok=True);err=raw.with_suffix('.stderr');start=time.monotonic()
    receipt=dict(job=job,ledger_sha256=digest,status='RUNNING',raw_file=str(raw.relative_to(r.LOCAL)),recording='STAGEASLIM1',physical_dt=request['options'].get('dt',1/30),recording_cadence='physical_tick_after_clock_advance')
    try:
        stream_host(r.BINARY,request,raw,err,deadline,monitor,receipt,profile=True,compact=True)
        validated=r.collect.validate_raw(raw,deadline,request['options']['duration'],receipt['physical_dt']);receipt.update(validated)
        if request['stageA'].get('shadow'):
            for row in rows(raw):
                if not row.get('stageA'):continue
                if {x['id'] for x in row.get('shadowLabels',[])}!={x['id'] for x in row['labels']}:raise RuntimeError('shadow coverage')
                r.data.labels(dict(row,labels=row['shadowLabels']),[u[0] for u in sorted(row['units']) if u[1]==0],[u[0] for u in sorted(row['units']) if u[1]==1])
        receipt.update(status='DONE',seconds=time.monotonic()-start,raw_sha256=r.sha(raw));r.write(path,receipt,exclusive=True)
        return receipt
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=str(e));raise
    finally:r.write(r.LOCAL/'attempts'/(job['tag']+'_'+token+'.json'),receipt,exclusive=True)

def disk_projection(sample,todo):
    if not sample:raise RuntimeError('full-fight sample needed')
    per=max(c['compressed_bytes']*150.04/max(c['stats']['t_end'],1e-9) for c in sample)
    required=2*per*len(todo)+5_000_000_000
    if shutil.disk_usage(r.LOCAL).free<required:raise RuntimeError('measured full-duration disk projection exceeds free space')
    return dict(max_full150_bytes=per,remaining_fights=len(todo),required_free_bytes=required)


def execute(job,deadline,monitor,digest):
    if getattr(monitor,'fixture_only',False):
        request=r.read(r.LOCAL/'requests'/(job['tag']+'.json'))
        suffix=job['tag'].removeprefix('host_fixture_')
        if os.environ.get('STAGEA_HOST_TEST')!='1' or job.get('split')!='integration' or not job['tag'].startswith('host_fixture_') or not suffix.isalnum() or digest!='FIXTURE_ONLY':raise RuntimeError('explicit integration fixture envelope required')
        if not 0<request['options']['duration']<=3 or request['stageA'].get('collect') is not True or not 0<deadline-time.monotonic()<=300:raise RuntimeError('fixture duration/cap envelope')
        from jobs import locked
        with locked():return _execute(job,deadline,monitor,digest)
    return _execute(job,deadline,monitor,digest)
