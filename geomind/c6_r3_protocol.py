"""Fixed R3 world construction, paired two-turn assay, coverage and verdicts."""
import copy
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from geomind import c4_detect as D
from geomind import c6_r3_background as B, c6_r3_assay as A

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'experiments/c6_r3_protocol.json'
CONDITIONS=('intact','no_r','no_backreaction')
CONTROLS=CONDITIONS[1:]
ARM_A_ENDPOINTS=tuple(f'{name}_l{level}' for level in (2,3) for name in
    ('formation','g_to_m','m_to_g','dose_response','parts_alive','downward_effect',
     'emergent_transfer','effective_state','coarse_vs_full','same_law_closure','scale_separation'))+('upward_transfer_l3','level_interface')
B_TURN_ENDPOINTS=('source_qualification','sham_preservation','no_r_control',
                 'background_position','before_and_control_formation','later_diagnostics')
ENDPOINTS=tuple(f'b_{name}_turn{turn}' for turn in (1,2) for name in B_TURN_ENDPOINTS)+tuple(
    f'b_{name}_vs_{control}_turn{turn}' for turn in (1,2) for control in CONTROLS
    for name in ('background_phase','later_formation'))+('b_chain_yield','b_chain_provenance','b_numerical_checks','b_costs','source_pin',*ARM_A_ENDPOINTS)


def load_settings():
    return json.loads(PROTOCOL.read_text())


def rng(entropy,world,purpose):
    return np.random.default_rng(np.random.SeedSequence([int(entropy),int(world),int(purpose)]))


def population(settings,entropy,world,purpose,centre,bath=False):
    r=rng(entropy,world,purpose);w=settings['worlds'];n=w['bath_elements'] if bath else w['source_elements']
    radius=w['disk_radius']*np.sqrt(r.random(n));angle=r.uniform(0,2*np.pi,n)
    x=np.c_[radius*np.cos(angle),radius*np.sin(angle)]+centre
    th=r.uniform(-np.pi,np.pi,n)
    omega=r.uniform(-w['bath_omega_half_width'],w['bath_omega_half_width'],n) if bath else np.zeros(n)
    order=r.permutation(n)
    return x[order],th[order],omega[order]


def publication(formation,state,omega,settings):
    if not formation['qualified']:
        return None
    selected=next(r for r in formation['candidates'] if r['digest']==formation['selected_digest'])
    members=np.array(selected['members']);stats=selected['stats']
    pub=D.active_unit(state[0],state[1],stats['collective_frequency'],members,stats)
    pub.update(member_digest=selected['digest'],qualification=formation['causal'])
    if not finite(pub):
        raise FloatingPointError('nonfinite candidate-linked publication')
    return pub


def finite(value):
    if isinstance(value,dict):return all(finite(v) for v in value.values())
    if isinstance(value,(list,tuple)):return all(finite(v) for v in value)
    if isinstance(value,(float,np.floating)):return bool(np.isfinite(value))
    return True


def numerics(apparatus):
    """Short deterministic diagnostics on this world; no outcomes select settings."""
    from geomind.c6_r3_reference import simulate
    x=np.vstack([apparatus.bath[0],apparatus.source[0]]);th=np.r_[apparatus.bath[1],apparatus.source[1]]
    nb=apparatus.nb;duration=min(2.,apparatus.reference.duration)
    args=(x[:nb],th[:nb],apparatus.bath[2],duration)
    kwargs={'source':apparatus.source,'reference':apparatus.reference,'prior':apparatus.prior}
    native=B.run(*args,**kwargs);reference=simulate(*args,**kwargs)
    error=max(float(np.max(np.abs(a-b))) for a,b in zip(native,reference))
    half=B.run(*args,**kwargs,dt=.01,sample_dt=.02)
    quarter=B.run(*args,**kwargs,dt=.005,sample_dt=.02)
    dt_error=max(float(np.max(np.abs(a-b))) for a,b in zip(native,quarter))
    half_error=max(float(np.max(np.abs(a-b))) for a,b in zip(half,quarter))
    angle=.73;rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    shift=np.array([7.,-3.]);phase=.41
    ref=B.Replay(apparatus.reference.x@rotation.T+shift,apparatus.reference.theta+phase,apparatus.reference.dt)
    prior=None if apparatus.prior is None else B.Replay(apparatus.prior.x@rotation.T+shift,apparatus.prior.theta+phase,apparatus.prior.dt)
    transformed=B.run(x[:nb]@rotation.T+shift,th[:nb]+phase,apparatus.bath[2],duration,
        source=(x[nb:]@rotation.T+shift,th[nb:]+phase,apparatus.source[2]),reference=ref,prior=prior)
    symmetry=max(float(np.max(np.abs(transformed[0]-(native[0]@rotation.T+shift)))),
                 float(np.max(np.abs(transformed[1]-(native[1]+phase)))))
    q=apparatus.settings['qualification']
    return {'native_reference_error':error,'dt_error':dt_error,'dt_half_error':half_error,
            'equivariance_error':symmetry,'passed':error<=q['native_reference_tolerance']
             and dt_error<=q['dt_tolerance'] and symmetry<=q['equivariance_tolerance']}


def numerical_windows(apparatus,flow,after):
    start=apparatus.settings['integration']['formation']
    end=B.exact_steps(start,apparatus.dt)
    duration=min(2.,apparatus.reference.duration-start)
    source=(flow[0][end,apparatus.nb:].copy(),flow[1][end,apparatus.nb:].copy(),apparatus.source[2])
    formed=A.Apparatus(after,source,apparatus.reference.slice(start,duration),
        None if apparatus.prior is None else apparatus.prior.slice(start,duration),apparatus.settings)
    checks={'initial':numerics(apparatus),'formation_snapshot':numerics(formed)}
    return {**checks,'passed':all(c['passed'] for c in checks.values())}


def next_turn_source(first):
    # The caller supplies episode zero. No scan, fallback or replacement is allowed.
    return first if first is not None and first[2]['qualified'] else None


def assess_turn(apparatus,flows,entropy,world,purpose,cached_intact=None):
    s=apparatus.settings;i=s['integration'];nb=apparatus.nb;end=B.exact_steps(i['formation'],apparatus.dt)
    formation={}
    for c in CONDITIONS:
        formation[c]=cached_intact if c=='intact' and cached_intact is not None else apparatus.formation(flows[c],c,rng(entropy,world,purpose))
    source_error=max(float(np.max(np.abs(flows['intact'][k][:end+1,nb:]-flows['no_backreaction'][k][:end+1,nb:]))) for k in (0,1))
    controls={'sham_source_error':source_error,'sham_outgoing_mask':0.,
              'sham_preserved':source_error<=s['qualification']['sham_source_tolerance'],
              'no_r_qualifies':formation['no_r']['qualified']}
    before_digest=B.digest_state(*apparatus.bath)
    after=tuple(flows['intact'][k][end,:nb].copy() for k in (0,1))+(apparatus.bath[2].copy(),)
    row={'formation':formation,'qualified':formation['intact']['qualified'],'controls':controls,
         'bath_before_digest':before_digest,'bath_after_digest':B.digest_state(*after),
         'source_input_digest':B.digest_state(*apparatus.source),'reference_digest':apparatus.reference.digest,
         'prior_digest':None if apparatus.prior is None else apparatus.prior.digest,
         'numerics':numerical_windows(apparatus,flows['intact'],after),'publication':publication(formation['intact'],
            (flows['intact'][0][end],flows['intact'][1][end]),np.r_[apparatus.bath[2],apparatus.source[2]],s),
         'background':None,'episodes':None,'before_episodes':None}
    if row['qualified']:
        L=D.radius_of_gyration(apparatus.bath[0])
        row['background']={'before':apparatus.measure(flows['intact'],0.,L,'intact'),
            **{c:apparatus.measure(flows[c],i['formation'],L,c) for c in CONDITIONS}}
    return row,after


def make_flows(apparatus,intact_duration,cached_intact=None):
    i=apparatus.settings['integration'];control_duration=i['formation']+max(i['recovery'],i['descriptor'])
    return {'intact':apparatus.run(intact_duration) if cached_intact is None else cached_intact,
            'no_r':apparatus.run(control_duration,'no_r'),
            'no_backreaction':apparatus.run(control_duration,'no_backreaction')}


def candidate_assay(baths,drivers,settings,entropy,world,turn,keep_first=False):
    """Same unformed candidates per paired bath; no relocation from observed groups."""
    i=settings['integration'];dt=i['dt'];duration=(2*i['formation']+i['recovery']) if keep_first else i['formation']+i['recovery']
    references={}
    for condition,bath in baths.items():
        frames=B.run(*bath,duration,prior=drivers.slice(0.,duration),dt=dt)
        references[condition]=B.Replay(*frames,dt)
    episodes={c:[] for c in baths};first=None
    for episode in range(settings['episodes']):
        source=population(settings,entropy,world,3000+turn*100+episode,settings['worlds']['candidate_centre'])
        for condition,bath in baths.items():
            app=A.Apparatus(bath,source,references[condition],drivers,settings)
            horizon=duration if keep_first and episode==0 and condition=='intact' else i['formation']+i['recovery']
            flow=app.run(horizon)
            form=app.formation(flow,'intact',rng(entropy,world,4000+turn*100+episode))
            digest=B.digest_state(*source)
            episodes[condition].append({'candidate_initial_digest':digest,'formation':form,
                                        'persistent_unit':form['qualified']})
            if keep_first and episode==0 and condition=='intact':first=(app,flow,form)
    assert all([e['candidate_initial_digest'] for e in episodes[c]]==[e['candidate_initial_digest'] for e in episodes['intact']] for c in baths)
    return episodes,first


def run_world(settings,entropy,world,progress=None):
    B.reset_costs();started=time.perf_counter();s=settings;i=s['integration'];dt=i['dt'];N=i['formation']
    bath=population(s,entropy,world,0,s['worlds']['bath_centre'],True)
    source=population(s,entropy,world,1,s['worlds']['source_centre'])
    # Long enough to supply every recovery/probe/later-assay continuation; never recycle terminal frames.
    total=3*N+i['recovery']
    reference=B.Replay(*B.run(*bath,total,dt=dt),dt)
    app=A.Apparatus(bath,source,reference,None,s)
    flows=make_flows(app,total);t1,after=assess_turn(app,flows,entropy,world,10)
    row={'world':world,'turns':[t1],'chain_link':None,'seconds':None,'status':'EVALUATED'}
    if progress:progress('turn1',row)
    if t1['qualified'] and t1['controls']['sham_preserved'] and not t1['controls']['no_r_qualifies'] and t1['numerics']['passed']:
        end=B.exact_steps(N,dt)
        drivers=B.Replay(flows['intact'][0][end:,app.nb:],flows['intact'][1][end:,app.nb:],dt)
        baths={c:tuple(flows[c][k][end,:app.nb].copy() for k in (0,1))+(bath[2].copy(),) for c in CONDITIONS}
        episodes,first=candidate_assay(baths,drivers,s,entropy,world,1,True)
        t1['episodes']=episodes
        # Before-background assay uses the same episode initial entropy, with continued common R0 drive.
        before_episodes,_=candidate_assay({'intact':bath},drivers,s,entropy,world,1)
        t1['before_episodes']=before_episodes['intact']
        continuation=next_turn_source(first)
        if continuation is not None:
            second_app,second_intact,first_form=continuation
            second_flows=make_flows(second_app,2*N+i['recovery'],cached_intact=second_intact)
            t2,after2=assess_turn(second_app,second_flows,entropy,world,4100,cached_intact=first_form)
            row['turns'].append(t2)
            row['chain_link']={'first_after':t1['bath_after_digest'],'second_before':t2['bath_before_digest'],
                'first_episode_source':episodes['intact'][0]['candidate_initial_digest'],
                'second_source_input':t2['source_input_digest'],'intact_episode_reused':True}
            if t2['qualified'] and t2['controls']['sham_preserved'] and not t2['controls']['no_r_qualifies'] and t2['numerics']['passed']:
                d1=drivers.slice(N,N+i['recovery'])
                d2=B.Replay(second_intact[0][end:,second_app.nb:],second_intact[1][end:,second_app.nb:],dt)
                new_drivers=B.combined(d1,d2)
                baths2={c:tuple(second_flows[c][k][end,:second_app.nb].copy() for k in (0,1))+(bath[2].copy(),) for c in CONDITIONS}
                t2['episodes'],_=candidate_assay(baths2,new_drivers,s,entropy,world,2)
                before2,_=candidate_assay({'intact':second_app.bath},new_drivers,s,entropy,world,2)
                t2['before_episodes']=before2['intact']
    row['seconds']=time.perf_counter()-started
    row['costs']=B.costs()
    row['unreached_turn_reason']=None if len(row['turns'])==2 else 'predefined episode-0 R1 or initial source did not qualify; no replacement'
    return row


def interval(values,draws,level):
    """Resample original world IDs, retaining missing-source masks and paired draws."""
    values=np.asarray(values,float);sampled=values[draws];counts=np.isfinite(sampled).sum(1)
    means=np.nansum(sampled,axis=1)/np.maximum(counts,1)
    means=means[counts>0]
    if not len(means):return None
    tail=(1-level)/2
    return [float(np.quantile(means,tail)),float(np.quantile(means,1-tail))]


def contrast_verdict(ci,margin,n,minimum):
    if ci is None or n<minimum:return 'INCONCLUSIVE'
    if ci[0]>margin:return 'PASS'
    if ci[1]<margin:return 'FAIL'
    return 'INCONCLUSIVE'


def claim(verdicts):
    if all(v=='PASS' for v in verdicts):return 'SUPPORTED_WITHIN_SCOPE'
    if any(v=='FAIL' for v in verdicts):return 'NOT_SUPPORTED'
    return 'INCONCLUSIVE'


def evaluate(records,settings,bootstrap_entropy=46033002):
    n=len(records);st=settings['statistics'];r=np.random.default_rng(bootstrap_entropy)
    draws=r.integers(0,n,size=(st['bootstrap_resamples'],n)) if n else np.empty((0,0),int)
    ev={};not_run={};hypotheses={};gates={'finite_records':finite(records),'source_controls':True,'numerical_checks':True,'chain_provenance':True}
    for name in ARM_A_ENDPOINTS:not_run[name]={'reason':settings['arm_a']}
    for turn in (1,2):
        cells=[row['turns'][turn-1] if len(row['turns'])>=turn else None for row in records]
        qualified=sum(bool(c and c['qualified']) for c in cells)
        ev[f'b_source_qualification_turn{turn}']={'value':{'qualified':qualified,'total_worlds':n},'verdict':'DIAGNOSTIC'}
        reached=[c for c in cells if c is not None]
        for name,passed in (('sham_preservation',all(c['controls']['sham_preserved'] for c in reached)),
                             ('no_r_control',all(not c['controls']['no_r_qualifies'] for c in reached))):
            endpoint=f'b_{name}_turn{turn}'
            if not reached:not_run[endpoint]={'reason':'turn not reached'}
            else:ev[endpoint]={'value':{'checked_worlds':len(reached),'passed':passed},'verdict':'PASS' if passed else 'FAIL'}
            gates['source_controls'] &= passed
        gates['numerical_checks'] &= all(c['numerics']['passed'] for c in reached)
        bgverdicts=[];psverdicts=[]
        for control in CONTROLS:
            for kind,field,margin,output in (
                ('background_phase','b_phase',st['phase_margin'],bgverdicts),
                ('later_formation','persistent_unit',st['formation_margin'],psverdicts)):
                values=[]
                for c in cells:
                    if c is None or not c['qualified'] or c['background'] is None or (kind=='later_formation' and c['episodes'] is None):
                        values.append(float('nan'));continue
                    value=(c['background']['intact'][field]-c['background'][control][field] if kind=='background_phase'
                      else np.mean([e[field] for e in c['episodes']['intact']])-np.mean([e[field] for e in c['episodes'][control]]))
                    values.append(float(value))
                valid=[v for v in values if np.isfinite(v)];name=f'b_{kind}_vs_{control}_turn{turn}'
                if not valid:
                    not_run[name]={'reason':'no qualified source with this paired assay'};output.append('INCONCLUSIVE');continue
                ci=interval(values,draws,st['primary_ci_level']);verdict=contrast_verdict(ci,margin,len(valid),st['minimum_qualified_worlds'])
                ev[name]={'value':{'mean':float(np.mean(valid)),'ci':ci,'nominal_ci':interval(values,draws,st['nominal_ci_level']),
                                   'n_worlds':len(valid),'per_world':[None if not np.isfinite(v) else v for v in values],
                                   'margin':margin},'verdict':verdict};output.append(verdict)
        bg=claim(bgverdicts);ps=claim(psverdicts)
        if bg!='SUPPORTED_WITHIN_SCOPE' and ps=='SUPPORTED_WITHIN_SCOPE':ps='INCONCLUSIVE'
        if not gates['source_controls'] or not gates['numerical_checks']:bg=ps='INCONCLUSIVE'
        hypotheses[f'H-BG_turn{turn}']=bg;hypotheses[f'H-PS_turn{turn}']=ps
        for name,key in (('background_position','background'),('before_and_control_formation','before_episodes'),('later_diagnostics','episodes')):
            values=[None if c is None else c[key] for c in cells]
            endpoint=f'b_{name}_turn{turn}'
            if not any(v is not None for v in values):not_run[endpoint]={'reason':'no qualified source or turn not reached'}
            else:ev[endpoint]={'value':values,'verdict':'DIAGNOSTIC'}
    links=[row['chain_link'] for row in records if row['chain_link'] is not None]
    gates['chain_provenance']=all(l['first_after']==l['second_before'] and l['first_episode_source']==l['second_source_input'] and l['intact_episode_reused'] for l in links)
    complete_chains=sum(row['chain_link'] is not None and len(row['turns'])==2 and all(c['qualified'] and c['background'] is not None and c['episodes'] is not None for c in row['turns']) for row in records)
    ev['b_chain_yield']={'value':{'complete_chains':complete_chains,'linked_turns':len(links),'total_worlds':n},'verdict':'DIAGNOSTIC'}
    ev['b_chain_provenance']={'value':{'links':links,'passed':gates['chain_provenance']},'verdict':'PASS' if gates['chain_provenance'] else 'FAIL'}
    ev['b_numerical_checks']={'value':[c['numerics'] for row in records for c in row['turns']],
                            'verdict':'PASS' if gates['numerical_checks'] else 'FAIL'}
    ev['b_costs']={'value':{'per_world_seconds':[row['seconds'] for row in records],'work_and_storage':[row.get('costs',{}) for row in records]},'verdict':'DIAGNOSTIC'}
    # Source pin check is supplied by the orchestration layer, not inferred from a publication event.
    not_run['source_pin']={'reason':'orchestrator must validate the pinned release inventory'}
    hypotheses['H-RBG']=claim(['PASS' if v=='SUPPORTED_WITHIN_SCOPE' else 'FAIL' if v=='NOT_SUPPORTED' else 'INCONCLUSIVE' for v in hypotheses.values()])
    if not gates['source_controls'] or not gates['numerical_checks'] or not gates['chain_provenance']:
        for name in hypotheses:hypotheses[name]='INCONCLUSIVE'
    if complete_chains<st['minimum_qualified_worlds']:
        hypotheses['H-RBG']='INCONCLUSIVE'
    for name in ('H-COMP','H-PRED','H-AI','H-EFF'):hypotheses[name]='NOT_TESTED'
    if set(ev)|set(not_run)!=set(ENDPOINTS) or set(ev)&set(not_run):raise ValueError('R3 endpoint coverage mismatch')
    return {'endpoint_coverage':{'evaluated':ev,'not_run':not_run},'hypotheses':hypotheses,'gates':gates}
