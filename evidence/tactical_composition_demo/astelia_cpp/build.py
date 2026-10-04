"""Build the standalone C++17 simulation; no external dependencies."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiler', default=shutil.which('clang++') or shutil.which('g++'))
    args = ap.parse_args()
    if not args.compiler:
        ap.error('clang++ or g++ is required')
    target = ROOT / 'build' / 'astelia'
    target.parent.mkdir(exist_ok=True)
    common = [args.compiler, '-std=c++17', '-O2', '-fno-fast-math', '-fwrapv', '-I' + str(ROOT / 'src')]
    compiler_identity = subprocess.check_output([args.compiler, '--version'])
    headers = b''.join(p.read_bytes() for p in sorted((ROOT / 'src').glob('*.h')))
    objects = []
    commands = []
    for source in sorted((ROOT / 'src').glob('*.cpp')):
        obj = target.parent / (source.stem + '.o')
        stamp = obj.with_suffix('.sha256')
        # The V8 C++ math was built with expression contraction in this Node.
        # Simulation arithmetic and the V8 hypot builtin retain separate ops.
        contraction = 'on' if source.name == 'v8_ieee754.cpp' else 'off'
        command = common + ['-ffp-contract=' + contraction, '-c', str(source), '-o', str(obj)]
        identity = hashlib.sha256(compiler_identity + headers + source.read_bytes() + json.dumps(command).encode()).hexdigest()
        if not obj.exists() or not stamp.exists() or stamp.read_text().strip() != identity:
            print(' '.join(command), flush=True)
            subprocess.run(command, check=True)
            stamp.write_text(identity + '\n')
        objects.append(str(obj))
        commands.append(command)
    command = [args.compiler, *objects, '-o', str(target)]
    print(' '.join(command), flush=True)
    subprocess.run(command, check=True)
    (target.parent / 'build.json').write_text(json.dumps(dict(compiler=compiler_identity.decode(), commands=commands,
        link=command, binary_sha256=hashlib.sha256(target.read_bytes()).hexdigest()), indent=2) + '\n')


if __name__ == '__main__':
    main()
