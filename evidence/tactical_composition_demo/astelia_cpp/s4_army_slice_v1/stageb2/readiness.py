"""Prospective fixed teacher-level rule from decision 0040; never outcome tuned."""
RULE=dict(version='0040_v1',win_share_ratio=.9,own_deaths_margin=3,looks=[20,50],panels=['regular','C3'],zero_teacher_wins='NO: teacher comparison has no positive win denominator',confirmation='same ledger/checkpoint must pass both look 20 and look 50')

def evaluate(rows,look,arms):
    checks=[]
    for panel in RULE['panels']:
        reference={r['pair_key']:r for r in rows if r['panel']==panel and r['arm']=='T'}
        for arm in arms:
            part=[r for r in rows if r['panel']==panel and r['arm']==arm]
            keys=[r['pair_key'] for r in part]
            paired=(len(reference)==len(part)==look and len(set(keys))==look and set(keys)==set(reference)
                    and all((r['seed'],r['orientation'],r['tactic'])==(reference[r['pair_key']]['seed'],reference[r['pair_key']]['orientation'],reference[r['pair_key']]['tactic']) for r in part))
            wins=sum(r['stats']['win'] for r in part)/len(part) if part else None
            tw=sum(r['stats']['win'] for r in reference.values())/len(reference) if reference else None
            deaths=sum(r['stats']['own_deaths'] for r in part)/len(part) if part else None
            td=sum(r['stats']['own_deaths'] for r in reference.values())/len(reference) if reference else None
            passed=paired and tw>0 and wins>=RULE['win_share_ratio']*tw and deaths<=td+RULE['own_deaths_margin']
            checks.append(dict(panel=panel,arm=arm,paired_complete=paired,win_share=wins,teacher_win_share=tw,own_deaths_per_fight=deaths,teacher_own_deaths_per_fight=td,READY='YES' if passed else 'NO'))
    return dict(rule=RULE,look=look,READY='YES' if all(c['READY']=='YES' for c in checks) else 'NO',per_arm={a:'YES' if all(c['READY']=='YES' for c in checks if c['arm']==a) else 'NO' for a in arms},checks=checks,confirmed=False)
