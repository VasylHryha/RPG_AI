"""Evaluator-only impact-time geometry; never policy input or action selection."""
import math
ROLES=('melee','ranged','artillery')
HAZARDS=('shell','shot','cast','field','melee','body','burn','unattributed')

class DodgeMetrics:
    def __init__(self):
        self.damage={role:{kind:0. for kind in HAZARDS} for role in ROLES}
        self.escape={role:{kind:dict(rows=0,evaluated=0,escaped=0,dead=0,censored=0) for kind in ('shell','shot','cast','field','no_public_hazard')} for role in ROLES}
        self.pending=[];self.missing_damage_tags=0

    def observe(self,row):
        if row.get('observerV1'):
            for d in row['damage']:
                if d['targetTeam']==0:
                    kind=d.get('hazardType','unattributed');self.missing_damage_tags+=kind=='unattributed'
                    self.damage[d['targetRole']][kind]+=d['dealt']
            positions={int(u[0]):u[3:5] for u in row['units'] if u[1]==0 and len(u)>=7}
            keep=[]
            for event in self.pending:
                if row['t']+1e-9<event['at']:keep.append(event);continue
                c=self.escape[event['role']][event['kind']];c['evaluated']+=1
                if event['id'] not in positions:c['dead']+=1
                else:c['escaped']+=all(math.dist(positions[event['id']],p)>radius for p,radius in event['disks'])
            self.pending=keep
        elif row.get('stageA'):
            byid={u[0]:u for u in row['units']};W,H=row['width'],row['height']
            # O itself supplies labels for the O comparator; student arms use O shadow.
            for lab in row.get('shadowLabels',row['labels']):
                if not lab['active']:continue
                u=byid[lab['id']];pos=u[3:5];radius=u[9];hazards=[]
                for s in row['shells']:
                    p=(s[2]*W,s[3]*H);r=s[5]*100+radius+4
                    if s[7]==1 and not s[6] and s[4]>0 and math.dist(pos,p)<=r:hazards.append(('shell',s[4],p,r))
                for s in row['casts']:
                    p=(s[2]*W,s[3]*H);r=s[6]*100+radius+4
                    if s[1]*256!=u[0] and math.dist(pos,p)<=r:hazards.append(('cast',max(0.,s[5]),p,r))
                for s in row['shots']:
                    p=(s[0]*W,s[1]*H);delta=(pos[0]-p[0],pos[1]-p[1]);along=delta[0]*s[2]+delta[1]*s[3];cross=delta[0]*s[3]-delta[1]*s[2];speed=s[5]*100
                    if s[4]>=.15 and 0<along<=min(s[6]*100,speed*.4) and abs(cross)<=radius+3:
                        hazards.append(('shot',along/speed,(p[0]+s[2]*along,p[1]+s[3]*along),radius+3))
                for s in row['fields']:
                    p=(s[0]*W,s[1]*H);r=s[2]*100+radius
                    if s[3]<=0 and s[4]>=.5 and math.dist(pos,p)<=r:hazards.append(('field',.5,p,r))
                for kind in ('shell','shot','cast','field'):
                    active=[h for h in hazards if h[0]==kind]
                    if not active:continue
                    first=min(h[1] for h in active);disks=[(h[2],h[3]) for h in active if abs(h[1]-first)<=1e-9]
                    self.escape[lab['role']][kind]['rows']+=1
                    self.pending.append(dict(id=u[0],role=lab['role'],kind=kind,at=row['t']+first,disks=disks))
                if not hazards:self.escape[lab['role']]['no_public_hazard']['rows']+=1

    def finish(self):
        for e in self.pending:self.escape[e['role']][e['kind']]['censored']+=1
        return dict(damage_taken_by_role_hazard=self.damage,damage_rows_without_hazard_tag=self.missing_damage_tags,dodge_escape=with_rates(self.escape),dodge_metric_definition='O-active predecision rows; actual post-step body position at first physical tick >= each public predicted impact time, not raw commanded goal. One exposure per role/unit/row/hazard kind, simultaneous disks all excluded; dead is failure, fight-ending pending is censored. Cast disks/times are public predictions and fields use 0.5-second escape horizon. Casts produce shells; slow fields apply no direct HP damage in this engine, so their direct damage totals are zero. Body/burn/unattributed remain separate.')

def with_rates(escape):
    return {role:{kind:dict(c,escape_rate=c['escaped']/c['evaluated'] if c['evaluated'] else None) for kind,c in kinds.items()} for role,kinds in escape.items()}

def aggregate(mechanisms):
    damage={role:{kind:sum(m['damage_taken_by_role_hazard'][role][kind] for m in mechanisms)/len(mechanisms) for kind in HAZARDS} for role in ROLES}
    escape={role:{kind:{key:sum(m['dodge_escape'][role][kind][key] for m in mechanisms) for key in ('rows','evaluated','escaped','dead','censored')} for kind in mechanisms[0]['dodge_escape'][role]} for role in ROLES}
    return dict(damage_taken_per_fight_by_role_hazard=damage,dodge_escape=with_rates(escape))
