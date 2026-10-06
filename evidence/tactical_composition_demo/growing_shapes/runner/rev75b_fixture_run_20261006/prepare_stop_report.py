"""Read existing timing evidence and pin; no fixture, world or entropy execution."""
import ast
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
from execute_once import OUT, ROOT, PIN_DIGEST, REVIEW, APPROVAL, PROVENANCE, digest, write

sys.path.insert(0, str(ROOT))
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs, PIN
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_protocol import STOP_ROWS
from evidence.tactical_composition_demo.growing_shapes.runner.rev7_verify import clocks


def main():
    started = clocks()
    assert digest(PIN) == PIN_DIGEST, 'execution pin mismatch; STOP'
    identity = assert_inputs()
    write(OUT / 'PREFLIGHT_IDENTITY.json', identity)
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    before = {p: digest(ROOT / p) for p in paths if p and (ROOT / p).is_file()}
    old = OUT.parent / 'rev75_fixture_run_20261006'
    historical = {str(p.relative_to(ROOT)): digest(p) for p in old.rglob('*') if p.is_file()}
    write(OUT / 'PRESERVATION_BASELINE.json', dict(tracked=before, previous_attempt=historical,
          staged_diff_sha256=__import__('hashlib').sha256(subprocess.check_output(
              ['git', 'diff', '--cached', '--binary'], cwd=ROOT)).hexdigest(),
          head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()))
    summary = json.loads((old / 'MEASURED_SUMMARY.json').read_text())
    t = summary['results']['F5']['starts']['i']['boundary_elapsed_utc_seconds']
    assert abs(t - 1431.108947) < 1e-6
    prefix = sum(json.loads((old / (n + '_TIMING.json')).read_text())['elapsed_utc_seconds']
                 for n in ('N1', 'F1', 'F2', 'F3', 'F4'))
    workload = dict(N1_RK4_substeps=120000, F1_RK4_substeps=192000,
                    F2_world_frames=320, F3_F4_diagnostic_substeps=40,
                    F4_assay_episodes=10, F5_growth_frames=16000,
                    F5_assay_episodes=180, F5_qualification_starts=24,
                    F6_assay_episodes=140, F7_growth_frames=8000,
                    F8_growth_frames=6400, F8_qualification_starts=10,
                    F9_decoder_observations=4)
    ratios = dict(live_frame_dominant=30400 / 8000,
                  frozen_assay_dominant=320 / 90,
                  qualification_recovery_dominant=34 / 12)
    scenarios = {name: t * ratio + prefix for name, ratio in ratios.items()}
    estimate = max(scenarios.values())
    sources = [old / 'EXECUTION_LOG.txt', old / 'MEASURED_SUMMARY.json',
               old / 'A7_DEVELOPMENT_COST_PROJECTION.json',
               OUT.parent / 'rev7_fixtures.py', OUT.parent / 'rev7_run.py',
               ROOT / APPROVAL, ROOT / REVIEW, PIN]
    estimate_record = dict(revision='7.5', estimate_seconds=estimate,
          scheduling_allowance_seconds=estimate * 1.2, exceeds_one_hour=estimate > 3600,
          qualification='CONSERVATIVE_PLANNING_SCENARIO_NOT_A_MEASURED_TOTAL_OR_BOUND',
          first_start_boundary_elapsed_seconds=t, first_start_component_rates=None,
          first_start_utc=summary['results']['F5']['starts']['i']['start_utc'],
          next_start_boundary_utc=summary['results']['F5']['starts']['i']['next_start_boundary_utc'],
          measured_early_fixture_elapsed_seconds=prefix, workload=workload,
          first_start_workload=dict(live_frames=8000, frozen_assay_episodes=90,
                                    qualification_starts=12), ratios=ratios,
          sensitivity_scenario_seconds=scenarios, margin_fraction=.2,
          method='Allocate the historical composite to an unknown live/assay/qualification mix. Scale by the largest full-sequence workload ratio, then add measured early-fixture costs once. F4 is in the early prefix, so late assays total 320, not 330. No sum of alternative allocations. 20% scheduling allowance is an explicit assumption for setup/persistence/task/population uncertainty.',
          limitations=['Old boundary includes line tracing and transition/cleanup; it is not an isolated method cost.',
                       'No measured no-tracing speedup exists; no arbitrary speedup discount applied.',
                       'Equal per-component rates across starts/tasks/populations are assumptions, not observations.',
                       'Assay allocation includes donor-capture overhead implicitly; no independent donor rate.',
                       'Sensitivity scenarios are neither lower/upper bounds nor statistical confidence intervals.',
                       'Stops may shorten execution; this estimate covers the complete sequence requested.'],
          sources={str(p.relative_to(ROOT)): digest(p) for p in sources})
    write(OUT / 'DURATION_ESTIMATE.json', estimate_record)
    assert estimate_record['exceeds_one_hour'], 'Report assumes the duration stop'
    rows = [dict(question=q, outcome='NO' if q in ('integration_not_tested_reviewed',
                'source_unit_endpoint_mismatch', 'engines_not_ready_reviewed',
                'protocol_changed_after_results') else 'NOT_EVALUATED', action=a, role=r)
            for q, a, r in STOP_ROWS]
    rows.insert(0, dict(question='Does the complete fixture estimate exceed one hour?',
                       outcome='YES', action='Stop before real fixtures; report estimate',
                       role='implementer', authority='Current explicit owner instruction'))
    write(OUT / 'STOP_ROW_OUTCOMES.json', rows)
    write(OUT / 'PRE_EXECUTION_STOP.json', dict(verdict='INVALID',
          fixture_execution='NOT_RUN', fixture_execution_count=0,
          reason='Explicit duration gate: complete-run estimate exceeds one hour',
          pin_sha256=PIN_DIGEST, scientific_inputs_checked=len(identity['sha256']),
          approval_reference=APPROVAL, integration_review=REVIEW,
          kind='MEASUREMENT_TOOL_RERUN_PREPARATION_ONLY',
          first_attempt_F5_persisted_or_observed=False,
          seed_inventory_claimed_or_consumed=False, provenance=PROVENANCE))
    a7 = json.loads((old / 'A7_DEVELOPMENT_COST_PROJECTION.json').read_text())
    a7.update(status='A7_NOT_QUALIFIED_NO_NEW_FIXTURE_MEASUREMENTS',
              development='NOT_RUN', measurement_source='Historical interrupted revision-7.5 evidence only',
              new_fixture_measurements=None,
              future_execution_estimate='See this attempt DURATION_ESTIMATE.json; explicit owner duration stop',
              source_sha256=digest(old / 'A7_DEVELOPMENT_COST_PROJECTION.json'))
    write(OUT / 'A7_DEVELOPMENT_COST_PROJECTION.json', a7)
    report = ['INVALID', '',
        '**Pre-execution duration stop; every real fixture is NOT_RUN.** This first-line delivery status does not assert a fixture measurement failure or a scientific code defect. No new Harness.run_all receipt exists.', '',
        f'Requested revision 7.5 measurement-tool re-run; execution pin `{PIN_DIGEST}` verified before preparation: all {len(identity["sha256"])} inputs match, including final committed designs and the current configuration/inventory. Execution grant reference = `{APPROVAL}`; integration_review = `{REVIEW}` (READY_FOR_FIXTURES, Claude). The grant was not started. Decision 0031 standing approval is subject to the owner\'s explicit instruction here to stop if the estimate exceeds one hour, regardless of clock time.', '',
        'The earlier rev75_fixture_run_20261006 and REV75_FIXTURE_REPORT.md remain unchanged. That attempt was invalidated by execute_once.py observing a non-executable finally line. F5 results of the first attempt were never persisted or observed; no A/B/E or F5 verdict is inferred. This requested re-run is a measurement-tool correction, not new scientific code, fresh entropy, independent replication or registration.', '',
        f'Complete sequence planning estimate: **{estimate:.6f} s ({estimate / 60:.3f} minutes)**; explicit 20% scheduling allowance **{estimate * 1.2 / 60:.3f} minutes**. The historical first-start transition took {t:.6f} elapsed UTC s ({t / 60:.3f} minutes). Its 8000 live frames, 90 frozen assays and 12 qualification starts are extrapolated against 30400 live frames, 320 late assays and 34 qualification starts. Maximum workload ratio = 3.8; add {prefix:.6f} s of early measured costs once (including F4\'s ten assays). No rehearsal, benchmark or real fixture was run to price this.', '',
        'Alternative single-component allocations, before scheduling allowance: ' + '; '.join(f'{k}: {v / 60:.3f} minutes' for k, v in scenarios.items()) + '. These are arithmetic sensitivity scenarios, not bounds. The historical boundary included line tracing; the new wrapper removes it, but the size of that speedup is unmeasured. Population/task differences, transition cleanup and unknown component costs prevent a qualified prediction. The conservative operational estimate triggers the explicit stop; it does not prove the true untraced execution would exceed an hour.', '',
        'The new execute_once.py uses whole-call timing and calls the unchanged pinned Harness.run_all. It persists every returned field, including both F5 starts, the descriptive qualification summary, all records/events and the exact harness receipt. There are no line or bytecode observation hooks. Individual F1a-c/F5i-ii execution costs are unavailable because they are inline blocks and the harness returns no execution clocks for them; their enclosing calls are timed. F1 contains F1d, so their aggregate clocks must not be summed. test_wrapper_double.py tests fabricated multi-start PASS and FAIL gate returns without importing the scientific harness. Its once-run result is in WRAPPER_SYNTHETIC_CHECK.json.', '',
        '| Fixture | Criterion / quantities required | New measurement | Start UTC / end UTC / awake s / elapsed UTC s |',
        '|---|---|---|---|',
        '| N1a-f | h=.005 vs .00125; wrapped/unwrapped phase differences each ≤.01 rad; free-position difference ≤.01 m.u.; Nθ and Nx agreement ≥.99; pins invariant; applicable entry times agree within .1 s or both absent. Report phase, position, unwrapped, entry, topology and masks. | NOT_RUN; all null | null / null / null / null |',
        '| N1g | Descriptive saddle escape as specified below; no accuracy cut. | NOT_RUN; all null | null / null / null / null |',
        '| F1a/F1b | Entry within .3 rad by t=16 after t=8 step; hold every endpoint through 16; path ≥.8 over 160 s. Report entry/delay, hold, access, direct drive, compaction spans/radii and topology. | NOT_RUN; all null | null / null / null / null |',
        '| F1c | Entry by 16; hold through 24; path and access ≥.8 over 160 s; response persistence ≥.8 over [16,160]; output pin invariant. Report compaction geometry, sustained delay, error at 12 and descriptive 4-second margin. | NOT_RUN; all null | null / null / null / null |',
        '| F1d | Descriptive same F1b at λ=1 vs 8 (also 32), h=.005: entry/delay, hold, deadline error, paths/access, geometry/topology; absent entry is censored. | NOT_RUN; all null | null / null / null / null |',
        '| F2 | Exact zero empty angle/magnitude; no paths; disconnected stepped/unstepped phases bitwise identical for 160 endpoints. | NOT_RUN; all null | null / null / null / null |',
        '| F3 | Output site-drive exactly +0.0 at all 80 RK4 stages. | NOT_RUN; all null | null / null / null / null |',
        '| F4 | Output internal coupling exactly zero at all 80 stages; exact site0/oracle decoder angles; native/reference magnitude/choice/path/output-presence exact, wrapped-angle tolerance 1e-12. | NOT_RUN; all null | null / null / null / null |',
        '| F5(i)/F5(ii) | Pool checkpoints 40/45/50: A≥.3, B≥.3, max(E)≥.5; B-out birth for i, B-path birth for ii. Record both A/B/E, complete B-out/B-path events and not-qualified fractions. | NOT_RUN; all null | null / null / null / null |',
        '| F6 | Descriptive encoding, retention and circular correlations with ≥5 defined pairs; baseline denominator uses unique recipient episodes. | NOT_RUN; all null | null / null / null / null |',
        '| F7 | Every requested control-M B1 birth matched; unmatched=0; fraction null if zero requests. Record requested/matched/unmatched/fraction and events. | NOT_RUN; all null | null / null / null / null |',
        '| F8 | Descriptive live F5(i) move then memory reward/eligibility/B1 demand. | NOT_RUN; all null | null / null / null / null |',
        '| F9 | Four literal descriptive decoder observations; demand and actions. | NOT_RUN; all null | null / null / null / null |', '',
        'N1f coarse/fine F1c hold agreement = NOT_RUN / null; coarse hold=null, fine hold=null. F1c has no new verdict. If measured holds disagree in an authorized later execution, report F1c NUMERICALLY_UNRESOLVED while preserving the harness verdict. Earlier agreement is historical and cannot stand in for this attempt.', '',
        'N1g definition: member 0\'s first endpoint departure ≥0.5 rad from its initial unwrapped carrier-relative phase π; direction is displacement sign; time is first crossing, bracketed by preceding endpoint (initial t=0 if first). At each h=.005/.00125: status, direction, time, preceding-endpoint bracket, departure displacement, final unwrapped phase/displacement and raw records are null / NOT_RUN here. With an actual no-crossing run, status would be NOT_OBSERVED with null direction/time/bracket. DESCRIPTIVE / SENSITIVITY_NOT_ACCURACY / used_in_verdict=False; escape does not mean a completed 2π winding.', '',
        'F5 descriptive not-qualified-window summary: for each start, check-endpoint intervals (0,640], (640,720], (720,800], and whole (0,800] s. Record qualification-window counts, not-qualified invalid-pair counts/fractions and frame counts. All starts including small cohorts stay in denominators; zero denominator gives null; fast-transient frames count once; recovery skips excluded; used_in_verdict=False. Every new value is null because F5 was not started.', '',
        'Required sequence retained in unchanged Harness.run_all: N1 first; FAIL/INVALID blocks all. F1a-c then descriptive F1d; F2-F4 still run after F1 FAIL; any F1-F4 FAIL stops before F5. Then F5 both starts; F5 FAIL stops. Then F6, F7; F7 FAIL stops; then F8, F9. Any fixture INVALID blocks the next stage. This preparation stopped before the sequence, so no scientific stop row was evaluated.', '',
        '| Stop question | Outcome | Yes action | Role |', '|---|---|---|---|']
    report += [f'| {r["question"]} | {r["outcome"]} | {r["action"]} | {r["role"]} |' for r in rows]
    report += ['',
        'A7: no new measured rates. Qualified development total=null / NOT_QUALIFIED. Historical small-scaffold composites retained only as explicitly unqualified arithmetic scenarios: N1 training proxy ' + f'{a7["unqualified_arithmetic_training_hours_N1_proxy"]:.6f} h OR F1 proxy {a7["unqualified_arithmetic_training_hours_F1_proxy"]:.6f} h; mixed F4 all-assay proxy {a7["unqualified_arithmetic_all_assay_hours_F4_proxy"]:.6f} h, including {a7["unqualified_arithmetic_site_body_off_added_hours_F4_proxy"]:.6f} h for the 2048 site-body-off episodes. Do not sum alternatives or count the comparator twice. Grown training/assay, qualification/recovery, B-path and donor-capture rates remain null. No development cost is qualified by the F5 boundary estimate.', '',
        'No real fixtures, training, development, evaluation panels, judging entropy or registration occurred. The scientific code and earlier evidence are unchanged. Review and disposition are tracked beside this attempt under the explicit owner restriction against editing docs/PLAN_CURRENT.md. Commit/bundle outcome and final preservation verification are in REV75B_FIXTURE_DELIVERY_NOTE.md and DELIVERY_VERIFICATION.json.', '', PROVENANCE]
    with (OUT.parent / 'REV75B_FIXTURE_REPORT.md').open('x') as stream:
        stream.write('\n'.join(report) + '\n')
    ended = clocks()
    write(OUT / 'PREPARATION_TIMING.json', dict(start=started, end=ended,
          awake_seconds=ended['awake'] - started['awake'],
          elapsed_utc_seconds=(datetime.fromisoformat(ended['utc']) - datetime.fromisoformat(started['utc'])).total_seconds(),
          scope='Read-only identity, historical duration analysis and report preparation; not fixture cost'))
    print(json.dumps(dict(estimate_minutes=estimate / 60,
                         scheduling_allowance_minutes=estimate * 1.2 / 60,
                         fixture_execution='NOT_RUN')))


if __name__ == '__main__':
    main()
