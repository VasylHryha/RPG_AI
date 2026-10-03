"""Models for experiment 0d Part A (PROPOSAL_0D.md revision 2): flat F1/F2, composed C, structured own-selection S1. Exploratory; NOT a milestone.

Everything is plain numpy with hand-written backpropagation. `tactics.py` (frozen) supplies the sandbox, the teacher and the recorded flat recipe F0 (`tactics.MLP`).
All models act on `Arrays` (a pool as arrays) and return `(chosen enemy per state, step per state)`, the two things the joint-action estimand scores.
"""
import numpy as np

from tcd_common import PARENT  # noqa: F401  (puts this folder on sys.path)
import tactics as T

N = T.N_UNITS
ARENA, DIRS = T.ARENA, 32
CLASSES = 1+DIRS
GRID = {'hidden': (8, 16, 32), 'lr': (0.001, 0.003, 0.01), 'wd': (0.0, 1e-4, 1e-3), 'steps': (4000, 8000, 16000)}
BATCH = 128


# ------------------------------------------------------------------ the pool as arrays

def teacher_move_batch(rel, pref):
    """Vectorized `tactics.teacher_move` (rel (n,2), pref (n,)). Tested equal to the scalar rule."""
    d = np.hypot(rel[:, 0], rel[:, 1])
    safe = np.where(d < 1e-9, 1.0, d)[:, None]
    out = np.zeros_like(rel)
    far = (d >= 1e-9) & (d > pref+0.3)
    back = (d >= 1e-9) & ~far & (pref > 2.0) & (d < pref-0.5)
    out[far] = (rel/safe)[far]
    out[back] = -(rel/safe)[back]
    return out


class Arrays:
    """Observations (and optionally teacher labels) as arrays; no python loops at training or evaluation time."""

    def __init__(self, pool, lab=None):
        own, en = np.asarray(pool['own'], float), np.asarray(pool['enemies'], float)
        self.n = len(own)
        self.own, self.en = own, en
        self.alive = en[:, :, 0] > 0
        self.REL = en[:, :, 1:3]
        self.PREF = own[:, 4]
        e = en
        self.AIMX = np.stack([e[:, :, 1]/ARENA, e[:, :, 2]/ARENA, e[:, :, 3]/ARENA, e[:, :, 4], e[:, :, 5]/6.0, e[:, :, 6]/10.0,
                              np.repeat(own[:, 2:3]/6.0, N, 1)], axis=2)
        o = np.stack([own[:, 0], own[:, 1]/0.3, own[:, 2]/6.0, own[:, 3]/10.0, own[:, 4]/5.0, own[:, 5], own[:, 6], own[:, 7]], axis=1)
        eb = np.stack([e[:, :, 0], e[:, :, 1]/ARENA, e[:, :, 2]/ARENA, e[:, :, 3]/ARENA, e[:, :, 4], e[:, :, 5]/6.0, e[:, :, 6]/10.0], axis=2)
        self.MONO = np.concatenate([o, eb.reshape(self.n, -1)], axis=1)
        self.pool = {'own': own, 'enemies': en}
        if lab is not None:
            self.lab = lab
            self.scores = np.asarray(lab['scores'], float)
            self.target = np.asarray(lab['target'], int)
            self.move = np.asarray(lab['move'], float)

    def move_input(self, rel, pref):
        return np.stack([rel[:, 0]/10.0, rel[:, 1]/10.0, pref/5.0], axis=1)


# ------------------------------------------------------------------ a small tanh network with explicit backpropagation

class Net:
    """d_in -> hidden -> hidden -> d_out, tanh, same initialization as `tactics.MLP`."""

    def __init__(self, d_in, hidden, d_out, rng):
        sizes = (d_in, hidden, hidden, d_out)
        self.W = [rng.normal(0, np.sqrt(1.0/a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]
        self.b = [np.zeros(b) for b in sizes[1:]]

    def params(self):
        return self.W+self.b

    @property
    def n_params(self):
        return int(sum(p.size for p in self.params()))

    def forward(self, Z):
        h1 = np.tanh(Z@self.W[0]+self.b[0])
        h2 = np.tanh(h1@self.W[1]+self.b[1])
        return h2@self.W[2]+self.b[2], (Z, h1, h2)

    def backward(self, cache, dout):
        """Gradients [gW0, gW1, gW2, gb0, gb1, gb2] and the gradient with respect to the input."""
        Z, h1, h2 = cache
        gW2, gb2 = h2.T@dout, dout.sum(0)
        d2 = (dout@self.W[2].T)*(1-h2**2)
        gW1, gb1 = h1.T@d2, d2.sum(0)
        d1 = (d2@self.W[1].T)*(1-h1**2)
        gW0, gb0 = Z.T@d1, d1.sum(0)
        return [gW0, gW1, gW2, gb0, gb1, gb2], d1@self.W[0].T


class Std:
    def __init__(self, X):
        self.m, self.s = X.mean(0), X.std(0)+1e-6

    def f(self, X):
        return (X-self.m)/self.s

    def inv(self, Y):
        return Y*self.s+self.m


def adam_train(params, grad_fn, n_rows, steps, batch, lr, wd, rng, decay_mask):
    """Adam as in the recorded recipe (`tactics.MLP.fit`), same batching and wrap-around, plus an L2 term on weights only. grad_fn(idx) -> grads aligned with params."""
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    batch = min(batch, n_rows)
    order, pos = rng.permutation(n_rows), 0
    for step in range(1, steps+1):
        if pos+batch > n_rows:
            order, pos = rng.permutation(n_rows), 0
        idx = order[pos:pos+batch]
        pos += batch
        grads = grad_fn(idx)
        for k, (p, g) in enumerate(zip(params, grads)):
            if wd and decay_mask[k]:
                g = g+wd*p
            m[k] = 0.9*m[k]+0.1*g
            v[k] = 0.999*v[k]+0.001*g**2
            p -= lr*(m[k]/(1-0.9**step))/(np.sqrt(v[k]/(1-0.999**step))+1e-8)


# ------------------------------------------------------------------ supervision from the same source states

def source_states(n_pool, n, rng):
    return rng.choice(n_pool, min(n, n_pool), replace=False)


def aim_rows(A, idx):
    """The living (state, enemy) pairs of the source states: inputs, teacher scores."""
    alive = A.alive[idx]
    return A.AIMX[idx][alive], A.scores[idx][alive][:, None]


def move_rows(A, idx):
    """(relative position of the teacher's target, preferred range) -> the teacher's step, one row per source state."""
    rel = A.REL[idx][np.arange(len(idx)), A.target[idx]]
    return A.move_input(rel, A.PREF[idx]), A.move[idx]


def direction_class(step):
    """0 = hold, otherwise 1 + the index of the nearest of 32 directions."""
    mag = np.hypot(step[:, 0], step[:, 1])
    k = np.round(np.arctan2(step[:, 1], step[:, 0])/(2*np.pi/DIRS)).astype(int) % DIRS
    return np.where(mag < 0.5, 0, 1+k)


def class_step(cls):
    ang = (np.asarray(cls)-1)*(2*np.pi/DIRS)
    return np.where((np.asarray(cls) == 0)[:, None], 0.0, np.stack([np.cos(ang), np.sin(ang)], axis=1))


def masked_argmax(scores, alive):
    return np.argmax(np.where(alive, scores, -np.inf), axis=1)


# ------------------------------------------------------------------ the models

class Flat:
    """F1 (squared-error step head) and F2 (discrete 32-direction head). Input: all of one state, fixed enemy slots."""

    def __init__(self, kind):
        self.kind = kind
        self.name = {'mse': 'F1', 'disc': 'F2'}[kind]

    def fit(self, A, idx, hp, rng):
        X = A.MONO[idx]
        score = np.where(A.alive[idx], A.scores[idx], -1.0)          # dead slots labelled -1 as in the recorded flat recipe
        if self.kind == 'mse':
            Y = np.c_[A.move[idx], score]
            d_out = 5
        else:
            Y = score
            cls = direction_class(A.move[idx])
            d_out = 3+CLASSES
        self.xs, self.ys = Std(X), Std(Y)
        Z, Tn = self.xs.f(X), self.ys.f(Y)
        self.net = Net(X.shape[1], hp['hidden'], d_out, rng)

        def grad_fn(b):
            out, cache = self.net.forward(Z[b])
            if self.kind == 'mse':
                dout = 2.0*(out-Tn[b])/(len(b)*d_out)
            else:
                dout = np.zeros_like(out)
                dout[:, :3] = 2.0*(out[:, :3]-Tn[b])/(len(b)*3)
                logits = out[:, 3:]
                p = np.exp(logits-logits.max(1, keepdims=True))
                p /= p.sum(1, keepdims=True)
                p[np.arange(len(b)), cls[b]] -= 1.0
                dout[:, 3:] = p/len(b)
            return self.net.backward(cache, dout)[0]
        adam_train(self.net.params(), grad_fn, len(Z), hp['steps'], BATCH, hp['lr'], hp['wd'], rng, [True]*3+[False]*3)
        self.n_params, self.supervision = self.net.n_params, int(Y.size+(len(idx) if self.kind == 'disc' else 0))
        return self

    def step_for(self, A, enemy):
        return self.act(A)[1]       # a flat model has one step output and cannot be told which enemy to act on

    def act(self, A):
        out, _ = self.net.forward(self.xs.f(A.MONO))
        if self.kind == 'mse':
            out = self.ys.inv(out)
            return masked_argmax(out[:, 2:5], A.alive), out[:, :2]
        scores = self.ys.inv(out[:, :3])
        return masked_argmax(scores, A.alive), class_step(np.argmax(out[:, 3:], axis=1))


class Wired:
    """The unit of two parts: a scorer shared by every enemy and a step head conditioned on the chosen enemy. C trains them separately; S1 jointly."""

    def __init__(self, name):
        self.name = name

    def set_standardizers(self, A, idx):
        Xa, Ya = aim_rows(A, idx)
        Xm, Ym = move_rows(A, idx)
        self.xa, self.ya, self.xm, self.ym = Std(Xa), Std(Ya), Std(Xm), Std(Ym)
        return Xa, Ya, Xm, Ym

    @property
    def n_params(self):
        return self.scorer.n_params+self.head.n_params

    def scores(self, A):
        out, _ = self.scorer.forward(self.xa.f(A.AIMX.reshape(-1, A.AIMX.shape[2])))
        return self.ya.inv(out).reshape(A.n, N)

    def step_for(self, A, enemy):
        """The step head's output when the unit is told to act on `enemy` (one slot per state)."""
        rel = A.REL[np.arange(A.n), enemy]
        out, _ = self.head.forward(self.xm.f(A.move_input(rel, A.PREF)))
        return self.ym.inv(out)

    def act(self, A):
        chosen = masked_argmax(self.scores(A), A.alive)
        return chosen, self.step_for(A, chosen)


def fit_composed(A, idx, hp, rng):
    """C: AIM and MOVE taught separately (as in Stage 0), each by Adam on its own rows. One setting is used for both pieces."""
    m = Wired('C')
    Xa, Ya, Xm, Ym = m.set_standardizers(A, idx)
    m.scorer = Net(Xa.shape[1], hp['hidden'], 1, rng)
    m.head = Net(Xm.shape[1], hp['hidden'], 2, rng)
    for net, X, Y, xs, ys in ((m.scorer, Xa, Ya, m.xa, m.ya), (m.head, Xm, Ym, m.xm, m.ym)):
        Z, Tn = xs.f(X), ys.f(Y)

        def grad_fn(b, net=net, Z=Z, Tn=Tn):
            out, cache = net.forward(Z[b])
            return net.backward(cache, 2.0*(out-Tn[b])/(len(b)*Tn.shape[1]))[0]
        adam_train(net.params(), grad_fn, len(Z), hp['steps'], BATCH, hp['lr'], hp['wd'], rng, [True]*3+[False]*3)
    m.supervision = int(Ya.size+Ym.size)
    m.oracle_queries = 0
    return m


def s1_step(model, A, b, mode, labels=None, ref_soft=None):
    """One S1 minibatch of source states b: loss and gradients [scorer params..., head params...].
    mode 'st': straight-through (forward takes the hard argmax enemy, backward uses the softmax weights); 'soft': forward uses the softmax-weighted enemy (tests only);
    'surrogate': hard value plus (soft - ref_soft), whose exact derivative is the straight-through gradient (tests only).
    labels: fixed step labels (tests); otherwise the teacher's rule applied to the enemy S1 itself selected (an oracle query on its own choice)."""
    B = len(b)
    alive = A.alive[b]
    Zin = model.xa.f(A.AIMX[b].reshape(-1, A.AIMX.shape[2]))
    out, cache = model.scorer.forward(Zin)
    z = out.reshape(B, N)
    t = model.ya.f(A.scores[b][..., None]).reshape(B, N)
    n_alive = alive.sum()
    d_score = np.where(alive, 2.0*(z-t)/n_alive, 0.0)
    loss_score = float(np.sum(np.where(alive, (z-t)**2, 0.0))/n_alive)
    zm = np.where(alive, z, -np.inf)
    sel = np.argmax(zm, axis=1)
    w = np.exp(np.where(alive, z-zm.max(1, keepdims=True), -np.inf))
    w = w/w.sum(1, keepdims=True)
    rel = A.REL[b]
    hard = rel[np.arange(B), sel]
    soft = (w[:, :, None]*rel).sum(1)
    rel_sel = hard if mode == 'st' else soft if mode == 'soft' else hard+soft-ref_soft
    fin = model.xm.f(A.move_input(rel_sel, A.PREF[b]))
    hout, hcache = model.head.forward(fin)
    lab = teacher_move_batch(hard, A.PREF[b]) if labels is None else labels
    tl = model.ym.f(lab)
    loss_step = float(np.mean((hout-tl)**2))
    hgrads, dfin = model.head.backward(hcache, 2.0*(hout-tl)/(B*2))
    drel = (dfin/model.xm.s)[:, :2]/10.0
    g = (rel*drel[:, None, :]).sum(-1)
    dz = d_score+w*(g-(w*g).sum(1, keepdims=True))
    sgrads, _ = model.scorer.backward(cache, dz.reshape(-1, 1))
    return loss_score+loss_step, sgrads+hgrads, {'loss_score': loss_score, 'loss_step': loss_step, 'soft': soft}


def fit_s1(A, idx, hp, rng):
    m = Wired('S1')
    m.set_standardizers(A, idx)
    m.scorer = Net(A.AIMX.shape[2], hp['hidden'], 1, rng)
    m.head = Net(3, hp['hidden'], 2, rng)
    params = m.scorer.params()+m.head.params()

    def grad_fn(pos):
        return s1_step(m, A, idx[pos], 'st')[1]
    adam_train(params, grad_fn, len(idx), hp['steps'], BATCH, hp['lr'], hp['wd'], rng, [True]*3+[False]*3+[True]*3+[False]*3)
    Xa, Ya = aim_rows(A, idx)
    m.supervision = int(Ya.size+len(idx)*2)          # the same label content as C
    m.oracle_queries = int(hp['steps']*min(BATCH, len(idx)))   # extra teacher-rule queries on S1's own selection (C has none)
    return m


def fit_f0(A, idx, hp, rng):
    """The recorded flat recipe: `tactics.MLP` (lr 0.003, batch 128, no weight decay, no search); the caller passes hidden 15 and 8,000 steps, as recorded."""
    X = A.MONO[idx]
    Y = np.c_[A.move[idx], np.where(A.alive[idx], A.scores[idx], -1.0)]
    net = T.MLP(X.shape[1], hp['hidden'], Y.shape[1], rng).fit(X, Y, rng, hp['steps'])
    return F0(net)


class F0:
    name = 'F0'

    def __init__(self, net):
        self.net = net
        self.n_params = int(sum(p.size for p in net.W+net.b))
        self.supervision = None

    def step_for(self, A, enemy):
        return self.act(A)[1]

    def act(self, A):
        out = self.net.predict(A.MONO)
        return masked_argmax(out[:, 2:5], A.alive), out[:, :2]


FITS = {'F1': lambda A, idx, hp, rng: Flat('mse').fit(A, idx, hp, rng), 'F2': lambda A, idx, hp, rng: Flat('disc').fit(A, idx, hp, rng),
        'C': fit_composed, 'S1': fit_s1, 'F0': fit_f0}


def policy_of(model):
    """Closed-loop controller for the sandbox: (own, enemies) -> (step, target slot, no burst)."""
    def policy(own, enemies):
        A = Arrays({'own': own[None], 'enemies': enemies[None]})
        chosen, step = model.act(A)
        return step[0], int(chosen[0]), False
    return policy
