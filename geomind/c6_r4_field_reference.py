"""Independent vectorized NumPy equation and RK4, with no native RHS calls."""
import copy
import numpy as np
from geomind import c6_r4_field as F

def rhs(owner):
    p=owner.model;ns=len(owner.z)
    def medium(z):
        s=np.abs(z)**2
        diffusion=owner.adjacency@z-owner.adjacency.sum(1)*z
        tones=np.array([-.7,-.5,-.3,-.1,.1,.3,.5,.7])
        drive=p['drive']*np.exp(1j*((.2+tones)*owner.time+owner.psi)).mean(1)
        return (p['mu']+1j*owner.omega+s-s*s)*z+p['diffusion']/4*diffusion+drive
    actual=medium(owner.z);parts=[]
    for c in owner.cohorts:
        n=len(c.theta);dx=c.x[None,:,:]-c.x[:,None,:]
        r2=np.sum(dx*dx,axis=-1);soft=np.sqrt(r2+p['soft_core']**2)
        phase=c.theta[None,:]-c.theta[:,None]
        J=0. if c.mode in ('no_r','no_mode_to_geometry') else p['J']
        K=0. if c.mode=='no_r' else p['K']
        force=(1+J*np.cos(phase))/soft-1/soft**2
        velocity=(dx*force[:,:,None]).sum(1)/(n-1)
        x=c.origin if c.mode=='no_geometry_to_mode' else c.x
        r2phase=np.sum((x[None,:]-x[:,None])**2,axis=-1)
        coupling=K*(np.exp(-r2phase)*np.sin(phase)).sum(1)/(n-1)
        weights=np.exp(-np.sum((owner.q[:,None,:]-x[None,:,:])**2,axis=-1)/(2*p['sigma']**2))
        denom=weights.sum(0)
        if np.any(denom<=1e-12):raise ValueError('invalid incoming normalization')
        saturated=c.carrier/np.sqrt(1+np.abs(c.carrier)**2)
        incoming=(weights*saturated[:,None]).sum(0)/denom
        theta=c.rates+coupling+p['incoming']*np.imag(incoming*np.exp(-1j*c.theta))
        if c.selected:
            m=np.array(c.selected);ow=np.exp(-np.sum((owner.q[:,None,:]-c.x[m][None,:,:])**2,axis=-1)/(2*p['sigma']**2))
            full=p['output']*(ow*np.exp(1j*c.theta[m])).mean(1)
            actual+=full*c.output
        parts.append(np.r_[velocity.ravel(),theta,medium(c.carrier).view('f8')])
    return np.concatenate([actual.view('f8'),*parts])

def advance(owner,duration,dt,sample_dt=None):
    sample=F.exact_steps(dt if sample_dt is None else sample_dt,dt)
    steps=F.exact_steps(duration,dt)
    if sample<1 or steps%sample:raise ValueError('incomplete reference grid')
    y=owner.pack();frames=[y.copy()]
    def stage(value,t):
        o=copy.copy(owner);o.time=t;ns=len(owner.z);offset=2*ns
        o.z=value[:offset].view('c16');o.cohorts=[]
        for original in owner.cohorts:
            c=copy.copy(original);n=len(c.theta)
            c.x=value[offset:offset+2*n].reshape(n,2);offset+=2*n
            c.theta=value[offset:offset+n];offset+=n
            c.carrier=value[offset:offset+2*ns].view('c16');offset+=2*ns;o.cohorts.append(c)
        return o
    for i in range(steps):
        t=owner.time+i*dt
        a=rhs(stage(y,t));b=rhs(stage(y+.5*dt*a,t+.5*dt))
        c=rhs(stage(y+.5*dt*b,t+.5*dt));d=rhs(stage(y+dt*c,t+dt))
        y=y+dt/6*(a+2*b+2*c+d)
        if (i+1)%sample==0:frames.append(y.copy())
    return owner.unpack(y,owner.time+duration),np.array(frames)

def isolated_radius(mu,which):
    return np.sqrt((1+which*np.sqrt(1+4*mu))/2)
