"""Numerical gate precedes dispatch/controller work and any combat."""
import json
import subprocess
import s4_v6_numerics as V

def test_native_kernel_contracts():
    run=subprocess.run([str(V.BINARY),'--contracts'],capture_output=True,text=True,timeout=30)
    record=dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,fights=0)
    V.write(V.CHECKS/'KERNEL_CONTRACTS.json',record)
    assert run.returncode==0,run.stderr
    assert json.loads(run.stdout)['status']=='passed'

def test_declared_component_and_commitment_accuracy_gate():
    result=V.acceptance()
    assert result['status']=='PASS',json.dumps(result,indent=2)
