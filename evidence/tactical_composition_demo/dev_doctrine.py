"""DEVELOPMENT record for the change-cost test, not the experiment: choose the changed targeting doctrine with a rule fixed in advance.

Candidates (weights of enemy damage, missing health, in range, distance): a (1.0, 0.5, 0.4, 0.04), b (2.0, 0.3, 0.3, 0.02), c (3.0, 0.2, 0.2, 0.01),
d (4.0, 0.1, 0.0, 0.0). Rule: take the weakest change, the candidate with the highest TIE-AWARE agreement with the current doctrine's target choice
(the current doctrine's chosen enemy is among the new doctrine's tied-best) on states with more than one living enemy, among those with agreement <= 0.70,
average win score against rush and the kiter at least the current doctrine's minus 0.08, and at least the rush baseline's plus 0.15 (seen mixes, 300
episodes per cell, pool of 150 episodes). The tie share of the chosen candidate is reported (a doctrine of damage and health has exact ties between
same-type enemies, which is why agreement is tie-aware; a tie-free variant, 'back line first', changed 64% of decisions but played 0.116 worse and
was not eligible). Own development
entropy, separate from every recorded run. No controller is learned here. An earlier inline look at the same candidates (before this record) found
agreements 0.82 (a), 0.78 (b), 0.76 (c), 0.55 (d), which is why the 0.70 cut was chosen; this file is the formal pass."""
import json
import secrets
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402

entropy = secrets.randbits(96)
rng = lambda *key: np.random.default_rng(np.random.SeedSequence([entropy, *key]))
CANDIDATES = {'a': (1.0, 0.5, 0.4, 0.04), 'b': (2.0, 0.3, 0.3, 0.02), 'c': (3.0, 0.2, 0.2, 0.01), 'd': (4.0, 0.1, 0.0, 0.0)}
pool = T.collect(rng(1), 150, T.SEEN_MIXES)
lab = T.labels(pool)
multi = np.array([(e[:, 0] > 0).sum() > 1 for e in pool['enemies']])


def scores_fn(w):
    wd, wh, wr, wdist = w
    return lambda own, en: np.where(en[:, 0] > 0, wd*en[:, 6]/10.0+wh*(1-en[:, 4])+wr*(en[:, 3] <= own[2])-wdist*en[:, 3], -9.0)


def policy_for(fn):
    def policy(own, en):
        t = int(np.argmax(fn(own, en)))
        return T.teacher_move(en[t, 1:3], own[4]), t, False
    return policy


def average_score(policy, k):
    return float(np.mean([T.win_score(policy, T.SEEN_MIXES, opp, rng(2, k, i), 300) for i, opp in enumerate((T.rush_policy, T.kiter_policy))]))


base, rush = average_score(T.teacher_policy, 0), average_score(T.rush_policy, 0)
out = {'dev_entropy': entropy, 'teacher1_average_score': base, 'rush_average_score': rush, 'candidates': {}}
for k, (name, w) in enumerate(CANDIDATES.items()):
    fn = scores_fn(w)
    sc = np.array([fn(o, e) for o, e in zip(pool['own'], pool['enemies'])])
    alive = pool['enemies'][:, :, 0] > 0
    best = np.where(alive, sc, -np.inf).max(1)
    agreement = float(np.mean((sc[np.arange(len(sc)), lab['target']] >= best-1e-9)[multi]))
    tie_share = float(np.mean((((np.where(alive, sc, -np.inf) >= best[:, None]-1e-9) & alive).sum(1) > 1)[multi]))
    score = average_score(policy_for(fn), 0)
    ok = bool(agreement <= 0.70 and score >= base-0.08 and score >= rush+0.15)
    out['candidates'][name] = {'weights': w, 'agreement_with_current_doctrine_tie_aware': agreement, 'tie_share_multi_enemy_states': tie_share, 'average_win_score': score, 'meets_rule': ok}
    print(name, w, 'agreement %.3f tie share %.3f score %.3f meets %s' % (agreement, tie_share, score, ok))
eligible = [n for n, v in out['candidates'].items() if v['meets_rule']]
out['chosen'] = max(eligible, key=lambda n: out['candidates'][n]['agreement_with_current_doctrine_tie_aware']) if eligible else None
out['matches_code_constant'] = bool(out['chosen'] and tuple(CANDIDATES[out['chosen']]) == tuple(T.DOCTRINE2))
print('teacher1 %.3f rush %.3f chosen %s matches code constant %s' % (base, rush, out['chosen'], out['matches_code_constant']))
(HERE/'dev_doctrine.json').write_text(json.dumps(out, indent=1, sort_keys=True))
