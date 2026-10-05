"""One-shot 0g revision-4 runner. Importing this module derives no seeds.

Only the registered output path is supported; there is no resume/output override.
Native workers consume JSON lines, one outstanding request per process, and
retain diagnostics with that request. Each worker handles one arm and one
HEAD cluster or POOL block, with registered timeouts and batch attribution.
"""
import argparse
import collections
import concurrent.futures
import copy
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import statistics
import subprocess
import tempfile
import threading
import time


class Refusal(RuntimeError):
    """Preflight failed: no output directory and no fights are permitted."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("w") as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def derive_seed(root, namespace, index):
    payload = bytes.fromhex(root) + namespace.encode("ascii") + index.to_bytes(8, "big")
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")


def namespace_sizes(spec):
    sizes = {}
    for name, description in spec["seeds"]["namespaces"].items():
        match = re.match(r"i = 0\.\.(\d+) \(", description)
        if not match:
            raise Refusal("Unrecognized namespace size: " + name)
        sizes[name] = int(match[1]) + 1
    return sizes


def development_seeds(base):
    """Read the two declared ledger schemas; malformed/missing ledgers refuse."""
    original = read_json(base / "astelia_cpp/S4_SEED_LEDGER.json")
    amended = read_json(base / "astelia_cpp/s4_amended_development/s4_seeds.json")
    seeds = set(range(2026100500, 2026100530)) | set(range(2026100700, 2026100730))
    seeds.update([101, 102, 301, 302, 303, 701, 702, 703, 704, 811, 812, 813])

    def add_range(bounds):
        if (not isinstance(bounds, list) or len(bounds) != 2
                or any(type(x) is not int for x in bounds)
                or bounds[0] > bounds[1]):
            raise Refusal("Malformed development seed range")
        seeds.update(range(bounds[0], bounds[1] + 1))

    for splits in original["ranges"].values():
        for bounds in splits.values():
            add_range(bounds)
    add_range(original["final_C_head_validation"])
    add_range(original["anomaly"])
    for use in amended["uses"]:
        seed = use["seed"]
        if type(seed) is not int:
            raise Refusal("Malformed amended development seed")
        seeds.add(seed)
    return seeds


def seed_preflight(spec, excluded):
    root = spec["seeds"]["judging_root_hex"]
    if len(bytes.fromhex(root)) != 16:
        raise Refusal("Root must be 128 bits")
    panels, seen = {}, set()
    for namespace, size in namespace_sizes(spec).items():
        values = [derive_seed(root, namespace, i) for i in range(size)]
        for seed in values:
            if seed in seen:
                raise Refusal("Duplicate judging seed within/across namespaces")
            if seed in excluded:
                raise Refusal("Judging/development seed overlap; drafter must replace root")
            seen.add(seed)
        panels[namespace] = values
    return panels


def preflight(spec_path, repo_root):
    """Gates and hashes precede seed derivation. Never invokes the native host."""
    spec_path, repo_root = Path(spec_path), Path(repo_root)
    base = spec_path.parent
    try:
        spec_bytes = spec_path.read_bytes()
        spec = json.loads(spec_bytes)
        if spec["experiment"] != "0g" or spec["revision"] != 4:
            raise Refusal("Only SPEC_0G.json revision 4 is implemented")
        spec_hash = hashlib.sha256(spec_bytes).hexdigest()
        review_path = repo_root / spec["gates"]["codex_review"].split(":", 1)[0]
        review_bytes = review_path.read_bytes()
        review = review_bytes.decode()
        if (review.splitlines()[0].strip() not in ("APPROVE", "APPROVE_WITH_NOTES")
                or not re.search(r"\b" + re.escape(spec_hash) + r"\b", review)):
            raise Refusal("Missing approving Codex review naming this spec sha256")
        auth_path = base / spec["gates"]["authorization_file"].split(":", 1)[0]
        auth_bytes = auth_path.read_bytes()
        auth = json.loads(auth_bytes)
        if auth.get("spec_sha256") != spec_hash:
            raise Refusal("Authorization spec sha256 mismatch")
        for gate in ("delta_approved", "n_approved", "s6_authorized"):
            if auth.get(gate) is not True:
                raise Refusal("Owner gate not true: " + gate)
        if not all(isinstance(auth.get(k), str) and auth[k].strip()
                   for k in ("owner_words", "date")):
            raise Refusal("Authorization must retain owner_words and date")
        binary = base / spec["engine"]["binary"]
        manifest = base / spec["engine"]["build_manifest"]
        binary_hash, manifest_hash = sha256(binary), sha256(manifest)
        if binary_hash != spec["engine"]["binary_sha256"]:
            raise Refusal("Binary sha256 mismatch")
        if manifest_hash != spec["engine"]["build_manifest_sha256"]:
            raise Refusal("Build manifest sha256 mismatch")
        if read_json(manifest).get("binary_sha256") != binary_hash:
            raise Refusal("Manifest does not name admitted binary")
        host = spec["failures"]["host"]
        for field in ("per_fight_timeout_seconds", "worker_shutdown_timeout_seconds"):
            if (type(host[field]) not in (int, float) or not math.isfinite(host[field])
                    or host[field] <= 0):
                raise Refusal("Invalid registered host timeout: " + field)
        seeds = seed_preflight(spec, development_seeds(base))
        identity = {"spec_sha256": spec_hash, "revision": spec["revision"],
                    "root": spec["seeds"]["judging_root_hex"],
                    "binary_sha256": binary_hash, "manifest_sha256": manifest_hash,
                    "authorization_record": auth,
                    "authorization_sha256": hashlib.sha256(auth_bytes).hexdigest(),
                    "review_sha256": hashlib.sha256(review_bytes).hexdigest(), "seeds": seeds,
                    "host": copy.deepcopy(host)}
        return spec, binary, seeds, identity
    except Refusal:
        raise
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise Refusal("Preflight record invalid: " + str(exc)) from exc


def scheduled_keys(spec, seeds):
    keys = []
    head = spec["panels"]["HEAD"]
    for level in head["levels"]:
        for i in range(len(seeds[head["namespace_per_level"][level]])):
            for orientation in head["orientations"]:
                for arm in head["arms"]:
                    keys.append(("HEAD", level, i, orientation, arm))
    pool = spec["panels"]["POOL"]
    for i in range(len(seeds[pool["namespace"]])):
        for doctrine in spec["opponents"]["pool"]["doctrines_in_order"]:
            for orientation in pool["orientations"]:
                for arm in pool["arms"]:
                    keys.append(("POOL", doctrine, i, orientation, arm))
    if len(set(keys)) != len(keys):
        raise Refusal("Duplicate scheduled key")
    return keys


def request_for(spec, seeds, key):
    panel, opponent, i, orientation, arm = key
    request = copy.deepcopy(spec["request_template"])
    request["diagnostics"] = panel == "POOL" and arm == "resonator" and i < 3 and not orientation
    if panel == "HEAD":
        namespace = spec["panels"]["HEAD"]["namespace_per_level"][opponent]
        request["opponent"] = "alone"
        profile = spec["opponents"]["head"][opponent]
    else:
        namespace = spec["panels"]["POOL"]["namespace"]
        request["opponent"] = opponent
        profile = spec["opponents"]["pool"]["profile_for_every_doctrine"]
    request["options"]["seed"] = seeds[namespace][i]
    request["options"]["swapSides"] = orientation
    request["options"]["ai"] = [copy.deepcopy(spec["arms"][panel.lower()][arm]),
                                copy.deepcopy(profile)]
    return request


def scheduled_batches(schedule):
    """One arm x HEAD (level, i) cluster or POOL i block, in schedule order."""
    groups = collections.defaultdict(list)
    for key in schedule:
        panel, opponent, i, _, arm = key
        groups[(panel, opponent if panel == "HEAD" else None, i, arm)].append(key)
    return list(groups.values())


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        return False
    if isinstance(value, dict):
        return all(_finite_tree(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite_tree(v) for v in value)
    return True


def safe_evidence(value):
    """Keep invalid native values in evidence without emitting invalid JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return {"non_finite": repr(value)}
    if isinstance(value, list):
        return [safe_evidence(v) for v in value]
    if isinstance(value, dict):
        return {k: safe_evidence(v) for k, v in value.items()}
    return value


def score_summary(spec, summary):
    if not isinstance(summary, dict) or not _finite_tree(summary):
        raise ValueError("malformed or non-finite summary")
    if "error" in summary:
        raise ValueError("native error: " + str(summary["error"]))
    for field in ("survivors", "enemySurvivors", "t"):
        if type(summary.get(field)) not in (int, float) or summary[field] < 0:
            raise ValueError("malformed summary field: " + field)
    for field in ("survivors", "enemySurvivors"):
        if summary[field] != int(summary[field]):
            raise ValueError("non-integer survivor count: " + field)
    for field in ("crossTeamDealt", "crossTeamTaken", "friendlyDealt", "friendlyTaken",
                  "controllerFailures"):
        vector = summary.get(field)
        if (not isinstance(vector, list) or len(vector) != 2
                or any(type(x) not in (int, float) or x < 0 for x in vector)):
            raise ValueError("malformed summary field: " + field)
    if summary.get("controllerStatus") not in ("completed", "controller_failure"):
        raise ValueError("malformed controllerStatus")
    if summary["controllerStatus"] == "controller_failure" or summary["controllerFailures"][0] > 0:
        return None, "controller_failure"
    options = spec["request_template"]["options"]
    return {"S": summary["survivors"] - summary["enemySurvivors"],
            "D": summary["crossTeamDealt"][0] - summary["crossTeamTaken"][0],
            "friendly_dealt": summary["friendlyDealt"][0],
            "friendly_taken": summary["friendlyTaken"][0],
            "timeout": summary["t"] >= options["duration"] - options["dt"] / 2
                       and summary["survivors"] > 0 and summary["enemySurvivors"] > 0}, None


def fight_record(spec, key, request, summary=None, failure=None, diagnostics=None):
    record = {"kind": "fight", "key": list(key), "request": request,
              "status": "technical_failure", "diagnostics": diagnostics or []}
    if summary is not None:
        record["summary"] = safe_evidence(summary)
    try:
        if failure:
            raise ValueError(failure)
        scores, controller = score_summary(spec, summary)
        if controller:
            record.update(status="controller_failure", reason=controller)
        else:
            record.update(status="completed", scores=scores)
    except ValueError as exc:
        record["reason"] = str(exc)
    return record


def _beta_fraction(a, b, x):
    """Continued fraction for regularized incomplete beta (modified Lentz)."""
    tiny, eps = 1e-300, 3e-14
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) >= tiny else tiny)
    h = d
    for m in range(1, 10001):
        aa = m * (b - m) * x / ((qam + 2 * m) * (a + 2 * m))
        d, c = 1 + aa * d, 1 + aa / c
        d = 1 / (d if abs(d) >= tiny else tiny)
        c = c if abs(c) >= tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + 2 * m) * (qap + 2 * m))
        d, c = 1 + aa * d, 1 + aa / c
        d = 1 / (d if abs(d) >= tiny else tiny)
        c = c if abs(c) >= tiny else tiny
        change = d * c
        h *= change
        if abs(change - 1) <= eps:
            return h
    raise ArithmeticError("Incomplete beta did not converge")


def _beta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    factor = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                      + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return factor * _beta_fraction(a, b, x) / a
    return 1 - factor * _beta_fraction(b, a, 1 - x) / b


def t_critical(alpha, df):
    """Positive t inverse at 1-alpha; alpha remains an exact Fraction in receipts."""
    alpha = Fraction(alpha)
    if df < 1 or not 0 < alpha < Fraction(1, 2):
        raise ValueError("Invalid t-bound parameters")
    target = float(alpha)

    def tail(t):
        return 0.5 * _beta(df / 2, 0.5, df / (df + t * t))

    lo, hi = 0.0, 1.0
    while tail(hi) > target:
        hi *= 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if tail(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def bounds(values, support_alpha, refutation_alpha):
    if len(values) < 2 or not all(math.isfinite(v) for v in values):
        raise ValueError("At least two finite complete sampling units required")
    mean, sd, n = statistics.mean(values), statistics.stdev(values), len(values)
    scale = sd / math.sqrt(n)
    return {"value": mean, "n": n, "sd": sd,
            "lower": mean if sd == 0 else mean - t_critical(support_alpha, n - 1) * scale,
            "upper": mean if sd == 0 else mean + t_critical(refutation_alpha, n - 1) * scale,
            "support_alpha": str(Fraction(support_alpha)),
            "refutation_alpha": str(Fraction(refutation_alpha))}


def verdict(bound, margin):
    if bound["lower"] > margin:
        return "SUPPORTED"
    if bound["upper"] < 0:
        return "REFUTED"
    return "INDETERMINATE"


def evaluate(spec, schedule, records, interrupted=None, *, attempts=None):
    """Evaluate against scheduled keys, never averages partial clusters/blocks."""
    schedule_counts = collections.Counter(schedule)
    # Reconstruct the registered key universe without deriving any seed. Even a
    # missing key in the caller's schedule must not shrink the required set.
    schedule = scheduled_keys(spec, {ns: range(n) for ns, n in namespace_sizes(spec).items()})
    expected = set(schedule)
    by_key, invalid = collections.defaultdict(list), collections.defaultdict(list)
    unknown = []
    for record in records:
        if record.get("kind") == "process_failure":
            for key in record["keys"]:
                invalid[tuple(key)].append(record["reason"])
        elif record.get("kind") == "fight":
            key = tuple(record["key"])
            if key in expected:
                by_key[key].append(record)
            else:
                unknown.append(key)
    attempted = collections.defaultdict(list)
    if attempts is not None:
        for record in attempts:
            key = tuple(record["key"])
            if key in expected:
                attempted[key].append(record)
            else:
                unknown.append(key)

    def issue(key):
        if schedule_counts[key] == 0:
            return "technical_failure: missing scheduled key"
        if schedule_counts[key] != 1 or len(by_key[key]) > 1:
            return "technical_failure: duplicate scheduled key"
        if attempts is not None:
            if len(attempted[key]) > 1:
                return "technical_failure: duplicate attempted key"
            if attempted[key] and not by_key[key]:
                return "technical_failure: unmatched attempt without returned record"
            if by_key[key] and not attempted[key]:
                return "technical_failure: returned record without attempt"
            if by_key[key] and attempted[key][0]["request"] != by_key[key][0]["request"]:
                return "technical_failure: attempt/return request mismatch"
        if key in invalid:
            return "technical_failure: " + "; ".join(invalid[key])
        if not by_key[key]:
            return "technical_failure: missing scheduled key"
        row = by_key[key][0]
        if row["status"] != "completed":
            return row["status"] + ": " + row.get("reason", "failure")
        # Recompute from the summary; do not trust a cached score/status.
        try:
            _, controller = score_summary(spec, row.get("summary"))
            if controller:
                return controller
        except ValueError as exc:
            return "technical_failure: " + str(exc)
        return None

    def score(key):
        return score_summary(spec, by_key[key][0]["summary"])[0]

    def failures(keys):
        return [{"key": list(k), "reason": issue(k)} for k in keys if issue(k)]

    def pending(bad):
        return {"status": "not_run", "value": None, "bounds": None,
                "verdict": "INDETERMINATE", "reason": "Required fights incomplete or failed",
                "failures": bad}

    support = Fraction(spec["alpha"]["support_per_test"])
    refute = Fraction(spec["alpha"]["refutation_per_endpoint"])
    p1_refute = Fraction(spec["alpha"]["refutation_per_P1_level"])
    coverage, subtests = {}, {}
    head_keys = [k for k in schedule if k[0] == "HEAD" and k[4] == "resonator"]
    for level in spec["panels"]["HEAD"]["levels"]:
        keys = [k for k in head_keys if k[1] == level]
        bad = failures(keys)
        if bad:
            subtests[level] = pending(bad)
        else:
            groups = collections.defaultdict(list)
            for k in keys:
                groups[k[2]].append(score(k)["S"])
            values = [statistics.mean(groups[i]) for i in sorted(groups)]
            b = bounds(values, support, p1_refute)
            subtests[level] = {"status": "evaluated", "value": b["value"],
                               "bounds": b, "verdict": verdict(b, 0), "clusters": values}
    p1_bad = failures(head_keys)
    if p1_bad:
        coverage["P1"] = pending(p1_bad)
    else:
        outcomes = [v["verdict"] for v in subtests.values()]
        joint = ("SUPPORTED" if all(v == "SUPPORTED" for v in outcomes)
                 else "REFUTED" if "REFUTED" in outcomes else "INDETERMINATE")
        coverage["P1"] = {"status": "evaluated", "verdict": joint,
                          "value": {k: v["value"] for k, v in subtests.items()},
                          "bounds": {k: v["bounds"] for k, v in subtests.items()}}
    for endpoint, baseline in (("P2", "morale"), ("P3", "pushpull")):
        keys = [k for k in schedule if k[0] == "POOL" and k[4] in ("resonator", baseline)]
        bad = failures(keys)
        if bad:
            coverage[endpoint] = pending(bad)
            continue
        blocks = collections.defaultdict(list)
        for k in keys:
            if k[4] == "resonator":
                other = k[:4] + (baseline,)
                blocks[k[2]].append(score(k)["S"] - score(other)["S"])
        values = [statistics.mean(blocks[i]) for i in sorted(blocks)]
        b = bounds(values, support, refute)
        coverage[endpoint] = {"status": "evaluated", "value": b["value"], "bounds": b,
                              "verdict": verdict(b, spec["delta_survivors"]["value"]),
                              "blocks": values}

    tables = []
    groups = collections.defaultdict(list)
    for key in schedule:
        groups[(key[0], key[1], key[4])].append(key)
    for (panel, opponent, arm), keys in groups.items():
        good = [score(k) for k in keys if not issue(k)]
        row = {"panel": panel, "opponent": opponent, "arm": arm, "scheduled": len(keys),
               "completed": len(good), "failures": len(keys) - len(good),
               "timeouts": sum(s["timeout"] for s in good),
               "complete": len(good) == len(keys)}
        # No apparent full-panel mean from the surviving part of a failed group.
        for field in ("S", "D", "friendly_dealt", "friendly_taken"):
            row["mean_" + field] = statistics.mean(s[field] for s in good) if row["complete"] else None
        tables.append(row)
    for arm in spec["panels"]["POOL"]["arms"]:
        keys = [k for k in schedule if k[0] == "POOL" and k[4] == arm]
        complete = not failures(keys)
        pooled = {"panel": "POOL", "opponent": "equal-weight pool", "arm": arm,
                  "scheduled": len(keys), "completed": sum(not issue(k) for k in keys),
                  "complete": complete}
        for field in ("S", "D", "friendly_dealt", "friendly_taken"):
            pooled["mean_" + field] = statistics.mean(score(k)[field] for k in keys) if complete else None
        pooled["timeouts"] = sum(score(k)["timeout"] for k in keys if not issue(k))
        tables.append(pooled)
    return {"experiment": spec["experiment"], "revision": spec["revision"],
            "run_status": "interrupted" if interrupted else "finished",
            "interruption_reason": interrupted, "scheduled_fights": len(schedule),
            "recorded_fights": sum(len(v) for v in by_key.values()),
            "attempted_fights": None if attempts is None else len(attempts),
            "endpoint_coverage": coverage, "P1_subtests": subtests,
            "descriptive_tables": tables, "unexpected_keys": [list(k) for k in unknown],
            "limits": [spec["statistics"]["assumption"],
                       "Diagnostic candidates and damage/timeout tables are descriptive only."]}


class Journal:
    def __init__(self, path):
        self.file = Path(path).open("a")
        self.lock = threading.Lock()
        self.records = []

    def append(self, record):
        with self.lock:
            self.file.write(json.dumps(record, allow_nan=False) + "\n")
            self.file.flush()
            os.fsync(self.file.fileno())
            self.records.append(record)

    def close(self):
        self.file.close()


def native_batch(binary, spec, seeds, keys, journal, attempts, stop):
    """One registered cluster/block batch; technical host faults veto all keys."""
    lines, process, reader = queue.Queue(), None, None
    host = spec["failures"]["host"]
    fight_timeout = host["per_fight_timeout_seconds"]
    shutdown_timeout = host["worker_shutdown_timeout_seconds"]

    def invalidate(reason, **details):
        journal.append({"kind": "process_failure", "keys": [list(k) for k in keys],
                        "reason": reason, **details})

    with tempfile.TemporaryFile() as errors:
        def read_lines():
            try:
                for line in process.stdout:
                    lines.put(line)
            finally:
                lines.put(None)

        try:
            if sha256(binary) != spec["engine"]["binary_sha256"]:
                invalidate("binary sha256 changed after preflight")
                return
            process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=errors, text=True, bufsize=1)
            reader = threading.Thread(target=read_lines, daemon=True)
            reader.start()
            for key in keys:
                if stop.is_set():
                    break
                request = request_for(spec, seeds, key)
                diagnostics, summary, failure = [], None, None
                # Durable before dispatch, in a separate journal. A hard
                # interruption leaves an unmatched attempt, which is invalid.
                attempts.append({"kind": "attempt", "key": list(key), "request": request})
                try:
                    if not lines.empty():
                        raise ValueError("unsolicited/duplicate native output")
                    process.stdin.write(json.dumps(request, allow_nan=False) + "\n")
                    process.stdin.flush()
                    deadline = time.monotonic() + fight_timeout
                    while True:
                        line = lines.get(timeout=max(0.001, deadline - time.monotonic()))
                        if line is None:
                            raise ValueError("missing summary / native exit")
                        response = json.loads(line)
                        if isinstance(response, dict) and response.get("diagnostics") is True:
                            if not request["diagnostics"] or not _finite_tree(response):
                                raise ValueError("unexpected or non-finite diagnostics")
                            diagnostics.append(safe_evidence(response))
                            if time.monotonic() >= deadline:
                                raise queue.Empty
                            continue
                        summary = response
                        # Malformed summaries/error lines must invalidate prior
                        # returns too. A controller failure is local to this fight.
                        score_summary(spec, summary)
                        break
                except queue.Empty:
                    failure = "host timeout"
                except (OSError, ValueError) as exc:
                    failure = str(exc)
                journal.append(fight_record(spec, key, request, summary, failure, diagnostics))
                if failure:
                    invalidate(failure)
                    process.kill()
                    break  # No retries; the entire batch, including prior returns, is invalid.
        except OSError as exc:
            invalidate("native launch/I/O failed: " + str(exc))
        finally:
            if process is not None:
                try:
                    process.stdin.close()
                except OSError:
                    pass
                try:
                    exit_code = process.wait(timeout=shutdown_timeout)
                except subprocess.TimeoutExpired:
                    invalidate("worker shutdown timeout")
                    process.kill()
                    exit_code = process.wait()
                reader.join(timeout=shutdown_timeout)
                extras = []
                while not lines.empty():
                    line = lines.get_nowait()
                    if line is not None:
                        extras.append(line)
                errors.seek(0)
                stderr = errors.read().decode("utf-8", errors="replace")
                if exit_code or extras or reader.is_alive():
                    invalidate("nonzero native exit" if exit_code else "duplicate native output"
                               if extras else "native output reader did not finish",
                               exit_code=exit_code, stderr=stderr, extra_output=extras)
                process.stdout.close()


def run(spec_path, repo_root, *, workers):
    if type(workers) is not int or workers < 1:
        raise Refusal("Positive integer worker count required")
    spec, binary, seeds, identity = preflight(spec_path, repo_root)
    schedule = scheduled_keys(spec, seeds)
    output = Path(spec_path).parent / spec["execution"]["output_dir"]
    try:
        os.mkdir(output)
    except FileExistsError as exc:
        raise Refusal("One-shot output latch already exists; never delete/reuse/resume it") from exc
    identity.update(workers=workers,
                    started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    dump(output / "identity.json", identity)
    dump(output / "schedule.json", [{"key": list(key), "request": request_for(spec, seeds, key)}
                                    for key in schedule])
    journal = Journal(output / "fights.jsonl")
    attempts = Journal(output / "attempts.jsonl")
    stop, interruption = threading.Event(), None
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
    try:
        batches = scheduled_batches(schedule)
        for panel in ("HEAD", "POOL"):
            futures = [executor.submit(native_batch, binary, spec, seeds, batch,
                                       journal, attempts, stop)
                       for batch in batches if batch[0][0] == panel]
            for future in concurrent.futures.as_completed(futures):
                future.result()
    except BaseException as exc:
        interruption = type(exc).__name__ + ": " + str(exc)
        stop.set()
    finally:
        executor.shutdown(wait=True)
        attempts.close()
        journal.close()
        results = evaluate(spec, schedule, journal.records, interruption, attempts=attempts.records)
        results["identity"] = identity
        dump(output / "results.json", results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    args = parser.parse_args()
    script = Path(__file__).resolve()
    try:
        result = run(script.parents[1] / "SPEC_0G.json", script.parents[3],
                     workers=args.workers)
    except Refusal as exc:
        parser.exit(2, "REFUSED: " + str(exc) + "\n")
    print(json.dumps({k: v["verdict"] for k, v in result["endpoint_coverage"].items()}))
    return 1 if result["run_status"] == "interrupted" else 0


if __name__ == "__main__":
    raise SystemExit(main())
