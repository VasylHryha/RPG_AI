"""Compile/check identical public-history state fixtures. Zero simulation steps."""
import copy
import gzip
import json
from pathlib import Path
import subprocess
import time
from a0_common import BINARY, CPP, HERE, LOCAL, code_hashes, load, read, sha, write


def synthetic():
    # Unit wire: id team role x y hp radius range minrange target vx vy maxhp
    # speed dmg cdMax cd crossDealt crossTaken guard prep windup energy cost busy.
    units=[]
    for side in (0,1):
        for k,role in enumerate((0,1,2,2)):
            uid=side*4+k+1;x=(210 if side==0 else 710)+k*5;y=350+k*30
            hp=(258,92,181)[role];radius=(16,9,10)[role];reach=(36,259,600)[role]
            units.append([uid,side,role,x,y,hp,radius,reach,100 if role==2 else 0,0,0,0,hp,60,40,1,0,0,0,0,0,.2,100,0,False])
    frames=[]
    for tick in range(30):
        u=copy.deepcopy(units);ready=tick%3
        for i,x in enumerate(u):
            x[3]+=tick*.5*(1 if x[1] else -1);x[10]=15*(1 if x[1] else -1)
            x[17]=tick*(i+1);x[18]=tick*(8-i)
            if x[1]==0 and x[2]==2:x[20]=.2 if (i==2 and ready>=1 or i==3 and ready==2) else 0
            if tick==15 and x[0]==1:x[19]=1
            if tick==16 and x[0]==2:x[24]=True
        frames.append(dict(reset=tick==0,params={},t=tick/30,dt=1/30,units=u,shells=[]))
    # Include shell-reaction windows and live target removal, independent histories.
    for tick in range(30,36):
        u=copy.deepcopy(frames[-1]['units'])
        u=[x for x in u if x[0]!=8]
        for x in u:
            x[17]+=x[0]
            x[18]+=9-x[0]
            x[19]=0
            x[24]=False
        frames.append(dict(reset=False,params={},t=tick/30,dt=1/30,units=u,
                           shells=[[220,410,tick/30+.2,40]]))
    return frames


def recorded():
    origin=HERE.parent;ledger=read(origin/'_local/A0_LEDGER.json');look=read(origin/'A0_LOOK_50.json')
    assert look['ledger_sha256']==sha(origin/'_local/A0_LEDGER.json')
    fixtures=[];sources={}
    jobs=[j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']==0]
    for job in jobs:
        receipt_path=origin/'_local/raw'/(job['tag']+'_COMPLETE.json');receipt=read(receipt_path)
        assert receipt['job']==job and sha(receipt_path)==look['completion_receipts'][job['tag']]
        raw=origin/'_local/raw'/receipt['raw_file'];assert sha(raw)==receipt['raw_sha256']
        request_path=origin/'_local/requests'/(job['tag']+'.json');assert sha(request_path)==job['request_sha256']
        request=read(request_path);params=request['options']['ai'][0]['params']
        outgoing={};incoming={};previous={};initial={};shells=[];first=True
        with gzip.open(raw,'rt') as f:
            for line in f:
                frame=json.loads(line)
                if not frame.get('observerV1'):continue
                if frame['t']>30:break
                if first:initial={u[0]:u for u in frame['units']}
                for d in frame['damage']:
                    if d['sourceTeam']!=d['targetTeam']:
                        outgoing[d['source']]=outgoing.get(d['source'],0)+d['dealt']
                        incoming[d['target']]=incoming.get(d['target'],0)+d['dealt']
                shells=[sh for sh in shells if sh[2]>frame['t']]
                shells.extend([[s[3],s[4],s[6],s[7]] for s in frame['launches'] if s[2]==1 and not s[9]])
                units=[]
                for u in frame['units']:
                    old=previous.get(u[0],u);role=u[2]
                    vx=(u[3]-old[3])*30;vy=(u[4]-old[4])*30
                    hp=initial[u[0]][5]
                    units.append([*u[:9],u[13] or 0,vx,vy,hp,(60,80,55)[role],(40,10.4,40)[role],1,0,
                        outgoing.get(u[0],0),incoming.get(u[0],0),0,u[12],.2,100,0,False])
                fixtures.append(dict(reset=first,params=params,t=frame['t'],dt=1/30,units=units,shells=shells))
                previous={u[0]:u for u in frame['units']};first=False
        sources[job['tag']]=dict(raw_sha256=receipt['raw_sha256'],receipt_sha256=sha(receipt_path))
    return fixtures,sources


def check():
    start=time.monotonic();admission=load('a0r2_equivalence_admission',CPP/'build_admission.py');admission.admit(BINARY)
    record=read(BINARY.with_suffix('.build.json'));out=BINARY.parent
    flags=record['commands'][0][:record['commands'][0].index('-c')]
    subprocess.run([*flags,'-c',str(HERE/'a0_equivalence.cpp'),'-o',str(out/'a0_equivalence.o')],check=True,timeout=60)
    objects=[p for p in record['link'][1:record['link'].index('-o')] if not p.endswith('/lean_host.o')]
    binary=out/'a0_equivalence'
    subprocess.run([record['link'][0],*objects,str(out/'a0_equivalence.o'),'-o',str(binary)],check=True,timeout=60)
    fixture=LOCAL/'equivalence_states.jsonl';frames=synth=synthetic();raw,sources=recorded();frames=frames+raw
    with fixture.open('w') as f:
        for row in frames:f.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
    result=subprocess.run([str(binary),str(fixture)],capture_output=True,text=True,check=True,timeout=90)
    proof=json.loads(result.stdout)
    assert proof['status']=='PASS' and proof['total_mismatches']==0 and proof['combat_steps']==0
    coverage=proof['coverage']
    for key in ('healthy_unit_rows','react_rows','guard_rows','body_rows','target_removal_frames','single_applied','multi_applied'):
        assert coverage.get(key,0)>0, 'missing exercised equivalence path: '+key
    for role in ('melee','ranged','artillery'):assert proof['by_role_and_decision'][role]['executed_command']['rows']>0
    for kind in ('aim_no_ready','aim_single_ready','aim_multi_ready'):assert proof['by_role_and_decision']['artillery'][kind]['rows']>0
    proof.update(binary_sha256=sha(BINARY),code_hashes=code_hashes(),fixture_sha256=sha(fixture),sources=sources,
        synthetic_frames=len(synth),recorded_position_frames=len(raw),seconds=time.monotonic()-start,
        declared_differences=[],scope='same public-history fixtures; separate controllers, native bridge and aim commands; no combat steps',
        limits='Recorded post-step positions, targets, prep and cross-damage counters are exact. Velocities are displacement estimates; speed/damage/cooldown/own resource fields use declared fixture values. This is not reconstruction of T hidden state or execution on the original raw fights.')
    write(HERE/'A0_EQUIVALENCE.json',proof);return proof

if __name__=='__main__':print(json.dumps(check(),indent=2))
