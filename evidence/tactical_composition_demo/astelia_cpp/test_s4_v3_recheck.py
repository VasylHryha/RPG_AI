"""Bounded recheck: pure contracts and immutable evidence, never tuning or parity fights."""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent


def test_original_native_contract_without_rebuilding():
    from build_admission import admit
    binary = ROOT/'build/native_s3_contract'
    admit(binary)
    assert json.loads(subprocess.check_output([str(binary)], text=True))['status'] == 'passed'


def test_synthetic_v3_pair_lifecycle_and_force_counterexample(tmp_path):
    # Only the controller translation unit; one compiler process, no shared build writes.
    binary = tmp_path/'v3_contract'
    command = ['clang++', '-std=c++17', '-O1', '-fno-fast-math', '-ffp-contract=off',
               '-I'+str(ROOT/'src'), str(ROOT/'native_s4_v3_recheck.cpp'),
               str(ROOT/'src/native/s3_controller.cpp'), '-o', str(binary)]
    subprocess.run(command, check=True, capture_output=True)
    row = json.loads(subprocess.check_output([str(binary)], text=True))
    assert row['status'] == 'passed' and row['fights'] == 0


def test_recorded_evidence_remains_byte_identical():
    receipt = json.loads((ROOT/'s4_v3_recheck_checks/ANALYSIS.json').read_text())
    for name, expected in receipt['preserved_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name


def test_recheck_diagnostics_match_original_orientations():
    result = json.loads((ROOT/'s4_v3_recheck_checks/ANALYSIS.json').read_text())
    assert len(result['diagnostic_equality']) == 2
    assert all(result['diagnostic_equality'].values())
    assert result['planning']['delta'] == 3.5
    assert result['planning']['n'] == {'P1':99, 'P2':16, 'P3':16}
