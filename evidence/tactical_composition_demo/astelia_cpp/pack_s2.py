"""Losslessly pack completed S2 stdout evidence; never executes combat.

XZ's larger dictionary retains repetition between full trace frames. Every
decoded byte hash is checked before replacing a task-generated gzip stream.
Identical streams share one content-addressed archive. The receipt retains all
logical output names and maps each to its stored path.
"""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import lzma
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=pathlib.Path)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    directory = args.directory.resolve()
    path = directory/'S2_RECEIPT.json'
    receipt = json.loads(path.read_text())
    if receipt['status'] != 'READY':
        ap.error('pack only a completed READY engineering batch')
    if args.check:
        checked = set()
        for row in receipt['outputs'].values():
            location = row['path']
            if location in checked:
                continue
            packed = (directory/location).read_bytes()
            if sha(packed) != row['sha256'] or sha(lzma.decompress(packed)) != row['raw_sha256']:
                raise RuntimeError('packed evidence identity mismatch: '+location)
            checked.add(location)
        print(f'{len(checked)} archives verified; {len(receipt["outputs"])} logical stdout streams')
        return
    if receipt.get('lossless_archive'):
        ap.error('already packed; use --check')
    original = path.read_bytes()
    (directory/'S2_RECEIPT.prepack.json').write_bytes(original)
    destination = directory/'stdout'
    destination.mkdir()
    groups = {}
    for name, row in receipt['outputs'].items():
        groups.setdefault(row['raw_sha256'], []).append((name, row))

    def convert(group):
        expected, names = group
        name, row = names[0]
        packed = (directory/name).read_bytes()
        if sha(packed) != row['sha256']:
            raise RuntimeError('gzip identity mismatch: '+name)
        raw = gzip.decompress(packed)
        if sha(raw) != expected:
            raise RuntimeError('stdout identity mismatch: '+name)
        result = lzma.compress(raw, preset=6)
        if lzma.decompress(result) != raw:
            raise RuntimeError('lossless round trip failed: '+name)
        location = 'stdout/'+expected+'.xz'
        (directory/location).write_bytes(result)
        # Check duplicate inputs too before replacing them with one archive.
        for other, entry in names[1:]:
            data = (directory/other).read_bytes()
            if sha(data) != entry['sha256'] or sha(gzip.decompress(data)) != expected:
                raise RuntimeError('duplicate stdout identity mismatch: '+other)
        return names, location, sha(result), len(raw), len(result)

    original_bytes = sum((directory/name).stat().st_size for name in receipt['outputs'])
    packed_bytes = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, (names, location, digest, raw_bytes, size) in enumerate(pool.map(convert, groups.items()), 1):
            packed_bytes += size
            for name, row in names:
                row.update(path=location, sha256=digest, raw_bytes=raw_bytes)
            if index % 19 == 0:
                print(f'packed {index}/{len(groups)} unique streams', flush=True)
    receipt['lossless_archive'] = {'codec': 'xz', 'logical_names': 'original capture names; use each entry path to read',
        'prepack_receipt_sha256': sha(original), 'packer_sha256': sha(pathlib.Path(__file__).read_bytes()),
        'unique_streams': len(groups), 'original_gzip_bytes': original_bytes, 'packed_bytes': packed_bytes,
        'raw_bytes_unchanged': True}
    path.write_text(json.dumps(receipt, indent=2)+'\n')
    # Only task-generated gzip captures are removed, after every archive passes.
    # Original stdout is reversible with lzma.decompress; no measurements change.
    for name in receipt['outputs']:
        (directory/name).unlink()
    print(f'packed {original_bytes/1024**2:.1f} MiB -> {packed_bytes/1024**2:.1f} MiB; all raw hashes unchanged')


if __name__ == '__main__':
    main()
