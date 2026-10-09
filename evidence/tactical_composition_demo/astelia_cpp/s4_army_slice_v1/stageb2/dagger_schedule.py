"""Prospectively sealed 5-10-round mixture and optional measured DART noise."""
from owner_approvals import load,snapshot

def declared():
    cfg=load()['dagger'];n=cfg['rounds']
    return dict(rounds=n,teacher_driving_share=[.5*(n-i)/(n-1) for i in range(1,n+1)],mixing='whole-fight Bernoulli, paired seed-derived draw shared by all arms; student physical-tick state evolves even in teacher-driven fights',dart=cfg['dart'],per_round_check='complete student-only paired look 20 after refit/parity, before collecting the next round',owner_approvals=snapshot())

def seal(r):
    path=r.LOCAL/'DAGGER_SCHEDULE.json'
    if path.exists():return r.read(path)
    value=declared();r.write(path,value,exclusive=True);return value

def round_check(r,round):
    if round<=1:return
    path=r.LOCAL/f'LOOK_STAGEB2_R{round-1}_20.json';proof=r.read(path)
    if not proof.get('complete') or proof.get('round')!=round-1 or proof.get('look')!=20 or proof.get('harm_stop'):
        raise RuntimeError('previous round real-fight check required')
    if proof['ledger_sha256']!=r.sha(r.LOCAL/f'OUTCOME_LEDGER_ROUND{round-1}.json'):
        raise RuntimeError('round real-fight check ledger drift')
    ledger=r.read(r.LOCAL/f'OUTCOME_LEDGER_ROUND{round-1}.json')
    if ledger['sources']!=r.sources() or ledger['binary']!=r.collect.identity() or ledger['parity_sha256']!=r.sha(r.LOCAL/f'round{round-1}/PARITY_STAGEB2.json'):
        raise RuntimeError('round real-fight check source/binary/parity drift')
    expected={j['tag'] for j in ledger['jobs'] if j['index']<20}
    records=proof['report'].get('completion_hashes',{})
    if set(records)!=expected:raise RuntimeError('round real-fight check completion coverage')
    jobs={j['tag']:j for j in ledger['jobs'] if j['index']<20}
    for tag,digest in records.items():
        path=r.LOCAL/'raw'/(tag+'_COMPLETE.json')
        if r.sha(path)!=digest:raise RuntimeError('round check completion drift')
        completion=r.read(path)
        if completion['status']!='DONE' or completion['job']!=jobs[tag] or completion['ledger_sha256']!=proof['ledger_sha256']:
            raise RuntimeError('round check completed job identity')
        if r.sha(r.LOCAL/completion['raw_file'])!=completion['raw_sha256']:
            raise RuntimeError('round check outcome raw drift')
