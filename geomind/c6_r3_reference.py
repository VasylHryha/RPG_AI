"""Slow, independent vector-matrix reference of the declared directed law.

No calls to the compiled RHS; used only for bounded deterministic qualification.
"""
import numpy as np
from geomind.c6_r3_background import exact_steps


def adjacency(x, y, self=False):
    distance = np.linalg.norm(x[:, None]-y[None], axis=-1)
    if self:
        np.fill_diagonal(distance, np.inf)
    ids = np.argsort(distance, axis=1, kind='stable')[:, :min(8, len(y)-(1 if self else 0))]
    weights = np.zeros(distance.shape)
    for i, js in enumerate(ids):
        weights[i, js[distance[i, js] < 3.]] = 1.
    return weights


def term(x, th, y, phi, weights, J=.8, K=1., weighted=True, gates=None):
    delta = y[None]-x[:, None]; distance = np.linalg.norm(delta, axis=-1)
    r = np.maximum(distance, 1e-6); phases = phi[None]-th[:, None]
    normalization = np.maximum(weights.sum(1), 1.)
    numerator = weights if gates is None else weights*gates[None]
    force = (1.+J*np.cos(phases)-1./r)/r*numerator
    dx = (delta*force[..., None]).sum(1)/normalization[:, None]
    dth = (K*np.sin(phases)*(np.exp(-distance**2) if weighted else 1.)*numerator).sum(1)/normalization
    return dx, dth


def simulate(bath_x, bath_th, bath_omega, duration, source=None, reference=None, prior=None,
             mode='intact', outbound=1., dt=.02, sample_dt=.02, phase_origin=None):
    nb = len(bath_x); ns = 0 if source is None else len(source[0])
    x = np.vstack([bath_x, np.empty((0, 2)) if source is None else source[0]]).astype(float)
    th = np.r_[bath_th, [] if source is None else source[1]].astype(float)
    omega = np.r_[bath_omega, [] if source is None else source[2]].astype(float)
    original = x if phase_origin is None else phase_origin
    if mode == 'no_geometry_to_mode':
        fin = adjacency(original[nb:], original[nb:], True)
        fex = adjacency(original[nb:], reference.sample(0.)[0])
    xs, ts = [x.copy()], [th.copy()]
    steps = exact_steps(duration, dt); every = exact_steps(sample_dt, dt)
    for step in range(steps):
        t = step*dt
        px, pt = (np.empty((0, 2)), np.empty(0)) if prior is None else prior.sample(t)
        own_b = adjacency(x[:nb], x[:nb], True)
        out_b = adjacency(x[:nb], np.vstack([x[nb:], px]))
        if ns:
            own_s = adjacency(x[nb:], x[nb:], True)
            rx, rt = reference.sample(t)
            in_s = adjacency(x[nb:], rx)
        def rhs(xx, tt, time):
            py, pp = (np.empty((0, 2)), np.empty(0)) if prior is None else prior.sample(time)
            dx, dth = term(xx[:nb], tt[:nb], xx[:nb], tt[:nb], own_b)
            vx, vt = term(xx[:nb], tt[:nb], np.vstack([xx[nb:], py]), np.r_[tt[nb:], pp],
                          out_b, gates=np.r_[np.full(ns, outbound), np.ones(len(py))])
            dx += vx; dth += vt+bath_omega
            if ns:
                ry, rp = reference.sample(time)
                J = 0. if mode in ('no_r', 'no_mode_to_geometry') else .8
                K = 0. if mode == 'no_r' else 1.
                sx, st = term(xx[nb:], tt[nb:], xx[nb:], tt[nb:], own_s, J=J, K=K)
                ex, et = term(xx[nb:], tt[nb:], ry, rp, in_s, J=J, K=K)
                sx += ex; st += et
                if mode == 'no_geometry_to_mode':
                    st = term(xx[nb:], tt[nb:], xx[nb:], tt[nb:], fin, weighted=False)[1]
                    st += term(xx[nb:], tt[nb:], ry, rp, fex, weighted=False)[1]
                dx = np.vstack([dx, sx]); dth = np.r_[dth, st+omega[nb:]]
            return dx, dth
        a, b = rhs(x, th, t)
        c, d = rhs(x+dt*a/2, th+dt*b/2, t+dt/2)
        e, f = rhs(x+dt*c/2, th+dt*d/2, t+dt/2)
        g, h = rhs(x+dt*e, th+dt*f, t+dt)
        x += dt/6*(a+2*c+2*e+g); th += dt/6*(b+2*d+2*f+h)
        if (step+1) % every == 0:
            xs.append(x.copy()); ts.append(th.copy())
    return np.array(xs), np.array(ts)
