"""Experiment 0e: the conventional flat family F*-plus (PROPOSAL_0E.md section 3). Exploratory; NOT a milestone.

A NEW file. One network over the whole observation (fixed enemy slots), any depth and width (tanh), three step heads:
- 'mse':     one continuous step (squared error) plus the three enemy scores, as the 0d flat models;
- 'disc':    hold or one of 32 directions (cross-entropy) plus the scores;
- 'perslot': one step per enemy slot plus the scores; the unit takes the step of the slot it chooses. This is a **structured conventional policy** (its step is
             conditioned on the selected slot), named as such; per-slot labels are the teacher's rule applied to every living slot (counterfactual teacher queries,
             counted).
"""
import numpy as np

from tcd_common import PARENT  # noqa: F401
import tactics as T
import zd_models as Z

N = T.N_UNITS


class DeepNet:
    """d_in -> hidden x depth (tanh) -> d_out; initialization as `tactics.MLP` (normal with variance 1/fan-in)."""

    def __init__(self, d_in, hidden, depth, d_out, rng):
        sizes = [d_in]+[hidden]*depth+[d_out]
        self.W = [rng.normal(0, np.sqrt(1.0/a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]
        self.b = [np.zeros(b) for b in sizes[1:]]

    def params(self):
        return self.W+self.b

    @property
    def n_params(self):
        return int(sum(p.size for p in self.params()))

    def forward(self, Z_):
        hs = [Z_]
        h = Z_
        for W, b in zip(self.W[:-1], self.b[:-1]):
            h = np.tanh(h@W+b)
            hs.append(h)
        return h@self.W[-1]+self.b[-1], hs

    def backward(self, hs, dout):
        L = len(self.W)
        gW, gb = [None]*L, [None]*L
        d = dout
        for k in range(L-1, -1, -1):
            gW[k], gb[k] = hs[k].T@d, d.sum(0)
            if k:
                d = (d@self.W[k].T)*(1-hs[k]**2)
        return gW+gb


class FlatPlus:
    def __init__(self, head, name=None):
        assert head in ('mse', 'disc', 'perslot')
        self.head = head
        self.name = name or 'Fp_'+head

    def fit(self, A, idx, hp, rng):
        X = A.MONO[idx]
        alive = A.alive[idx]
        score = np.where(alive, A.scores[idx], -1.0)                       # dead slots labelled -1, as in the recorded flat recipe
        self.xs = Z.Std(X)
        Zi = self.xs.f(X)
        self.ss = Z.Std(score)
        Ts = self.ss.f(score)
        if self.head == 'mse':
            Ym = A.move[idx]
            self.ms = Z.Std(Ym)
            Tm = self.ms.f(Ym)
            d_out = 3+2
        elif self.head == 'disc':
            cls = Z.direction_class(A.move[idx])
            d_out = 3+Z.CLASSES
        else:
            per = np.stack([Z.teacher_move_batch(A.REL[idx, j], A.PREF[idx]) for j in range(N)], axis=1)     # (n, 3, 2)
            flat = per.reshape(len(idx), -1)
            self.ms = Z.Std(flat)
            Tm = self.ms.f(flat)
            mask = np.repeat(alive, 2, axis=1).astype(float)
            d_out = 3+2*N
        self.net = DeepNet(X.shape[1], hp['hidden'], hp['depth'], d_out, rng)

        def grad_fn(b):
            out, hs = self.net.forward(Zi[b])
            dout = np.zeros_like(out)
            B = len(b)
            dout[:, :3] = 2.0*(out[:, :3]-Ts[b])/(B*3)
            if self.head == 'mse':
                dout[:, 3:] = 2.0*(out[:, 3:]-Tm[b])/(B*2)
            elif self.head == 'disc':
                logits = out[:, 3:]
                p = np.exp(logits-logits.max(1, keepdims=True))
                p /= p.sum(1, keepdims=True)
                p[np.arange(B), cls[b]] -= 1.0
                dout[:, 3:] = p/B
            else:
                m = mask[b]
                dout[:, 3:] = 2.0*(out[:, 3:]-Tm[b])*m/max(m.sum(), 1.0)
            return self.net.backward(hs, dout)
        L = len(self.net.W)
        Z.adam_train(self.net.params(), grad_fn, len(Zi), hp['steps'], Z.BATCH, hp['lr'], hp['wd'], rng, [True]*L+[False]*L)
        self.n_params = self.net.n_params
        self.oracle_queries = int(alive.sum()) if self.head == 'perslot' else 0          # living supervised per-slot labels
        self.oracle_labels_computed = int(alive.size) if self.head == 'perslot' else 0   # labels computed for every slot (dead ones masked out of the loss)
        return self

    def scores(self, A):
        out, _ = self.net.forward(self.xs.f(A.MONO))
        return self.ss.inv(out[:, :3])

    def act(self, A):
        out, _ = self.net.forward(self.xs.f(A.MONO))
        chosen = Z.masked_argmax(self.ss.inv(out[:, :3]), A.alive)
        if self.head == 'mse':
            return chosen, self.ms.inv(out[:, 3:])
        if self.head == 'disc':
            return chosen, Z.class_step(np.argmax(out[:, 3:], axis=1))
        per = self.ms.inv(out[:, 3:]).reshape(A.n, N, 2)
        return chosen, per[np.arange(A.n), chosen]

    def step_for(self, A, enemy):
        if self.head != 'perslot':
            return self.act(A)[1]                 # unconditional step: cannot be told which enemy to act on
        out, _ = self.net.forward(self.xs.f(A.MONO))
        return self.ms.inv(out[:, 3:]).reshape(A.n, N, 2)[np.arange(A.n), enemy]


def fit_flat_plus(A, idx, hp, rng):
    return FlatPlus(hp['head']).fit(A, idx, hp, rng)
