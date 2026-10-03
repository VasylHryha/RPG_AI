"""One fixed ten-world readiness gate. No final seeds, panel or model search."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from geomind import c6_r4_field as F,c6_r4_field_reference as R,c6_r4_field_protocol as P
from geomind.c6_r4_integrity import sha256,validate_pin,load_worlds,finite
from tools.c6_r3_design_gate import write_world,jsonable

def dependencies():
    """World/readiness identity; final pipeline separately binds tests/mutants.

    Owner chose review Finding 2(a) before any R005 development. Changing a
    result-producing or interpreting dependency still invalidates readiness.
    """
    patterns=('geomind/c6_r4_field*.py','geomind/run_c6_r4.py','native/c6_r4/*.cpp','tools/c6_r4_design_gate.py',
       'tools/build_c6_r4.py','tools/c6_r3_design_gate.py','milestones/c6.json','geomind/c6_r4_integrity.py',
       'geomind/c4_model.py','geomind/c4_detect.py','experiments/c6_r4_protocol.json','experiments/c6_proposal_r4.md',
       'docs/decisions/0019-approve-c6-r4-implementation.md','research/rrg/v0.2.1.import.json',
       'research/rrg/v0.2.1.expected.json','docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md','pyproject.toml','uv.lock')
    return {str(p.relative_to(ROOT)):sha256(p) for pattern in patterns for p in ROOT.glob(pattern) if p.is_file()}

def reference_battery(settings,deadline=None):
    fixture_rng=np.random.default_rng(settings['reference_battery']['entropy'])
    base=F.population(fixture_rng,F.medium(fixture_rng,settings['model']),0,0)
    base.z=.6*np.exp(1j*fixture_rng.uniform(-np.pi,np.pi,len(base.z)))
    base.cohorts[0].carrier=base.z.copy();base.cohorts[0].selected=(0,1,2)
    rows=[]
    for condition in settings['reference_battery']['conditions']:
        a=base.clone();c=a.cohorts[0];c.mode='intact' if condition=='no_backreaction' else condition
        c.output=0. if condition=='no_backreaction' else 1.
        if c.mode=='no_geometry_to_mode':c.origin=c.x.copy();c.x[0]+=np.array([.1,-.2])
        if c.mode=='no_mode_to_geometry':c.theta[0]+=.3
        b=a.clone();initial=P.snapshot(a);rhs_max=float(np.max(np.abs(F.rhs(a)-R.rhs(b))))
        # Three treatment exposures, complete ablation/probe/recovery horizons.
        duration=100. if condition in P.CONDITIONS else 30.
        maximum=rhs_max
        for second in range(int(duration)):
            if deadline is not None and time.perf_counter()>=deadline:raise TimeoutError('reference battery exceeds development budget')
            a,aa=F.advance(a,1.,settings['dt'],settings['dt']);b,bb=R.advance(b,1.,settings['dt'],settings['dt'])
            maximum=max(maximum,float(np.max(np.abs(aa-bb))))
        rows.append({'condition':condition,'duration':duration,'initial_state':initial,'maximum_error':maximum,'rhs_maximum_error':rhs_max,
                     'passed':maximum<=settings['numerics']['reference']})
        # Full field impulse and geometry/phase recovery fixtures.
    for name,duration in [('probe',10.),('recovery',30.)]:
        a=base.clone();a.cohorts[0].output=0.
        if name=='probe':a.z[0]+=.05j
        else:a.cohorts[0].x[0]+=.1;a.cohorts[0].theta[0]+=.3
        b=a.clone();maximum=0.;initial=P.snapshot(a)
        for second in range(int(duration)):
            if deadline is not None and time.perf_counter()>=deadline:raise TimeoutError('reference battery exceeds development budget')
            a,aa=F.advance(a,1.,settings['dt'],settings['dt']);b,bb=R.advance(b,1.,settings['dt'],settings['dt'])
            maximum=max(maximum,float(np.max(np.abs(aa-bb))))
        rows.append({'condition':name,'duration':duration,'initial_state':initial,'maximum_error':maximum,'passed':maximum<=settings['numerics']['reference']})
    # Independent exact isolated periodic/zero solutions, full 10-C0 horizon.
    for radius in (0.,R.isolated_radius(-.18,-1),R.isolated_radius(-.18,1)):
        o=F.Owner(np.array([radius+0j]),np.zeros((1,2)),np.array([.2]),np.zeros((1,8)),np.zeros((1,1),dtype='i4'),dict(settings['model']),(0,))
        o.model.update(diffusion=0.,drive=0.)
        end,flow=F.advance(o,10.,settings['dt'],settings['dt']);times=np.arange(len(flow))*settings['dt']
        expected=radius*np.exp(.2j*times);error=float(np.abs(flow.copy().view('c16').ravel()-expected).max())
        rows.append({'condition':'isolated_periodic','radius':float(radius),'duration':10.,'maximum_error':error,'passed':error<=1e-10})
    return {'passed':all(r['passed'] for r in rows),'fixtures':rows,'tolerance':settings['numerics']['reference'],'native_build':F.native()[1]}

def transform(owner,element_order=None,site_order=None,angle=0.,shift=(0.,0.),phase=0.):
    o=owner.clone();rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    o.scene_origin=tuple(np.asarray(o.scene_origin)@rotation.T+shift)
    o.scene_angle+=angle;o.phase_origin+=phase
    o.q=o.q@rotation.T+shift;o.z*=np.exp(1j*phase);o.psi+=phase
    for c in o.cohorts:
        c.x=c.x@rotation.T+shift;c.theta+=phase;c.carrier*=np.exp(1j*phase)
        if c.origin is not None:c.origin=c.origin@rotation.T+shift
        if element_order is not None:
            indices=np.asarray(element_order);old_selected=set(c.selected)
            c.x=c.x[indices];c.theta=c.theta[indices];c.rates=c.rates[indices]
            if c.origin is not None:c.origin=c.origin[indices]
            c.ids=tuple(c.ids[i] for i in indices);c.tokens=tuple(c.tokens[i] for i in indices)
            c.selected=tuple(j for j,i in enumerate(indices) if int(i) in old_selected)
    if site_order is not None:
        p=np.asarray(site_order);o.q=o.q[p];o.z=o.z[p];o.omega=o.omega[p];o.psi=o.psi[p];o.adjacency=o.adjacency[p][:,p]
        o.site_ids=tuple(o.site_ids[i] for i in p)
        for c in o.cohorts:c.carrier=c.carrier[p]
    return o.validate()

def equivariance(settings):
    rng=np.random.default_rng(settings['equivariance_entropy']);o=F.population(rng,F.medium(rng,settings['model']),0,0)
    o.cohorts[0].selected=(0,2,4);o.cohorts[0].output=1.
    ep=rng.permutation(len(o.cohorts[0].theta));sp=rng.permutation(len(o.z));angle=.71;phase=.29;shift=np.array([1.1,-.7])
    transformed=transform(o,ep,sp,angle,shift,phase)
    end,_=F.advance(o,5.,settings['dt'],.1);other,_=F.advance(transformed,5.,settings['dt'],.1)
    expected=transform(end,ep,sp,angle,shift,phase);err=float(np.max(np.abs(expected.pack()-other.pack())))
    # Label rename is metadata-only; no physical group or perturbation redraw.
    renamed=o.clone();renamed.site_ids=tuple(i+100 for i in renamed.site_ids)
    for c in renamed.cohorts:c.ids=tuple('renamed/'+i for i in c.ids)
    renamed_end,_=F.advance(renamed,5.,settings['dt'],.1)
    label_error=float(np.max(np.abs(end.pack()-renamed_end.pack())))
    return {'passed':max(err,label_error)<=settings['numerics']['equivariance'],'scene_maximum_error':err,'rename_maximum_error':label_error,
            'element_order':ep.tolist(),'site_order':sp.tolist(),'angle':angle,'phase':phase,'shift':shift.tolist(),'horizon':5.}

def readiness(rows,s,workers,elapsed):
    complete=len(rows)==s['development_worlds'] and sorted(r['world'] for r in rows)==list(range(s['development_worlds']))
    sources=sum(bool(r.get('initial_source',{}).get('qualification',{}).get('qualified')) for r in rows)
    chains=sum(r['chain_complete'] for r in rows);valid=not any(r['invalid'] for r in rows)
    # Each complete world exercised all controls, five candidates and 50 probes.
    full=[r['seconds'] for r in rows if r['chain_complete']]
    projection=max(r['seconds'] for r in rows)*s['final_worlds']/workers*1.5 if full else None
    reason=('incomplete development worlds' if not complete else 'engineering/numerical failure' if not valid else
            'initial source quorum below 5/10' if sources<s['budget']['development_sources'] else
            'mechanical chain quorum below 5/10' if chains<s['budget']['development_chains'] else
            'panel workload/runtime remains unknown' if projection is None else
            'projected panel budget exceeded' if projection>s['budget']['panel_seconds'] else None)
    return {'passed':reason is None,'reason':reason,'qualified_sources':sources,'mechanical_chains':chains,
            'enabled_witnesses':sum(r['enabled_witness'] for r in rows),'worlds':len(rows),'panel_seconds':projection,
            'workers':workers,'peak_worker_rss_bytes':max((r['peak_rss_bytes'] for r in rows),default=None),'seconds':elapsed}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--worker',type=int);args=parser.parse_args(argv);s=P.load_settings()
    if args.worker is not None:
        receipt=json.loads((args.output/'results.json').read_text())
        if receipt['kind']!='DEVELOPMENT_ONLY' or receipt['status']!='RUNNING' or receipt['file_hashes']!=dependencies() or args.worker not in range(10):raise ValueError('worker lacks live development receipt')
        row=P.run_world(s,s['development_entropy'],args.worker);write_world(args.output,row);return 0
    if args.output.exists():raise SystemExit('one-shot development evidence exists; never overwrite/repeat')
    manifest=json.loads((ROOT/'experiments/c6_manifest.json').read_text())
    if manifest.get('status')!='REGISTERED_DEVELOPMENT_ONLY' or args.output.resolve()!=(ROOT/manifest['development_gate']).resolve():
        raise SystemExit('development requires owner-approved prospective registration and its exact output path')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip():raise SystemExit('commit all implementation before development')
    started=time.perf_counter();deadline=started+s['budget']['development_seconds'];before=dependencies();pin=validate_pin(ROOT)
    args.output.mkdir(parents=True);rows=[]
    receipt={'kind':'DEVELOPMENT_ONLY','status':'RUNNING','hypotheses':'NOT_ASSIGNED','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'file_hashes':before,'source_pin':pin,'protocol':s,'world_artifacts':[],'errors':[],'engineering':{}}
    def save():(args.output/'results.json').write_text(json.dumps(jsonable(receipt),indent=2,allow_nan=False)+'\n')
    save()
    try:
        receipt['engineering']['b_reference_equivalence']=reference_battery(s,deadline);save()
        receipt['engineering']['b_transform_equivariance']=equivariance(s);save()
        if not all(v['passed'] for v in receipt['engineering'].values()):raise ValueError('independent reference or covariance qualification failed')
        def one(world):
            remaining=deadline-time.perf_counter()
            if remaining<=0:raise TimeoutError('development budget exhausted')
            result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(world),'--output',str(args.output.resolve())],cwd=ROOT,capture_output=True,text=True,timeout=remaining)
            if result.returncode:raise RuntimeError(result.stderr[-1500:])
            path=args.output/f'world_{world:03d}.json.gz';raw=gzip.decompress(path.read_bytes());row=json.loads(raw)
            return row,{'world':world,'path':path.name,'sha256':sha256(path),'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'seconds':row['seconds']}
        with ThreadPoolExecutor(max_workers=s['budget']['workers']) as pool:
            futures=[pool.submit(one,w) for w in range(s['development_worlds'])]
            for f in as_completed(futures):
                row,artifact=f.result();rows.append(row);receipt['world_artifacts'].append(artifact);save()
                print(f"world {row['world']}: qualified={bool(row.get('initial_source',{}).get('qualification',{}).get('qualified'))}, chain={row['chain_complete']}, invalid={row['invalid']}, {row['seconds']:.1f}s",flush=True)
        ready=readiness(rows,s,s['budget']['workers'],time.perf_counter()-started)
        if dependencies()!=before or validate_pin(ROOT)!=pin:raise ValueError('dependencies/source changed during development')
        receipt.update(status='PASS' if ready['passed'] else 'STOP',readiness=ready)
    except Exception as exc:
        receipt.update(status='STOP');receipt['errors'].append({'type':type(exc).__name__,'message':str(exc)})
        # Preserve and index workers that finished before a budget/infrastructure stop.
        known={e['world'] for e in receipt['world_artifacts']}
        for path in sorted(args.output.glob('world_*.json.gz')):
            raw=gzip.decompress(path.read_bytes());row=json.loads(raw)
            if row['world'] not in known:
                receipt['world_artifacts'].append({'world':row['world'],'path':path.name,'sha256':sha256(path),'uncompressed_sha256':hashlib.sha256(raw).hexdigest(),'seconds':row['seconds']})
    receipt['seconds']=time.perf_counter()-started
    if 'readiness' in receipt:receipt['readiness']['seconds']=receipt['seconds']
    save()
    (args.output/'README.md').write_text('# C6 R4 fixed development gate\n\nDevelopment only. No final seeds or scientific verdicts.\n\nStatus: '+receipt['status']+'\n')
    print(json.dumps({'status':receipt['status'],'readiness':receipt.get('readiness'),'seconds':receipt['seconds'],'errors':receipt['errors']}),flush=True)
    return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
