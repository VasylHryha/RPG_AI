"""C2 stage isolation, native-source fingerprints and evaluator provenance."""
import json
from pathlib import Path
import pytest
from tools import gate


def test_c2_and_c1_stamp_namespaces_are_distinct():
    assert gate.stamp_path('abc','c2')!=gate.stamp_path('abc','c1')
    assert Path('native/c2/relaxation.cpp') in {p.relative_to(gate.ROOT) for p in gate.source_files()}
    with pytest.raises(ValueError): gate.stamp_path('abc','other')


def test_c2_check_requires_its_own_stages(monkeypatch):
    monkeypatch.setattr(gate,'tree_problems',lambda:[])
    monkeypatch.setattr(gate,'verified',lambda milestone='c1': ['preflight','tests','smoke','mutation','panel'] if milestone=='c1' else [])
    assert gate.check('panel',milestone='c2')
    assert not gate.check('panel')


def test_c2_panel_receipt_rejects_failed_gates(tmp_path):
    p=tmp_path/'results.json'; p.write_text(json.dumps({'check_status':'ASSERTION_FAILURE','gates':{'numerics':False}}))
    assert not gate._artifact_valid('panel',p)


def test_c2_execution_hooks_select_its_stage_namespace(monkeypatch):
    from tools import gate_hook
    calls=[]
    def closed(stage,milestone='c1'):
        calls.append((stage,milestone)); return ['missing prerequisites']
    monkeypatch.setattr(gate_hook.gate,'check',closed)
    for command in ('.venv/bin/python -m geomind.run_c2 --output x', '.venv/bin/python tools/c2_mutation_probe.py x'):
        assert gate_hook.decide({'tool_name':'Bash','tool_input':{'command':command}})
    assert calls==[('panel','c2'),('mutation','c2')]
