"""Fresh paired looks with complete per-invocation readouts, including stops."""
import runtime as r
import argparse,random,secrets,time
from execution import execute,disk_projection
from parity_run import gate
from dagger import used_seeds
from recording import rows
POLICIES=(*r.ARMS,'O','T')

def mechanism(raw):
    previous={};enemy_credit={};own_damage=0.;deaths={role:0 for role in ('melee','ranged','artillery')};killers={};m=dict(dodges=0,launches=0,ready_rows=0,active_fire_rows=0,react_rows=0,phase_samples=0,phase_abs_rate_sum=0.,spacing_norm_sum=0.,forcing_abs_sum=0.)
    for row in rows(raw):
        if row.get('observerV1'):
            m['dodges']+=sum(x[1]==0 for x in row['dodges']);m['launches']+=sum(x[2]==0 for x in row['launches'])
            for d in row['damage']:
                if d['sourceTeam']==0 and d['targetTeam']==1:own_damage+=d['dealt']
                if d['died'] and d['targetTeam']==1:
                    key=f"{d['sourceTeam']}:{d['sourceRole']}";enemy_credit[key]=enemy_credit.get(key,0)+1
                if d['died'] and d['targetTeam']==0:
                    deaths[d['targetRole']]+=1;k=f"{d['sourceTeam']}:{d['sourceRole']}:{d['source']}";killers[k]=killers.get(k,0)+1
        elif row.get('stageA'):
            for state in row.get('networkState',[]):
                if row.get('networkKind')=='N2' and len(state)>=11:
                    uid=state[0];m['phase_samples']+=1;m['spacing_norm_sum']+=__import__('math').hypot(state[9],state[10]);m['forcing_abs_sum']+=abs(state[6])
                    if uid in previous:m['phase_abs_rate_sum']+=abs(state[1]-previous[uid][0])/(row['t']-previous[uid][1]);m['phase_rate_samples']=m.get('phase_rate_samples',0)+1
                    previous[uid]=(state[1],row['t'])
            for v in row['labels']:m['ready_rows']+=v['ready'];m['active_fire_rows']+=v['executed']['fire']!='hold';m['react_rows']+=v['active']
    return dict(per_role_deaths=deaths,killer_sources=killers,enemy_death_credit=enemy_credit,own_damage_to_enemy=own_damage,**m)

def prepare(round):
    if round<1:raise RuntimeError('full-fight DAgger refit required before looks')
    gate(round);path=r.LOCAL/f'OUTCOME_LEDGER_ROUND{round}.json'
    if path.exists():return check(round)
    rng=random.Random(secrets.randbits(256));used=used_seeds();base=r.collect.a0();cells=list(base.CELLS);rng.shuffle(cells);jobs=[]
    for panel in ('regular','C3'):
        for i in range(50):
            cell='regular' if panel=='regular' else cells[i%len(cells)];orientation=i%2 if panel=='regular' else (i//len(cells))%2;seed=rng.randrange(1,2**32)
            while seed in used:seed=rng.randrange(1,2**32)
            used.add(seed);pair=f'{panel}_{i:03}'
            for arm in POLICIES:
                tag=f'look_r{round}_{pair}_{arm}';req=base.request('T' if arm=='T' else 'O',cell,seed,orientation);req['stageA']=dict(collect=True);req['decisionTrace']=False
                if arm in r.ARMS:req['stageA'].update(weights=r.read(r.LOCAL/f'round{round}/training/{arm}.weights.json'),shadow=True)
                p=r.LOCAL/'requests'/(tag+'.json');r.write(p,req,exclusive=True);jobs.append(dict(tag=tag,pair_key=pair,index=i,arm=arm,panel=panel,tactic=cell,orientation=orientation,seed=seed,request_sha256=r.sha(p),split='outcome'))
    ledger=dict(round=round,sources=r.sources(),binary=r.collect.identity(),parity_sha256=r.sha(r.LOCAL/f'round{round}/PARITY_STAGEB.json'),jobs=jobs,looks=[20,50]);r.write(path,ledger,exclusive=True);return ledger

def check(round):
    gate(round);ledger=r.read(r.LOCAL/f'OUTCOME_LEDGER_ROUND{round}.json')
    if ledger['binary']!=r.collect.identity() or ledger['sources']!=r.sources() or ledger['parity_sha256']!=r.sha(r.LOCAL/f'round{round}/PARITY_STAGEB.json'):raise RuntimeError('outcome identity drift')
    for j in ledger['jobs']:
        if r.sha(r.LOCAL/'requests'/(j['tag']+'.json'))!=j['request_sha256']:raise RuntimeError('outcome request drift')
    return ledger

def _run(round,look,run_id):
    ledger=check(round);digest=r.sha(r.LOCAL/f'OUTCOME_LEDGER_ROUND{round}.json');start=time.monotonic();receipt=dict(round=round,look=look,status='RUNNING',ledger_sha256=digest,records=[])
    if look==50:
        prior=r.read(r.HERE/f'LOOK_STAGEB_R{round}_20.json')
        if not prior['complete'] or prior['ledger_sha256']!=digest:raise RuntimeError('same revision complete look 20 required')
    from jobs import admitted
    cap=r.collect.a0().owner_cap();jobs=[j for j in ledger['jobs'] if j['index']<look]
    try:
        with admitted(cap['cap_seconds']) as (deadline,monitor):
            calibration=[execute(j,deadline,monitor,digest) for j in jobs if j['index']==0]
            rates={a:max(c['seconds']*150.04/c['stats']['t_end'] for c in calibration if c['job']['arm']==a) for a in POLICIES};todo=[j for j in jobs if not (r.LOCAL/'raw'/(j['tag']+'_COMPLETE.json')).exists()]
            projection=1.2*sum(rates[j['arm']] for j in todo);receipt['projection']=dict(seconds=projection,per_arm_full150_seconds=rates,disk=disk_projection(calibration,todo))
            if projection>deadline-time.monotonic():raise RuntimeError('paired-look projection exceeds current LAB_CAP')
            from dagger import disagreement
            for j in jobs:
                c=execute(j,deadline,monitor,digest);m=mechanism(r.LOCAL/c['raw_file'])
                if sum(m['per_role_deaths'].values())!=c['stats']['own_deaths']:raise RuntimeError('death attribution gap')
                receipt['records'].append(dict(**j,stats=c['stats'],mechanism=m,seconds=c['seconds'],on_policy=disagreement(r.LOCAL/c['raw_file']) if j['arm'] in r.ARMS else None,completion_sha256=r.sha(r.LOCAL/'raw'/(j['tag']+'_COMPLETE.json'))))
                disk_projection(calibration,[k for k in jobs if not (r.LOCAL/'raw'/(k['tag']+'_COMPLETE.json')).exists()])
            import readout
            summary=readout.report(receipt['records'],look);harm=look==50 and any(c['deaths_saved']<=-2 or c['enemy_kills_gained']<=-2 for p in summary['panels'].values() for c in p['comparisons'].values())
            payload=dict(round=round,look=look,ledger_sha256=digest,complete=True,harm_stop=harm,report=summary)
            path=r.HERE/f'LOOK_STAGEB_R{round}_{look}.json'
            if path.exists():
                if r.read(path)!=payload:raise RuntimeError('look drift')
            else:r.write(path,payload,exclusive=True)
            receipt.update(status='DONE',**payload)
    except BaseException as e:receipt.update(status='STOP_RESUMABLE',error=str(e));raise
    finally:
        # Every invocation is its own readout, even interrupted or refused runs.
        receipt['partial_summary']={a:dict(completed=len(v),wins=sum(x['stats']['win'] for x in v),own_deaths=sum(x['stats']['own_deaths'] for x in v),enemy_body_deaths=sum(x['stats']['enemy_kills'] for x in v)) for a in POLICIES if (v:=[x for x in receipt['records'] if x['arm']==a])}
        receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('READOUT_STAGEB_RUN_'+run_id+'.json'),receipt,exclusive=True)

def run(round,look):
    run_id=secrets.token_hex(8);start=time.monotonic();path=r.HERE/('READOUT_STAGEB_RUN_'+run_id+'.json')
    try:return _run(round,look,run_id)
    except BaseException as e:
        if not path.exists():r.write(path,dict(status='REFUSED',round=round,error=str(e),seconds=time.monotonic()-start),exclusive=True)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','run'));p.add_argument('--round',type=int,choices=(1,2),default=1);p.add_argument('--look',type=int,choices=(20,50),default=20);a=p.parse_args();prepare(a.round) if a.command=='prepare' else run(a.round,a.look)
