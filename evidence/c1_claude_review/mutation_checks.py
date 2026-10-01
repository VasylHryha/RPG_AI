"""Mutation probe of the R002 focused checks (Claude review).

Copies the archived R002 source snapshot plus the accepted C0 receipt into a
scratch directory, applies one deliberate defect at a time, and runs
tests/test_c1.py there. The live checkout and all receipts are never modified.

Run: .venv/bin/python evidence/c1_claude_review/mutation_checks.py <scratch-dir> [--live]
--live probes the current (R005) checkout instead of the archived R002 snapshot.
mutation_checks_r004.json was produced with R004_MUTANTS against R004.
mutation_checks_r003.json was produced by this script's previous R003 mutant list.
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "evidence/c1_review/source"  # exact archived R002 inputs

R002_MUTANTS = {
    "frame_offset_sign_flipped": ("geomind/incremental.py", "offset = offsets[k] - (coordinates[target[k]] - coordinates[source[k]])", "offset = (coordinates[target[k]] - coordinates[source[k]]) - offsets[k]"),
    "regauge_removed": ("geomind/incremental.py", "coordinates[i] -= origins[component]", "coordinates[i] -= 0 * origins[component]"),
    "freed_old_anchor_not_dirty": ("geomind/incremental.py", "dirty |= {index[old.nodes[a]]", "dirty |= set() or {index[old.nodes[a]] for a in () if a"),
    "local_quiet_ignores_update_tolerance": ("geomind/incremental.py", " and alpha * magnitude < self.settings.update_tolerance:", ":"),
    "local_quiet_ignores_update_tolerance_r003": ("geomind/incremental.py", " and alpha * magnitude < self.settings.update_tolerance\n                        if node in forced:", "\n                        if node in forced:"),  # R003 only
    "local_force_ignores_weight": ("geomind/incremental.py", "force += sign * weights[k] * residual", "force += sign * residual"),
    "single_certificate_instead_of_ten": ("geomind/incremental.py", "if stable >= self.settings.stable_sweeps:", "if stable >= 1:"),  # R002 only
    "certificate_forced_step_removed": ("geomind/incremental.py", "                            forced.discard(node)\n                        elif quiet:", "                            forced.discard(node)\n                        if quiet:"),  # R003 only
    "certificate_visits_not_charged": ("geomind/incremental.py", 'spend(len(edges), "certificate_edge_visits")', "pass"),
    "warm_start_reads_not_charged": ("geomind/incremental.py", 'spend(1, "warm_start_edge_visits")\n                    touched.add(k)\n                    a, b', 'touched.add(k)\n                    a, b'),
    "budget_never_enforced": ("geomind/incremental.py", 'if trace["dynamic_edge_visits"] + count > edge_visit_budget:', "if False:"),
    "duplicate_removal_allowed": ("geomind/incremental.py", "if old_counts - new_counts:", "if set(old_counts) - set(new_counts):"),
    "frozen_update_allowed": ("geomind/incremental.py", "        if self._frozen:\n            raise RuntimeError(\"Frozen geometry cannot update", "        if False:\n            raise RuntimeError(\"Frozen geometry cannot update"),
    "local_norm_guard_removed": ("geomind/incremental.py", "if not np.isfinite(magnitude):", "if False:"),
    "reference_rhs_sign_flipped": ("geomind/c1_reference.py", "rhs[i] -= w * np.asarray(d)\n            rhs[j] += w * np.asarray(d)", "rhs[i] += w * np.asarray(d)\n            rhs[j] -= w * np.asarray(d)"),
    "evaluator_energy_gate_removed": ("geomind/run_c1.py", ' and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"]', ""),
    "evaluator_status_equality_ignored": ("geomind/run_c1.py", "statuses_equal &= a.status == b.status", "statuses_equal &= True"),
}

# Current (R004) candidate, reference and evaluator.
R004_MUTANTS = {
    "frame_shift_sign_flipped": ("geomind/incremental.py", "dx = self._edx[k] - (self._x[t] - self._x[s])", "dx = (self._x[t] - self._x[s]) - self._edx[k]"),
    "certificate_skips_neighbors_of_moved_nodes": ("geomind/incremental.py", "                        certify.add(other)\n", "                        pass\n"),
    "certificate_skips_freed_anchors": ("geomind/incremental.py", "tx.dirty = endpoints | set(new_ids) | freed", "tx.dirty = endpoints | set(new_ids)"),
    "certificate_margin_removed": ("geomind/incremental.py", "CERTIFICATE_MARGIN = 1 - 1e-6", "CERTIFICATE_MARGIN = 1.0"),
    "rollback_skips_coordinates": ("geomind/incremental.py", "        for node, (x, y) in self.coordinates.items():\n            state._x[node], state._y[node] = x, y", "        for node, (x, y) in self.coordinates.items():\n            pass"),
    "rollback_skips_journal": ("geomind/incremental.py", "        for undo in reversed(self.journal):", "        for undo in ():"),
    "degree_list_unsorted": ("geomind/incremental.py", "            insort(self._src_w[s], item)", "            self._src_w[s].append(item)"),
    "anchor_tie_break_flipped": ("geomind/incremental.py", "self._names[a] < self._names[b])", "self._names[a] > self._names[b])"),
    "translation_not_charged": ("geomind/incremental.py", 'tx.spend(len(members), "translation_writes")', "pass"),
    "local_reads_not_charged": ("geomind/incremental.py", '                    tx.spend(len(incident), "local_edge_reads")\n                    touched.update(incident)', "                    touched.update(incident)"),
    "budget_never_enforced": ("geomind/incremental.py", 'if self.trace["charged_operations"] + count > self.budget:', "if False:"),
    "fallback_cap_never_enforced": ("geomind/incremental.py", 'if self.trace["fallback_operations"] + count > self.fallback_budget:', "if False:"),
    "fallback_skips_final_certificate": ("geomind/incremental.py", "bad = self._certify(everyone, alpha, tx.spend_fallback, trace)", "bad = []"),
    "query_ignores_anchor_gauge": ("geomind/incremental.py", "dx = (self._x[j] - self._x[anchor]) - (self._x[i] - self._x[anchor])", "dx = self._x[j] - self._x[i]"),
    "duplicate_removal_allowed": ("geomind/incremental.py", "if old_counts - new_counts:", "if set(old_counts) - set(new_counts):"),
    "frozen_apply_allowed": ("geomind/incremental.py", '"""Atomically apply one additive delta; refusals undo every change."""\n        if self._frozen:', '"""Atomically apply one additive delta; refusals undo every change."""\n        if False:'),
    "relation_redefinition_allowed": ("geomind/incremental.py", "or name in catalog or", "or"),
    "forced_certificate_step_removed": ("geomind/incremental.py", "                    elif quiet:\n", "                    if quiet:\n"),
    "local_quiet_ignores_update_tolerance": ("geomind/incremental.py", " and alpha * magnitude < utol\n", "\n"),
    "local_norm_guard_removed": ("geomind/incremental.py", '        if not math.isfinite(magnitude):\n            raise ValueError("Nonfinite local force norm")', "        pass"),
    "reference_rhs_sign_flipped": ("geomind/c1_reference.py", "rhs[i] -= w * np.asarray(d)\n            rhs[j] += w * np.asarray(d)", "rhs[i] += w * np.asarray(d)\n            rhs[j] -= w * np.asarray(d)"),
    "evaluator_energy_gate_removed": ("geomind/run_c1.py", '\n                          and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"])', ")"),
    "evaluator_status_equality_ignored": ("geomind/run_c1.py", "statuses_equal &= a.status == b.status", "statuses_equal &= True"),
}


LIVE = "--live" in sys.argv

# R005: the R004 list adapted to the export-gauge code, plus the independent review's findings.
R005_MUTANTS = {
    "frame_shift_sign_flipped": ("geomind/incremental.py", "dx = self._edx[k] - (self._x[t] - self._x[s])", "dx = (self._x[t] - self._x[s]) - self._edx[k]"),
    "certificate_skips_neighbors_of_moved_nodes": ("geomind/incremental.py", "                        certify.add(other)\n", "                        pass\n"),
    "certificate_skips_freed_anchors": ("geomind/incremental.py", "tx.dirty = endpoints | set(new_ids) | freed", "tx.dirty = endpoints | set(new_ids)"),
    "certificate_skips_translated_nodes": ("geomind/incremental.py", "certify = set(tx.dirty) | tx.translated", "certify = set(tx.dirty)"),
    "rounding_bound_removed": ("geomind/incremental.py", "            upper = magnitude + bound\n", "            upper = magnitude\n"),
    "anchor_change_not_restored": ("geomind/incremental.py", "                if frame == root and best == self._anchor[root]:\n                    continue", "                if frame == root:\n                    continue"),
    "largest_frame_kept_instead_of_anchor_frame": ("geomind/incremental.py", "            root = self._comp[best]\n", "            root = min(group, key=lambda c: (-len(self._members[c]), self._names[previous_anchors[c]]))\n"),
    "degree_overflow_unchecked": ("geomind/incremental.py", "            if not (math.isfinite(self._deg[s]) and math.isfinite(self._deg[t])):", "            if False:"),
    "energy_bound_unchecked": ("geomind/incremental.py", "            if not energy_bound <= ENERGY_LIMIT:", "            if False:"),
    "relation_map_copied": ("geomind/incremental.py", "        fresh = {}\n", "        fresh = {}\n        _copy = dict(self._relation_map)\n"),
    "validation_after_charge": ("geomind/incremental.py", "            self._validate_delta(added_nodes, added_edges, added_relations)\n            tx.spend(input_records + len(added_nodes) + len(added_edges) + len(added_relations), \"input_records\")", "            tx.spend(input_records + len(added_nodes) + len(added_edges) + len(added_relations), \"input_records\")\n            self._validate_delta(added_nodes, added_edges, added_relations)"),
    "rollback_skips_coordinates": ("geomind/incremental.py", "        for node, (x, y) in self.coordinates.items():\n            state._x[node], state._y[node] = x, y", "        for node, (x, y) in self.coordinates.items():\n            pass"),
    "rollback_skips_journal": ("geomind/incremental.py", "        for undo in reversed(self.journal):", "        for undo in ():"),
    "degree_list_unsorted": ("geomind/incremental.py", "            insort(self._src_w[s], item)", "            self._src_w[s].append(item)"),
    "anchor_tie_break_flipped": ("geomind/incremental.py", "self._names[a] < self._names[b])", "self._names[a] > self._names[b])"),
    "translation_not_charged": ("geomind/incremental.py", 'tx.spend(len(members), "translation_writes")', "pass"),
    "local_reads_not_charged": ("geomind/incremental.py", '                    tx.spend(len(incident), "local_edge_reads")\n                    touched.update(incident)', "                    touched.update(incident)"),
    "budget_never_enforced": ("geomind/incremental.py", 'if self.trace["charged_operations"] + count > self.budget:', "if False:"),
    "fallback_cap_never_enforced": ("geomind/incremental.py", 'if self.trace["fallback_operations"] + count > self.fallback_budget:', "if False:"),
    "fallback_skips_final_certificate": ("geomind/incremental.py", "bad, energy = self._certify(everyone, alpha, tx.spend_fallback, trace)", "bad, energy = [], 0.0"),
    "duplicate_removal_allowed": ("geomind/incremental.py", "if old_counts - new_counts:", "if set(old_counts) - set(new_counts):"),
    "frozen_apply_allowed": ("geomind/incremental.py", '"""Atomically apply one additive delta; refusals undo every change."""\n        if self._frozen:', '"""Atomically apply one additive delta; refusals undo every change."""\n        if False:'),
    "relation_redefinition_allowed": ("geomind/incremental.py", "name in self._relation_map or name in fresh or", "name in fresh or"),
    "forced_certificate_step_removed": ("geomind/incremental.py", "                    elif quiet:\n", "                    if quiet:\n"),
    "local_quiet_ignores_update_tolerance": ("geomind/incremental.py", " and alpha * magnitude < utol\n", "\n"),
    "local_norm_guard_removed": ("geomind/incremental.py", '        if not math.isfinite(magnitude):\n            raise ValueError("Nonfinite local force norm")', "        pass"),
    "reference_rhs_sign_flipped": ("geomind/c1_reference.py", "rhs[i] -= w * np.asarray(d)\n            rhs[j] += w * np.asarray(d)", "rhs[i] += w * np.asarray(d)\n            rhs[j] -= w * np.asarray(d)"),
    "baseline_translation_sign_flipped": ("geomind/c1_reference.py", "moving, keep, sx, sy = a, b, xt - xs - e.offset[0], yt - ys - e.offset[1]", "moving, keep, sx, sy = a, b, e.offset[0] - (xt - xs), e.offset[1] - (yt - ys)"),
    "evaluator_energy_gate_removed": ("geomind/run_c1.py", '\n                          and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"])', ")"),
    "evaluator_status_equality_ignored": ("geomind/run_c1.py", "statuses_equal &= a.status == b.status", "statuses_equal &= True"),
    "evaluator_baseline_gate_removed": ("geomind/run_c1.py", "old.export() == saved and baseline_ok", "old.export() == saved"),
    "endpoint_time_rule_removed": ("geomind/run_c1.py", ' and time_ratio <= e["time_locality_max_ratio"])', ")"),
}


def prepare(scratch):
    if scratch.exists():
        shutil.rmtree(scratch)
    if LIVE:
        scratch.mkdir(parents=True)
        for name in ("geomind", "tests", "experiments"):
            shutil.copytree(ROOT / name, scratch / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copyfile(ROOT / name, scratch / name)
        (scratch / "evidence/c1_review/states").mkdir(parents=True)
        for archived in ("evidence/c1_review/states/32_inconsistent_edge_after.json", "evidence/c1_r003/states/32_bridge_w0_after.json", "evidence/c1_r004/states/32_bridge_w0_queue_after.json.gz"):
            (scratch / archived).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / archived, scratch / archived)
    else:
        shutil.copytree(SOURCE, scratch)
    (scratch / "evidence/c0_review").mkdir(parents=True)
    for name in ("results.json", "ACCEPTANCE.md"):
        shutil.copyfile(ROOT / "evidence/c0_review" / name, scratch / "evidence/c0_review" / name)


def run(scratch):
    started = time.perf_counter()
    try:
        result = subprocess.run([str(ROOT / ".venv/bin/python"), "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_c1.py"],
                                cwd=scratch, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        # A suite that cannot finish cannot pass: count the mutant as detected.
        return {"exit": "TIMEOUT", "summary": "timed out after 180 s", "failed": [], "seconds": time.perf_counter() - started}
    tail = [line for line in result.stdout.splitlines() if line.startswith("FAILED") or " passed" in line or " failed" in line]
    return {"exit": result.returncode, "summary": tail[-1] if tail else result.stdout[-300:], "failed": [line.split(" - ")[0] for line in tail if line.startswith("FAILED")], "seconds": time.perf_counter() - started}


def main():
    scratch = Path(sys.argv[1]).resolve()
    prepare(scratch)
    report = {"baseline": run(scratch), "mutants": {}}
    mutants = R005_MUTANTS if LIVE else R002_MUTANTS
    for name, (path, old, new) in mutants.items():
        prepare(scratch)
        target = scratch / path
        text = target.read_text()
        if text.count(old) != 1:
            report["mutants"][name] = {"error": f"pattern occurs {text.count(old)} times"}
            continue
        target.write_text(text.replace(old, new))
        outcome = run(scratch)
        outcome["detected"] = outcome["exit"] != 0
        report["mutants"][name] = outcome
        print(name, "DETECTED" if outcome["detected"] else "SURVIVED", outcome["summary"], flush=True)
    report["detected"] = sum(m.get("detected", False) for m in report["mutants"].values())
    report["total"] = len(mutants)
    target = HERE / ("mutation_checks_r005.json" if LIVE else "mutation_checks.json")
    if target.exists():
        raise FileExistsError("mutation_checks.json exists; do not overwrite reviewer evidence")
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"baseline": report["baseline"]["summary"], "detected": report["detected"], "total": report["total"]}))


if __name__ == "__main__":
    main()
