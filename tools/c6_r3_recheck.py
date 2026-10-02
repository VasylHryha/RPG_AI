"""Read/hash-check the stopped R3 development receipt; never run or rescore a panel."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geomind import c6_r4_integrity as I  # noqa: E402


def inspect(folder, root=ROOT):
    folder = Path(folder)
    receipt_path = folder / 'results.json'
    receipt = json.loads(receipt_path.read_text())
    if receipt.get('kind') != 'DEVELOPMENT_ONLY' or receipt.get('status') != 'STOP':
        raise ValueError('recheck only the existing stopped development receipt')
    rows = I.load_worlds(folder, receipt, list(range(receipt['protocol']['development_worlds'])))
    problems = I.dependency_problems(root, receipt['file_hashes'])
    if problems:
        raise ValueError('receipt-bound implementation changed: ' + ', '.join(problems))
    pin = I.validate_pin(root)
    if pin['import_record_sha256'] != receipt['source_pin']['import_record_sha256']:
        raise ValueError('source import differs from the stopped receipt')
    groups = [candidate for row in rows for candidate in row['turns'][0]['formation']['intact']['candidates']]
    source = [g for g in groups if g['attribution'] == 'source']
    mixed = [g for g in groups if g['attribution'] == 'mixed_or_prior']
    windows = [row['turns'][0]['numerics'][scope] for row in rows for scope in ('initial', 'formation_snapshot')]
    return {'kind': 'IMPLEMENTER_RECHECK_ONLY', 'source_commit': receipt['source_commit'],
        'reviewed_receipt_sha256': I.sha256(receipt_path), 'original_status': 'STOP',
        'hypothesis_verdicts': 'NOT_ASSIGNED; original development receipt unchanged',
        'world_artifacts_verified': len(rows), 'receipt_bound_files_verified': len(receipt['file_hashes']),
        'source_pin': pin, 'qualified_sources': sum(row['turns'][0]['qualified'] for row in rows),
        'source_cohort_candidates': len(source), 'source_cohort_candidates_accepted': sum(g['accepted'] for g in source),
        'mixed_candidates_without_recovery_assay': sum(g['recovery_status'] == 'NOT_RUN' for g in mixed),
        'mixed_candidate_worlds': [row['world'] for row in rows if any(g['attribution'] == 'mixed_or_prior' for g in row['turns'][0]['formation']['intact']['candidates'])],
        'dt_failures': [{'world': row['world'], 'scope': scope, 'error': row['turns'][0]['numerics'][scope]['dt_error']}
            for row in rows for scope in ('initial', 'formation_snapshot')
            if row['turns'][0]['numerics'][scope]['dt_error'] > receipt['protocol']['qualification']['dt_tolerance']],
        'native_reference_max_error': max(w['native_reference_error'] for w in windows),
        'equivariance_max_error': max(w['equivariance_error'] for w in windows),
        'all_sham_controls_passed': all(row['turns'][0]['controls']['sham_preserved'] for row in rows),
        'all_no_r_controls_passed': all(not row['turns'][0]['controls']['no_r_qualifies'] for row in rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt-folder', type=Path, default=ROOT / 'evidence/c6_r3_design_gate')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    result = inspect(args.receipt_folder)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as target:
        target.write(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'original_status': result['original_status'], 'worlds_verified': result['world_artifacts_verified'],
        'qualified_sources': result['qualified_sources'], 'mixed_unassayed': result['mixed_candidates_without_recovery_assay'],
        'dt_failures': result['dt_failures']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
