"""Construct and check entropy reservations without executing a fixture or world."""
import hashlib
import json
from pathlib import Path
from .rev7_protocol import seed,donor_entries,training_episode,TASKS
from .protocol import canonical

HERE=Path(__file__).parent
EARLIER=(HERE/'REV6_SEED_INVENTORY.json',HERE/'rev6_history/SPECIFICATION_STOP_SEEDS.json',HERE/'rev6_history/REV65_PRE_REPAIR_SEEDS.json',HERE/'fixture_run_20261006/PRE_EXECUTION_SEED_INVENTORY.json')


def construct():
    prior=json.loads(EARLIER[0].read_text())
    # The inherited consumer table is instantiated, including domains reserved
    # but unused by the empty start. No PCG64 instance is advanced here.
    keys=[]
    for key in prior['seed_inventory']:
        pieces=key.split('/')
        if pieces[0] in ('random_policy','lesion'):pieces[-1]=str(int(pieces[-1])+10000000)
        keys.append('/'.join(pieces))
    values={key:seed(key) for key in keys}
    pools={}
    for arm in ('task_blind','reward'):
        for k in range(8):pools[f'training/{arm}/{k}']=dict(namespace='dev',ids=[training_episode(arm,k,e) for e in range(2000)])
    for name,namespace,first,last in [('recipients','validation',10000512,10000639),('donors','validation',10000640,10000767),('F5_assays','validation',10000768,10000787),('F6','validation',10000788,10000807),('F9_scenario_ids','validation',10000808,10000811),('F5_growth','dev',12000000,12000049),('F8','dev',12100000,12100039)]:
        pools[name]=dict(namespace=namespace,ids=list(range(first,last+1)))
    result=dict(version='rev7_inventory_v1',status='PRE_EXECUTION_INVENTORY_ONLY',fixture_execution='NOT_RUN',development_execution='NOT_RUN',evaluation_result_exists=False,
        seed_recipe='uint64(first 8 bytes big-endian SHA256(ASCII("0h-rev7/" + key)))',recovery_recipe='default_rng(uint64(first 8 bytes little-endian SHA256(ASCII(decimal(master)+":kick:"+decimal(index)))))',
        seed_inventory=values,world_pools=pools,donor_permutation=donor_entries(),F5_pairs=[dict(recipient=10000768+j,donor=10000778+j) for j in range(10)],F6_pairs=[dict(recipient=10000788+j,donor=10000798+j) for j in range(10)],
        deterministic_no_entropy=['N1','F1','F2','F3','F4 literal/stage portions'],
        reused=[dict(use='calibration',namespace='validation',ids=list(range(256)),label='REUSED_5_1_CALIBRATION_UNCHANGED'),dict(use='historical_5_1_reference_only',namespace='dev',ids=list(range(2000)))],
        sharing='intact/M/U share world ids and bindings; own/donor/lesion share immutable checkpoint; master streams distinct',
        empty_start_medium_keys='reserved for compatibility with consumer table; no initial-state draw',
        earlier_inventory_sha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in EARLIER})
    result['disjointness']=check_disjoint(result)
    return result


def check_disjoint(value):
    new={}
    for name,pool in value['world_pools'].items():
        for id in pool['ids']:
            pair=(pool['namespace'],id)
            if pair in new:raise ValueError(f'new inventory overlap: {name} / {new[pair]}')
            new[pair]=name
    seeds=set(value['seed_inventory'].values())
    if len(seeds)!=len(value['seed_inventory']):raise ValueError('new master seed collision')
    checked=[]
    for path in EARLIER:
        expected=value['earlier_inventory_sha256'].get(str(path.relative_to(HERE)))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('historical inventory identity changed')
        old=json.loads(path.read_text());old_seeds=set(old.get('seed_inventory',{}).values())
        if seeds&old_seeds:raise ValueError('historical seed collision')
        pools=old.get('world_panels',{})
        for name,pool in pools.items():
            if 'range' in pool:
                first,last=pool['range'];namespace=pool['namespace']
                if any((namespace,id) in new for id in range(first,last+1)):raise ValueError('historical world overlap')
        for slot in old.get('training_slots',[]):
            if any((slot['namespace'],id) in new for id in range(slot['first_episode'],slot['last_episode']+1)):raise ValueError('historical training overlap')
        checked.append(str(path.relative_to(HERE)))
    if any(('validation',id) in new for id in range(256)) or any(('dev',id) in new for id in range(2000)):raise ValueError('5.1 reuse overlap')
    return dict(status='DISJOINT',earlier_inventories=checked,world_id_count=len(new),master_seed_count=len(seeds),reuse_excluded=['calibration','historical_5_1_reference_only'])


def write(path=None):
    value=construct();data=canonical(value)+b'\n';target=path or HERE/'REV7_SEED_INVENTORY.json';Path(target).write_bytes(data)
    return dict(path=str(target),sha256=hashlib.sha256(data).hexdigest(),disjointness=value['disjointness'])

if __name__=='__main__':print(json.dumps(write(),indent=2))
