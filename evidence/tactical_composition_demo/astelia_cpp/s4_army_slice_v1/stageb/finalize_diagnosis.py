"""Seal archived zero-fight diagnosis; finish missing control and causal audit."""
import runtime as r
import collections,math,time
from recording import rows
from diagnose import offline_distribution,ROLES

def supplement(raw):
    role_ids={};first={};events={};own_damage=0.;credit=collections.Counter();kills=collections.Counter()
    for row in rows(raw):
        if row.get('stageA'):
            for u in row['units']:
                if u[1]==0:role_ids[u[0]]=ROLES[u[2]]
        elif row.get('observerV1'):
            for shot in row.get('shotsV6',[]):
                if shot[1] in role_ids:
                    first.setdefault(str(shot[1]),shot[2]);events[str(shot[1])]=events.get(str(shot[1]),0)+1
            for shot in row.get('launches',[]):
                if shot[2]==0 and shot[0] in role_ids:
                    first.setdefault(str(shot[0]),row['t']);events[str(shot[0])]=events.get(str(shot[0]),0)+1
            for d in row['damage']:
                if d['sourceTeam']==0 and d['targetTeam']==1:
                    own_damage+=d['dealt']
                    if d['sourceRole']=='melee':first.setdefault(str(d['source']),row['t'])
                if d['died'] and d['targetTeam']==1:credit[f"{d['sourceTeam']}:{d['sourceRole']}"]+=1
                if d['died'] and d['targetTeam']==0:kills[f"{d['sourceTeam']}:{d['sourceRole']}"]+=1
    return dict(own_damage_to_enemy=own_damage,enemy_death_credit=dict(credit),own_deaths_by_source=dict(kills),actual_first_attack={role:dict(times={id:t for id,t in first.items() if role_ids[int(id)]==role},never_started=[id for id,v in role_ids.items() if v==role and str(id) not in first],projectile_births=sum(n for id,n in events.items() if role_ids[int(id)]==role)) for role in ROLES})

def state_divergence(a,b):
    left=(x for x in rows(a) if x.get('stageA'));right=(x for x in rows(b) if x.get('stageA'))
    for x,y in zip(left,right):
        if abs(x['t']-y['t'])>1e-8:raise RuntimeError('paired clock mismatch')
        u={v[0]:v for v in x['units']};v={v[0]:v for v in y['units']}
        for id in sorted(set(u)|set(v)):
            if id not in u or id not in v:return dict(t=x['t'],id=id,reason='living identity')
            delta=math.hypot(u[id][3]-v[id][3],u[id][4]-v[id][4])
            if delta>1e-8:return dict(t=x['t'],id=id,reason='position',distance_px=delta)
    return None

def run():
    start=time.monotonic();out=r.LOCAL/'diagnosis';archive=r.LOCAL/'diagnosis_revision'
    import parity,training
    parity.LOCAL=r.A_LOCAL;training.environment()
    missing=out/'N2J0_training_distribution.json'
    if not missing.exists():
        fights=[f for f in r.read(r.A_LOCAL/'INDEX.json')['fights'] if f['split']=='train']
        r.write(missing,offline_distribution('N2J0',fights,'train'),exclusive=True)
    index=r.read(r.A_LOCAL/'INDEX.json');records=[];ledger=r.read(r.A_LOCAL/'OUTCOME_LEDGER.json');jobs={j['tag']:j for j in ledger['jobs']}
    archived={p.name:r.sha(p) for p in archive.iterdir() if p.is_file()}
    for path in sorted((r.A_LOCAL/'raw').glob('outcome*_COMPLETE.json')):
        c=r.read(path);j=jobs[c['job']['tag']];request=r.A_LOCAL/'requests'/(j['tag']+'.json');raw=r.A_LOCAL/c['raw_file'];cached=out/(j['tag']+'.json');x=r.read(cached)
        if c['job']!=j or c['ledger_sha256']!=r.sha(r.A_LOCAL/'OUTCOME_LEDGER.json') or r.sha(raw)!=c['raw_sha256'] or r.sha(request)!=j['request_sha256'] or x['binding']['raw_sha256']!=c['raw_sha256'] or x['binding']['completion_sha256']!=r.sha(path) or x['binding']['oracle_binary_sha256']!=r.sha(archive/'tactics_react_host_stageb'):raise RuntimeError('archived diagnosis identity mismatch')
        x['provenance']=dict(raw_sha256=c['raw_sha256'],request_sha256=r.sha(request),completion_sha256=r.sha(path),cache_sha256=r.sha(cached),ledger_sha256=r.sha(r.A_LOCAL/'OUTCOME_LEDGER.json'),source_archive=archived)
        x['causal_audit']=supplement(raw);records.append(x)
    bypair={(x['job']['pair_key'],x['job']['arm']):x for x in records};paired={}
    for arm in (*r.ARMS,'N2J0'):
        pairs=[]
        for x in records:
            key=x['job']['pair_key']
            if x['job']['arm']!=arm or (key,'O') not in bypair:continue
            o=bypair[key,'O'];a=r.read(r.A_LOCAL/'raw'/(x['job']['tag']+'_COMPLETE.json'));b=r.read(r.A_LOCAL/'raw'/(o['job']['tag']+'_COMPLETE.json'))
            pairs.append(dict(net=x,oracle=o,first_paired_state_divergence=state_divergence(r.A_LOCAL/a['raw_file'],r.A_LOCAL/b['raw_file'])))
        paired[arm]=pairs
    distribution={arm:r.read(out/(arm+'_training_distribution.json')) for arm in (*r.ARMS,'N2J0')}
    proof={arm:dict(cache_sha256=r.sha(out/(arm+'_training_distribution.json')),index_sha256=r.sha(r.A_LOCAL/'INDEX.json'),export_sha256=r.sha(r.A_LOCAL/'training'/(arm+'.weights.json')),raw_hashes={f['tag']:r.sha(r.A_LOCAL/f['raw_file']) for f in index['fights'] if f['split']=='train'},source_archive=archived,completion_note='four retained arms produced before registry failure; N2J0 finished with only historical-arm registry allowance') for arm in distribution}
    control_rows=sum(sum(v['rows'] for v in x['roles'].values()) for x in records if x['job']['arm']=='O');control_errors=sum(sum(h['error_sum'] for h in v['heads'].values()) for x in records if x['job']['arm']=='O' for v in x['roles'].values())
    payload=dict(status='DESCRIPTIVE_PARTIAL',fresh_fights=0,completed_fights=len(records),paired_counts={a:len(p) for a,p in paired.items()},records=records,paired=paired,training_distribution=distribution,training_provenance=proof,oracle_control=dict(rows=control_rows,total_head_error=control_errors),supplement_seconds=time.monotonic()-start,supplement_provenance=dict(sources=r.sources(),scope='causal audit/state divergence and any missing distribution; older caches retain source_archive'),top_causes=['No melee targets/attacks in all five nets; severe target None collapse in other roles','Fire suppression on physically eligible ticks; not sufficient to explain failure alone','Large movement and artillery aim errors already on training distribution; goal/aim loss scale too small','Ranged/artillery target disagreement grows on student occupancy: DAgger gap','Formation collapse and earlier enemy melee deaths; enemy body deaths include enemy friendly fire'],definitions=dict(opportunities='physical eligible ticks, not independent chances',release_intent='legacy roles.releases counts intent ticks, not births',first_attack='causal_audit uses shotsV6 born for ranged, shell launch for artillery, dealt-to-enemy for melee; no event means right censored',paired='9 regular + 1 C3 matching seeds per net; 3 unmatched student fights excluded',gap='compare roles.raw_heads vs training_distribution; heads separately report effective commands',limits='descriptive association, no causal intervention; single C3 seed; no full new fights; no population qualification'))
    r.write(r.HERE/'STAGEB_DIAGNOSIS_COUNTS.json',payload)
if __name__=='__main__':run()
