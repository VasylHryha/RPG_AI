"""Lossless semantic families, nearest-first pages of at most 64 members.

No label-dependent pruning. Distance is binned to 1e-6 px; native enumeration
index breaks ties. Fixed page slots keep every candidate reachable.
"""
import numpy as np
MEMBERS=64
FAMILY_SLOTS=32
# (native type, maximum pages), derived from the declared 64/64 actor envelope.
LAYOUT={'aim':((0,2),(1,1),(2,1),(3,1)),
        'move':((4,1),(5,1),(6,1),(7,1),(8,2),(9,1),(10,3),
                (18,2),(19,1),(20,1),(21,1),(22,1),(23,6),(24,1),(25,3))}

def partition(features,valid,head):
    table=np.full((len(valid),FAMILY_SLOTS,MEMBERS),-1,dtype=np.int64)
    reverse=np.full(valid.shape+(2,),-1,dtype=np.int64)
    for i in range(len(valid)):
        slot=0;seen=[]
        for typ,pages in LAYOUT[head]:
            indices=np.flatnonzero((valid[i]>=.5)&(features[i,:,typ]>=.5))
            distance=np.floor(features[i,indices,13]*1e8+.5)
            indices=indices[np.lexsort((indices,distance))]
            if len(indices)>pages*MEMBERS:raise ValueError('hierarchical family overflow: '+str(typ))
            for rank,j in enumerate(indices):
                family=slot+rank//MEMBERS;member=rank%MEMBERS
                table[i,family,member]=j;reverse[i,j]=[family,member];seen.append(j)
            slot+=pages
        expected=np.flatnonzero(valid[i]>=.5)
        if sorted(seen)!=expected.tolist():raise ValueError('candidate hierarchy loses or duplicates candidates')
    return table,reverse

def attach(arrays):
    for head in ('aim','move'):
        table,reverse=partition(arrays[head+'_features'],arrays[head+'_valid'],head)
        arrays[head+'_members']=table;arrays[head+'_mapping']=reverse
    return arrays

def reachable(features,index,head):
    # Coverage uses the full exact bank and checks its nearest candidate maps
    # through a real family/member pair, rather than redefining coveredness.
    table,reverse=partition(features[None],np.ones((1,len(features))),head)
    family,member=reverse[0,index]
    return int(family),int(member),bool(table[0,family,member]==index)
