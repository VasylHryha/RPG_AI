"""Read-only audit of committed pilot trajectories; never integrate or load native."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / 'evidence/c6_dev_pilot/r4_sensitivity'
sys.path.insert(0,str(ROOT))
SUMMARY_SHA256 = '4b0d82536d2e3b977baf82a9ca07c50088d9a25dc0dbb4b6d87e20bb0965db18'


class InvalidRecord(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidRecord(message)


def unique_object(pairs):
    out = {}
    for k,v in pairs:
        require(k not in out, 'duplicate JSON key: '+k)
        out[k]=v
    return out


def invalid_number(token):
    raise InvalidRecord('nonfinite JSON: '+token)


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object, parse_constant=invalid_number)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_rows(rows):
    out={}
    for row in rows:
        pair,arm=row.get('pair'),row.get('arm')
        require(type(pair) is int and 0<=pair<16 and arm in ('Q','H'),'invalid arm identity')
        require((pair,arm) not in out,'duplicate arm identity')
        out[pair,arm]=row
    require(set(out)=={(p,a) for p in range(16) for a in ('Q','H')},'missing/extra arm')
    return out


def failed(stats,d):
    return [name for name,ok in [
        ('membership',stats['size']>=d['min_size'] and stats['membership_jaccard']>=d['membership_jaccard']),
        ('shape',stats['shape_cv']<=d['shape_cv']),('mode_lock',stats['lock_std']<=d['lock_std']),
        ('frequency_stationarity',stats['freq_change']<=d['freq_tol']),('phase_pattern',stats['pattern_change']<=d['pattern_tol'])] if not ok]


def derive_structure(flow,s):
    import numpy as np
    from geomind import c4_detect as D
    width=2*25; n=s['elements'];window=round(s['window']/s['frame_dt'])+1
    path=np.asarray(flow,dtype='f8')[-window:]
    xs=path[:,width:width+2*n].reshape(-1,n,2);th=path[:,width+2*n:width+3*n]
    d=s['detector'];locks=D.locked_pairs(th,d['lock_std']);labels=D.components(xs[-1],d['link_factor'],locks)
    result=[]
    for label in np.unique(labels):
        m=np.flatnonzero(labels==label)
        if len(m)<d['min_size']:continue
        stats=D.window_statistics(xs,th,m,s['frame_dt'],d['link_factor'],locks)
        require(np.isfinite(list(stats.values())).all(),'nonfinite derived detector statistics')
        result.append({'members':m.tolist(),'stats':stats,'failures':failed(stats,d)})
    return result


def compare_stats(actual,expected):
    for name,value in actual.items():
        require(name in expected and abs(value-expected[name])<=1e-12,'derived statistic mismatch: '+name)


def derive_rolling(prefix,continuation,members,s,start_time):
    import numpy as np
    from geomind import c4_detect as D
    n=s['elements'];offset=50;window=round(s['window']/s['frame_dt'])
    path=np.concatenate((np.asarray(prefix)[-window-1:-1],np.asarray(continuation)))
    xs=path[:,offset:offset+2*n].reshape(-1,n,2);th=path[:,offset+2*n:offset+3*n];out=[]
    for i in range(len(continuation)):
        x,t=xs[i:i+window+1],th[i:i+window+1]
        locks=D.locked_pairs(t,s['detector']['lock_std'])
        stats=D.window_statistics(x,t,np.asarray(members),s['frame_dt'],s['detector']['link_factor'],locks)
        require(np.isfinite(list(stats.values())).all(),'nonfinite derived rolling statistics')
        failure=failed(stats,s['detector'])
        out.append({'time':start_time+i*s['frame_dt'],'stats':stats,'failures':failure,'passed':not failure})
    return out


def restored(snapshot):
    import numpy as np
    from geomind import c6_r4_field as F
    def complex_state(pairs):
        a=np.asarray(pairs,dtype='f8');return a[:,0]+1j*a[:,1]
    o=F.Owner(complex_state(snapshot['fields_real_imag']),np.asarray(snapshot['q']),np.asarray(snapshot['omega']),
              np.asarray(snapshot['psi']),np.asarray(snapshot['adjacency'],dtype='i4'),snapshot['model'],tuple(snapshot['site_ids']),
              time=snapshot['time'],scene_origin=tuple(snapshot['scene_origin']),scene_angle=snapshot['scene_angle'],phase_origin=snapshot['phase_origin'])
    for c in snapshot['cohorts']:
        o.cohorts.append(F.Cohort(np.asarray(c['x']),np.asarray(c['theta']),np.asarray(c['rates']),complex_state(c['carrier_real_imag']),
                                tuple(c['ids']),tuple(c['tokens']),selected=tuple(c['selected']),output=c['output'],mode=c['mode'],
                                origin=None if c['origin'] is None else np.asarray(c['origin'])))
    o.validate();require(o.identity()==snapshot['identity'],'snapshot identity mismatch')
    return o


def verify_row(row,s,derive=True):
    import numpy as np
    require(row['status']=='COMPLETE','incomplete arm')
    q=row['qualification'];require(type(q['qualified']) is bool,'qualification must be bool')
    require(type(row['retention']['retained']) is bool,'retention must be bool')
    require(row['retention']['applicable']==q['qualified'],'continuation applicability mismatch')
    require(bool(row['checks']),'missing scope checks')
    for c in row['checks']:
        require(c['passed'] is True and c['dt_values']==[s['dt'],s['dt']/2,s['dt']/4],'failed/inconsistent refinement')
        require(all(0<=c['max_errors'][k]<=s['numerics'][k] for k in ('position','phase','field')),'invalid error limits')
    d=s['detector'];initial=row['initial_background'];introduced=row['introduced_states']
    for key in ('background_before_quiet','quiet_end_states','initial_background','introduced_states','formation_end_states'):
        require(len(row[key])==3,'missing snapshot grids')
        for snap in row[key]:restored(snap)
    require(len(initial)==len(introduced)==3,'missing three-grid snapshots')
    require(all(o['time']==100. and o['model']==s['model'] and len(o['site_ids'])==25 for o in initial),'initial background mismatch')
    require(len(set(row['patch_site_ids']))==8,'invalid patch inventory')
    boundary=.485206;selected_patch=set(row['patch_site_ids'])
    for k,o in enumerate(initial):
        amplitude=np.linalg.norm(np.array(o['fields_real_imag']),axis=1)
        actual_high={i for i,a in zip(o['site_ids'],amplitude) if a>boundary}
        require(actual_high==(set() if row['arm']=='Q' else selected_patch),'wrong initial patch')
        c=introduced[k]['cohorts'][0]
        require({key:c[key] for key in ('x','theta','rates','ids','tokens')}==row['paired_material'],'introduced material mismatch')
        require(c['carrier_real_imag']==o['fields_real_imag'] and c['output']==0. and c['selected']==[],'wrong initial carrier/output')
    for stage,key in [('formation','formation_prefix_by_dt'),('quiet','quiet_prefix_by_dt')]:
        flows=row[key];require(len(flows)==3,'missing grid trajectory')
        for f in flows:
            a=np.array(f);require(a.shape==((101,172) if stage=='formation' else (101,50)) and np.isfinite(a).all(),'bad trajectory')
    for k,f in enumerate(row['formation_prefix_by_dt']):
        require(f[0]==restored(introduced[k]).pack().tolist() and f[-1]==restored(row['formation_end_states'][k]).pack().tolist(),'formation endpoint mismatch')
    derived=[derive_structure(f,s) for f in row['formation_prefix_by_dt']] if derive else None
    if derived is not None:
        require(len(derived[0])==len(q['candidates']),'candidate inventory mismatch')
        for actual,recorded in zip(derived[0],q['candidates']):
            require(actual['members']==recorded['members'] and actual['failures']==recorded['structural_failures'],'candidate identity/failures mismatch')
            require(recorded['structural']==(not actual['failures']),'structural verdict mismatch')
            compare_stats(actual['stats'],recorded['stats'])
        accepted_sets=[{tuple(r['members']) for r in rows if not r['failures']} for rows in derived]
        require(accepted_sets[0]==accepted_sets[1]==accepted_sets[2],'grid-dependent accepted inventory')
    accepted=[]
    for c in q['candidates']:
        if not c['structural']:continue
        require(len(c['recovery_by_dt'])==3,'missing recovery grids')
        decisions=[r['recovery_jaccard']>=d['recovery_jaccard'] and r['recovery_pattern_error']<=d['pattern_tol'] for r in c['recovery_by_dt']]
        require(len(set(decisions))==1 and c['accepted']==decisions[0],'recovery decision mismatch')
        if c['accepted']:accepted.append(c)
    tokens=row['paired_material']['tokens']
    expected=min(accepted,key=lambda c:(-len(c['members']),tuple(sorted(tokens[i] for i in c['members'])))) if accepted else None
    require(q['selected_members']==(expected['members'] if expected else None),'wrong candidate selection')
    if expected:
        causal_ok=True
        for direction in ('g_to_m','m_to_g'):
            a=q['causal'][direction]['intact'];b=q['causal'][direction]['ablated'];iv=s['causal']
            require(len(a)==len(b)==3 and np.isfinite(a+b).all() and min(a+b)>=0,'invalid causal data')
            decisions=[v>iv['floor'] for v in a]
            require(len(set(decisions))==1,'causal grid disagreement')
            require(not all(decisions) or max(a)-min(a)<=iv['relative_spread']*min(a),'causal refinement exceeded')
            require(max(b)<=max(iv['vanish_absolute'],iv['vanish_fraction']*min(a)),'causal ablation failure')
            causal_ok=causal_ok and all(decisions)
        require(q['qualified']==causal_ok,'qualification decision mismatch')
    else:
        require(not q['qualified'] and q['causal'] is None,'unselected qualified arm')
    rolling=None
    if q['qualified']:
        require(len(row['continuation_by_dt'])==3,'missing continuation grids')
        for f in row['continuation_by_dt']:
            require(np.asarray(f).shape==(101,172) and np.isfinite(f).all(),'bad continuation')
        require(len(row['continuation_end_states'])==3,'missing continuation snapshots')
        for k,f in enumerate(row['continuation_by_dt']):
            require(f[0]==row['formation_prefix_by_dt'][k][-1] and f[-1]==restored(row['continuation_end_states'][k]).pack().tolist(),'continuation endpoint mismatch')
        require(all(c['output']==0. for o in row['continuation_end_states'] for c in o['cohorts']),'unexpected continuation output')
        if derive:
            rolling=[]
            for k in range(3):
                data=derive_rolling(row['formation_prefix_by_dt'][k],row['continuation_by_dt'][k],q['selected_members'],s,200.)
                stored=row['retention']['rolling_by_dt'][k];require(len(data)==len(stored),'missing rolling windows')
                for actual,recorded in zip(data,stored):
                    compare_stats(actual['stats'],recorded['stats'])
                    require(actual['time']==recorded['time'] and actual['passed']==recorded['passed'] and actual['failures']==recorded['structural_failures'],'rolling decision mismatch')
                first=next((r for r in data if not r['passed']),None)
                stored_first=row['retention']['first_loss_by_dt'][k]
                require((first is None)==(stored_first is None),'first-loss mismatch')
                if first:require(first['time']==stored_first['time'] and first['failures']==stored_first['structural_failures'],'first-loss identity mismatch')
                rolling.append(data)
            masks=[[r['passed'] for r in rows] for rows in rolling]
            require(masks[0]==masks[1]==masks[2] and row['retention']['retained']==all(masks[0]),'retention disagreement')
    else:require(not row['retention']['retained'] and 'continuation_by_dt' not in row,'unexpected unqualified continuation')
    require(set(row['carrier_actual_amplitudes_by_stage'])==({'formation','continuation'} if q['qualified'] else {'formation'}),'missing/extra amplitude stage')
    patch_ok=True
    for stage,records in row['carrier_actual_amplitudes_by_stage'].items():
        flows=row['formation_prefix_by_dt'] if stage=='formation' else row['continuation_by_dt']
        require(len(records)==3,'missing amplitude grids')
        for k,(f,record) in enumerate(zip(flows,records)):
            a=np.asarray(f);actual=np.abs(a[:,:50].copy().view('c16'));carrier=np.abs(a[:,122:].copy().view('c16'))
            require(np.array_equal(actual,np.asarray(record['actual'])) and np.array_equal(carrier,np.asarray(record['carrier'])),'amplitude record differs from raw state')
            sites=initial[k]['site_ids'];indices=[sites.index(i) for i in row['patch_site_ids']]
            held=bool(np.all(carrier<boundary)) if row['arm']=='Q' else bool(np.all(carrier[:,indices]>boundary))
            require(record['condition_held']==held,'false condition flag');patch_ok=patch_ok and held
    require(row['background_condition_held']==patch_ok,'false background-retention flag')
    return {'structure_by_dt':derived,'rolling_rederived':rolling is not None}


def run_audit():
    summary=PILOT/'run/SUMMARY.json';require(sha(summary)==SUMMARY_SHA256,'reviewed summary identity changed')
    spec=read(PILOT/'SPEC.json');s=read(summary)
    require(s['status']=='COMPLETE' and s['stop_reason'] is None and not s['missing_arms'] and not s['unsubmitted'],'bad final completion')
    require(s['seconds']<900 and s['cpu_seconds']<1800,'recorded total cost exceeds cap')
    require(sha(PILOT/'SPEC.json')==s['spec_sha256'],'specification identity mismatch')
    require(all(sha(ROOT/name)==v for name,v in spec['file_hashes'].items()),'dependency drift')
    expected={f'pair_{i:02d}_{a}.{ext}' for i in range(16) for a in ('Q','H') for ext in ('json','log')}|{'PROGRESS.json','RUN_STARTED.json'}
    require(set(s['artifact_hashes'])==expected,'wrong artifact inventory')
    require({p.name for p in (PILOT/'run').iterdir() if p.is_file()}==expected|{'SUMMARY.json'},'extra/missing run file')
    require(all(sha(PILOT/'run'/name)==v for name,v in s['artifact_hashes'].items()),'artifact corruption')
    by=index_rows([read(PILOT/f'run/pair_{i:02d}_{a}.json') for i in range(16) for a in ('Q','H')])
    accounting=index_rows(s['accounting']);settings=spec['settings'];derived={}
    for key,row in by.items():
        derived[key]=verify_row(row,settings)
        resource_row=accounting[key]
        require(resource_row['exit_code']==0 and resource_row['seconds']<300 and resource_row['peak_rss_bytes']<2*1024**3,'bad completed resource accounting')
    for i in range(16):
        q,h=by[i,'Q'],by[i,'H']
        require(q['paired_material']==h['paired_material'] and q['perturbations']==h['perturbations'],'material/probe pairing mismatch')
        require(q['background_before_quiet']==h['background_before_quiet'] and q['quiet_end_states']==h['quiet_end_states'],'unpaired quiet initialization')
        for a,b in zip(q['initial_background'],h['initial_background']):
            require(all(a[k]==b[k] for k in a if k not in ('identity','fields_real_imag')),'unpaired background metadata')
    qualification_forward=[i for i in range(16) if by[i,'Q']['qualification']['qualified'] and not by[i,'H']['qualification']['qualified']]
    qualification_reverse=[i for i in range(16) if by[i,'H']['qualification']['qualified'] and not by[i,'Q']['qualification']['qualified']]
    fine_association=[]
    for i in qualification_forward:
        rows=derived[i,'H']['structure_by_dt']
        if all(not any(not r['failures'] for r in grid) and any(r['failures']==['frequency_stationarity'] for r in grid) for grid in rows):fine_association.append(i)
    result={'kind':'READ_ONLY_PILOT_RECHECK_NOT_C6_EVIDENCE','summary_sha256':sha(summary),'status':'STORED_OBSERVATIONS_RECHECKED',
            'complete_arms':32,'minimum_size_candidate_rows_all_grids':sum(len(rows) for v in derived.values() for rows in v['structure_by_dt']),
            'rolling_windows_rederived':sum(3*101 for row in by.values() if row['qualification']['qualified']),
            'Q_qualified':sum(r['qualification']['qualified'] for (i,a),r in by.items() if a=='Q'),
            'H_qualified':sum(r['qualification']['qualified'] for (i,a),r in by.items() if a=='H'),
            'Q_structurally_retained':sum(r['retention']['retained'] for (i,a),r in by.items() if a=='Q'),
            'H_structurally_retained':sum(r['retention']['retained'] for (i,a),r in by.items() if a=='H'),
            'qualification_forward_pairs':qualification_forward,'qualification_reverse_pairs':qualification_reverse,
            'frequency_only_qualification_association_all_three_grids':fine_association,
            'patch_conditions_all_grids':all(r['background_condition_held'] for r in by.values()),
            'raw_recovery_causal_trajectories':'not stored; returned effects and decisions checked, no independent effect reconstruction',
            'integration':'not rerun; per-production-step errors remain recorded diagnostics, not independently reconstructed',
            'no_new_inputs_no_native_calls':True}
    v=s['interpretation']
    require((result['Q_qualified'],result['H_qualified'],result['Q_structurally_retained'],result['H_structurally_retained'])==(v['Q_qualified'],v['H_qualified'],v['structural_retention']['Q_successes'],v['structural_retention']['H_successes']),'reported counts disagree')
    require(qualification_forward==v['qualification']['Q_success_H_failure'] and qualification_reverse==v['qualification']['H_success_Q_failure'],'reported discordances disagree')
    return result

if __name__=='__main__':
    output=Path(__file__).with_name('STORED_RECHECK.json')
    result=run_audit()
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
