"""Published-state effective recipes and open-loop paired response scoring."""
import copy
import math

import numpy as np
from geomind import c5_coarse
from geomind.c5_experiment import efold
from geomind.c6_levels import linear_summary, response_norm

E1 = c5_coarse.run


def matrix_exp(A):
    """General scaling/squaring exponential, Taylor core; no eigenvectors."""
    A = np.asarray(A, float)
    if A.ndim != 2 or A.shape[0] != A.shape[1] or not np.all(np.isfinite(A)):
        raise ValueError("matrix exponential needs a finite square matrix")
    norm = float(np.linalg.norm(A, 1))
    squarings = max(0, int(math.ceil(math.log2(norm/.5)))) if norm else 0
    small = A / 2.**squarings
    out = term = np.eye(len(A))
    for k in range(1, 100):
        term = term @ small / k
        out = out + term
        if np.linalg.norm(term, 1) <= np.finfo(float).eps * max(np.linalg.norm(out, 1), 1):
            break
    else:
        raise FloatingPointError("matrix exponential core did not converge")
    with np.errstate(over="raise", invalid="raise"):
        for _ in range(squarings):
            out = out @ out
    if not np.all(np.isfinite(out)):
        raise FloatingPointError("non-finite matrix exponential")
    return out


def linear_input(states, paired_initial, grouping):
    """ONE constructor for both recipes; owner membership stays outside the effective model."""
    delta = linear_summary(np.asarray(paired_initial), grouping)
    if delta.shape != (len(states), 3):
        raise ValueError("one linear paired displacement/phase per published part required")
    return np.r_[delta[:, :2].ravel(), delta[:, 2]]


def require_published(states, expected_level=None):
    from geomind.c5_units import INTERFACE_FIELDS
    if not states or len({s["level"] for s in states}) != 1:
        raise ValueError("need published states at one level")
    if any(set(s) != set(INTERFACE_FIELDS) for s in states):
        raise ValueError("effective model accepts published interface fields only")
    if expected_level is not None and any(s['level'] != expected_level for s in states):
        raise ValueError("effective model received states from the wrong level")


def normalized_jacobian(J, lengths, C):
    lengths = np.asarray(lengths, float)
    if np.any(lengths <= 0) or not np.all(np.isfinite(lengths)):
        raise ValueError("positive finite published sizes required")
    D = np.r_[np.repeat(1/lengths, 2), np.ones(len(lengths))]
    return C*D[:, None]*J/D[None, :]


def convergence(Jh, Jhalf, lengths, C):
    a, b = normalized_jacobian(Jh, lengths, C), normalized_jacobian(Jhalf, lengths, C)
    difference, tolerance = float(np.linalg.norm(a-b)), 1e-3*max(float(np.linalg.norm(b)), 1.)
    return {"converged": bool(np.isfinite(difference) and difference <= tolerance),
            "difference": difference, "tolerance": tolerance}


def central_jacobian(function, state, steps):
    columns = []
    for i, h in enumerate(steps):
        delta = np.zeros_like(state)
        delta[i] = h
        columns.append((function(state+delta)-function(state-delta))/(2*h))
    return np.stack(columns, axis=1)


def jacobian(states, params, C):
    require_published(states)
    cs = c5_coarse.CoarseState(states, params.k)
    held = c5_coarse.links(cs, cs.X, params)
    M = len(states)
    lengths = np.array([s["characteristic_size"] for s in states])
    state = np.r_[cs.X.ravel(), cs.theta]
    steps = 1e-4*np.r_[np.repeat(lengths, 2), np.ones(M)]
    def rhs(z):
        dx, dth = c5_coarse.rhs(cs, z[:2*M].reshape(M, 2), z[2*M:], held, params)
        return np.r_[dx.ravel(), dth]
    Jh = central_jacobian(rhs, state, steps)
    Jhalf = central_jacobian(rhs, state, steps/2)
    check = convergence(Jh, Jhalf, lengths, C)
    return Jhalf, check


def E2(states, params, C, delta, times):
    J, check = jacobian(states, params, C)
    responses = np.array([matrix_exp(J*t) @ delta for t in times]) if check["converged"] else np.zeros((len(times), len(delta)))
    return {"response": unpack(responses, len(states)), "abstained": not check["converged"], "convergence": check}


def unpack(vectors, M):
    return np.concatenate([vectors[..., :2*M].reshape(*vectors.shape[:-1], M, 2),
                           vectors[..., 2*M:, None]], axis=-1)


def predict(states, params, C, recipe, delta, times, dt=.02, expected_level=None):
    """No reopen callback and no full-state argument exists on the prediction path."""
    from geomind.c6_experiment import steps_exact
    require_published(states, expected_level)
    if recipe == "E2":
        return E2(states, params, C, delta, times)
    if recipe != "E1":
        raise ValueError("unknown recipe")
    changes = unpack(np.asarray(delta)[None], len(states))[0]
    shifted = copy.deepcopy(states)
    for s, d in zip(shifted, changes):
        s["effective_position"] = (np.asarray(s["effective_position"])+d[:2]).tolist()
        s["optional_phase"] += float(d[2])
    steps, every = steps_exact(times[-1], dt), steps_exact(times[1]-times[0], dt)
    control, excited = [E1(s, params, dt, steps, every) for s in (states, shifted)]
    response = np.concatenate([excited["X"]-control["X"],
                               (excited["theta"]-control["theta"])[..., None]], axis=-1)
    return {"response": response, "abstained": False, "flagged": excited["flagged"]+control["flagged"],
            "work": excited["work"]+control["work"]}


def tau_estimate(deviation, C):
    deviation = np.asarray(deviation, float)
    if len(deviation) != 101 or not np.all(np.isfinite(deviation)):
        raise ValueError("tau requires 101 finite samples at .1 C over 10 C")
    tau = efold(deviation, .1*C)
    censored = not np.isfinite(tau)
    return {"tau": None if censored else tau, "censored": censored, "limit": 10*C,
            "sample_dt": .1*C, "deviation": deviation.tolist()}


def error_parts(truth, prediction, lengths):
    error = truth-prediction
    from geomind.c4_model import wrap
    phase = float(np.sqrt(np.mean(wrap(error[..., 2])**2)))
    position = float(np.sqrt(np.mean(np.sum(error[..., :2]**2, axis=-1)/np.asarray(lengths)**2)))
    return {"phase": phase, "position": position, "total": phase+position}


def relaxation_response(times, amount, M, count, kind, u):
    response = np.zeros((len(times), count, 3))
    share = (1-np.exp(-np.asarray(times)*u))/M
    if kind == "pulse":
        response[..., 2] = share[:, None]*amount
    elif kind == "push":
        response[..., :2] = share[:, None, None]*np.asarray(amount)
    else:
        raise ValueError("excitation must be pulse or push")
    return response


def censored_bounds(truth, times, amount, M, lengths, kind, T):
    """Certified continuous tau>T bounds: 65 inverse-tau points and the Lipschitz covering margin."""
    if T <= 0 or not np.isfinite(T):
        raise ValueError("finite positive censoring horizon required")
    grid = np.arange(65)/(64*T)
    errors = [error_parts(truth, relaxation_response(times, amount, M, truth.shape[1], kind, u), lengths)["total"] for u in grid]
    amplitude = abs(float(amount))/M if kind == "pulse" else np.linalg.norm(amount)/M*np.max(1/np.asarray(lengths))
    K = float(amplitude*np.sqrt(np.mean(np.asarray(times)**2)))
    h = 1/(128*T)
    return {"lower": max(0., min(errors)-K*h), "upper": max(errors)+K*h,
            "grid_u": grid.tolist(), "grid_errors": errors, "K": K, "h": h, "margin": K*h}


def score_excitation(truth, prediction, times, excited, lengths, kind, amount, tau):
    others = [i for i in range(truth.shape[1]) if i != excited]
    f, p, L = truth[:, others], prediction[:, others], np.asarray(lengths)[others]
    model = error_parts(f, p, L)
    zero = error_parts(f, np.zeros_like(f), L)
    rigid = np.zeros_like(f)
    # A rigid baseline is the complete initial amount at EVERY sample, including t0.
    if kind == "pulse":
        rigid[..., 2] = amount
    else:
        rigid[..., :2] = amount
    rigid_error = error_parts(f, rigid, L)
    if tau["censored"]:
        bounds = censored_bounds(f, times, amount, truth.shape[1], L, kind, tau["limit"])
        relax = {"lower": bounds["lower"], "upper": bounds["upper"], "certificate": bounds}
    else:
        if tau["tau"] <= 0:
            raise ValueError("nonpositive baseline tau")
        r = relaxation_response(times, amount, truth.shape[1], len(others), kind, 1/tau["tau"])
        er = error_parts(f, r, L)
        relax = {"lower": er["total"], "upper": er["total"], "errors": er}
    gains = {"no_transfer": {"lo": zero["total"]-model["total"], "hi": zero["total"]-model["total"]},
             "rigid_transfer": {"lo": rigid_error["total"]-model["total"], "hi": rigid_error["total"]-model["total"]},
             "relaxation": {"lo": relax["lower"]-model["total"], "hi": relax["upper"]-model["total"]}}
    eligible = zero["total"] >= .01
    return {"model": model, "no_transfer": zero, "rigid_transfer": rigid_error, "relaxation": relax,
            "gains": gains, "r": model["total"]/zero["total"] if eligible else None,
            "response_status": "ELIGIBLE" if eligible else "BELOW_RESPONSE_FLOOR", "tau": tau}


def separation_bounds(numerator, denominators):
    lower_den = np.mean([r["limit"] if r["censored"] else r["tau"] for r in denominators])
    lower_num = numerator["limit"] if numerator["censored"] else numerator["tau"]
    return {"lo": 0. if any(r["censored"] for r in denominators) else lower_num/lower_den,
            "hi": float("inf") if numerator["censored"] else numerator["tau"]/lower_den}
