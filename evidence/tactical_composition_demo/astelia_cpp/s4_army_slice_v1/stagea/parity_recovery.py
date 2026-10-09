"""Logged near-tie recovery; preserve failed parity and every trained artifact."""
import argparse
from common import CPP, HERE, LOCAL, read, sha, sources, write
from parmem_recovery import ALLOWED, RECOVERY as MEMORY_RECOVERY, verify_baseline
from parity import PARITY_RULE

RECOVERY=HERE/'RECOVERY_STAGEA_PARTIE.json'
FAILURE=HERE/'PARITY_RUN_5838d7b675e8dc7e.json'
FAILED_PROOF=LOCAL/'parity/N2J0_validation_0083.receipt.json'
ALLOWED_CHANGES=('parity.py','readout.py','parmem_recovery.py','parity_recovery.py',
                 'test_stagea_partie.py','test_stagea_partie_host.py')

def validate_previous():
    previous=read(MEMORY_RECOVERY)
    budget,current,_=verify_baseline(previous['baseline'],ALLOWED+ALLOWED_CHANGES)
    now=sources();old=previous['sources']
    delta={k for k in old.keys()|now.keys() if old.get(k)!=now.get(k)}
    allowed={str((HERE/n).relative_to(CPP)) for n in ALLOWED_CHANGES}
    if not delta or not delta<=allowed:raise RuntimeError('near-tie recovery unauthorized source changes')
    failure=read(FAILURE);proof=read(FAILED_PROOF)
    build_before=previous['binary'];build_after=current
    build_delta={k for k in build_before['sources'].keys()|build_after['sources'].keys()
                 if build_before['sources'].get(k)!=build_after['sources'].get(k)}
    if (not build_delta<=allowed or
            any(build_before[k]!=build_after[k] for k in ('binary_sha256','engine','scope','sanitized','portable'))):
        raise RuntimeError('near-tie recovery native build identity drift')
    expected=dict(binary=build_before,budget_sha256=sha(LOCAL/'TRAIN_BUDGET.json'),
                  index_sha256=sha(LOCAL/'INDEX.json'),exports=failure['manifest']['exports'])
    if (previous['status']!='REGISTERED_INFERENCE_ONLY_NO_RETRY' or
            previous['budget_sha256']!=expected['budget_sha256'] or previous['index_sha256']!=expected['index_sha256'] or
            previous['failure_sha256']!=sha(HERE/'PARITY_RUN_c7136052e0485bba.json') or
            failure['status']!='STOP_RESUMABLE' or failure['error']!='RuntimeError: categorical/numeric export parity defect' or
            failure['manifest']!=expected or proof['manifest']!=expected or proof['status']!='FAIL' or
            proof['arm']!='N2J0' or proof['fight']!='validation_0083' or
            proof['native_float64']['categorical_mismatches']!=0 or proof['native_float64']['max_abs_error']>1e-8 or
            proof['float32_export']['categorical_mismatches']!=1):
        raise RuntimeError('near-tie recovery failed baseline identity mismatch')
    return budget,current,sorted(delta)

def checked():
    note=read(RECOVERY)
    budget,current,delta=validate_previous()
    if (note['status']!='REGISTERED_INFERENCE_ONLY_RERUN_ALL_ARMS' or note['sources']!=sources() or
            note['binary']!=current or note['changed_sources']!=delta or note['parity_rule']!=PARITY_RULE):
        raise RuntimeError('near-tie recovery registration drift')
    for name,digest in note['preserved'].items():
        if sha(HERE/name)!=digest:raise RuntimeError('near-tie recovery preserved evidence drift: '+name)
    return budget

def register():
    from jobs import locked
    with locked():
        if RECOVERY.exists():return checked()
        budget,current,delta=validate_previous()
        # Keep all old per-fight receipts, including successful old-rule records.
        preserved={str(p.relative_to(HERE)):sha(p) for p in (MEMORY_RECOVERY,FAILURE,*sorted((LOCAL/'parity').glob('*.receipt.json')))}
        write(RECOVERY,dict(status='REGISTERED_INFERENCE_ONLY_RERUN_ALL_ARMS',
            reason='Owner requested certified float32 near-ties; decision 0036; no fitting or export changes',
            scope='Rerun every arm on every validation fight into parity/certified_near_tie_v1; old receipts unchanged',
            parity_rule=PARITY_RULE,sources=sources(),binary=current,changed_sources=delta,preserved=preserved),exclusive=True)
        return checked()

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    register()
    print('Near-tie recovery registered; all arms must rerun parity; trained artifacts unchanged.')
