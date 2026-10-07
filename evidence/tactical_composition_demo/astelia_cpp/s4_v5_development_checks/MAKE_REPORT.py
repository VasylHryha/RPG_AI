"""Render seed-free reporting from existing development/audit records."""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
OUT = BASE / 's4_v5_development'


def load(path):
    return json.loads(path.read_text())


def fmt(value):
    return '—' if value is None else f'{value:.4f}'


def table(lines, headings, rows):
    lines.extend(['', '| ' + ' | '.join(headings) + ' |', '| ' + ' | '.join(['---'] * len(headings)) + ' |'])
    lines.extend('| ' + ' | '.join(str(x) for x in row) + ' |' for row in rows)
    lines.append('')


def main():
    if (HERE/'AUDIT_NOT_COMPLETED.json').exists() or not (HERE / 'AUDIT.json').exists():
        report_without_audit()
        return
    receipt = load(OUT / ('summary.json' if (OUT / 'summary.json').exists() else 'failure.json'))
    audit = load(HERE / 'AUDIT.json')
    timing = load(HERE / 'SUPERVISOR_TIMING.json')
    runner_time = load(OUT / 'RUN_TIMING.json')
    identity = load(OUT / 'run_identity.json')
    label = 'STOP' if receipt['status'] == 'STOP' else 'NOT_READY'
    lines = [label, '', '# S4 v5 development report', '',
        'Implementer family: Codex (GPT-6). Owner-authorized single exploratory development run under decision 0031 and amended DESIGN_0G section 17. A/B only; no C, judging, registration, S5 execution or scientific acceptance.', '',
        f"Runner outcome: **{receipt['status']}**; report outcome: **{label}**. The amended protocol reports PROGRESS after passing B and explicitly precludes READY_FOR_S5. Continuing to C requires a later declared allocation; PROGRESS does not establish beating regular or authorize S5.", '',
        "The native v5 policy is the v3 skeleton: range-aware movement and binary commit/escape with ±0.2 hysteresis; travel-time hold and commit focus are disabled. H/F/HF/v4 remain labelled variants. Dimensions remain 11/11/3; nearest is untuned. No experiment code was changed by this task.", '',
        "CMA-ES 4.5.0, population 16, sigma .25 and 16 generations; 19 fixed common tuning clusters, both orientations. A starts at midpoints and selects novice melee mean S. B inherits A's tuning winners and ranks separately averaged ten novice/nine regular clusters by (novice mean ≥0 eligibility, regular mean S), with eligibility first and earlier exact ties retained. The same ordering feeds CMA adaptation and incumbent retention; validation never chooses knobs. Each completed arm/stage accounts for 9,766 tuning evaluations, including cache hits.", '',
        "After all four arms validate, resonator novice mean must be strictly positive at both A and B. After all-arm B validation, resonator regular mean must be strictly greater than −7.62; equality stops. Novice tuning eligibility (≥0) and novice validation (>0) are separate predicates. S = own survivors − enemy survivors is the only score; guns, damage, timeouts and elimination times are descriptive.", '',
        f"Expected 4–6 hours, ten workers. Runner elapsed/awake monotonic time: **{runner_time['elapsed_seconds']/60:.3f} min**. Outer wall elapsed: **{timing['elapsed_seconds']/60:.3f} min**; outer awake: **{timing['awake_seconds']/60:.3f} min**; exit {timing['returncode']}. The full 360-minute absolute monotonic allowance starts at runner entry. Projection checks, bounded submissions, clamped subprocess deadlines and child termination remain unchanged. Outer elapsed uses time.time; awake uses macOS time.monotonic/mach_absolute_time (excludes system sleep).", '',
        "The readiness command was launched once under /usr/bin/caffeinate -i -s at or after 22:00 into the new s4_v5_development directory. It refused existing output and permanently claimed the fresh declaration before combat. The earlier C6 supervisor had exited with BrokenPipeError before its timing batch; that scheduling failure is disclosed in LAUNCH.json and was not repaired or rerun here. Load at launch is recorded, without a claim of independently verified machine idleness.", '',
        f"Implementation commit: `{identity['implementation_commit']}`. [run_identity.json](s4_v5_development/run_identity.json) binds the admitted native binary/build, source pin, optimizer and {audit['runtime_hashes_verified']} runtime hashes. All runtime identities still match at audit. Fresh development entropy and every orientation/cache/configuration use remain local and hash-bound. No judging-root entropy was used.", '',
        f"[Stored-record audit](s4_v5_development_checks/AUDIT.json): **{audit['raw_rows']:,} accounted rows**, {audit['fresh_rows']:,} recorded fresh fights, {audit['cache_hits']:,} cache hits; {audit['completed_candidates']:,} completed-generation candidates, {audit['partial_generation_candidates']} complete candidates from a partial generation, and {audit['cma_generations_reconstructed']} CMA generations reconstructed. Every raw row matches its ledger/configuration and declared allocation; complete tuning records reproduce incumbent retention and CMA ask/tell. All completed endpoint scores and descriptive end states reconstruct. Recorded controller-failure rows: {audit['recorded_controller_failure_rows']}; zero planner counters in recorded rows. Audit executed zero combat fights. On a worker/deadline failure, unreturned in-flight work is not added to recorded fight totals.", '']
    if 'B' in receipt['gates']:
        g = receipt['gates']['B']
        lines[6:6] = [f"Stage B resonator: novice mean S **{g['novice_mean']:+.4f}**; regular mean S **{g['regular_mean']:+.4f}**. Regular minus the declared section-16 v3 baseline: **{g['regular_mean'] + 7.62:+.4f}**. Novice validation predicate: **{g['novice_validation_pass']}**; regular progress predicate: **{g['regular_progress_pass']}**.", '']
    if 'error' in receipt:
        error_kind = receipt['error'].split('(', 1)[0]
        explanation = 'The attempt stopped on an execution/identity error.'
        if 'projected remaining A/B work exceeds 360-minute deadline' in receipt['error']:
            explanation = 'The conservative forecast stopped further submission because projected remaining A/B work exceeded the remaining 360-minute allowance; this does not mean the absolute deadline expired.'
        elif 'input changed' in receipt['error'] or 'identity changed' in receipt['error']:
            explanation = 'An identity guard detected a changed input or executable and stopped the attempt.'
        lines += [f"Execution failure class: `{error_kind}`. {explanation} Full error and native output remain local in failure.json and raw logs. Partial tuning is retained and cannot substitute for missing validation.", '']
    table(lines, ['Stage', 'Novice validation mean S', 'Novice >0', 'Regular validation mean S', 'Regular >−7.62', 'Runner gate'],
          [(stage, fmt(g['novice_mean']), g['novice_validation_pass'], fmt(g['regular_mean']), g['regular_progress_pass'], g['status']) for stage, g in receipt['gates'].items()])
    table(lines, ['Stage', 'Arm', 'Split', 'Recorded rows'],
          [(a['stage'], a['arm'], a['split'], a['recorded_rows']) for a in audit['accounting_by_stage_arm_split']])
    for stage in ('A', 'B'):
        lines += [f'## Stage {stage} validation', '',
            'Two orientations are averaged within each of 100 independent seed clusters per endpoint. Intervals are descriptive normal 95% intervals (mean ±1.96 sample SD/√100). Guns/timeouts/damage describe 200 fights per endpoint. Team 0 is the controlled arm in both orientations; side swaps change geometry.']
        entries = [(key.split('|')[1], key.split('|')[-1], value) for key, value in audit['validation'].items() if key.startswith(stage+'|')]
        if not entries:
            lines += ['', 'not_run: this validation stage did not complete; no tuning score is substituted.', '']
            continue
        table(lines, ['Arm', 'Head', 'Mean S', 'SD', 'SE', '95% interval', 'Own / enemy guns', 'Timeouts / fights'],
            [(arm, head, fmt(v['stats']['mean']), fmt(v['stats']['sd']), fmt(v['stats']['se']),
              '['+', '.join(fmt(x) for x in v['stats']['descriptive_normal_95'])+']',
              fmt(v['descriptive']['own_guns_alive_mean'])+' / '+fmt(v['descriptive']['enemy_guns_alive_mean']),
              str(v['descriptive']['timeouts'])+' / '+str(v['descriptive']['fights'])) for arm, head, v in entries])
        table(lines, ['Arm', 'Head', 'Cross-team damage dealt / taken', 'Mean terminal s', 'Own eliminations; mean s', 'Enemy eliminations; mean s'],
            [(arm, head, fmt(v['descriptive']['damage_dealt_mean'])+' / '+fmt(v['descriptive']['damage_taken_mean']),
              fmt(v['descriptive']['mean_termination_time']), str(v['descriptive']['own_eliminations'])+'; '+fmt(v['descriptive']['own_elimination_time_mean']),
              str(v['descriptive']['enemy_eliminations'])+'; '+fmt(v['descriptive']['enemy_elimination_time_mean'])) for arm, head, v in entries])
    lines += ['A regular is not_run by design (novice melee only). A/B army composition also changes, so their difference does not isolate projectile observation. Damage is cross-team HP damage; friendly damage is excluded. Elimination times are conditional on actual elimination; timeouts are censored with no imputation. Both armies may be eliminated on the same terminal tick.', '',
              '## Tuning selections and omega diagnostics']
    table(lines, ['Stage', 'Arm', 'Complete', 'Generations', 'Selected novice tuning mean', 'Selected regular tuning mean', 'B eligible', 'Accounted tuning rows'],
          [(t['stage'], t['arm'], t['completed'], str(t['completed_generations'])+'/16', fmt(t['selection']['novice_mean']),
            fmt(t['selection']['regular_mean']), t['selection']['eligible'],
            t['accounted_rows']) for t in audit['tuning']])
    table(lines, ['Stage', 'Selected melee omega (rad/s)', 'Selected ranged omega (rad/s)'],
          [(t['stage'], fmt(t['knobs']['omega_melee']), fmt(t['knobs']['omega_ranged'])) for t in audit['tuning'] if t['arm']=='resonator'])
    lines += [f"Latest retained role omega, including any partial stage: `{json.dumps(receipt['selected_omega'],sort_keys=True)}` rad/s. These are optimizer diagnostics only, with no matched zero-omega ablation or rotation-necessity inference. Stage A contains no ranged units, so its ranged omega is not identified by that tuning panel. No separate artillery omega is a tuned parameter in this policy. All selected knobs remain in the stage-best and local tuning files. Partial-stage values are not promoted to completed selections.", '',
              '## Comparison with v3, v4 and section-16 cells', '',
              'These are descriptive comparisons across fresh, unmatched development seed panels. Historical v3 B and v4 B used separately tuned knobs; section 16 used fixed historical v3 B knobs for all v3/H/F/HF cells. HF is the v4 skeleton at v3 knobs, not the independently retuned v4 package. Differences below are arithmetic differences, not paired estimates, causal attribution, statistical superiority or registered verdicts. The B gate uses the section-16 resonator v3 −7.620 baseline, not historical v3 B −7.570 or v3 C −1.655.']
    old3 = load(BASE/'s4_v3_development/B_validation.json')['results']
    old4 = load(BASE/'s4_v4_development/B_validation.json')['results']
    attribution = load(BASE/'s4_attribution_checks/ANALYSIS.json')['endpoints']
    rows = []
    comparison = {}
    for arm in ('resonator', 'morale', 'pushpull', 'nearest'):
        for head in ('novice', 'regular'):
            key = f'B|{arm}|s4_full_head|{head}'
            current = audit['validation'].get(key, {}).get('stats', {}).get('mean')
            for label0, historical in [('historical v3 B', old3[arm]['s4_full_head|'+head]['stats']['mean']),
                                      ('historical v4 B', old4[arm]['s4_full_head|'+head]['stats']['mean'])]:
                rows.append((arm, head, label0, fmt(historical), fmt(current), fmt(None if current is None else current-historical)))
            if arm in ('resonator', 'morale'):
                for cell, measurements in attribution[arm+'|'+head]['cells'].items():
                    historical = measurements['S']['mean']
                    rows.append((arm, head, 'section 16 '+cell, fmt(historical), fmt(current), fmt(None if current is None else current-historical)))
            comparison[arm+'|'+head] = current
    table(lines, ['Arm', 'Head', 'Reference', 'Reference mean S', 'v5 B mean S', 'v5 minus reference'], rows)
    lines += ['## Unrun work and delivery boundaries', '',
        'Stage C and its doctrine/novice/regular endpoints are explicitly not_run: outside the amended v5 A/B scope, even if B reports PROGRESS. P2/P3, fresh margin/sample-size planning, judging and S5 are not_run. No milestone status was changed.', '',
        'Decision traces, trajectory replays, movement reversal rates and feasibility distributions are not_run for v5: the reviewed readiness runner stores terminal fight records and performs no extra replay fights. Historical v4 and section-16 traces remain unchanged. Terminal records cannot reconstruct trajectories; no claim of improved movement stability is made.', '',
        '[RAW_FILES_OUTSIDE_GIT.json](s4_v5_development_checks/RAW_FILES_OUTSIDE_GIT.json) lists SHA256 and byte counts for local raw fight rows, seed declarations/uses, candidate and validation records, permanent claim, and logs. [AUDIT.json](s4_v5_development_checks/AUDIT.json) carries seed-free summaries and endpoint coverage; local raw files are required for full reconstruction. Every committed payload file is below 50,000,000 bytes. [DELIVERY_NOTE.md](s4_v5_development_checks/DELIVERY_NOTE.md) describes the normal-hook commit or verified bundle and its separate transport identity.', '',
        'Owner recheck request, verbatim:', '',
        "> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.", '',
        'Owner recheck and disposition: pending; the delivery will record the reviewer family, exact reviewed report hash, findings and corrections in OWNER_RECHECK.md and docs/PLAN_CURRENT.md.', '']
    (BASE/'S4_V5_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines))
    print(label)


def report_without_audit():
    timing = load(HERE/'SUPERVISOR_TIMING.json')
    summary_path = OUT / ('summary.json' if (OUT/'summary.json').exists() else 'failure.json')
    receipt = load(summary_path) if summary_path.exists() else None
    audit_path = HERE/'AUDIT_NOT_COMPLETED.json'
    audit = load(audit_path) if audit_path.exists() else dict(status='NOT_COMPLETED', error_class='NoStoredReceipt')
    lines = ['NOT_READY', '', '# S4 v5 development report', '',
        'Implementer family: Codex (GPT-6). Owner-authorized single v5 A/B development attempt under decision 0031. No judging, registration, C, S5 or scientific acceptance.', '',
        'NOT_READY: the stored-record audit did not complete. This report does not claim verified runtime identities, reconstructed selection, complete endpoints or development readiness.', '',
        f"Audit/refusal class: `{audit['error_class']}`. Raw error, native stdout and logs remain local and hash-bound; no raw error is embedded in this report.", '',
        f"Supervisor exit {timing['returncode']}; outer elapsed {timing['elapsed_seconds']/60:.3f} min; awake {timing['awake_seconds']/60:.3f} min. One launch under caffeinate, hard runner allowance 360 minutes. MacOS time.monotonic supplies awake time; time.time supplies elapsed time.", '',
        f"Permanent declaration claim present: **{(BASE/'s4_v5_part1_checks/LEDGER_USED.json').exists()}**. Output present: **{OUT.exists()}**. This records observed files, without equating claim presence with completed combat.", '']
    if receipt is None:
        lines += ['The runner left no execution receipt. No validation endpoint or role omega is available; A/B endpoints are not_run/unverified because preflight or initialization did not complete. No fight execution is established by this report.', '']
    else:
        lines += [f"Runner-recorded status: **{receipt['status']}**; completed stages: `{receipt.get('stages_completed',[])}`. Recorded totals: {receipt.get('executed_fights',0)} fresh rows, {receipt.get('cache_hits',0)} hits. These values and any partial results are unverified by the incomplete audit.", '',
            f"Retained role omega, unverified diagnostics only: `{json.dumps(receipt.get('selected_omega',{}),sort_keys=True)}` rad/s. No rotation-necessity claim or promotion of partial knobs.", '']
    lines += ['The B progress threshold remains resonator regular mean S >−7.62, together with positive novice validation at A/B. Tuning eligibility remains novice mean ≥0 before regular mean ranking. Without completed audit, no threshold result or comparison with historical v3/section-16 cells is asserted. Historical v3 B regular was −7.570; the exact threshold uses section-16 v3 −7.620. Historical source reports and raw measurements are unchanged.', '',
        'C is not_run, outside the amended scope. Trajectory replays, reversal/feasibility telemetry, margins and sample-size planning are not_run. No retry, new seed declaration, code repair, budget extension or extra combat occurred during this attempt.', '',
        '[RAW_FILES_OUTSIDE_GIT.json](s4_v5_development_checks/RAW_FILES_OUTSIDE_GIT.json) retains hashes and sizes of available local raw evidence. [DELIVERY_NOTE.md](s4_v5_development_checks/DELIVERY_NOTE.md) identifies the scoped normal-hook commit or verified bundle. Raw seeds, logs, native outputs and fight records are excluded from git; payload files are below 50,000,000 bytes.', '',
        'Owner recheck request, verbatim:', '',
        "> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.", '',
        'Owner recheck and disposition: pending, to be recorded in OWNER_RECHECK.md and docs/PLAN_CURRENT.md.', '']
    (BASE/'S4_V5_DEVELOPMENT_REPORT.md').write_text('\n'.join(lines))
    print('NOT_READY')


if __name__ == '__main__':
    main()
