"""Fixed two-turn apparatus; prospective settings, no final-seed fallback."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from geomind import c4_detect as D
from geomind import c6_r4_field as F, c6_r4_field_assay as A
ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'experiments/c6_r4_protocol.json'
CONDITIONS=('intact','no_r','no_backreaction')
CONTROLS=CONDITIONS[1:]

def load_settings():return json.loads(PROTOCOL.read_text())
def rng(entropy,world,*purpose):return np.random.default_rng(np.random.SeedSequence([entropy,world,*purpose]))
def introduce(grid,entropy,world,generation,episode):
    states=[]
    for o in grid.owners:
        states.append(F.population(rng(entropy,world,10,generation,episode),o,generation,episode,grid.s['elements']))
    return A.GridSet(states,grid.s,grid.checks)

def qualify_episode(background,entropy,world,generation,episode,scope):
    grid=introduce(background,entropy,world,generation,episode)
    initial=grid.identities();introduced_states=[snapshot(o) for o in grid.owners];arrays=grid.owners[0].cohorts[-1]
    inputs={'ids':list(arrays.ids),'tokens':list(arrays.tokens),'x':arrays.x.tolist(),'theta':arrays.theta.tolist(),'rates':arrays.rates.tolist()}
    pert=A.perturbations(rng(entropy,world,20,generation,episode),len(arrays.theta))
    flow=grid.run(grid.s['formation'],scope+'/prefix')
    q=A.qualification(grid,flow,pert,scope+'/qualification')
    return grid,q,{'episode':episode,'inputs':inputs,'initial_ids':initial,'qualified_ids':grid.identities(),
                   'introduced_states':introduced_states,'qualified_states':[snapshot(o) for o in grid.owners],
                   'qualification_window':flow[0][-F.exact_steps(grid.s['window'],grid.s['frame_dt'])-1:].tolist(),
                   'qualification':q,'perturbations':{k:v.tolist() for k,v in pert.items()},'_prefixes':flow}

def snapshot(o):
    return {'identity':o.identity(),'time':o.time,'fields_real_imag':np.stack((o.z.real,o.z.imag),axis=-1).tolist(),
            'site_ids':list(o.site_ids),'q':o.q.tolist(),'omega':o.omega.tolist(),'psi':o.psi.tolist(),
            'adjacency':o.adjacency.tolist(),'model':o.model,'cohorts':[
             {'x':c.x.tolist(),'theta':c.theta.tolist(),'rates':c.rates.tolist(),'carrier_real_imag':np.stack((c.carrier.real,c.carrier.imag),axis=-1).tolist(),
              'ids':list(c.ids),'tokens':list(c.tokens),'selected':list(c.selected),'output':c.output,'mode':c.mode,
              'origin':None if c.origin is None else c.origin.tolist()} for c in o.cohorts]}

def rolling_persistence(prefix,operation,owner,members,s):
    window=F.exact_steps(s['window'],s['frame_dt']);px,pt=A.frames(prefix,owner);ox,ot=A.frames(operation,owner)
    xs=np.concatenate((px[-window:],ox));ths=np.concatenate((pt[-window:],ot));rows=[]
    d=s['detector']
    for i in range(len(ox)):
        x=xs[i:i+window+1];th=ths[i:i+window+1];locks=D.locked_pairs(th,d['lock_std'])
        stats=D.window_statistics(x,th,members,s['frame_dt'],d['link_factor'],locks)
        ok=(stats['membership_jaccard']>=d['membership_jaccard'] and stats['shape_cv']<=d['shape_cv'] and
            stats['lock_std']<=d['lock_std'] and stats['freq_change']<=d['freq_tol'] and stats['pattern_change']<=d['pattern_tol'])
        if not np.isfinite(list(stats.values())).all():raise ValueError('nonfinite persistence statistics')
        rows.append({'time':owner.time-s['exposure']+i*s['frame_dt'],'passed':bool(ok),'stats':stats})
    return rows

def operation(grid,qualification,qualification_flows,entropy,world,turn,alpha,scope):
    s=grid.s;members=qualification['selected_members'];before=grid.identities()
    branches={};records={};operation_checks={}
    pert=A.perturbations(rng(entropy,world,30,turn),s['elements'])
    for condition in CONDITIONS:
        branch=grid.clone()
        for o in branch.owners:
            for c in o.cohorts:c.output=0.
            c=o.cohorts[-1];c.selected=tuple(members);c.output=0. if condition=='no_backreaction' else 1.
            c.mode='no_r' if condition=='no_r' else 'intact'
        branch_start=branch.identities()
        flows=branch.run(s['exposure'],scope+'/operation/'+condition)
        op_check=next(c for c in reversed(grid.checks) if c['scope']==scope+'/operation/'+condition)
        operation_checks[condition]=op_check
        persistent=[rolling_persistence(qualification_flows[k],flows[k],branch.owners[k],members,s) for k in range(3)]
        masks=[[r['passed'] for r in rows] for rows in persistent]
        if masks[1:]!=[masks[0],masks[0]]:raise A.NumericalFailure('grid-dependent persistence')
        end=A.qualification(branch,flows,pert,scope+'/operation/'+condition+'/endpoint',forced_members=members)
        record={'start_ids':branch_start,'operation_end_ids':branch.identities(),'persistence_by_dt':persistent,
                'operation_end_states':[snapshot(o) for o in branch.owners],'operation_frames':flows[0].tolist(),
                'endpoint_qualification':end,'output_check':op_check}
        for o in branch.owners:
            for c in o.cohorts:c.output=0.
        record['after_ids']=branch.identities();record['after_states']=[snapshot(o) for o in branch.owners]
        record['background_diagnostics']={'mean_amplitude_by_dt':[float(np.mean(np.abs(o.z))) for o in branch.owners],
            'amplitude_weighted_coherence_by_dt':[float(abs(np.sum(o.z))/np.sum(np.abs(o.z))) if np.sum(np.abs(o.z))>0 else None for o in branch.owners]}
        branches[condition]=branch;records[condition]=record
    if (operation_checks['intact']['source_trace_hash_by_dt']!=operation_checks['no_backreaction']['source_trace_hash_by_dt']
            or any(operation_checks['no_backreaction']['output_max_by_dt'])):
        raise ValueError('sham source preservation/output failure')
    if records['no_r']['endpoint_qualification']['qualified']:raise ValueError('NO-R remains qualified')
    for control in CONTROLS:
        records[control]['background_diagnostics']['state_distance_vs_intact_by_dt']=[float(np.sqrt(np.mean(np.abs(a.z-b.z)**2))) for a,b in zip(branches['intact'].owners,branches[control].owners)]
    eligible=all(r['passed'] for r in records['intact']['persistence_by_dt'][0]) and records['intact']['endpoint_qualification']['qualified']
    outcome='PERSISTENT_UNIT' if eligible else 'SOURCE_LOST_DURING_OPERATION'
    first_loss=next((r['time'] for r in records['intact']['persistence_by_dt'][0] if not r['passed']),
                    grid.owners[0].time+s['exposure'] if not eligible else None)
    # Keep all reached field/output data and scheduled operation even on loss.
    cell={'turn':turn,'before_ids':before,'source':qualification,'operation_eligible':bool(eligible),
          'physical_outcome':outcome,'first_loss_time':first_loss,'conditions':records,'controls_passed':True,'response':{},'episodes':{},'before_formation':None,'before_response':None}
    if not eligible:return cell,None
    cell['before_response']=A.descriptor(grid,alpha,scope+'/before-response')
    # Before candidates are diagnostics only, same arrays at the earlier clock.
    diagnostics=[]
    for episode in s['measurement_episodes']:
        _,_,record=qualify_episode(grid,entropy,world,turn,episode,scope+f'/before/e{episode}')
        diagnostics.append(record)
    cell['before_formation']=diagnostics
    continuation=None
    for condition in CONDITIONS:
        branch=branches[condition]
        cell['response'][condition]=A.descriptor(branch,alpha,scope+'/response/'+condition)
        episodes=[]
        for episode in [0,*s['measurement_episodes']]:
            next_grid,q,record=qualify_episode(branch,entropy,world,turn,episode,scope+f'/{condition}/e{episode}')
            episodes.append(record)
            if condition=='intact' and episode==0 and q['qualified']:
                continuation=(next_grid,q)
        cell['episodes'][condition]=episodes
    for control in CONTROLS:
        diff=np.array(cell['response']['intact']['gain_by_dt'])-np.array(cell['response'][control]['gain_by_dt'])
        if np.max(np.abs(diff[:2]-diff[2]))>s['numerics']['response']:raise A.NumericalFailure('paired gain refinement')
    cell['witness_tuple']=[cell['episodes'][c][0]['qualification']['qualified'] for c in CONDITIONS]
    return cell,continuation

def run_world(settings,entropy,world):
    started=time.perf_counter();checks=[]
    row={'world':world,'turns':[],'checks':checks,'invalid':None,'chain_complete':False,'enabled_witness':False,'links':[]}
    current_turn=1
    try:
        base=F.medium(rng(entropy,world,1),settings['model']);alpha=float(rng(entropy,world,2).uniform(-np.pi,np.pi))
        grid=A.GridSet([base]*3,settings,checks)
        source,qualification,initial=qualify_episode(grid,entropy,world,0,0,'turn1/source')
        row['initial_source']=initial
        if qualification['qualified']:
            # Reconstruct sampled prefix from recorded grid evolution is not
            # allowed. retain the actual qualification frames for operation.
            prefixes=initial.pop('_prefixes',None)
            if prefixes is None:raise ValueError('missing live source prefix')
            for turn in (1,2):
                current_turn=turn
                cell,next_source=operation(source,qualification,prefixes,entropy,world,turn,alpha,'turn'+str(turn))
                row['turns'].append(cell)
                if not cell['operation_eligible'] or next_source is None:break
                reserved=cell['episodes']['intact'][0]
                link={'after_ids':cell['conditions']['intact']['after_ids'],'introduced_ids':reserved['initial_ids'],
                      'qualified_ids':reserved['qualified_ids'],'next_operation_ids':next_source[0].identities(),
                      'episode':0,'clock':next_source[0].owners[0].time}
                row['links'].append(link)
                if turn==1:
                    source,qualification=next_source
                    prefixes=reserved.pop('_prefixes')
                else:
                    row['chain_complete']=True
                    row['enabled_witness']=all(c['witness_tuple']==[True,False,False] for c in row['turns'])
        else:row['stop_reason']='INITIAL_SOURCE_NOT_QUALIFIED'
    except (ValueError,RuntimeError,FloatingPointError) as exc:
        row['invalid']={'type':type(exc).__name__,'message':str(exc),'turn':current_turn}
    # Prefix arrays are transient state, not JSON evidence fields.
    def discard(value):
        if isinstance(value,dict):
            value.pop('_prefixes',None)
            for v in value.values():discard(v)
        elif isinstance(value,list):
            for v in value:discard(v)
    discard(row)
    row['seconds']=time.perf_counter()-started
    row['peak_rss_bytes']=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    row['native_build']=F.native()[1]
    return row
