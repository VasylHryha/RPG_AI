"""Evaluator-owned targets and independent teacher; never imported by candidate."""
import numpy as np
from .c2_reference import equilibrium

GENERATOR='c2-independent-linear-tasks.v1'
EDGES=tuple((i,j) for i in range(16) for j in range(i+1,16)
            if j-i==4 or (j-i==1 and i//4==j//4))


def generate_trial(manifest,index):
    inputs=np.random.default_rng(manifest['dataset_seed_start']+index).uniform(0,1,(350,2))
    teacher=np.random.default_rng(manifest['teacher_seed_start']+index).uniform(.5,1.5,24)
    labels={'affine':.2*inputs[:,0]+.5*inputs[:,1],
            'realizable':np.array([equilibrium(teacher,EDGES,16,(0,3),x,10)[10] for x in inputs])}
    order_rng=np.random.default_rng(manifest['order_seed_start']+index)
    orders=np.array([order_rng.permutation(100) for _ in range(manifest['epochs'])])
    return inputs,labels,teacher,orders
