"""Synthetic public observations; no native fight or teacher data generation."""
import copy
from schema import COMMON,OWN

def unit(id,team,role=2,x=400,y=400):
    u=dict(id=id,team=team,role=role,x=x,y=y,vx=0.,vy=0.,hp=100.,maxhp=100.,radius=10.,speed=80.,range=320.,min_range=30.,damage=20.,cooldown=0.,cooldown_max=.4,target=0)
    if team==0:u.update(prep=0.,windup=.1,time_rate=1.,energy=100.,cost=6.,guard_until=0.,busy=False,lob=300.,splash=40.,last_launch=-1.,consumed=False)
    return u

def threat(kind,ordinal=1):
    return dict(kind=kind,ordinal=ordinal,x=430.,y=400.,dx=-1.,dy=0.,born=0.,at=1.,radius=40.,speed=300.,left=320.,**{'from':0.,'until':3.},release_at=.2,landing_at=1.,caster=101,target=1,slow=False)

def snapshot(guns=2):
    us=[unit(i+1,0,x=400,y=400+i*30) for i in range(guns)]+[unit(101,1,x=650),unit(102,1,role=1,x=670,y=440)]
    for u in us:
        if u['team']==0:u['target']=101
    return dict(version='NS1',fight='fixture',tick=1,side=0,self=1,t=1/30,dt=1/30,width=1400.,height=800.,units=us,threats=[threat(k,i+1) for i,k in enumerate(('shell','shot','field','cast'))])

def reflected(s):
    s=copy.deepcopy(s);s['side']=1-s['side']
    for u in s['units']:
        u['team']=1-u['team'];u['x']=s['width']-u['x'];u['vx']=-u['vx']
    for t in s['threats']:t['x']=s['width']-t['x'];t['dx']=-t['dx']
    return s
