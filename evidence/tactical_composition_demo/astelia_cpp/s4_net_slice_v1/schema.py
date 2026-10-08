"""NS1 public wire boundary and deterministic 1008-column encoder; no Torch needed."""
import math

VERSION = 'NS1'
WIDTH = 1008
COMMON = {'id','team','role','x','y','vx','vy','hp','maxhp','radius','speed','range','min_range','damage','cooldown','cooldown_max','target'}
OWN = {'prep','windup','time_rate','energy','cost','guard_until','busy','lob','splash','last_launch','consumed'}
ROOT = {'version','fight','tick','side','self','t','dt','width','height','units','threats'}
THREAT = {'kind','ordinal','x','y','dx','dy','born','at','radius','speed','left','from','until','release_at','landing_at','caster','target','slow','damage'}
KINDS = ('shell','shot','field','cast','own_shell')

def check(s):
    if set(s) != ROOT or s['version'] != VERSION: raise ValueError('schema root/version')
    integer=lambda v,lo=0,hi=4294967295:isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and lo<=v<=hi and v==math.floor(v)
    if s['side'] not in (0,1) or not integer(s['tick'],1,9007199254740991) or not integer(s['self'],1) or not isinstance(s['fight'],str) or s['t']<0: raise ValueError('side/tick/identity')
    ids = set()
    for u in s['units']:
        expected = COMMON | (OWN if u['team']==s['side'] else set())
        if set(u) != expected: raise ValueError('unit allowlist')
        if not integer(u['id'],1) or not integer(u['target']) or u['id'] in ids or u['id']<=0 or u['team'] not in (0,1) or u['role'] not in (0,1,2): raise ValueError('unit identity')
        ids.add(u['id'])
        if u['maxhp']<=0 or u['radius']<0 or u['speed']<0 or not 0<=u['min_range']<=u['range']: raise ValueError('unit dimensions')
        if u['team']==s['side'] and (u['time_rate']<=0 or u['windup']<=0): raise ValueError('own cast dimensions')
    if s['self'] not in ids: raise ValueError('self absent')
    if s['width']<=0 or s['height']<=0 or not 0<s['dt']<=.2: raise ValueError('arena/dt')
    for t in s['threats']:
        if not integer(t['caster']) or not integer(t['target']) or not integer(t['ordinal'],1) or set(t)!=THREAT or t['kind'] not in KINDS: raise ValueError('threat allowlist')
    def finite(v):
        if isinstance(v,dict): return all(finite(x) for x in v.values())
        if isinstance(v,list): return all(finite(x) for x in v)
        return not isinstance(v,(int,float)) or math.isfinite(v)
    if not finite(s): raise ValueError('nonfinite observation')
    me=next(u for u in s['units'] if u['id']==s['self'])
    if me['team']!=s['side'] or me['role']!=2: raise ValueError('self must be own gun')
    return me

def mirror_vector(side,x,y): return (-x if side else x,y)
def inverse_point(s,x,y):
    me=check(s);dx,dy=mirror_vector(s['side'],x,y);return [me['x']+dx,me['y']+dy]
def slots(s):
    me=check(s)
    key=lambda u: ((u['x']-me['x'])**2+(u['y']-me['y'])**2,u['id'])
    friends=sorted((u for u in s['units'] if u['team']==s['side'] and u['id']!=s['self'] and u['hp']>0),key=key)
    enemies=sorted((u for u in s['units'] if u['team']!=s['side'] and u['hp']>0),key=key)
    return friends[:12],enemies[:12],len(friends)>12,len(enemies)>12

def encode(s):
    me=check(s);friends,enemies,fo,eo=slots(s);sgn=-1 if s['side'] else 1
    eid=[u['id'] for u in enemies]
    def pointer(t): return 0 if not t else (eid.index(t)+1)/12 if t in eid else -1
    def row(u):
        if u is None:return [0.]*32
        a=[1.,*map(float,(u['role']==i for i in range(3))),sgn*(u['x']-me['x'])/100,(u['y']-me['y'])/100,sgn*u['vx']/200,u['vy']/200,u['hp']/u['maxhp'],u['radius']/100,u['speed']/200,u['range']/1000,u['min_range']/1000,u['damage']/200,u['cooldown']/10,u['cooldown_max']/10,pointer(u['target']),float(u['target']==me['id']),float(u['team']==s['side'])]
        if u['team']==s['side']:
            target=next((e for e in s['units'] if e['id']==u['target'] and e['hp']>0 and e['team']!=u['team']),None)
            reach=target is not None and u['min_range']<=math.hypot(u['x']-target['x'],u['y']-target['y'])<=u['range']
            body=u['guard_until']<=s['t'] and not u['busy']
            a += [u['prep']/10,u['windup']/10,u['time_rate']/4,u['energy']/1000,u['cost']/1000,max(0,u['guard_until']-s['t'])/10,float(u['busy']),u['lob']/1000,u['splash']/100,float(body and reach and u['prep']<=0 and u['cooldown']<=0 and u['energy']>=u['cost']),float(body and reach and u['prep']>0 and u['prep']+s['dt']*u['time_rate']>=u['windup']-1e-9),-1 if u['last_launch']<0 else (s['t']-u['last_launch'])/10,float(u['consumed'])]
        else:a += [0.]*13
        assert len(a)==32
        return a
    features=row(me)
    for group in (friends,enemies):
        for i in range(12):features+=row(group[i] if i<len(group) else None)
    def urgency(t):
        when={'shell':t['at'],'own_shell':t['at'],'cast':t['landing_at'],'field':max(s['t'],t['from']),'shot':s['t']+max(0,((me['x']-t['x'])*t['dx']+(me['y']-t['y'])*t['dy']))/max(t['speed'],1e-6)}[t['kind']]
        inside=math.hypot(t['x']-me['x'],t['y']-me['y'])<=t['radius']+me['radius']+4
        return (not inside,max(0,when-s['t']),KINDS.index(t['kind']),t['ordinal'])
    threats=sorted(s['threats'],key=urgency)
    for i in range(8):
        if i>=len(threats):features += [0.]*24;continue
        t=threats[i]
        features += [1.,*map(float,(t['kind']==k for k in KINDS[:4])),sgn*(t['x']-me['x'])/100,(t['y']-me['y'])/100,sgn*t['dx'],t['dy'],(s['t']-t['born'])/10,(t['at']-s['t'])/10,t['radius']/100,t['speed']/1000,t['left']/1000,(t['from']-s['t'])/10,(t['until']-s['t'])/10,(t['release_at']-s['t'])/10,(t['landing_at']-s['t'])/10,pointer(t['caster']),float(t['target']==me['id']),float(not urgency(t)[0]),float(t['slow']),float(t['kind']=='own_shell'),t['damage']/200]
    counts=[sum(u['hp']>0 and u['team']==team and u['role']==role for u in s['units'])/64 for team in (s['side'],1-s['side']) for role in range(3)]
    cent=[]
    for team in (s['side'],1-s['side']):
        us=[u for u in s['units'] if u['team']==team and u['hp']>0]
        cent += [sgn*(sum(u['x'] for u in us)/len(us)-me['x'])/100 if us else 0,(sum(u['y'] for u in us)/len(us)-me['y'])/100 if us else 0]
    borders=[me['x'],s['width']-me['x'],me['y'],s['height']-me['y']]
    if s['side']:borders[:2]=borders[1::-1]
    features += [s['t']/150,s['dt']*30,*[x/1000 for x in borders],*counts,*cent]
    assert len(features)==WIDTH
    return features,{'enemy_ids':eid,'friend_overflow':fo,'enemy_overflow':eo,'threat_overflow':max(0,len(threats)-8),'own_shell_overflow':sum(t['kind']=='own_shell' for t in threats[8:]),'enemy_threat_overflow':sum(t['kind']!='own_shell' for t in threats[8:])}

def candidates(s,target):
    me=check(s);step=me['speed'];aimradius=min(200,me['splash'])
    moves=[[me['x'],me['y']]];aims=[[target['x'],target['y']]] if target else []
    for f in (.6,1.):
        for j in range(16):
            dx,dy=mirror_vector(s['side'],math.cos(j*math.pi/8),math.sin(j*math.pi/8))
            moves.append([min(s['width']-me['radius'],max(me['radius'],me['x']+step*f*dx)),min(s['height']-me['radius'],max(me['radius'],me['y']+step*f*dy))])
    if target:
        for f in (.5,1.):
            for j in range(16):
                dx,dy=mirror_vector(s['side'],math.cos(j*math.pi/8),math.sin(j*math.pi/8));aims.append([target['x']+aimradius*f*dx,target['y']+aimradius*f*dy])
    return moves,aims

def decode(s,logits):
    if len(logits)!=81 or not all(math.isfinite(v) for v in logits):raise ValueError('numeric policy failure')
    me=check(s);_,es,_,_=slots(s)
    arg=lambda indices:max(indices,key=lambda i:(logits[i],-i))
    ti=arg([33,*range(34,34+len(es))])-33;target=es[ti-1] if ti else None
    moves,aims=candidates(s,target)
    valid=[i for i,a in enumerate(aims) if 0<=a[0]<=s['width'] and 0<=a[1]<=s['height'] and me['min_range']<=math.hypot(a[0]-me['x'],a[1]-me['y'])<=me['range']]
    mi=arg(range(33));ai=max(valid,key=lambda i:(logits[48+i],-i)) if valid else None
    start_opportunity,release_opportunity=opportunities(s,target,aims[ai] if ai is not None else None)
    return {'multiplier':float(mi!=0),'stop':0.,'goal':moves[mi],'target':target['id'] if target else 0,'start':logits[46]>=0 and start_opportunity,'release':logits[47]>=0 and release_opportunity,'start_opportunity':start_opportunity,'release_opportunity':release_opportunity,'aim':aims[ai] if ai is not None else None,'move_index':mi,'aim_index':ai,'target_index':ti,'volley':0}


def opportunities(s,target,aim):
    """Decision-tick gates; release includes this tick's native prep increment."""
    me=check(s)
    body=me['guard_until']<=s['t'] and not me['busy']
    reach=target is not None and me['min_range']<=math.hypot(target['x']-me['x'],target['y']-me['y'])<=me['range']
    legal=body and reach and aim is not None and 0<=aim[0]<=s['width'] and 0<=aim[1]<=s['height'] and me['min_range']<=math.hypot(aim[0]-me['x'],aim[1]-me['y'])<=me['range']
    return (bool(legal and me['prep']<=0 and me['cooldown']<=0 and me['energy']>=me['cost']),bool(legal and me['prep']>0 and me['prep']+s['dt']*me['time_rate']>=me['windup']-1e-9))
