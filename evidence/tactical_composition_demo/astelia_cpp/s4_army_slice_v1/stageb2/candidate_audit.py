"""Chosen candidate families, before offsets, spacing drift and body arbitration."""
FAMILIES={0:'direct',1:'lead',2:'cluster',3:'splash',4:'hold',5:'band',6:'safe',7:'approach',8:'flank',9:'retreat',10:'dodge',18:'escort',19:'anchor',20:'anchor_spacing',21:'approach',22:'continuation',23:'band',24:'spacing',25:'ring'}

def add(counts,role,head,family):
    c=counts.setdefault(role,{}).setdefault(head,{})
    c[family]=c.get(family,0)+1

def observe_prediction(counts,row,ids,y):
    roles={u[0]:('melee','ranged','artillery')[int(u[2])] for u in row['units'] if u[1]==0}
    for head in ('aim','move'):
        chosen=y[head+'_logits'].argmax(-1).tolist()
        for i,uid in enumerate(ids):
            if not bool(y[head+'_valid'][i].any()):continue
            typ=int(y[head+'_features'][i,chosen[i],list(FAMILIES)].argmax())
            add(counts,roles[uid],head,FAMILIES[list(FAMILIES)[typ]])

def observe_record(counts,row):
    for pick in row.get('candidatePicks',[]):add(counts,pick['role'],pick['head'],FAMILIES[int(pick['type'])])

def merge(tables):
    result={}
    for table in tables:
        for role,heads in table.items():
            for head,families in heads.items():
                for family,count in families.items():
                    target=result.setdefault(role,{}).setdefault(head,{})
                    target[family]=target.get(family,0)+count
    return result

def report(counts):
    result={}
    for role in ('melee','ranged','artillery'):
        result[role]={}
        for head in ('aim','move'):
            c=counts.get(role,{}).get(head,{});total=sum(c.values())
            result[role][head]=dict(chosen=total,counts={f:c.get(f,0) for f in sorted(set(FAMILIES.values()))},share={f:c.get(f,0)/total if total else None for f in sorted(set(FAMILIES.values()))})
    return result
