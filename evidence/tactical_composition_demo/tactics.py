"""Tactical sandbox, scripted teacher and baselines, and the learned pieces for the tactical composition demo (Stage 0).

NOT a milestone, NOT C6 evidence. See PROPOSAL.md and SPECIFICATION.md.

One unit works from its own stats and what it sees. Stage 0 pieces: AIM (which enemy) and MOVE (where to step). The mage's burst
(ABILITY piece) is Stage 0b and switched off (USE_BURST = False); its code is kept for that stage. Pieces are small ordinary networks
taught one job each from a scripted teacher, wired into a unit controller, and compared with one big learned controller of the same
size taught on the same teacher's full decisions.
"""
import numpy as np

ARENA = 20.0
MAX_TICKS = 300
N_UNITS = 3
FIGHTER, ARCHER, MAGE, SKIRMISHER = 0, 1, 2, 3
USE_BURST = False   # Stage 0 is AIM + MOVE; the mage's burst (ABILITY piece) is Stage 0b

# name, hp, speed per tick, range, damage, cooldown ticks, preferred range, is mage
UNIT_TYPES = {
    FIGHTER: dict(hp=100.0, speed=0.30, range=1.5, damage=9.0, cooldown=4, pref=1.2, mage=0.0),
    ARCHER: dict(hp=60.0, speed=0.30, range=6.0, damage=7.0, cooldown=4, pref=5.0, mage=0.0),
    MAGE: dict(hp=50.0, speed=0.25, range=4.0, damage=5.0, cooldown=4, pref=3.5, mage=1.0),
    SKIRMISHER: dict(hp=60.0, speed=0.30, range=6.0, damage=7.0, cooldown=4, pref=2.5, mage=0.0)}   # never seen: an archer's range with a short preferred range
BURST = dict(radius=3.0, range=5.0, damage=12.0, cooldown=15)

SEEN_MIXES = [(FIGHTER, FIGHTER, FIGHTER), (FIGHTER, FIGHTER, ARCHER), (FIGHTER, ARCHER, ARCHER), (ARCHER, ARCHER, ARCHER),
              (MAGE, FIGHTER, FIGHTER), (MAGE, FIGHTER, ARCHER), (MAGE, ARCHER, ARCHER)]
UNSEEN_MIXES = [(SKIRMISHER, FIGHTER, FIGHTER), (SKIRMISHER, FIGHTER, ARCHER), (SKIRMISHER, ARCHER, ARCHER),
                (SKIRMISHER, SKIRMISHER, FIGHTER), (SKIRMISHER, SKIRMISHER, ARCHER)]

OWN_DIM, ENEMY_DIM = 8, 7           # own: hp frac, speed, range, damage, pref, attack ready, burst ready, is mage
AIM_DIM, MOVE_DIM, ABILITY_DIM = 7, 3, 13
FINISHER_HP = 0.35
MONO_IN, MONO_OUT = OWN_DIM+N_UNITS*ENEMY_DIM, 2+N_UNITS


# ---------------------------------------------------------------- the world

class World:
    """Two teams of three on an open arena. Simultaneous resolution, deterministic given its random stream."""

    def __init__(self, mix_a, mix_b, rng, types=UNIT_TYPES):
        self.types = np.array([mix_a, mix_b])
        shape = (2, N_UNITS)
        get = lambda key: np.array([[types[int(t)][key] for t in row] for row in self.types], float)
        self.hpmax, self.speed, self.range = get('hp'), get('speed'), get('range')
        self.damage, self.cooldown, self.pref, self.mage = get('damage'), get('cooldown'), get('pref'), get('mage')
        self.hp = self.hpmax.copy()
        self.cd, self.ab = np.zeros(shape), np.zeros(shape)
        ys = np.array([6.0, 10.0, 14.0])
        self.pos = np.zeros(shape+(2,))
        for team, x in ((0, 3.0), (1, 17.0)):
            order = rng.permutation(N_UNITS)
            self.pos[team, :, 0] = x+rng.uniform(-0.5, 0.5, N_UNITS)
            self.pos[team, :, 1] = ys[order]+rng.uniform(-1.0, 1.0, N_UNITS)
        self.alive = self.hp > 0
        self.t = 0
        self.done = False

    def alive_count(self, team):
        return int(self.alive[team].sum())

    def observe(self, team, i):
        e = 1-team
        own = np.array([self.hp[team, i]/self.hpmax[team, i], self.speed[team, i], self.range[team, i],
                        self.damage[team, i], self.pref[team, i], float(self.cd[team, i] <= 0),
                        float(self.ab[team, i] <= 0), self.mage[team, i]])
        rel = self.pos[e]-self.pos[team, i]
        dist = np.hypot(rel[:, 0], rel[:, 1])
        enemies = np.c_[self.alive[e].astype(float), rel, dist, self.hp[e]/self.hpmax[e], self.range[e], self.damage[e]]
        return own, enemies

    def step(self, actions):
        """actions[team][i] = (move vector, target slot, fire flag). Movement first, then attacks and bursts, then damage."""
        for team in (0, 1):
            for i in range(N_UNITS):
                if not self.alive[team, i]:
                    continue
                move = np.asarray(actions[team][i][0], float)
                norm = float(np.hypot(*move))
                if norm > 1.0:
                    move = move/norm
                self.pos[team, i] = np.clip(self.pos[team, i]+move*self.speed[team, i], 0.0, ARENA)
        damage = np.zeros((2, N_UNITS))
        for team in (0, 1):
            e = 1-team
            for i in range(N_UNITS):
                if not self.alive[team, i]:
                    continue
                _, target, fire = actions[team][i]
                target = int(target)
                if not self.alive[e, target]:
                    continue
                gap = float(np.hypot(*(self.pos[e, target]-self.pos[team, i])))
                if fire and self.mage[team, i] and self.ab[team, i] <= 0 and gap <= BURST['range']:
                    centre = self.pos[e, target]
                    for j in range(N_UNITS):
                        if self.alive[e, j] and float(np.hypot(*(self.pos[e, j]-centre))) <= BURST['radius']:
                            damage[e, j] += BURST['damage']
                    self.ab[team, i] = BURST['cooldown']
                elif self.cd[team, i] <= 0 and gap <= self.range[team, i]:
                    damage[e, target] += self.damage[team, i]
                    self.cd[team, i] = self.cooldown[team, i]
        self.hp = np.maximum(self.hp-damage, 0.0)
        self.alive = self.hp > 0
        self.cd = np.maximum(self.cd-1, 0.0)
        self.ab = np.maximum(self.ab-1, 0.0)
        self.t += 1
        if self.alive_count(0) == 0 or self.alive_count(1) == 0 or self.t >= MAX_TICKS:
            self.done = True

    def score(self, team=0):
        """1 win, 0.5 draw (including timeout), 0 loss."""
        a, b = self.alive_count(team), self.alive_count(1-team)
        return 1.0 if (a > 0 and b == 0) else 0.0 if (a == 0 and b > 0) else 0.5


# ---------------------------------------------------------------- scripted teacher and baselines (observation in, action out)

def alive_slots(enemies):
    return np.flatnonzero(enemies[:, 0] > 0)


def teacher_scores(own, enemies):
    """Teacher's AIM score per enemy: weak ones, ones in range and near ones first. Dead enemies get -9."""
    s = (1.0-enemies[:, 4])+0.6*(enemies[:, 3] <= own[2])-0.08*enemies[:, 3]
    return np.where(enemies[:, 0] > 0, s, -9.0)


def teacher_move(rel, pref):
    """Close in beyond the preferred range, back off (ranged units only) inside it, otherwise hold."""
    d = float(np.hypot(*rel))
    if d < 1e-9:
        return np.zeros(2)
    if d > pref+0.3:
        return rel/d
    if pref > 2.0 and d < pref-0.5:
        return -rel/d
    return np.zeros(2)


def teacher_fire(own, enemies, target):
    """A ready mage bursts when the target is in burst range and the blast would hit two or more enemies, or hit a nearly dead one."""
    if own[7] < 0.5 or own[6] < 0.5 or enemies[target, 0] < 0.5 or enemies[target, 3] > BURST['range']:
        return False
    centre = enemies[target, 1:3]
    hits = sum(1 for e in enemies if e[0] > 0 and float(np.hypot(*(e[1:3]-centre))) <= BURST['radius'])
    return hits >= 2 or (hits >= 1 and enemies[target, 4] <= FINISHER_HP)


def teacher_policy(own, enemies):
    scores = teacher_scores(own, enemies)
    target = int(np.argmax(scores))
    return teacher_move(enemies[target, 1:3], own[4]), target, USE_BURST and teacher_fire(own, enemies, target)


def rush_policy(own, enemies):
    """Baseline and opponent 1: attack the nearest enemy, walk straight at it until in range, never burst."""
    alive = alive_slots(enemies)
    target = int(alive[np.argmin(enemies[alive, 3])])
    rel = enemies[target, 1:3]
    d = float(np.hypot(*rel))
    move = rel/d if (d > 0.9*own[2] and d > 1e-9) else np.zeros(2)
    return move, target, False


def kiter_policy(own, enemies):
    """Opponent 2: focus the weakest enemy, keep the preferred range, burst when it pays."""
    scores = np.where(enemies[:, 0] > 0, 1.0-enemies[:, 4]-0.01*enemies[:, 3], -9.0)
    target = int(np.argmax(scores))
    return teacher_move(enemies[target, 1:3], own[4]), target, USE_BURST and teacher_fire(own, enemies, target)


def make_random_policy(rng):
    def policy(own, enemies):
        alive = alive_slots(enemies)
        angle = rng.uniform(0, 2*np.pi)
        return np.array([np.cos(angle), np.sin(angle)])*rng.random(), int(rng.choice(alive)), bool(USE_BURST and rng.random() < 0.3)
    return policy


OPPONENTS = {'rush': rush_policy, 'kiter': kiter_policy}


# ---------------------------------------------------------------- features

def aim_features(own, enemies, j):
    e = enemies[j]
    return np.array([e[1]/ARENA, e[2]/ARENA, e[3]/ARENA, e[4], e[5]/6.0, e[6]/10.0, own[2]/6.0])


def move_features(rel, pref):
    return np.array([rel[0]/10.0, rel[1]/10.0, pref/5.0])


def ability_features(own, enemies, target):
    rel = enemies[target, 1:3]
    out = [own[6], rel[0]/10.0, rel[1]/10.0, enemies[target, 4]]
    for e in enemies:
        out += [e[0], e[1]/10.0, e[2]/10.0]
    return np.array(out)


def mono_features(own, enemies):
    o = np.array([own[0], own[1]/0.3, own[2]/6.0, own[3]/10.0, own[4]/5.0, own[5], own[6], own[7]])
    e = np.c_[enemies[:, 0], enemies[:, 1]/ARENA, enemies[:, 2]/ARENA, enemies[:, 3]/ARENA, enemies[:, 4],
              enemies[:, 5]/6.0, enemies[:, 6]/10.0]
    return np.concatenate([o, e.ravel()])


# ---------------------------------------------------------------- the learned model (ordinary matrix math, multi-output)

class MLP:
    def __init__(self, d_in, hidden, d_out, rng):
        sizes = (d_in, hidden, hidden, d_out)
        self.W = [rng.normal(0, np.sqrt(1.0/a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]
        self.b = [np.zeros(b) for b in sizes[1:]]

    @staticmethod
    def parameter_count(d_in, hidden, d_out):
        return d_in*hidden+hidden+hidden*hidden+hidden+hidden*d_out+d_out

    def forward(self, Z):
        h1 = np.tanh(Z@self.W[0]+self.b[0])
        h2 = np.tanh(h1@self.W[1]+self.b[1])
        return h1, h2, h2@self.W[2]+self.b[2]

    def fit(self, X, Y, rng, steps, batch=128, lr=0.003):
        self.mx, self.sx = X.mean(0), X.std(0)+1e-6
        self.my, self.sy = Y.mean(0), Y.std(0)+1e-6
        Z, T = (X-self.mx)/self.sx, (Y-self.my)/self.sy
        params = self.W+self.b
        m = [np.zeros_like(p) for p in params]
        v = [np.zeros_like(p) for p in params]
        order, pos = rng.permutation(len(Z)), 0
        for step in range(1, steps+1):
            if pos+batch > len(Z):
                order, pos = rng.permutation(len(Z)), 0
            idx = order[pos:pos+batch]
            pos += batch
            z, t = Z[idx], T[idx]
            h1, h2, out = self.forward(z)
            g = 2.0*(out-t)/(len(idx)*t.shape[1])
            gW2, gb2 = h2.T@g, g.sum(0)
            d2 = (g@self.W[2].T)*(1-h2**2)
            gW1, gb1 = h1.T@d2, d2.sum(0)
            d1 = (d2@self.W[1].T)*(1-h1**2)
            gW0, gb0 = z.T@d1, d1.sum(0)
            for k, (p, gr) in enumerate(zip(params, [gW0, gW1, gW2, gb0, gb1, gb2])):
                m[k] = 0.9*m[k]+0.1*gr
                v[k] = 0.999*v[k]+0.001*gr**2
                p -= lr*(m[k]/(1-0.9**step))/(np.sqrt(v[k]/(1-0.999**step))+1e-8)
        return self

    def predict(self, X):
        return self.forward((np.atleast_2d(X)-self.mx)/self.sx)[2]*self.sy+self.my


# ---------------------------------------------------------------- data from play

def random_action(rng, enemies):
    alive = alive_slots(enemies)
    angle = rng.uniform(0, 2*np.pi)
    return np.array([np.cos(angle), np.sin(angle)])*rng.random(), int(rng.choice(alive)), bool(USE_BURST and rng.random() < 0.3)


def collect(rng, episodes, mixes, noise=0.3, opponents=None):
    """States met while the scripted teacher plays (with some random actions mixed in), each with the teacher's labels."""
    opponents = list(OPPONENTS.values()) if opponents is None else opponents
    rows = {k: [] for k in ('own', 'enemies')}
    for _ in range(episodes):
        mix_a = tuple(rng.permutation(mixes[int(rng.integers(len(mixes)))]))
        mix_b = tuple(rng.permutation(SEEN_MIXES[int(rng.integers(len(SEEN_MIXES)))]))
        world = World(mix_a, mix_b, rng)
        opponent = opponents[int(rng.integers(len(opponents)))]
        while not world.done:
            actions = [[None]*N_UNITS, [None]*N_UNITS]
            for i in range(N_UNITS):
                if not world.alive[0, i]:
                    actions[0][i] = (np.zeros(2), 0, False)
                    continue
                own, enemies = world.observe(0, i)
                rows['own'].append(own)
                rows['enemies'].append(enemies)
                actions[0][i] = random_action(rng, enemies) if rng.random() < noise else teacher_policy(own, enemies)
            for i in range(N_UNITS):
                actions[1][i] = (np.zeros(2), 0, False) if not world.alive[1, i] else opponent(*world.observe(1, i))
            world.step(actions)
    return {'own': np.array(rows['own']), 'enemies': np.array(rows['enemies'])}


def labels(pool):
    """Teacher labels for every logged state."""
    n = len(pool['own'])
    scores = np.zeros((n, N_UNITS))
    target = np.zeros(n, int)
    move = np.zeros((n, 2))
    fire = np.zeros(n)
    for k in range(n):
        own, enemies = pool['own'][k], pool['enemies'][k]
        scores[k] = teacher_scores(own, enemies)
        target[k] = int(np.argmax(scores[k]))
        move[k] = teacher_move(enemies[target[k], 1:3], own[4])
        fire[k] = float(USE_BURST and teacher_fire(own, enemies, target[k]))
    return {'scores': scores, 'target': target, 'move': move, 'fire': fire}


def piece_datasets(pool, lab, n_aim, n_move, rng, n_ability=0):
    """One dataset per piece; a row is one labeled decision of that piece."""
    out = {}
    rows = [(k, j) for k in range(len(pool['own'])) for j in alive_slots(pool['enemies'][k])]
    pick = rng.choice(len(rows), min(n_aim, len(rows)), replace=False)
    X = np.array([aim_features(pool['own'][rows[p][0]], pool['enemies'][rows[p][0]], rows[p][1]) for p in pick])
    Y = np.array([[lab['scores'][rows[p][0]][rows[p][1]]] for p in pick])
    out['AIM'] = (X, Y)
    pick = rng.choice(len(pool['own']), min(n_move, len(pool['own'])), replace=False)
    X = np.array([move_features(pool['enemies'][k][lab['target'][k], 1:3], pool['own'][k][4]) for k in pick])
    out['MOVE'] = (X, lab['move'][pick])
    if n_ability:   # Stage 0b: the piece decides when a ready burst fires
        mages = np.flatnonzero((pool['own'][:, 7] > 0.5) & (pool['own'][:, 6] > 0.5))
        pick = rng.choice(mages, min(n_ability, len(mages)), replace=False)
        X = np.array([ability_features(pool['own'][k], pool['enemies'][k], lab['target'][k]) for k in pick])
        out['ABILITY'] = (X, lab['fire'][pick][:, None])
    return out


def mono_dataset(pool, lab, n, rng):
    pick = rng.choice(len(pool['own']), min(n, len(pool['own'])), replace=False)
    X = np.array([mono_features(pool['own'][k], pool['enemies'][k]) for k in pick])
    scores = np.where(pool['enemies'][pick][:, :, 0] > 0, lab['scores'][pick], -1.0)
    Y = np.c_[lab['move'][pick], scores]
    return X, Y


# ---------------------------------------------------------------- controllers

def composed_policy(aim, move, ability=None):
    """Unit controller by wiring: AIM picks the target, MOVE steps toward it (ABILITY, when present, decides the burst). No joint training."""
    def policy(own, enemies):
        alive = alive_slots(enemies)
        scores = aim.predict(np.array([aim_features(own, enemies, j) for j in alive]))[:, 0]
        target = int(alive[int(np.argmax(scores))])
        step = move.predict(move_features(enemies[target, 1:3], own[4]))[0]
        fire = bool(ability is not None and own[7] > 0.5 and own[6] > 0.5
                    and ability.predict(ability_features(own, enemies, target))[0, 0] > 0.5)
        return step, target, fire
    return policy


def mono_policy(model):
    def policy(own, enemies):
        out = model.predict(mono_features(own, enemies))[0]
        alive = alive_slots(enemies)
        target = int(alive[int(np.argmax(out[2:2+N_UNITS][alive]))])
        return out[:2], target, False
    return policy


# ---------------------------------------------------------------- playing

def play(policy_a, mix_a, opponent, mix_b, rng):
    world = World(mix_a, mix_b, rng)
    while not world.done:
        actions = [[None]*N_UNITS, [None]*N_UNITS]
        for team, policy in ((0, policy_a), (1, opponent)):
            for i in range(N_UNITS):
                actions[team][i] = (np.zeros(2), 0, False) if not world.alive[team, i] else policy(*world.observe(team, i))
        world.step(actions)
    return world.score(0)


def win_score(policy, mixes, opponent, rng, episodes):
    scores = []
    for _ in range(episodes):
        mix_a = tuple(rng.permutation(mixes[int(rng.integers(len(mixes)))]))
        mix_b = tuple(rng.permutation(SEEN_MIXES[int(rng.integers(len(SEEN_MIXES)))]))
        scores.append(play(policy, mix_a, opponent, mix_b, rng))
    return float(np.mean(scores))


# ---------------------------------------------------------------- fidelity of each piece to its teacher (held-out states)

def move_metrics(pred, truth, rel):
    """Angular error where the teacher moves, hold agreement where it holds, and the angle on back-off states alone."""
    out = {}
    moving = np.hypot(truth[:, 0], truth[:, 1]) > 0.5
    if moving.any():
        cos = (pred[moving]*truth[moving]).sum(1)/(np.hypot(pred[moving, 0], pred[moving, 1])*np.hypot(truth[moving, 0], truth[moving, 1])+1e-9)
        angles = np.degrees(np.arccos(np.clip(cos, -1, 1)))
        out['move_median_angle_deg'], out['move_p90_angle_deg'] = float(np.median(angles)), float(np.quantile(angles, 0.9))
    out['move_hold_agreement'] = float(np.mean(np.hypot(pred[~moving, 0], pred[~moving, 1]) < 0.5)) if (~moving).any() else None
    out['move_share_moving'] = float(np.mean(moving))
    back = moving & ((truth*rel).sum(1) < 0)
    out['move_share_backoff'] = float(np.mean(back))
    if back.any():
        cos = (pred[back]*truth[back]).sum(1)/(np.hypot(pred[back, 0], pred[back, 1])*np.hypot(truth[back, 0], truth[back, 1])+1e-9)
        out['move_backoff_median_angle_deg'] = float(np.median(np.degrees(np.arccos(np.clip(cos, -1, 1)))))
    return out


def target_rel(pool, lab):
    return np.array([pool['enemies'][k][lab['target'][k], 1:3] for k in range(len(pool['own']))])


def fidelity(models, pool, lab):
    """AIM top-1 agreement per state (with a nearest-enemy floor) and the MOVE metrics (ABILITY balanced accuracy in Stage 0b)."""
    out = {}
    agree, nearest = [], []
    for k in range(len(pool['own'])):
        alive = alive_slots(pool['enemies'][k])
        pred = models['AIM'].predict(np.array([aim_features(pool['own'][k], pool['enemies'][k], j) for j in alive]))[:, 0]
        agree.append(int(alive[int(np.argmax(pred))]) == int(lab['target'][k]))
        nearest.append(int(alive[int(np.argmin(pool['enemies'][k][alive, 3]))]) == int(lab['target'][k]))
    out['aim_top1'] = float(np.mean(agree))
    out['aim_nearest_enemy_floor'] = float(np.mean(nearest))
    rel = target_rel(pool, lab)
    X = np.array([move_features(rel[k], pool['own'][k][4]) for k in range(len(pool['own']))])
    out.update(move_metrics(models['MOVE'].predict(X), lab['move'], rel))
    if 'ABILITY' in models:
        mages = np.flatnonzero((pool['own'][:, 7] > 0.5) & (pool['own'][:, 6] > 0.5))
        X = np.array([ability_features(pool['own'][k], pool['enemies'][k], lab['target'][k]) for k in mages])
        pred_fire, truth_fire = models['ABILITY'].predict(X)[:, 0] > 0.5, lab['fire'][mages] > 0.5
        pos, neg = truth_fire.sum(), (~truth_fire).sum()
        recall = float((pred_fire & truth_fire).sum()/pos) if pos else None
        specificity = float((~pred_fire & ~truth_fire).sum()/neg) if neg else None
        out['ability_balanced_accuracy'] = None if recall is None or specificity is None else (recall+specificity)/2
        out['ability_positive_rate'] = float(truth_fire.mean())
    return out


def mono_fidelity(model, pool, lab):
    """The one big controller's agreement with the same teacher on the same held-out states (a check that the baseline learned)."""
    X = np.array([mono_features(o, e) for o, e in zip(pool['own'], pool['enemies'])])
    pred = model.predict(X)
    alive = pool['enemies'][:, :, 0] > 0
    scores = np.where(alive, pred[:, 2:2+N_UNITS], -np.inf)
    out = {'aim_top1': float(np.mean(np.argmax(scores, axis=1) == lab['target']))}
    out.update(move_metrics(pred[:, :2], lab['move'], target_rel(pool, lab)))
    return out
