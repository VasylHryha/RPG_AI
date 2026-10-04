"""Build explicit legacy/native targets and bind sources to the executable."""
import argparse
import hashlib
import json
import pathlib
import platform
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
COMBAT_SOURCES = ['src/native/world.cpp', 'src/native/combat.cpp', 'src/native/spatial.cpp',
                  'src/native/combat_rules.cpp', 'src/native/abilities.cpp', 'src/native/player.cpp',
                  'src/native/formation.cpp', 'src/native/formation_tables.cpp', 'src/native/commander.cpp',
                  'src/native/targeting.cpp', 'src/native/coord_abilities.cpp', 'src/native/dodge.cpp',
                  'src/native/decisions.cpp', 'src/native/director.cpp', 'src/native/network.cpp', 'src/native/network_tables.cpp', 'src/native/search.cpp']
TARGETS = {
    'legacy': ('astelia', ['src/main.cpp', 'src/formation_sim.cpp', 'src/v8_ieee754.cpp']),
    'native': ('astelia_native', ['src/native/host.cpp', 'src/native/config_codec.cpp', *COMBAT_SOURCES]),
    'core-check': ('native_core_contract', ['native_core_contract.cpp', *COMBAT_SOURCES]),
    'search-check': ('native_search_contract', ['native_search_contract.cpp', *COMBAT_SOURCES]),
    'formation-check': ('native_formation_contract', ['native_formation_contract.cpp', *COMBAT_SOURCES]),
    'combat-check': ('native_combat_contract', ['native_combat_contract.cpp', *COMBAT_SOURCES]),
    'layout': ('native_layout_probe', ['native_layout_probe.cpp', *COMBAT_SOURCES]),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiler', default=shutil.which('clang++') or shutil.which('g++'))
    ap.add_argument('--portable', action='store_true', help='omit host-specific CPU tuning')
    ap.add_argument('--engine', choices=TARGETS, default='legacy')
    ap.add_argument('--sanitize', action='store_true', help='instrument development lifetime/bounds checks')
    args = ap.parse_args()
    if not args.compiler:
        ap.error('clang++ or g++ is required')
    compiler = pathlib.Path(shutil.which(args.compiler) or args.compiler).resolve()
    compiler_identity = subprocess.check_output([str(compiler), '--version'])
    compiler_sha256 = sha(compiler)
    name, names = TARGETS[args.engine]
    if args.sanitize:
        name += '_sanitized'
    target = ROOT / 'build' / name
    target.parent.mkdir(exist_ok=True)
    common = [str(compiler), '-std=c++17', '-O1' if args.sanitize else '-O3',
              '-fno-fast-math', '-fwrapv', '-I' + str(ROOT / 'src')]
    lto = '-flto=thin' if b'clang' in compiler_identity.lower() else '-flto'
    optimization = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g'] if args.sanitize else [lto]
    common += optimization
    if not args.portable:
        common.append('-mcpu=native' if platform.machine() in ('arm64', 'aarch64') else '-march=native')
    sources = [ROOT / name for name in names]
    # Conservatively pin all project headers. No recursive wildcard source linking.
    headers = sorted((ROOT / 'src').rglob('*.h'))
    inputs = sources + headers
    extra = [ROOT / 'build.py']
    if args.engine != 'legacy':
        extra += [ROOT / 'generate_native_tables.cjs', ROOT / 'generate_native_network.py', ROOT.parent / 'astelia_snapshot/bc_net.json', ROOT.parent / 'astelia_snapshot/formation_sim.js']
    if args.engine == 'legacy':
        extra += [ROOT / 'generate.cjs', ROOT.parent / 'astelia_snapshot/formation_sim.js']
    input_hashes = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p)
                    for p in inputs + extra}
    header_identity = json.dumps({str(p):sha(p) for p in headers}, sort_keys=True).encode()
    objects, commands, object_hashes = [], [], {}
    for source in sources:
        stem = source.stem if args.engine == 'legacy' and not args.sanitize else name + '_' + source.stem
        obj = target.parent / (stem + '.o')
        stamp = obj.with_suffix('.sha256')
        contraction = 'on' if source.name == 'v8_ieee754.cpp' else 'off'
        command = common + ['-ffp-contract=' + contraction, '-c', str(source), '-o', str(obj)]
        fingerprint = hashlib.sha256(compiler_identity + compiler_sha256.encode() + header_identity + source.read_bytes() +
                                     json.dumps(command).encode()).hexdigest()
        existing = stamp.read_text().splitlines() if stamp.exists() else []
        if not obj.exists() or len(existing) != 2 or existing[0] != fingerprint or existing[1] != sha(obj):
            print(' '.join(command), flush=True)
            subprocess.run(command, check=True)
            stamp.write_text(fingerprint + '\n' + sha(obj) + '\n')
        object_hashes[str(obj.relative_to(ROOT))] = sha(obj)
        objects.append(str(obj)); commands.append(command)
    command = [str(compiler), *optimization, *objects, '-o', str(target)]
    print(' '.join(command), flush=True)
    subprocess.run(command, check=True)
    if sha(compiler) != compiler_sha256:
        raise RuntimeError('compiler executable changed during build')
    for name, expected in object_hashes.items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('object changed during link: ' + name)
    # A source edit during compilation invalidates the build instead of producing a misleading manifest.
    for location, expected in input_hashes.items():
        path = pathlib.Path(location)
        if not path.is_absolute():
            path = ROOT / path
        if sha(path) != expected:
            raise RuntimeError('input changed during build: ' + location)
    record = dict(schema=2, engine=args.engine, compiler=compiler_identity.decode(),
                  compiler_path=str(compiler), compiler_sha256=compiler_sha256, commands=commands,
                  link=command, binary_sha256=sha(target), source_hashes=input_hashes,
                  object_hashes=object_hashes,
                  portable=args.portable, sanitized=args.sanitize,
                  scope='native_search_checkpoint' if args.engine != 'legacy' else 'legacy_mechanical_port')
    manifest = target.with_suffix('.build.json')
    manifest.write_text(json.dumps(record, indent=2) + '\n')
    if args.engine == 'legacy' and not args.sanitize:
        (target.parent / 'build.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
