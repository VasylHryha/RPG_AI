"""Adversarial storage tests using tiny captures; no combat or new arms."""
import copy
import gzip
import json
import lzma
import pytest
from pack_s2 import check_archives, pack, sha


def captures(directory):
    rows = {}
    for name, raw in [('a.gz', b'first\n'), ('b.gz', b'first\n'), ('c.gz', b'second\n')]:
        data = gzip.compress(raw, mtime=0)
        (directory/name).write_bytes(data)
        rows[name] = {'sha256': sha(data), 'raw_sha256': sha(raw)}
    receipt = {'status': 'READY', 'outputs': rows}
    (directory/'S2_RECEIPT.json').write_text(json.dumps(receipt))
    return receipt


@pytest.fixture
def archived(tmp_path):
    captures(tmp_path)
    pack(tmp_path, workers=2)
    return tmp_path, json.loads((tmp_path/'S2_RECEIPT.json').read_text())


def test_lossless_pack_preserves_every_logical_stream(archived):
    directory, receipt = archived
    assert len(check_archives(directory, receipt)) == 2
    assert len(receipt['outputs']) == 3
    assert receipt['outputs']['a.gz']['path'] == receipt['outputs']['b.gz']['path']
    for name, row in receipt['outputs'].items():
        assert not (directory/name).exists()
        assert sha(lzma.decompress((directory/row['path']).read_bytes())) == row['raw_sha256']
    with pytest.raises(RuntimeError, match='already packed'):
        pack(directory)


@pytest.mark.parametrize('key,value', [('sha256', '0'*64), ('raw_sha256', '0'*64), ('raw_bytes', 0)])
def test_duplicate_path_does_not_skip_logical_identity(archived, key, value):
    directory, receipt = archived
    receipt['outputs']['b.gz'][key] = value
    with pytest.raises(RuntimeError, match='logical archive identity'):
        check_archives(directory, receipt)


@pytest.mark.parametrize('kind', ['empty', 'omitted', 'rebound', 'prepack', 'aggregate', 'corrupt'])
def test_invalid_evidence_fails_closed(archived, kind):
    directory, receipt = archived
    if kind == 'empty':
        receipt['outputs'] = {}
    elif kind == 'omitted':
        del receipt['outputs']['c.gz']
    elif kind == 'rebound':
        receipt['outputs']['b.gz'] = copy.deepcopy(receipt['outputs']['c.gz'])
    elif kind == 'prepack':
        (directory/'S2_RECEIPT.prepack.json').write_bytes(b'{}')
    elif kind == 'aggregate':
        receipt['lossless_archive']['unique_streams'] = 1
    else:
        (directory/receipt['outputs']['a.gz']['path']).write_bytes(b'corrupt')
    with pytest.raises((RuntimeError, lzma.LZMAError)):
        check_archives(directory, receipt)


@pytest.mark.parametrize('name', ['../foreign.gz', '/tmp/foreign.gz', 'nested/../../foreign.gz', 'nested\\foreign.gz', './a.gz'])
def test_pack_rejects_escaping_names_before_writes(tmp_path, name):
    receipt = captures(tmp_path)
    receipt['outputs'][name] = receipt['outputs'].pop('a.gz')
    original = json.dumps(receipt).encode()
    (tmp_path/'S2_RECEIPT.json').write_bytes(original)
    with pytest.raises(RuntimeError, match='unsafe evidence path'):
        pack(tmp_path)
    assert (tmp_path/'S2_RECEIPT.json').read_bytes() == original
    assert not (tmp_path/'stdout').exists()
    assert (tmp_path/'a.gz').exists()


def test_pack_rejects_symlink_and_bad_duplicate_before_writes(tmp_path):
    receipt = captures(tmp_path)
    original = (tmp_path/'S2_RECEIPT.json').read_bytes()
    (tmp_path/'b.gz').unlink()
    (tmp_path/'b.gz').symlink_to(tmp_path/'a.gz')
    with pytest.raises(RuntimeError, match='symlink'):
        pack(tmp_path)
    (tmp_path/'b.gz').unlink()
    (tmp_path/'b.gz').write_bytes(gzip.compress(b'changed', mtime=0))
    with pytest.raises(RuntimeError, match='identity mismatch'):
        pack(tmp_path)
    assert (tmp_path/'S2_RECEIPT.json').read_bytes() == original
    assert not (tmp_path/'S2_RECEIPT.prepack.json').exists()


@pytest.mark.parametrize('kind', ['escape', 'symlink'])
def test_checker_rejects_foreign_archive_paths(archived, kind):
    directory, receipt = archived
    row = receipt['outputs']['a.gz']
    if kind == 'escape':
        row['path'] = '../foreign.xz'
    else:
        (directory/'alias.xz').symlink_to(directory/row['path'])
        row['path'] = 'alias.xz'
    with pytest.raises(RuntimeError, match='evidence path'):
        check_archives(directory, receipt)
