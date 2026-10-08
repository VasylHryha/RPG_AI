"""Streaming mechanism counts. Landed enemy shells include zero-hit shells."""
import collections
import gzip
import json


def measure(path):
    initial = latest = terminal = None
    shells = []
    dodges = 0
    unassigned = 0.0
    with gzip.open(path,'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if row.get('observerV1'):
                if initial is None:
                    if row['step'] != 0:
                        raise RuntimeError('missing initial observer')
                    initial = row['units']
                latest = row['units']
                dodges += sum(d[1] == 0 for d in row['dodges'])
                for launch in row['launches']:
                    if not launch[9]:
                        shells.append(dict(source=launch[0],team=launch[2],at=launch[6],targets=set(),damage=0.0))
                for damage in row['damage']:
                    if damage['sourceTeam'] != 1 or damage['targetTeam'] != 0 or damage['sourceRole'] != 'artillery' or damage['dealt'] <= 0:
                        continue
                    candidates = [s for s in shells if s['source']==damage['source'] and
                                  -1e-8 <= damage['t']-s['at'] <= 1/30+1e-7]
                    if len(candidates)>1:
                        raise RuntimeError('ambiguous shell attribution; preserve streams and investigate')
                    if candidates:
                        candidates[0]['targets'].add(damage['target'])
                        candidates[0]['damage'] += damage['dealt']
                    else:
                        unassigned += damage['dealt']
            elif 'survivors' in row:
                terminal = row
            else:
                raise RuntimeError('unexpected heavy or malformed stream row')
    if initial is None or terminal is None:
        raise RuntimeError('incomplete observer fight')
    landed = [s for s in shells if s['team']==1 and s['at']<=terminal['t']+1e-8]
    hits = sum(len(s['targets']) for s in landed)
    dealt = sum(s['damage'] for s in landed)
    stats = dict(win=terminal['enemySurvivors']==0 and terminal['survivors']>0 and terminal['t']<150,
                 timeout=terminal['t']>=150, own_initial=sum(u[1]==0 for u in initial),
                 own_lost=sum(u[1]==0 for u in initial)-terminal['survivors'],
                 t_end=terminal['t'], own_dodges=dodges, enemy_shells_landed=len(landed),
                 own_shell_hit_units=hits, enemy_shell_damage=dealt,
                 own_units_hit_per_enemy_shell=hits/len(landed) if landed else None,
                 damage_taken_per_enemy_shell=dealt/len(landed) if landed else None,
                 unassigned_enemy_artillery_damage=unassigned,
                 enemy_shells_unresolved=sum(s['team']==1 and s['at']>terminal['t']+1e-8 for s in shells))
    survivors = [dict(id=u[0],role=('melee','ranged','artillery')[u[2]]) for u in latest if u[1]==0]
    if len(survivors)!=terminal['survivors']:
        raise RuntimeError('survivor identity/count drift')
    return stats,survivors


def average(values):
    values = [v for v in values if v is not None]
    return dict(n=len(values),mean=sum(values)/len(values) if values else None)


def summarize(records):
    stats = [r['stats'] for r in records]
    shells = sum(s['enemy_shells_landed'] for s in stats)
    return dict(n=len(stats), wins=sum(s['win'] for s in stats),
                own_losses_on_wins=average([s['own_lost'] for s in stats if s['win']]),
                own_losses_on_nonwins=average([s['own_lost'] for s in stats if not s['win']]),
                dodges_per_fight=average([s['own_dodges'] for s in stats]),
                enemy_shells_landed=shells,
                hit_units=sum(s['own_shell_hit_units'] for s in stats),
                shell_damage=sum(s['enemy_shell_damage'] for s in stats),
                own_units_hit_per_landed_enemy_shell=sum(s['own_shell_hit_units'] for s in stats)/shells if shells else None,
                damage_taken_per_landed_enemy_shell=sum(s['enemy_shell_damage'] for s in stats)/shells if shells else None,
                unassigned_enemy_artillery_damage=sum(s['unassigned_enemy_artillery_damage'] for s in stats),
                unresolved_enemy_shells=sum(s['enemy_shells_unresolved'] for s in stats))


def paired(records, key='pair'):
    pairs = collections.defaultdict(dict)
    for record in records:
        arm = record['meta']['arm']
        index = record['meta'][key]
        if arm in pairs[index]:
            raise RuntimeError('duplicate paired cell')
        pairs[index][arm] = record['stats']
    matched = [p for p in pairs.values() if len(p)==2]
    fields = ('win','own_lost','own_dodges','own_units_hit_per_enemy_shell','damage_taken_per_enemy_shell')
    return dict(n=len(matched), unmatched_pairs=sum(len(p)!=2 for p in pairs.values()),
                direction='forcedP16+react minus forcedP16',
                differences={field:average([float(p['forcedP16+react'][field])-float(p['forcedP16'][field])
                                           for p in matched if p['forcedP16+react'][field] is not None and p['forcedP16'][field] is not None])
                             for field in fields})
