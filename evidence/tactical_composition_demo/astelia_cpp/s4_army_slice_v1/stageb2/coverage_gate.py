"""Declared B2 availability gate; fixed before any corrected-revision timing."""
from owner_approvals import load
THRESHOLDS=load()['coverage']['thresholds']
STRUCTURALLY_EMPTY=load()['coverage']['structurally_empty']
CAUSE='Reject vocabulary-limited fits: at least 90% ordinary/all labels and 80% O-dodge labels must have nearby candidates and fit bounded residuals, separately per role/head/arm. These are development admission floors, not measured success or teacher acceptance.'

def admission(receipt,arms):
    cfg=load()['coverage'];thresholds=cfg['thresholds'];empty=cfg['structurally_empty']
    checks=[]
    for arm in arms:
        table=receipt['fit_target_coverage'].get('train:'+arm,{})
        for role in ('melee','ranged','artillery'):
            for head in (('move','aim') if role=='artillery' else ('move',)):
                for category,threshold in thresholds.items():
                    key=f'{role}:{head}:{category}';value=table.get(key,{})
                    for metric in ('coverage','bounded_residual_coverage'):
                        observed=value.get(metric);rows=value.get('rows',0)
                        # Claude 2026-10-09: artillery aim during O dodge is structurally empty (react vetoes
                        # release, so no aim label exists); a 0-row stratum there is not applicable, not a failure.
                        if rows==0 and key in empty:
                            checks.append(dict(arm=arm,key=key,metric=metric,rows=0,value=None,threshold=threshold,passed=True,not_applicable=empty[key]));continue
                        passed=rows>0 and observed is not None and observed>=threshold and value.get('no_candidates',0)==0
                        checks.append(dict(arm=arm,key=key,metric=metric,rows=rows,value=observed,threshold=threshold,passed=passed))
    failed=[c for c in checks if not c['passed']]
    return dict(passed=not failed,thresholds=thresholds,cause=CAUSE,checks=checks,failed=failed)

def require(receipt,arms):
    result=admission(receipt,arms)
    if not result['passed']:
        detail='; '.join(f"{c['arm']}:{c['key']}:{c['metric']}={c['value']} ({c['rows']} rows), requires {c['threshold']}" for c in result['failed'])
        raise RuntimeError('B2 coverage admission refused: '+detail)
    return result
