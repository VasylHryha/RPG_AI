"""Prospective 16-contrast analysis and complete 79-endpoint evidence coverage."""
import copy
import hashlib
import json
import numpy as np
from geomind.c6_r4_integrity import finite, ordered_worlds
from geomind import c6_r4_field_protocol as P

PRIMARY=tuple(f'b_{prefix}{kind}_vs_{control}_turn{turn}' for prefix in ('','chain_')
              for turn in (1,2) for kind in ('response','later_formation') for control in P.CONTROLS)
TURN_DIAGNOSTICS=('source_qualification','operation_eligibility','source_persistence','sham_preservation','no_r_control',
    'publication','background_snapshots','response_raw','background_diagnostics','before_and_control_formation',
    'measurement_episodes','continuation_episodes','numerical_refinement','output_power','normalization')
GLOBAL=('b_source_population_inputs','b_chain_yield','b_chain_provenance','b_enablement_witnesses','b_reference_equivalence',
        'b_transform_equivariance','b_costs','b_sensitivity','source_pin')
ARM_A=tuple(f'{name}_l{level}' for level in (2,3) for name in ('formation','g_to_m','m_to_g','dose_response','parts_alive',
    'downward_effect','emergent_transfer','effective_state','coarse_vs_full','same_law_closure','scale_separation'))+('upward_transfer_l3','level_interface')
ENDPOINTS=PRIMARY+tuple(f'b_{name}_turn{turn}' for turn in (1,2) for name in TURN_DIAGNOSTICS)+GLOBAL+ARM_A

def formation(episodes):
    ids=[e['episode'] for e in episodes]
    if ids!=[0,1,2,3,4]:raise ValueError('candidate episode inventory/order mismatch')
    # Reserved continuation outcome NEVER enters the measurement mean.
    return sum(bool(e['qualification']['qualified']) for e in episodes if e['episode'] in (1,2,3,4))/4

def change_verdict(ci,n,margin,minimum=10):
    if ci is None or n<minimum:return 'INCONCLUSIVE'
    if len(ci)!=2 or not np.isfinite(ci).all() or ci[0]>ci[1]:raise ValueError('invalid confidence interval')
    if ci[0]>margin or ci[1]<-margin:return 'PASS'
    if ci[0]>-margin and ci[1]<margin:return 'FAIL'
    return 'INCONCLUSIVE'

def combine(verdicts,valid=True,background=None):
    if not valid:return 'INCONCLUSIVE'
    if 'FAIL' in verdicts:return 'NOT_SUPPORTED'
    if all(v=='PASS' for v in verdicts) and background in (None,'SUPPORTED_WITHIN_SCOPE'):return 'SUPPORTED_WITHIN_SCOPE'
    return 'INCONCLUSIVE'

def recursive(required,n,witnesses,valid):
    if not valid or n<10:return 'INCONCLUSIVE'
    if 'NOT_SUPPORTED' in required:return 'NOT_SUPPORTED'
    if witnesses<10 or any(v!='SUPPORTED_WITHIN_SCOPE' for v in required):return 'INCONCLUSIVE'
    return 'SUPPORTED_WITHIN_SCOPE'

def publication_valid(q,expected_snapshot=None):
    p=q.get('publication')
    if not q['qualified']:return p is None
    matches=[r for r in q['candidates'] if r.get('accepted') and r['members']==q['selected_members']]
    required={'candidate','snapshot','ids','size','centroid','phase','rate','S','units'}
    if not isinstance(p,dict) or set(p)!=required:return False
    numeric=lambda v:isinstance(v,(int,float,np.number)) and not isinstance(v,(bool,np.bool_))
    if (not all(numeric(p[k]) for k in ('size','phase','rate')) or not isinstance(p['centroid'],list)
            or len(p['centroid'])!=2 or not all(numeric(v) for v in p['centroid'])
            or not isinstance(p['ids'],list) or not all(isinstance(v,str) and v for v in p['ids'])):return False
    member_hash=hashlib.sha256(json.dumps(sorted(p['ids'])).encode()).hexdigest()
    return (len(matches)==1 and isinstance(p,dict) and set(p)==required and finite(p)
            and p.get('candidate')==q['selected_identity']==member_hash and (expected_snapshot is None or p['snapshot']==expected_snapshot)
            and p.get('size',0)>0 and len(p['centroid'])==2 and p.get('S')==matches[0]['stats']
            and p['units']=={'size':'L0','centroid':'L0','phase':'rad','rate':'rad/C0'}
            and len(set(p.get('ids',[])))==len(q['selected_members']))

def validate_world(row):
    if type(row.get('chain_complete')) is not bool or type(row.get('enabled_witness')) is not bool:raise ValueError('invalid chain flags')
    if row['enabled_witness'] and (not row['chain_complete'] or any(c.get('witness_tuple')!=[True,False,False] for c in row['turns'])):
        raise ValueError('false enabled witness')
    if row['chain_complete']:
        if len(row['turns'])!=2 or len(row['links'])!=2 or row['invalid']:raise ValueError('invalid complete chain')
        for i,(cell,link) in enumerate(zip(row['turns'],row['links'])):
            if not cell['operation_eligible'] or not cell['episodes']['intact'][0]['qualification']['qualified']:raise ValueError('false mechanical completion')
            reserved=cell['episodes']['intact'][0]
            if (link['episode']!=0 or link['qualified_ids']!=reserved['qualified_ids'] or link['qualified_ids']!=link['next_operation_ids']
                    or link['after_ids']!=cell['conditions']['intact']['after_ids'] or link['introduced_ids']!=reserved['initial_ids']
                    or abs(link['clock']-(300+200*i))>1e-7):raise ValueError('chain provenance mismatch')
            if i==0 and link['next_operation_ids']!=row['turns'][1]['before_ids']:raise ValueError('restaged second source')
            for after,introduced in zip(cell['conditions']['intact']['after_states'],reserved['introduced_states']):
                if (after['time']!=introduced['time'] or after['fields_real_imag']!=introduced['fields_real_imag']
                        or after['cohorts']!=introduced['cohorts'][:-1]
                        or introduced['cohorts'][-1]['carrier_real_imag']!=after['fields_real_imag']):
                    raise ValueError('reset environment/carrier/previous source on introduction')
    for cell in row['turns']:
        if not publication_valid(cell['source'],cell['before_ids'][0]):raise ValueError('invalid source publication')
        if cell['operation_eligible']:
            if set(cell['episodes'])!=set(P.CONDITIONS) or set(cell['response'])!=set(P.CONDITIONS):raise ValueError('missing condition')
            if not isinstance(cell['before_formation'],list) or [e['episode'] for e in cell['before_formation']]!=[1,2,3,4]:
                raise ValueError('before episode inventory mismatch')
            for episode in cell['before_formation']:
                if not publication_valid(episode['qualification'],episode['qualified_ids'][0]):raise ValueError('invalid before episode publication')
            for condition in P.CONDITIONS:
                formation(cell['episodes'][condition])
                for episode in cell['episodes'][condition]:
                    if not publication_valid(episode['qualification'],episode['qualified_ids'][0]):raise ValueError('invalid episode publication')
            for condition in P.CONTROLS:
                for a,b in zip(cell['episodes']['intact'],cell['episodes'][condition]):
                    if a['inputs']!=b['inputs'] or a['perturbations']!=b['perturbations']:raise ValueError('unmatched candidate inputs')
            if cell['witness_tuple']!=[cell['episodes'][c][0]['qualification']['qualified'] for c in P.CONDITIONS]:raise ValueError('witness tuple mismatch')
        if not cell['controls_passed']:raise ValueError('invalid control recorded as clean')
        intact=cell['conditions']['intact']['output_check'];sham=cell['conditions']['no_backreaction']['output_check']
        if intact['source_trace_hash_by_dt']!=sham['source_trace_hash_by_dt'] or any(sham['output_max_by_dt']):raise ValueError('broken sham')
        if cell['conditions']['no_r']['endpoint_qualification']['qualified']:raise ValueError('qualified NO-R')

def bootstrap(values,draws,level):
    array=np.asarray(values,float);valid=np.isfinite(array);numbers=valid[draws].sum(1)
    sums=np.where(valid,array,0.)[draws].sum(1)
    means=np.divide(sums,numbers,out=np.full(len(draws),np.nan),where=numbers>0)
    if np.any(~np.isfinite(means)):return None
    tail=(1-level)/2
    return np.quantile(means,[tail,1-tail]).tolist()

def source_inputs_summary(row):
    initial=row.get('initial_source')
    if initial is None:return None
    summary=dict(initial)
    if initial.get('no_treatment_response') is not None:
        summary['no_treatment_response']={**initial['no_treatment_response'],
            'raw':{'artifact':f"world_{row['world']:03d}.json.gz",'json_pointer':'/initial_source/no_treatment_response/raw'}}
    return summary

def evaluate(records,settings,entropy,engineering):
    if settings['ci_level']<1-.05/len(PRIMARY):raise ValueError('uncorrected primary confidence level')
    if settings['bootstrap_empty_policy']!='INCONCLUSIVE_IF_ANY_EMPTY':raise ValueError('unregistered empty bootstrap policy')
    rows=ordered_worlds(records,range(settings['final_worlds']))
    for row in rows:validate_world(row)
    ev={};nr={};hyp={};n=len(rows)
    draws=np.random.default_rng(entropy).integers(0,n,size=(settings['bootstrap_resamples'],n))
    chain=[r['world'] for r in rows if r['chain_complete']]
    invalid_turn={t:any(r['invalid'] and r['invalid'].get('turn',1)<=t for r in rows) for t in (1,2)}
    gate=all(v.get('passed',False) for v in engineering.values())
    grid_verdicts_valid=True
    for prefix in ('','chain_'):
        for turn in (1,2):
            valid=gate and not (any(invalid_turn.values()) if prefix else invalid_turn[turn]);claims={}
            for kind in ('response','later_formation'):
                verdicts=[]
                for control in P.CONTROLS:
                    values_by_grid=[np.full(n,np.nan) for _ in range(3)]
                    ids=[]
                    for r in rows:
                        if prefix and r['world'] not in chain:continue
                        if len(r['turns'])<turn:continue
                        c=r['turns'][turn-1]
                        if not c['operation_eligible']:continue
                        ids.append(r['world'])
                        if kind=='response':
                            diffs=np.array(c['response']['intact']['gain_by_dt'])-np.array(c['response'][control]['gain_by_dt'])
                        else:
                            value=formation(c['episodes']['intact'])-formation(c['episodes'][control]);diffs=[value]*3
                        for k in range(3):values_by_grid[k][r['world']]=diffs[k]
                    cis=[bootstrap(v,draws,settings['ci_level']) if ids else None for v in values_by_grid]
                    margin=settings['margins'][kind]
                    vv=[change_verdict(ci,len(ids),margin,settings['worlds_minimum']) for ci in cis]
                    numeric_agreement=len(set(vv))==1
                    effective_valid=valid and numeric_agreement
                    verdict=vv[0] if effective_valid else 'INCONCLUSIVE';verdicts.append(verdict)
                    name=f'b_{prefix}{kind}_vs_{control}_turn{turn}'
                    ev[name]={'value':{'world_ids':ids,'values_by_dt':[[None if not np.isfinite(x) else float(x) for x in v] for v in values_by_grid],
                        'ci_by_dt':cis,'ci95':bootstrap(values_by_grid[0],draws,.95) if ids else None,'margin':margin,'n':len(ids),
                        'empty_resamples':int(np.sum(np.isfinite(values_by_grid[0])[draws].sum(1)==0)),
                        'bootstrap_empty_policy':settings['bootstrap_empty_policy']},
                        'verdict':verdict,'engineering_valid':effective_valid,'reason':None if effective_valid else 'engineering scope or grid-verdict agreement failed'}
                    if not numeric_agreement:valid=False;grid_verdicts_valid=False
                background=None if kind=='response' else claims['H-BG']
                claim=combine(verdicts,valid,background);claims['H-BG' if kind=='response' else 'H-PS']=claim
            for key,value in claims.items():hyp[key+('_chain' if prefix else '')+'_turn'+str(turn)]=value
    required=[hyp[k+'_turn1'] for k in ('H-BG','H-PS')]+[hyp[k+'_chain_turn'+str(t)] for t in (1,2) for k in ('H-BG','H-PS')]
    witnesses=sum(r['enabled_witness'] for r in rows)
    hyp['H-RBG']=recursive(required,len(chain),witnesses,gate and not any(invalid_turn.values()))
    for key in ('H-COMP','H-PRED','H-AI','H-EFF'):hyp[key]='NOT_TESTED'
    for turn in (1,2):
        reached=[{'world':r['world'],'cell':r['turns'][turn-1]} for r in rows if len(r['turns'])>=turn]
        for name in TURN_DIAGNOSTICS:
            endpoint=f'b_{name}_turn{turn}'
            if not reached:
                nr[endpoint]={'reason':'operation not reached; see source qualification and invalid records'};continue
            values=[]
            for r in reached:
                c=r['cell'];conditions=c['conditions']
                mapping={'source_qualification':c['source'],'operation_eligibility':c['operation_eligible'],'source_persistence':{q:v['persistence_by_dt'] for q,v in conditions.items()},
                    'sham_preservation':conditions['no_backreaction']['output_check'],'no_r_control':conditions['no_r']['endpoint_qualification'],
                    'publication':c['source']['publication'],'background_snapshots':{'before':c['before_ids'],'after':{q:v['after_ids'] for q,v in conditions.items()}},
                    'response_raw':c['response'],'background_diagnostics':{'physical_outcome':c['physical_outcome'],'fields':{q:v.get('background_diagnostics',{}) for q,v in conditions.items()}},
                    'before_and_control_formation':c['before_formation'],'measurement_episodes':{q:[e for e in es if e['episode'] in (1,2,3,4)] for q,es in c['episodes'].items()},
                    'continuation_episodes':{q:es[0] for q,es in c['episodes'].items()},'numerical_refinement':next(v['checks'] for v in rows if v['world']==r['world']),
                    'output_power':{q:v['output_check'] for q,v in conditions.items()},'normalization':{'base_length':1.,'base_time':1.,'field_amplitude':1.}}
                values.append({'world':r['world'],'value':mapping[name]})
                # Raw diagnostics stay in the hash-bound world artifact instead
                # of being duplicated into a multi-gigabyte aggregate receipt.
                if name in ('response_raw','measurement_episodes','continuation_episodes','numerical_refinement','source_persistence'):
                    pointer=('/checks' if name=='numerical_refinement' else f'/turns/{turn-1}/'+
                        ('response' if name=='response_raw' else 'conditions' if name=='source_persistence' else 'episodes'))
                    values[-1]['value']={'artifact':f"world_{r['world']:03d}.json.gz",'json_pointer':pointer,
                        'episode_numbers':[0] if name=='continuation_episodes' else [1,2,3,4] if name=='measurement_episodes' else None}
            ev[endpoint]={'value':values,'verdict':'PASS' if not invalid_turn[turn] else 'FAIL'}
        if turn==1:
            values=[{'world':r['world'],'value':r['initial_source']['qualification']} for r in rows if r.get('initial_source')]
            if values:
                nr.pop('b_source_qualification_turn1',None)
                ev['b_source_qualification_turn1']={'value':values,'verdict':'PASS' if not invalid_turn[1] else 'FAIL'}
    globals_values={'b_source_population_inputs':[{'world':r['world'],'source':source_inputs_summary(r),'invalid':r['invalid']} for r in rows],
        'b_chain_yield':{'complete':len(chain),'worlds':n,'eligible_first':sum(bool(r['turns'] and r['turns'][0]['operation_eligible']) for r in rows),'ids':chain},
        'b_chain_provenance':[{'world':r['world'],'links':r['links']} for r in rows],
        'b_enablement_witnesses':{'count':witnesses,'worlds':n,'ids':[r['world'] for r in rows if r['enabled_witness']]},
        'b_costs':[{'world':r['world'],'seconds':r['seconds'],'peak_rss_bytes':r['peak_rss_bytes'],
                    'memory_measurement':r['memory_measurement'],'native_build':r['native_build']} for r in rows],
        'b_sensitivity':{'eligible_chains':len(chain),'minimum_worlds':10,'approximate_halfwidth_coefficient':2.96,'bootstrap_resamples':settings['bootstrap_resamples']}}
    for key in ('b_reference_equivalence','b_transform_equivariance','source_pin'):globals_values[key]=engineering[key]
    for key in GLOBAL:ev[key]={'value':globals_values[key],'verdict':'PASS' if gate else 'FAIL'}
    for key in ARM_A:nr[key]={'reason':'Arm A retained STOP: '+settings['arm_a_stop']}
    if set(ev)|set(nr)!=set(ENDPOINTS) or set(ev)&set(nr):raise ValueError('endpoint coverage mismatch')
    gates={'engineering':gate,'controls_numerics':not any(invalid_turn.values()) and grid_verdicts_valid,'world_inventory':len(rows)==settings['final_worlds'],'endpoint_coverage':True}
    return {'hypotheses':hyp,'gates':gates,'endpoint_coverage':{'evaluated':ev,'not_run':nr},'primary_contrasts':16}
