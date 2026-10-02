"""Revision-four evidence integrity. No dynamics, selection, or hypothesis fitting.

R3 inputs remain receipt-bound history. These checks reject accidental omissions,
shape aliases, duplicate worlds, and partial release inventories in new work.
They do not replace independent review or establish experimental validity.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

import numpy as np

REQUIRED_SOURCE_NAMES = frozenset((
    'README.md', '04_recursive_background_generation.md',
    '05_mathematical_source_model.md', '06_evidence_catalog.md',
    '07_audit_report.md', '08_claim_coverage.md', 'CHANGELOG.md',
    'foundations/01_world_explanation.md', 'foundations/02_scientific_framework.md',
    'foundations/03_mathematical_core.md', 'foundations/ERRATA.md', 'MANIFEST.json',
))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite(item) for item in value)
    if isinstance(value, np.ndarray):
        if value.dtype.kind not in 'biuf':
            return False
        return bool(np.isfinite(value).all())
    if isinstance(value, (float, np.floating)):
        return bool(np.isfinite(value))
    return value is None or isinstance(value, (str, bool, int, np.integer, np.bool_))


def array_digest(kind, *arrays, metadata=None):
    """Bind names, shapes, time grids, ID inventories and separate array boundaries."""
    header = {'schema': 'geomind/array-identity/1', 'kind': kind, 'metadata': metadata or {}}
    encoded = json.dumps(header, sort_keys=True, allow_nan=False).encode()
    digest = hashlib.sha256(struct.pack('<Q', len(encoded)) + encoded)
    for value in arrays:
        array = np.asarray(value, dtype='<f8')
        if not np.isfinite(array).all():
            raise ValueError('nonfinite array identity')
        descriptor = json.dumps({'shape': array.shape, 'dtype': '<f8'}, sort_keys=True).encode()
        payload = array.tobytes(order='C')
        digest.update(struct.pack('<Q', len(descriptor)))
        digest.update(descriptor)
        digest.update(struct.pack('<Q', len(payload)))
        digest.update(payload)
    return digest.hexdigest()


def ordered_worlds(records, expected_world_ids):
    """World identity is experimental provenance, not row number or list length."""
    expected = list(expected_world_ids)
    ids = [row.get('world') for row in records]
    if (not expected or any(type(i) is not int or i < 0 for i in expected + ids)
            or len(set(expected)) != len(expected) or len(set(ids)) != len(ids)
            or set(ids) != set(expected)):
        raise ValueError('missing, duplicate, extra or invalid original world IDs')
    if not finite(records):
        raise ValueError('nonfinite or unsupported world record')
    by_id = {row['world']: row for row in records}
    return [by_id[i] for i in expected]


def safe_file(folder, name):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts or str(relative) != name:
        raise ValueError('noncanonical artifact path')
    base = Path(folder).resolve()
    path = base / relative
    if path.is_symlink():
        raise ValueError('artifact symlink is not an immutable file')
    try:
        path.resolve().relative_to(base)
    except ValueError as exc:
        raise ValueError('artifact escapes its evidence directory') from exc
    return path


def load_worlds(folder, receipt, expected_world_ids):
    """Verify index → compressed bytes → raw bytes → JSON world identity."""
    records = []
    entries = receipt.get('world_artifacts', [])
    ids = []
    for entry in entries:
        world = entry.get('world')
        if type(world) is not int or world < 0 or entry.get('path') != f'world_{world:03d}.json.gz':
            raise ValueError('world artifact index/name mismatch')
        path = safe_file(folder, entry['path'])
        if sha256(path) != entry.get('sha256'):
            raise ValueError('compressed world hash mismatch')
        raw = gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest() != entry.get('uncompressed_sha256'):
            raise ValueError('raw world hash mismatch')
        def invalid_constant(name):
            raise ValueError('nonfinite JSON constant: ' + name)
        record = json.loads(raw, parse_constant=invalid_constant)
        if record.get('world') != world or type(record.get('world')) is not int:
            raise ValueError('raw world identity differs from artifact index')
        records.append(record)
        ids.append(world)
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate world artifact index')
    return ordered_worlds(records, expected_world_ids)


def dependency_problems(root, hashes):
    if not hashes:
        return ['empty dependency inventory']
    problems = []
    for name, digest in hashes.items():
        path = safe_file(root, name)
        if not path.is_file() or sha256(path) != digest:
            problems.append(name)
    return problems


def validate_pin(root):
    """Compare the import with the owner table AND the complete audited release."""
    root = Path(root)
    handoff = root / 'docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md'
    expected_path = root / 'research/rrg/v0.2.1.expected.json'
    imported_path = root / 'research/rrg/v0.2.1.import.json'
    release = root / 'research/rrg/v0.2.1'
    expected = json.loads(expected_path.read_text())
    imported = json.loads(imported_path.read_text())
    owner = dict(re.findall(r'\| `([^`]+)` \| `([0-9a-f]{64})` \|', handoff.read_text()))
    if set(owner) != REQUIRED_SOURCE_NAMES or expected.get('expected_sha256') != owner:
        raise ValueError('owner source inventory missing or inconsistent')
    if expected.get('handoff_sha256') != sha256(handoff):
        raise ValueError('source inventory bound to a different owner handoff')
    hashes = imported.get('file_sha256', {})
    if (imported.get('verification_status') != 'VERIFIED'
            or expected.get('verification_status') != 'VERIFIED'
            or imported.get('release') != expected.get('release')
            or len(hashes) != 25 or imported.get('release_files_copied') != 25
            or any(hashes.get(name) != digest for name, digest in owner.items())):
        raise ValueError('incomplete or conflicting audited import inventory')
    actual = {str(path.relative_to(release)) for path in release.rglob('*') if path.is_file()}
    if actual != set(hashes) or dependency_problems(release, hashes):
        raise ValueError('release files differ from complete import inventory')
    manifest = json.loads((release / 'MANIFEST.json').read_text())
    entries = manifest.get('files', [])
    names = [entry['path'] for entry in entries]
    if (len(entries) != 23 or len(set(names)) != 23
            or set(names) | {'MANIFEST.json', 'SHA256SUMS.txt'} != set(hashes)):
        raise ValueError('release manifest is incomplete or duplicated')
    for entry in entries:
        path = safe_file(release, entry['path'])
        if entry.get('sha256') != hashes[entry['path']] or entry.get('bytes') != path.stat().st_size:
            raise ValueError('release manifest identity mismatch')
    checksums = {}
    for line in (release / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.lstrip('*')
        if name in checksums:
            raise ValueError('duplicate release checksum')
        checksums[name] = digest
    if checksums != {name: digest for name, digest in hashes.items() if name != 'SHA256SUMS.txt'}:
        raise ValueError('release checksum inventory mismatch')
    return {'status': 'PASS', 'source_files_verified': 25, 'owner_identities_verified': 12,
            'manifest_entries_verified': 23, 'checksum_entries_verified': 24,
            'handoff_sha256': sha256(handoff), 'expected_record_sha256': sha256(expected_path),
            'import_record_sha256': sha256(imported_path)}
