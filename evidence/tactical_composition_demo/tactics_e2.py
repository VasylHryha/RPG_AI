"""Task revision e2 for experiment 0e (PROPOSAL_0E.md section 7: the teacher-necessity gate failed in the original sandbox, so the task is revised in NEW files).
Exploratory; NOT a milestone. `tactics.py` stays frozen: this module reuses its world, rules and opponents and changes only what a variant declares:

- formation: melee units start in a front line, ranged units in a back line (so the nearest enemy is often a front-line unit);
- unit statistics (optionally glass-cannon ranged units and tank fighters);
- the teacher's targeting doctrine (a linear score over what a unit observes); the teacher's stepping rule is unchanged (`tactics.teacher_move`);
- team mixes: only mixed teams (melee and ranged together).

Three variants are declared before any measurement (VARIANTS, in order); `dev_0e/dev_step4_task.py` applies the fixed selection rule.
"""
import numpy as np

import tactics as T

F, A, M = T.FIGHTER, T.ARCHER, T.MAGE
MIXES = [(F, F, A), (F, A, A), (M, F, A), (M, F, F), (M, A, A)]
GLASS = {F: dict(hp=140.0, speed=0.30, range=1.5, damage=9.0, cooldown=4, pref=1.2, mage=0.0),
         A: dict(hp=40.0, speed=0.30, range=6.0, damage=12.0, cooldown=4, pref=5.0, mage=0.0),
         M: dict(hp=45.0, speed=0.25, range=4.0, damage=8.0, cooldown=4, pref=3.5, mage=1.0),
         T.SKIRMISHER: T.UNIT_TYPES[T.SKIRMISHER]}
# doctrine weights: ranged (range > 3), damage / 10, missing health, in own range, distance (subtracted)
VARIANTS = {
    'V1': {'types': T.UNIT_TYPES, 'formation': True, 'doctrine': (1.0, 0.0, 1.0, 0.6, 0.03)},
    'V2': {'types': GLASS, 'formation': True, 'doctrine': (0.0, 1.0, 1.0, 0.3, 0.03)},
    'V3': {'types': GLASS, 'formation': False, 'doctrine': (0.0, 1.0, 1.0, 0.3, 0.03)},
}


def doctrine_scores(variant):
    w_rng, w_dmg, w_miss, w_in, w_dist = VARIANTS[variant]['doctrine']

    def scores(own, enemies):
        s = w_rng*(enemies[:, 5] > 3.0)+w_dmg*enemies[:, 6]/10.0+w_miss*(1.0-enemies[:, 4])+w_in*(enemies[:, 3] <= own[2])-w_dist*enemies[:, 3]
        return np.where(enemies[:, 0] > 0, s, -9.0)
    return scores


def doctrine_scores_batch(variant):
    w_rng, w_dmg, w_miss, w_in, w_dist = VARIANTS[variant]['doctrine']

    def scores(Ar):
        e, own = Ar.en, Ar.own
        s = w_rng*(e[:, :, 5] > 3.0)+w_dmg*e[:, :, 6]/10.0+w_miss*(1.0-e[:, :, 4])+w_in*(e[:, :, 3] <= own[:, 2:3])-w_dist*e[:, :, 3]
        return np.where(Ar.alive, s, -9.0)
    return scores


def teacher_policy(variant):
    sc = doctrine_scores(variant)

    def policy(own, enemies):
        target = int(np.argmax(sc(own, enemies)))
        return T.teacher_move(enemies[target, 1:3], own[4]), target, False
    return policy


def world_fn(variant):
    v = VARIANTS[variant]

    def make(mix_a, mix_b, rng):
        w = T.World(mix_a, mix_b, rng, types=v['types'])
        if v['formation']:
            for team, (front, back) in ((0, (7.0, 2.0)), (1, (13.0, 18.0))):
                for i in range(T.N_UNITS):
                    w.pos[team, i, 0] = (front if w.range[team, i] < 3.0 else back)+rng.uniform(-0.5, 0.5)
        return w
    return make


def collect(variant, rng, episodes, noise=0.3):
    """States met while this variant's teacher plays (with random actions mixed in), as `tactics.collect`."""
    make, teacher = world_fn(variant), teacher_policy(variant)
    opponents = list(T.OPPONENTS.values())
    rows = {'own': [], 'enemies': []}
    for _ in range(episodes):
        mix_a = tuple(rng.permutation(MIXES[int(rng.integers(len(MIXES)))]))
        mix_b = tuple(rng.permutation(MIXES[int(rng.integers(len(MIXES)))]))
        world = make(mix_a, mix_b, rng)
        opponent = opponents[int(rng.integers(len(opponents)))]
        while not world.done:
            actions = [[None]*T.N_UNITS, [None]*T.N_UNITS]
            for i in range(T.N_UNITS):
                if not world.alive[0, i]:
                    actions[0][i] = (np.zeros(2), 0, False)
                    continue
                own, enemies = world.observe(0, i)
                rows['own'].append(own)
                rows['enemies'].append(enemies)
                actions[0][i] = T.random_action(rng, enemies) if rng.random() < noise else teacher(own, enemies)
            for i in range(T.N_UNITS):
                actions[1][i] = (np.zeros(2), 0, False) if not world.alive[1, i] else opponent(*world.observe(1, i))
            world.step(actions)
    return {'own': np.array(rows['own']), 'enemies': np.array(rows['enemies'])}


def labels(variant, pool):
    return T.labels(pool, doctrine_scores(variant))
