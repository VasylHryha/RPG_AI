"""Additive note-3 check; preserves original receipts/report prefix, tests once.

Only dev/validation 0..255; no speed rerun, growth, learning or judging.
Compares every original observation, action field, seed tag and final score
against the independently built original commit, in addition to the old table.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

from build import build, digest
from verify_world import SOURCE_FILES
from world import Library, Policy, TASKS, World

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
PREFIX = ROOT.relative_to(REPO).as_posix()
BASELINE = "aeb75a73c1d00706ff8e264563ae0f9a554c5f1c"
MARKER = "\n## Additive remember_static (Claude review note 3)\n"


def original(name):
    return subprocess.check_output(["git", "show", f"{BASELINE}:{PREFIX}/{name}"], cwd=REPO)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def table(scores):
    metrics = {"perceive": ("angular_error", "distance_error"),
               "move": ("goal_error", "settle_seconds", "in_range_rate"),
               "remember": ("angular_error",), "choose": ("correct_choice_rate",),
               "chase": ("goal_error", "in_range_rate", "settle_seconds"),
               "pursuit": ("goal_error", "in_range_rate", "settle_seconds"),
               "focus_fire": ("damage_per_second", "in_range_rate")}
    rows = ["| Namespace | Task | Metric | Reference | Random |",
            "|---|---|---|---:|---:|"]
    for ns, tasks in scores.items():
        for task, policies in tasks.items():
            for metric in metrics[task]:
                a, b = (policies[k]["mean"][metric] for k in ("reference", "random"))
                rows.append(f"| {ns} | {task} | {metric} | {a:.6g} | {b:.6g} |")
    return ("\n".join(rows) + "\n").encode()


def streams(baseline, baseline_library, library):
    records = []
    for ns in ("dev", "validation"):
        for task in TASKS[:7]:
            for kind in ("reference", "random"):
                old_hash, new_hash = hashlib.sha256(), hashlib.sha256()
                for seed in range(256):
                    with baseline.World(task, seed, ns, library=baseline_library) as old, \
                            baseline.Policy(task, seed, kind, ns, library=baseline_library) as op, \
                            World(task, seed, ns, library=library) as new, \
                            Policy(task, seed, kind, ns, library=library) as np:
                        assert old.seed_tag == new.seed_tag
                        seed_bytes = struct.pack("<Q", old.seed_tag)
                        old_hash.update(seed_bytes); new_hash.update(seed_bytes)
                        for step in range(161):
                            oo, no = old.observe(), new.observe()
                            assert bytes(oo) == bytes(no), (ns, task, kind, seed, step)
                            old_hash.update(bytes(oo)); new_hash.update(bytes(no))
                            if step == 160:
                                break
                            oa, na = op.action(oo), np.action(no)
                            # Pack fields explicitly; trailing C action padding is not API data.
                            ob = struct.pack("<ddi", oa.angle, oa.magnitude, oa.choice)
                            nb = struct.pack("<ddi", na.angle, na.magnitude, na.choice)
                            assert ob == nb, (ns, task, kind, seed, step)
                            old_hash.update(ob); new_hash.update(nb)
                            old.step(oa); new.step(na)
                        assert bytes(old.score()) == bytes(new.score())
                        old_hash.update(bytes(old.score())); new_hash.update(bytes(new.score()))
                records.append({"namespace": ns, "task": task, "policy": kind,
                                "first_seed": 0, "episodes": 256,
                                "baseline_sha256": old_hash.hexdigest(),
                                "current_sha256": new_hash.hexdigest()})
    return records


def verify():
    started = time.perf_counter()
    baseline_dir = ROOT / "_build" / "original"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    preserved = {name: original(name) for name in ("WORLD_CHECKS.json", "WORLD_TEST_LOG.txt")}
    old_report = original("WORLD_REPORT.md")
    assert (ROOT / "WORLD_REPORT.md").read_bytes().split(MARKER.encode())[0] == old_report
    assert all((ROOT / name).read_bytes() == data for name, data in preserved.items())
    old_receipt = json.loads(preserved["WORLD_CHECKS.json"])
    for name in SOURCE_FILES:
        data = original(name)
        assert hashlib.sha256(data).hexdigest() == old_receipt["source_sha256"][name]
        (baseline_dir / name).write_bytes(data)
    old_build = load("original_build", baseline_dir / "build.py").build()
    current_build = build()
    baseline = load("original_world", baseline_dir / "world.py")
    baseline_library, library = baseline.Library(), Library()
    contract = subprocess.run([str(ROOT / "_build" / "native_contract")],
                              cwd=ROOT, capture_output=True, text=True, check=True)
    current_scores = {ns: {task: {kind: library.evaluate(task, 0, 256, kind, ns).as_dict()
                                for kind in ("reference", "random")}
                           for task in TASKS[:7]} for ns in ("dev", "validation")}
    assert current_scores == old_receipt["scores"], "Original comparison scores changed"
    table_bytes = table(current_scores)
    old_table = old_report.split(b"Reference vs random task scores (reference / random):\n\n")[1].split(b"\nSpeed (")[0]
    assert table_bytes == old_table, "Original comparison table bytes changed"
    (ROOT / "ORIGINAL_COMPARISON_TABLE.md").write_bytes(table_bytes)
    records = streams(baseline, baseline_library, library)
    scores = {ns: {"remember_static": {kind: library.evaluate("remember_static", 0, 256, kind, ns).as_dict()
                                       for kind in ("reference", "random")}}
              for ns in ("dev", "validation")}
    receipt = {"status": "PENDING_TESTS", "baseline_commit": BASELINE,
               "scope": "engine verification only; no judging, growth or learning",
               "source_sha256": {name: digest(ROOT / name) for name in
                                 SOURCE_FILES + ("verify_remember_static.py",)},
               "build": current_build, "baseline_build": old_build,
               "contract": contract.stdout + contract.stderr,
               "scores": scores,
               "compatibility": {"original_scores_equal": True, "original_scores": current_scores,
                                 "original_table_equal": True,
                                 "original_table_sha256": hashlib.sha256(table_bytes).hexdigest(),
                                 "original_artifacts_unchanged": True,
                                 "original_artifact_sha256": {name: hashlib.sha256(data).hexdigest()
                                                              for name, data in preserved.items()},
                                 "original_report_prefix_sha256": hashlib.sha256(old_report).hexdigest(),
                                 "streams": records}}
    receipt_path = ROOT / "REMEMBER_STATIC_CHECKS.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    command = [sys.executable, "-m", "pytest", "-q", "-x", "--confcutdir", str(ROOT),
               "-o", f"cache_dir={ROOT / '.pytest_cache'}", str(ROOT / "test_world.py")]
    test_start = time.perf_counter()
    tests = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    receipt["pytest"] = {"command": command, "returncode": tests.returncode,
                         "seconds": time.perf_counter() - test_start,
                         "output": tests.stdout + tests.stderr}
    receipt["status"] = "PASS" if tests.returncode == 0 else "FAIL"
    receipt["elapsed_seconds"] = time.perf_counter() - started
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    (ROOT / "REMEMBER_STATIC_TEST_LOG.txt").write_text(contract.stdout + contract.stderr + tests.stdout + tests.stderr)
    assert all((ROOT / name).read_bytes() == data for name, data in preserved.items())
    lines = [MARKER.rstrip(), "", "Task id 7 is appended; original task ids 0..6 and ABI layouts are unchanged.",
             "One enemy; stationary agent; initial radius [3,6], HP [10,100],",
             "and the same placement procedure/distributions as remember, with vx=vy=0.",
             "The new task id supplies its own deterministic world and policy streams.",
             "Visible decisions 0..39, hidden 40..159; every hidden value slot is zero.",
             "The target stays at its last visible position. The reference stores that",
             "position and points at it while hidden, without extrapolation. Random uses",
             "the remember policy rule: independent uniform angle [-pi,pi] and magnitude",
             "[0,1] each decision; magnitude is validated but ignored, choice=-1.",
             "Score: mean absolute circular angular error (radians) on 120 hidden decisions.",
             "This implements WORLD_REVIEW.md note 3 only, under decision 0028 item 17.", "",
             "Engine comparison: dev and validation 0..255, 256 episodes per policy.", "",
             "| Namespace | Task | Metric | Reference | Random |", "|---|---|---|---:|---:|"]
    for ns in scores:
        a, b = (scores[ns]["remember_static"][kind]["mean"]["angular_error"]
                for kind in ("reference", "random"))
        lines.append(f"| {ns} | remember_static | angular_error | {a:.6g} | {b:.6g} |")
    lines += ["", "Compatibility: PASS for all seven original tasks, both namespaces and policies.",
              "The rerun comparison table is byte-identical (30 rows); all full-precision",
              "batch score fields also match WORLD_CHECKS.json exactly. Side-by-side builds",
              "from aeb75a7 and current source match every observation (including terminal),",
              "action field, seed tag and final score over 7,168 original episodes.",
              "ORIGINAL_COMPARISON_TABLE.md and REMEMBER_STATIC_CHECKS.json retain this proof.",
              "The original report prefix, WORLD_CHECKS.json and WORLD_TEST_LOG.txt keep their bytes.",
              "Original test cases are retained; their invalid task sentinel now follows TASKS",
              "length, receipt identity uses the additive current receipt, and shared memory",
              "contracts cover the new task. No old benchmark was repeated.", "",
              f"Additive verification status: {receipt['status']}.",
              f"pytest (one invocation): {receipt['pytest']['output'].strip()}.",
              f"Elapsed verification seconds: {receipt['elapsed_seconds']:.3f}.",
              "The report above remains the original historical verification; for this revision use:", "",
              "```sh", f".venv/bin/python {PREFIX}/verify_remember_static.py", "```", "",
              "No growth, learning or judging run occurred. Implementation is REVIEW_READY",
              "for Claude; this check accepts no atom, proposal, experiment or milestone.", ""]
    (ROOT / "WORLD_REPORT.md").write_bytes(old_report + "\n".join(lines).encode())
    print(json.dumps({"status": receipt["status"], "pytest": receipt["pytest"],
                      "original_comparison_table": "byte-identical", "matched_episodes": 7168,
                      "scores": scores, "seconds": receipt["elapsed_seconds"]}, indent=2))
    return tests.returncode


if __name__ == "__main__":
    raise SystemExit(verify())
