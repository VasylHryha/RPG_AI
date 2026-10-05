"""Claude's cross-family review of the typed C++ port: is it the same game IN DISTRIBUTION as the frozen JS?

Whole-fight equality was relaxed by the owner-approved revision-2 plan, so the review compares outcome distributions. For each (player profile, opponent
setting) cell, both engines play the same fight requests: 19 pool opponents x review seeds x both sides. The script compares the mean margin
(survivors - enemySurvivors) and the win rate, and checks that the ladder order is the same. Requests are identical for both engines; outcomes are not paired,
since fights are chaotic and are expected to diverge individually.

  python3 equiv.py <out_dir> [js_workers]
"""
import json, math, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CPP_DIR = os.path.join(HERE, '..', 'astelia_cpp')
JS_HOST = ['node', os.path.join(CPP_DIR, 'js_host.cjs')]
NATIVE = [os.path.join(CPP_DIR, 'build', 'astelia_native')]
SEEDS = [701, 702, 703, 704]   # review seeds: never used by runs 1-5 (selection 101-102, confirmation 301-303)

catalog = json.loads(subprocess.run(JS_HOST + ['--catalog'], capture_output=True, text=True, check=True).stdout)
POOL, LEVELS = catalog['POOL'], catalog['LEVELS']
run4 = json.load(open(os.path.join(HERE, '..', 'astelia_compose', 'dev', 'run4_seq_twostep.json')))
PLAYERS = {'novice': {'level': 'novice'}, 'regular': {'level': 'regular'}, 'veteran': {'level': 'veteran'}, 'elite-fast': {'level': 'elite-fast'},
           'run4-best': run4['final']['profile']}
ELITE_NO_ROLLOUT = {'skills': {k: v for k, v in LEVELS['elite']['skills'].items() if k != 'artyRollout'}}
SETTINGS = {'pool-defaults': {}, 'elite-no-rollout': ELITE_NO_ROLLOUT}


def requests():
    out = []
    for setting, enemy in SETTINGS.items():
        for name, prof in PLAYERS.items():
            for opp in POOL:
                for seed in SEEDS:
                    for swap in (False, True):
                        out.append({'mode': 'reactive', 'opponent': opp, '_cell': [name, setting],
                                    'options': {'seed': seed, 'scenario': 'mirror', 'duration': 150, 'abilities': True, 'swapSides': swap, 'rules': 'game', 'ai': [prof, enemy]}})
    return out


def run_engine(cmd, reqs, workers):
    chunks = [reqs[i::workers] for i in range(workers)]

    def one(chunk):
        body = ''.join(json.dumps({k: v for k, v in r.items() if k != '_cell'}) + '\n' for r in chunk)
        res = subprocess.run(cmd, input=body, capture_output=True, text=True, check=True).stdout.strip().split('\n')
        assert len(res) == len(chunk), (len(res), len(chunk))
        return [(r['_cell'], json.loads(x)) for r, x in zip(chunk, res)]
    t0 = time.time()
    with ThreadPoolExecutor(workers) as ex:
        out = [x for part in ex.map(one, chunks) for x in part]
    return out, time.time() - t0


def stats(rows):
    ms = [r['survivors'] - r['enemySurvivors'] for r in rows if 'error' not in r]
    wins = [1 if r['enemySurvivors'] == 0 and r['survivors'] > 0 else 0 for r in rows if 'error' not in r]
    n = len(ms); m = sum(ms) / n; var = sum((x - m) ** 2 for x in ms) / (n - 1)
    return {'n': n, 'errors': len(rows) - n, 'margin': m, 'margin_var': var, 'won': sum(wins) / n}


def main():
    out_dir, js_workers = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 6
    os.makedirs(out_dir, exist_ok=False)
    reqs = requests()
    res, rep = {}, {'seeds': SEEDS, 'players': PLAYERS, 'settings': SETTINGS, 'n_requests': len(reqs), 'load_before': os.getloadavg()}
    for eng, cmd, w in (('cpp', NATIVE, 4), ('js', JS_HOST, js_workers)):
        rows, secs = run_engine(cmd, reqs, w)
        res[eng] = rows
        rep[f'{eng}_seconds'] = secs; rep[f'{eng}_workers'] = w
        with open(os.path.join(out_dir, f'{eng}_results.jsonl'), 'w') as f:
            for cell, r in rows: f.write(json.dumps({'cell': cell, 'result': r}) + '\n')
        print(eng, 'done', round(secs, 1), 's', flush=True)
    cells = {}
    for eng in ('js', 'cpp'):
        for cell, r in res[eng]: cells.setdefault(tuple(cell), {}).setdefault(eng, []).append(r)
    table = []
    for (name, setting), d in sorted(cells.items(), key=lambda x: (x[0][1], x[0][0])):
        a, b = stats(d['js']), stats(d['cpp'])
        diff = b['margin'] - a['margin']; se = math.sqrt(a['margin_var'] / a['n'] + b['margin_var'] / b['n'])
        table.append({'player': name, 'setting': setting, 'js': a, 'cpp': b, 'margin_diff': diff, 'se': se, 'z': diff / se if se else 0.0, 'won_diff': b['won'] - a['won']})
    rep['cells'] = table
    for setting in SETTINGS:
        rows = [t for t in table if t['setting'] == setting]
        rep[f'order_{setting}'] = {'js': [t['player'] for t in sorted(rows, key=lambda t: -t['js']['margin'])], 'cpp': [t['player'] for t in sorted(rows, key=lambda t: -t['cpp']['margin'])]}
    rep['load_after'] = os.getloadavg()
    json.dump(rep, open(os.path.join(out_dir, 'equivalence.json'), 'w'), indent=1)
    print(f"{'setting':18} {'player':11} {'JS margin':>9} {'C++ margin':>10} {'diff':>6} {'se':>5} {'z':>5} {'JS won':>6} {'C++ won':>7} {'err js/cpp':>10}")
    for t in table:
        print(f"{t['setting']:18} {t['player']:11} {t['js']['margin']:9.2f} {t['cpp']['margin']:10.2f} {t['margin_diff']:6.2f} {t['se']:5.2f} {t['z']:5.1f} {t['js']['won']:6.3f} {t['cpp']['won']:7.3f} {t['js']['errors']:>4}/{t['cpp']['errors']}")
    for s in SETTINGS: print('order', s, 'JS:', rep[f'order_{s}']['js'], 'C++:', rep[f'order_{s}']['cpp'])


if __name__ == '__main__':
    main()
