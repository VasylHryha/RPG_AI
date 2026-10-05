"""Losslessly pack completed S2 captures; never executes combat.

Every logical entry is verified, even when several names share one archive.
Paths must stay inside the selected evidence directory. This checks storage
identity and preservation against the prepack receipt, not scientific validity.
"""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import lzma
import pathlib
import tempfile
import os


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local_path(directory, name):
    relative = pathlib.PurePosixPath(name)
    if (not relative.parts or name != relative.as_posix() or relative.is_absolute()
            or '..' in relative.parts or '\\' in name):
        raise RuntimeError('unsafe evidence path: '+name)
    root = directory.resolve()
    path = root.joinpath(*relative.parts)
    # Reject symlinks even when they point inside the directory: packing removes
    # source captures, so it must operate on the named owned regular files.
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise RuntimeError('symlink evidence path: '+name)
    if not path.resolve().is_relative_to(root):
        raise RuntimeError('escaping evidence path: '+name)
    return path


def atomic_write(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(data)
        temporary.flush()
        os.fsync(temporary.fileno())
        name = temporary.name
    os.replace(name, path)


def check_archives(directory, receipt):
    if receipt.get('status') != 'READY' or not receipt.get('outputs'):
        raise RuntimeError('nonempty READY receipt required')
    metadata = receipt.get('lossless_archive', {})
    if metadata.get('codec') != 'xz' or metadata.get('raw_bytes_unchanged') is not True:
        raise RuntimeError('lossless XZ archive metadata required')
    original = local_path(directory, 'S2_RECEIPT.prepack.json').read_bytes()
    if sha(original) != metadata.get('prepack_receipt_sha256'):
        raise RuntimeError('prepack receipt identity mismatch')
    previous = json.loads(original)['outputs']
    if receipt['outputs'].keys() != previous.keys():
        raise RuntimeError('logical stdout coverage changed')
    checked = {}
    for name, row in receipt['outputs'].items():
        local_path(directory, name)
        location = row['path']
        if location not in checked:
            packed = local_path(directory, location).read_bytes()
            raw = lzma.decompress(packed)
            checked[location] = {'sha256': sha(packed), 'raw_sha256': sha(raw),
                                 'raw_bytes': len(raw), 'packed_bytes': len(packed)}
        actual = checked[location]
        if any(row.get(key) != actual[key] for key in ('sha256', 'raw_sha256', 'raw_bytes')):
            raise RuntimeError('logical archive identity mismatch: '+name)
        if row['raw_sha256'] != previous[name]['raw_sha256']:
            raise RuntimeError('prepack stdout identity mismatch: '+name)
    if metadata.get('unique_streams') != len(checked) or metadata.get('packed_bytes') != sum(
            row['packed_bytes'] for row in checked.values()):
        raise RuntimeError('archive aggregate metadata mismatch')
    return checked


def pack(directory, workers=4):
    path = local_path(directory, 'S2_RECEIPT.json')
    original = path.read_bytes()
    receipt = json.loads(original)
    if receipt.get('status') != 'READY' or not receipt.get('outputs'):
        raise RuntimeError('nonempty READY receipt required')
    if receipt.get('lossless_archive'):
        raise RuntimeError('already packed; use --check')
    destination = local_path(directory, 'stdout')
    prepack = local_path(directory, 'S2_RECEIPT.prepack.json')
    if destination.exists() or prepack.exists():
        raise RuntimeError('packing destinations exist; preserve the incomplete attempt')
    groups, original_bytes = {}, 0
    # Validate every source before creating archives or replacing metadata.
    for name, row in receipt['outputs'].items():
        source = local_path(directory, name)
        if not name.endswith('.gz') or not source.is_file():
            raise RuntimeError('regular gzip capture required: '+name)
        data = source.read_bytes()
        raw = gzip.decompress(data)
        if sha(data) != row.get('sha256') or sha(raw) != row.get('raw_sha256'):
            raise RuntimeError('gzip/stdout identity mismatch: '+name)
        if 'raw_bytes' in row and row['raw_bytes'] != len(raw):
            raise RuntimeError('stdout size mismatch: '+name)
        original_bytes += len(data)
        groups.setdefault(row['raw_sha256'], []).append((name, row))
    destination.mkdir()
    atomic_write(prepack, original)

    def convert(group):
        expected, names = group
        raw = gzip.decompress(local_path(directory, names[0][0]).read_bytes())
        if sha(raw) != expected:
            raise RuntimeError('source changed during packing')
        result = lzma.compress(raw, preset=6)
        if lzma.decompress(result) != raw:
            raise RuntimeError('lossless round trip failed')
        location = 'stdout/'+expected+'.xz'
        atomic_write(local_path(directory, location), result)
        return names, location, sha(result), len(raw), len(result)

    packed_bytes = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
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
    check_archives(directory, receipt)
    # Recheck gzip identities before finalization and deletion, catching edits
    # made while compression ran. A failed attempt retains its source captures.
    prior = json.loads(original)['outputs']
    for name, row in prior.items():
        if sha(local_path(directory, name).read_bytes()) != row['sha256']:
            raise RuntimeError('source changed during packing: '+name)
    atomic_write(path, (json.dumps(receipt, indent=2)+'\n').encode())
    for name in prior:
        local_path(directory, name).unlink()
    print(f'packed {original_bytes/1024**2:.1f} MiB -> {packed_bytes/1024**2:.1f} MiB; all raw hashes unchanged')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=pathlib.Path)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if args.workers < 1:
        ap.error('workers must be positive')
    directory = args.directory.resolve()
    if args.check:
        receipt = json.loads(local_path(directory, 'S2_RECEIPT.json').read_text())
        checked = check_archives(directory, receipt)
        print(f'{len(checked)} archives verified; {len(receipt["outputs"])} logical stdout streams')
    else:
        pack(directory, args.workers)


if __name__ == '__main__':
    main()
