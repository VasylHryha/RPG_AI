"""Deterministic descriptive summaries; no experimental execution."""
from collections import Counter
import math
from ..medium.design_0h import wrap

INTERPRETATION={
    'revision_7_motion':dict(status='DESCRIPTIVE',observation_channel='active input sites act as external motion bodies in addition to phase drives',
        claim='anchoring is an engineering hypothesis, not established by adding the site-body law',
        site_body_off='total effect of removing site bodies, including motion-neighbour selection and normalization changes'),
    'revision_7_clocks':dict(status='ENGINEERING_ADMISSION',windows_seconds=[10,60],
        claim='unchanged fixed windows for new driven anchored snapshots; no source-recursion qualification',
        geometric_reference='geometry_rate*A/r_star in inverse world seconds; r_star=1/(1+J), a declared length reference, not a measured relaxation rate'),
    'section_19_9':dict(status='DESCRIPTIVE',used_in_verdict=False,
        input_phasor='perceive: weighted input angle, C=1; failure to beat it shows no computation beyond averaging inputs',
        k_zero='internal C4 phase coupling zero at every RK4 stage; drives, motion and readout retained',
        fixed_structure='final copy with frozen positions and growth off; compare with normal mobile copy'),
    'choose':dict(status='SECONDARY_DESCRIPTIVE',ceiling='lossy strength encoding; identical drives can require different targets; exact general target selection impossible',claim='no target selection claim'),
    'move':dict(status='SECONDARY_DESCRIPTIVE',ceiling='singleton C=1 gives magnitude=1, including zero demand',claim='no stopping or braking claim'),
    'remember_static':dict(status='SECONDARY_DESCRIPTIVE',claim='no memory or multi-oscillator computation claim from superiority to default/random alone',clocks='visible encoding 4 s; hidden retention 12 s; no established-block B1 demand or reward eligibility'),
    'output_channel_lesion':'terminal readout dependence: necessity of coupling into O; internal mechanism unidentified; geometry-mediated internal routes remain',
    'path_exposure_and_locking':'descriptive; not causal proof',
    'six_of_eight':'development continuation rule; fair-sign one-sided tail 0.145; not significance or confirmation',
    'snapshots':'nested dependent evidence; not independent functional modules',
    'coverage':'F5/F7 perceive-only; F9 move only; secondary rows on the fixed evaluation panel',
}


def clock_ledger(native):
    """Endpoint coupling coefficients and dimensionless comparisons, not new cuts."""
    es=native.elements;ds=native.reference_drives();p=native.params
    indices,masks,_=native.neighbors();scale,_,_=native.policy()
    r_star=p.B/(p.A*(1+p.J))
    geometric=p.geometry_rate*p.A/r_star
    rows=[]
    def row(kind,source,target,coefficient):
        return dict(kind=kind,source=source,target=target,scaled_coefficient=coefficient,
            against_carrier=coefficient/math.pi,against_geometric_reference=coefficient/geometric if geometric else None)
    lesions=set(native.reference_lesions())
    for e,links,mask in zip(es,indices,masks):
        selected=[j for j,on in zip(links,mask) if on]
        for j in selected:
            f=es[j];r=math.hypot(f.x-e.x,f.y-e.y)
            w=math.exp(-r*r) if p.distance_weighted else 1.
            coefficient=0. if e.id in lesions else scale*p.K*w/max(1,len(selected))
            rows.append(row('element',f.id,e.id,coefficient))
        if not e.silent and native.role(e.id)!='output':
            for d in ds:
                r=math.hypot(d.x-e.x,d.y-e.y)
                if d.strength>0 and r<d.reach:
                    rows.append(row('site',d.id,e.id,scale*native.gain(e.id)*d.strength*math.exp(-r*r/(2*d.width*d.width))))
    return dict(lambda_value=scale,carrier_rate=math.pi,geometric_length_reference=r_star,
        geometric_rate_reference=geometric,coefficient_units='radians per world second; radians dimensionless for ratios',
        ratio_units='dimensionless',estimator_seconds=10.,qualification_seconds=60.,rows=rows)


def memory_windows(decisions,carrier_offset=0.):
    """Keep encoding accuracy and retention drift distinct, including absence."""
    visible=decisions[:40];hidden=decisions[40:160]
    cue=None
    for j,row in enumerate(visible):
        active=[d for d in row['drives'] if d[5]>0]
        if active:cue=float(wrap(active[0][3]-carrier_offset-math.pi*j*.1))
    def summary(rows,reference):
        available=[r for r in rows if r['has_output']]
        errors=[abs(float(wrap(r['angle']-reference))) for r in available] if reference is not None else []
        return dict(decisions=len(rows),defined_output_decisions=len(available),reference=reference,
            mean_abs_error=None if not errors else sum(errors)/len(errors),
            angles=[r['angle'] for r in rows],has_output=[r['has_output'] for r in rows])
    last=visible[-1]['angle'] if visible and visible[-1]['has_output'] else None
    retained=[r for r in hidden if r['has_output']]
    drift=sum(abs(float(wrap(r['angle']-last))) for r in retained)/len(retained) if last is not None and retained else None
    return dict(encoding=dict(window_seconds=[0,4],**summary(visible,cue)),
        retention=dict(window_seconds=[4,16],**summary(hidden,cue),encoded_output=last,
            mean_abs_drift_from_encoded_output=drift))



def descriptive(events,diagnostics,counts,*,start=0.,end=32000.):
    events=[r for r in events if start<=r['time']<=end]
    roles={}
    for role in ('B-out','B-path','B1'):
        terminals=[r for r in events if r['rule']=='birth_terminal' and r['values']['birth_rule']==role]
        requests=[r for r in events if r['rule']=='birth_request' and r['values']['birth_rule']==role]
        opportunities=len(requests);attempts=sum(r['values']['attempts'] for r in terminals)
        outcomes=Counter(r['values']['outcome'] for r in terminals);accepted=outcomes['accepted']
        failures=Counter()
        for r in terminals:failures.update(r['values'].get('failures',{}))
        roles[role]=dict(opportunities=opportunities,attempts=attempts,accepted=accepted,
            terminal_requests=len(terminals),outcomes=dict(outcomes),trial_failures=dict(failures),
            acceptance_per_opportunity=accepted/opportunities if opportunities else None,
            acceptance_per_attempt=accepted/attempts if attempts else None,
            resource_rejections={code:dict(count=outcomes[code],per_opportunity=outcomes[code]/opportunities if opportunities else None,
                per_attempt=outcomes[code]/attempts if attempts else None,per_acceptance=outcomes[code]/accepted if accepted else None)
                for code in ('cap','cost')})
    rows=[r for r in diagnostics if start<r['index']*.1<=end]
    sample_counts=[n for t,n in counts if start<=t<=end]
    samples=wall=no_access=wall_no_access=0;maximum=None;per_element={}
    active_exposure=[0]*8;path_exposure=[0]*8;uncovered=eligible=warmup=0
    for row in rows:
        for site in range(8):
            path_exposure[site]+=int(row['paths'][site])
            if site in row.get('active_sites',[]):
                active_exposure[site]+=1
                covered=row.get('covered_sites',{}).get(site,row.get('covered_sites',{}).get(str(site)))
                if covered is None:warmup+=1
                else:eligible+=1;uncovered+=int(not covered)
        for id,v in row['exposure'].items():
            id=str(id);samples+=1;wall+=int(v['wall']);no_access+=int(not v['sensor_access']);wall_no_access+=int(v['wall'] and not v['sensor_access'])
            maximum=v['radius'] if maximum is None else max(maximum,v['radius'])
            item=per_element.setdefault(id,dict(samples=0,wall_samples=0,no_sensor_access_samples=0,max_radius=0.))
            item['samples']+=1;item['wall_samples']+=int(v['wall']);item['no_sensor_access_samples']+=int(not v['sensor_access']);item['max_radius']=max(item['max_radius'],v['radius'])
    for item in per_element.values():
        item['penetration_seconds']=item['wall_samples']*.1
        item['no_sensor_access_seconds']=item['no_sensor_access_samples']*.1
    deaths=Counter(r['rule'] for r in events if r['rule'] in ('D1','D3','D4'))
    return dict(window_seconds=[start,end],birth_roles=roles,
        cap_limited=any(v['outcomes'].get('cap',0) for v in roles.values()),cost_limited=any(v['outcomes'].get('cost',0) for v in roles.values()),
        unmet_output_or_path_demand=any(v['outcomes'].get(code,0) for role,v in roles.items() if role in ('B-out','B-path') for code in ('cap','cost','placement','exhausted','no_output','no_root','quota')),
        turnover=dict(births=sum(v['accepted'] for v in roles.values()),deaths=sum(deaths.values()),death_rules=dict(deaths),growth_checks=sum(r['rule']=='growth_check' for r in events)),
        count_range=[min(sample_counts),max(sample_counts)] if sample_counts else None,
        uncovered_sensor_exposure=dict(uncovered_site_steps=uncovered,defined_active_site_steps=eligible,undefined_warmup_site_steps=warmup,fraction=uncovered/eligible if eligible else None),
        path_exposure=dict(world_steps=len(rows),site_path_steps=path_exposure,site_active_steps=active_exposure,fractions=[n/len(rows) if rows else None for n in path_exposure]),
        wall=dict(maximum_radius=maximum,element_steps=samples,penetration_element_seconds=wall*.1,
            no_sensor_access_element_seconds=no_access*.1,wall_without_sensor_access_element_seconds=wall_no_access*.1,per_element=per_element))
