"""Complete future 48-training orchestration. No run is started on import/CLI."""
from .rev6_run import Run
from .rev6_evaluator import reused_calibration
from .rev6_protocol import aggregate,paired_bounds,stops


def seed_unit(intact,control):
    panel=intact.final_panel
    return dict(complete=intact.complete and control.complete,invalid=intact.invalid or control.invalid,
        perceive_usable=intact.rows['perceive'].usable,
        eligible=len(intact.coverage_samples),control_eligible=len(control.coverage_samples),
        coverage=sum(intact.coverage_samples)/len(intact.coverage_samples) if intact.coverage_samples else None,
        control_coverage=sum(control.coverage_samples)/len(control.coverage_samples) if control.coverage_samples else None,
        matched=not control.queue.unmatched,
        matching_slots=control.queue.slots,
        g0=paired_bounds(panel['perceive']['intact'],control.final_panel['perceive']['intact']),
        descriptive_comparators={t:v.get('descriptive_comparators',{}) for t,v in panel.items()},
        bounds={t:v['bounds'] for t,v in panel.items()},late=intact.report()['late'],
        identity_snapshot=intact.identity_snapshot,snapshots=len(intact.snapshots),g5=[v['G5_D'] for v in intact.evaluations])


def run_development(execution,*,output,rows=None,backend='native',on_seed=None):
    identity_snapshot=execution.start('development')
    from pathlib import Path
    output=Path(output).resolve()
    if Path(__file__).resolve().parents[1] not in output.parents:raise ValueError('development ledgers must stay in growing_shapes')
    output.mkdir(parents=True,exist_ok=False)
    rows=rows or reused_calibration()[0]
    if not rows['perceive'].usable:raise ValueError('perceive unusable: G0/G2 blocked, no task substitution')
    arms={}
    for arm in ('task_blind','reward'):
        units=[];reports=[]
        for k in range(8):
            runs={p:Run(k,rows,reward=arm=='reward',policy=p,arm=arm,backend=backend,execution=execution,audit_dir=output/arm/str(k)/p) for p in ('intact','M','U')}
            try:
                for e in range(2000):
                    runs['intact'].episode(e)
                    for p in ('M','U'):runs[p].episode(e,runs['intact'])
                for run in runs.values():run.evaluate()
                units.append(seed_unit(runs['intact'],runs['M']))
                report={p:r.report() for p,r in runs.items()};reports.append(report)
                if on_seed:on_seed(arm,k,report)
            except Exception as error:
                for run in runs.values():run.invalid=f'{type(error).__name__}: {error}'
                return dict(status='INVALID',arm=arm,k=k,reason=str(error),raw={p:r.report() for p,r in runs.items()},completed=arms)
            finally:
                for run in runs.values():run.close()
        outcomes=aggregate(units)
        stop=stops(dict(readout_invalid=any(v=='INVALID' for v in outcomes.values()),
                        task_blind_G1_fail=arm=='task_blind' and outcomes['G1']=='FAIL',G0prime_fail=outcomes["G0'"]=='FAIL',G2_fail_or_inconclusive=outcomes['G2'] in ('FAIL','INCONCLUSIVE')))
        arms[arm]=dict(identity_snapshot=identity_snapshot,units=units,readouts=outcomes,reports=reports,stops=stop)
        if stop:return dict(status='STOP',arms=arms)
    return dict(status='COMPLETE_DEVELOPMENT_ONLY',arms=arms)
