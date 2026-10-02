"""Build the C6 element law with the approved local toolchain pin."""

import hashlib
import json
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
# One registration-ready constant; the output paths are not compiler flags.
TOOLCHAIN = (
    "Apple clang version 21.0.0 (clang-2100.3.34.2)",
    ("-std=c++17", "-O2", "-fno-fast-math", "-ffp-contract=off", "-dynamiclib"),
)


def compiler_line():
    return subprocess.check_output(["clang++", "--version"], text=True).splitlines()[0]


def build(flags=None):
    expected_compiler, expected_flags = TOOLCHAIN
    flags = expected_flags if flags is None else tuple(flags)
    compiler = compiler_line()
    if compiler != expected_compiler:
        raise RuntimeError(f"C6 compiler pin mismatch: {compiler!r} != {expected_compiler!r}")
    if flags != expected_flags:
        raise RuntimeError(f"C6 compiler flags mismatch: {flags!r} != {expected_flags!r}")
    source = ROOT / "native/c6/element_law.cpp"
    folder = ROOT / "build/c6"
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / "element_law.dylib"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    start = time.perf_counter()
    subprocess.run(["clang++", *flags, str(source), "-o", str(output)], check=True)
    record = {
        "compiler": compiler,
        "flags": list(flags),
        "source_sha256": source_hash,
        "binary_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "seconds": time.perf_counter() - start,
    }
    (folder / "BUILD.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    try:
        print(json.dumps(build(), indent=2))
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
