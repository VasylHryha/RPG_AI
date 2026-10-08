"""Synthetic build-amendment admission only; no collection or native execution."""
import pytest
import collection as c


def test_tooling_amendment_preserves_build_identity_and_fails_on_drift(tmp_path,monkeypatch):
    root=tmp_path/'slice';root.mkdir();binary=root/'_local/build/net_host'
    binary.parent.mkdir(parents=True);binary.write_text('binary')
    (root/'frozen').mkdir();(root/'frozen/collection_CONTRACT.md').write_text('contract')
    names=('requests.py','collection.py','test_collection.py','project.py','protocol.py','process_gate.py')
    for name in names:(root/name).write_text('before '+name)
    build=root/'BUILD.json'
    c.atomic(build,dict(status='PASS',sources={str(root/name):c.sha(root/name) for name in names},
                        reused_object_sha256={},binaries={'net_host':c.sha(binary)}))
    monkeypatch.setattr(c,'HERE',root);monkeypatch.setattr(c,'BINARY',binary)
    assert 'BUILD_TOOLING_AMENDMENT.json' not in c.admission()
    original=c.sha(build);hashes={}
    for name in ('collection.py','test_collection.py'):
        before=c.sha(root/name);(root/name).write_text('after '+name)
        hashes[name]=dict(before=before,after=c.sha(root/name))
    with pytest.raises(RuntimeError,match='source/object drift'):c.admission()
    amendment=root/'BUILD_TOOLING_AMENDMENT.json'
    payload=dict(build_sha256=original,source_hashes=hashes)
    c.atomic(amendment,payload)
    pins=c.admission()
    assert pins['BUILD_TOOLING_AMENDMENT.json']==c.sha(amendment) and c.sha(build)==original
    (root/'test_collection.py').write_text('further drift')
    with pytest.raises(RuntimeError,match='source/object drift'):c.admission()
    (root/'test_collection.py').write_text('after test_collection.py')
    (root/'requests.py').write_text('generator drift')
    with pytest.raises(RuntimeError,match='source/object drift'):c.admission()
    (root/'requests.py').write_text('before requests.py')
    c.atomic(amendment,{**payload,'build_sha256':'wrong'})
    with pytest.raises(RuntimeError,match='invalid collection tooling'):c.admission()
    c.atomic(amendment,{**payload,'source_hashes':{**hashes,'requests.py':hashes['collection.py']}})
    with pytest.raises(RuntimeError,match='invalid collection tooling'):c.admission()
    c.atomic(amendment,{**payload,'source_hashes':{**hashes,'collection.py':{**hashes['collection.py'],'before':'wrong'}}})
    with pytest.raises(RuntimeError,match='baseline drift'):c.admission()
    c.atomic(amendment,payload)
    collection=root/'collection';collection.mkdir();monkeypatch.setattr(c,'ROOT',collection)
    inv=c.seal(20);assert c.admit_inventory()==inv
    c.atomic(amendment,{**payload,'reason':'changed amendment bytes'})
    with pytest.raises(RuntimeError,match='sealed collection admission drift'):c.admit_inventory()
