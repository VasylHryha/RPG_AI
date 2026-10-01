"""Independent dense Kirchhoff equilibrium and implicit-differentiation controls.

This file neither imports the candidate nor calls its native kernel.
"""
import numpy as np


def system(g,edges,n,inputs,x,output,leak=.01,beta=0.,y=0.):
    matrix=leak*np.eye(n)
    for conductance,(i,j) in zip(g,edges):
        matrix[i,i]+=conductance; matrix[j,j]+=conductance
        matrix[i,j]-=conductance; matrix[j,i]-=conductance
    matrix[output,output]+=beta
    free=[i for i in range(n) if i not in inputs]
    rhs=-matrix[np.ix_(free,inputs)]@np.asarray(x)
    if output in free: rhs[free.index(output)]+=beta*y
    return matrix[np.ix_(free,free)],rhs,free


def equilibrium(g,edges,n,inputs,x,output,leak=.01,beta=0.,y=0.):
    matrix,rhs,free=system(g,edges,n,inputs,x,output,leak,beta,y)
    u=np.zeros(n); u[list(inputs)]=x; u[free]=np.linalg.solve(matrix,rhs)
    return u


def gradient(g,edges,n,inputs,x,output,y,leak=.01):
    matrix,rhs,free=system(g,edges,n,inputs,x,output,leak)
    u=np.zeros(n); u[list(inputs)]=x; u[free]=np.linalg.solve(matrix,rhs)
    rhs_adjoint=np.zeros(len(free)); rhs_adjoint[free.index(output)]=u[output]-y
    adjoint=np.zeros(n); adjoint[free]=np.linalg.solve(matrix,rhs_adjoint)
    return np.array([-(u[i]-u[j])*(adjoint[i]-adjoint[j]) for i,j in edges])


def finite_difference(g,edges,n,inputs,x,output,y,leak=.01,h=1e-5):
    result=[]
    for e in range(len(edges)):
        plus=np.array(g); minus=np.array(g); plus[e]+=h; minus[e]-=h
        up=equilibrium(plus,edges,n,inputs,x,output,leak)[output]
        um=equilibrium(minus,edges,n,inputs,x,output,leak)[output]
        result.append((.5*(up-y)**2-.5*(um-y)**2)/(2*h))
    return np.array(result)


def direct_local_update(g,edges,n,inputs,x,output,y,eta=.01,beta=.05,leak=.01):
    # Both independent solves explicitly receive the same old array.
    old=np.array(g,copy=True)
    f=equilibrium(old,edges,n,inputs,x,output,leak)
    nudged=equilibrium(old,edges,n,inputs,x,output,leak,beta,y)
    return np.clip(old+eta/(2*beta)*np.array([(f[i]-f[j])**2-(nudged[i]-nudged[j])**2 for i,j in edges]),.05,5)
