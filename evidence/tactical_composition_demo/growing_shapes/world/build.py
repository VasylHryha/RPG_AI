"""Build the dependency-free C++17 C ABI and contract, with an identity manifest."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "_build"
LIBRARY = BUILD / ("libgs_world.dylib" if sys.platform == "darwin" else "libgs_world.so")
SOURCES = ("world.h", "world.cpp", "native_contract.cpp", "build.py", "world.py", "../native_guard.py")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(sanitize=False):
    BUILD.mkdir(exist_ok=True)
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    flags = ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-pedantic"]
    if sanitize:
        # Optional diagnostic build, not the optimized speed artifact.
        flags += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
    shared = "-dynamiclib" if sys.platform == "darwin" else "-shared"
    commands = [
        compiler + flags + ["-fPIC", shared, str(ROOT / "world.cpp"), "-o", str(LIBRARY)],
        compiler + flags + [str(ROOT / "world.cpp"), str(ROOT / "native_contract.cpp"),
                            "-o", str(BUILD / "native_contract")],
    ]
    # Remove an old identity before compilation: a failed rebuild cannot look current.
    (BUILD / "build.json").unlink(missing_ok=True)
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    manifest = {
        "commands": commands,
        "compiler": subprocess.check_output(compiler + ["--version"], text=True).splitlines()[0],
        "sanitized": sanitize,
        "source_sha256": {name: digest(ROOT / name) for name in SOURCES},
        "binary_sha256": {path.name: digest(path) for path in (LIBRARY, BUILD / "native_contract")},
    }
    (BUILD / "build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args.sanitize), indent=2))
