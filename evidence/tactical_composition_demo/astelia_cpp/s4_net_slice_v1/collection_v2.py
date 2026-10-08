"""New collection namespace, with legacy process/resource/crash guards preserved.

Explicit host commands only. No import-time entropy allocation or execution.
"""
from pathlib import Path
import collection as legacy
from requests_v2 import drill
from stage1_uniqueness import gate, state_hash

# Load the historical orchestration into an isolated namespace. Function globals
# bind the v2 root/generator/admission below; no legacy globals are mutated.
exec(compile((Path(__file__).with_name('collection.py')).read_text().replace('used=set(range(10000));rows=[];seen=Counter()', 'used=set(range(10000)) | legacy_seeds();rows=[];seen=Counter()'),
             str(Path(__file__).with_name('collection.py')), 'exec'),
     namespace := {'__name__':'_collection_v2_core','__file__':legacy.__file__})
namespace['ROOT']=ROOT=legacy.HERE/'_local/collection_v2'
def legacy_seeds():
    path=legacy.ROOT/'INVENTORY.json'
    return {r['seed'] for r in read(path)['rows']} if path.exists() else set()

namespace['legacy_seeds']=legacy_seeds
namespace['drill']=drill
HERE=legacy.HERE
read,sha,atomic=legacy.read,legacy.sha,legacy.atomic
original_inventory=namespace['inventory']


def inventory(*args,**kwargs):
    inv=original_inventory(*args,**kwargs)
    inv['version']='NS1-collection-2'
    return inv


def admission():
    pins=legacy.admission()
    pins.update({n:sha(HERE/n) for n in ('collection_v2.py','requests_v2.py','stage1_uniqueness.py','CONTRACT_AMENDMENT_STAGE1_V2.md')})
    return pins


def uniqueness(inv,sample=False):
    rows=[]
    for row in inv['rows']:
        if sample and not row['sample']:
            continue
        receipt=namespace['completed'](row)
        if receipt is None:
            raise RuntimeError('uniqueness requires complete requested collection')
        rows.append(dict(cell=row['cell'],guns=row['guns'],orientation=row['orientation'],
            records=receipt['record_count'],decision_rows=receipt['decision_count'],
            first_k_state_sha256=state_hash(ROOT/(row['group']+'.jsonl'))))
    value=gate(rows)
    path=ROOT/('UNIQUENESS_SAMPLE.json' if sample else 'UNIQUENESS_COLLECTION.json')
    atomic(path,value)
    if value['status']!='PASS':
        raise RuntimeError('collection uniqueness below declared 90% threshold; stop before downstream use')
    return value


namespace.update(inventory=inventory,admission=admission)
admit_inventory=namespace['admit_inventory']
original_sample=namespace['sample_measurements']
original_resource_gate=namespace['resource_gate']
original_run=namespace['run']


def sample_measurements(inv):
    uniqueness(inv,True)
    return original_sample(inv)


def resource_gate(inv):
    uniqueness(inv,True)
    return original_resource_gate(inv)


namespace.update(sample_measurements=sample_measurements,resource_gate=resource_gate)


def run(stage,fights):
    import fcntl
    # Common exclusion lock with historical collection and stage1 jobs; no
    # changes to historical ledger/entropy/inventory/receipts.
    with (legacy.ROOT/'RUN.lock').open('r') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        original_run(stage,fights)
    if stage=='collect':
        uniqueness(admit_inventory())


namespace['run']=run
if __name__=='__main__':
    # The original main routes into the isolated v2 globals.
    namespace['main']()
