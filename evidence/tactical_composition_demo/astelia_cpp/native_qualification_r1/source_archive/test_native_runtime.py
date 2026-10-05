"""Native specialization edge cases and ordered hashed collections."""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent


def test_native_runtime(tmp_path):
    recorded = json.loads((ROOT/'build/build.json').read_text())['commands'][0]
    compiler = recorded[0]
    lto = [flag for flag in recorded if flag.startswith('-flto')]
    binary = tmp_path/'runtime_contract'
    subprocess.run([compiler,'-std=c++17','-O2','-fno-fast-math','-fwrapv','-ffp-contract=off',
                    '-I'+str(ROOT/'src'),str(ROOT/'runtime_contract.cpp'),
                    str(ROOT/'build/v8_ieee754.o'),*lto,'-o',str(binary)],check=True)
    assert subprocess.check_output([str(binary)],text=True)=='runtime contracts identical\n'
