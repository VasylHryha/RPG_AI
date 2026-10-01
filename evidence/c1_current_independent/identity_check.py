"""Fresh read-only R005 audit, adapted from the archived R004 review script."""
import re, gzip, hashlib, json, sys, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "evidence/c1_r005"
sha = lambda b: hashlib.sha256(b).hexdigest()
out = {}
raw = (E / "results.json").read_bytes()
r = json.loads(raw)
out["results_sha256"] = sha(raw)
out["manifest_file_sha256"] = sha((ROOT / "experiments/c1_manifest.json").read_bytes())
sys.path.insert(0, str(ROOT))
from geomind.geometry import digest
live_manifest = json.loads((ROOT / "experiments/c1_manifest.json").read_text())
out["manifest_digest_live"] = digest(live_manifest)
out["manifest_digest_receipt"] = r["manifest_hash"]
out["manifest_equal"] = r["manifest"] == live_manifest
fh = r["file_hashes"]
live_bad = [n for n, h in fh.items() if sha((ROOT / n).read_bytes()) != h]
snap_bad = [n for n, h in fh.items() if sha((E / "source" / n).read_bytes()) != h]
snap_files = sorted(str(p.relative_to(E / "source")) for p in (E / "source").rglob("*") if p.is_file())
# Live files that would be hashed now but are not in the receipt (new sources)
live_set = sorted([str(p.relative_to(ROOT)) for p in list((ROOT/"geomind").glob("*.py"))+list((ROOT/"tests").glob("*.py"))+list((ROOT/"experiments").glob("*.json"))] + ["pyproject.toml","uv.lock"])
out.update(file_count=len(fh), live_mismatch=live_bad, snapshot_mismatch=snap_bad,
           snapshot_extra=sorted(set(snap_files) - set(fh)), live_not_in_receipt=sorted(set(live_set) - set(fh)),
           snapshot_hashes_equal=r["source_snapshot_hashes"] == fh)
for name in ("geomind/incremental.py", "geomind/run_c1.py", "geomind/c1_cases.py", "geomind/c1_reference.py", "tests/test_c1.py", "geomind/geometry.py", "geomind/references.py"):
    out[name] = sha((ROOT / name).read_bytes())
# Contract report bound to the source hashes
xml = (E / "contracts.xml").read_bytes()
props = {p.attrib["name"]: p.attrib["value"] for p in ET.fromstring(xml).iter("property")}
cases = list(ET.fromstring(xml).iter("testcase"))
out["contracts_sha256"] = sha(xml)
out["contracts_receipt_sha256"] = r["contracts"]["report_sha256"]
out["contracts_hashes_bound"] = json.loads(props["c1_file_hashes"]) == fh
out["contracts_scope"] = props.get("c1_contract_scope")
out["contracts_cases"] = len(cases)
out["contracts_failures"] = sum(1 for c in cases if list(c.iter("failure")) or list(c.iter("error")) or list(c.iter("skipped")))
# States
inst = r["instances"]
jsonl = [json.loads(l) for l in (E / "instances.jsonl").read_text().splitlines()]
out["instances_jsonl_equal"] = jsonl == inst
state_bad, checked, missing = [], 0, []
def text(name):
    p = E / "states" / f"{name}.json.gz"
    if not p.exists():
        missing.append(name); return None
    return gzip.decompress(p.read_bytes()).decode().rstrip("\n")
for row in inst:
    label = f"{row['nodes']}_{row['kind']}_w{row['replicate']}"
    t = text(f"{label}_before")
    checked += 1
    if t is None or sha(t.encode()) != row["old_artifact_hash"]:
        state_bad.append(label + "_before")
    for arm in ("queue", "fallback"):
        g = row["arms"][arm]
        if not g["committed"]:
            if g["after_artifact_hash"] != g["fork_before_artifact_hash"]:
                state_bad.append(label + f"_{arm}_rollback_not_identical")
            continue
        if arm == "fallback" and not (E / "states" / f"{label}_fallback_after.json.gz").exists():
            if g["after_artifact_hash"] != row["arms"]["queue"]["after_artifact_hash"]:
                state_bad.append(label + "_fallback_not_written_but_differs")
            t = text(f"{label}_queue_after")  # identical export written once
        else:
            t = text(f"{label}_{arm}_after")
        checked += 1
        if t is None or sha(t.encode()) != g["after_artifact_hash"]:
            state_bad.append(label + f"_{arm}_after")
out.update(states_checked=checked, state_mismatch=state_bad, states_missing=missing,
           state_files=len(list((E / "states").glob("*.gz"))))
# Accepted C0 inputs
c0 = json.loads((ROOT / "evidence/c0_review/results.json").read_bytes())
out["c0_inputs"] = len(c0["file_hashes"])
out["c0_changed"] = [n for n, h in c0["file_hashes"].items() if sha((ROOT / n).read_bytes()) != h]
m = re.search(r"Original `results.json` SHA256 at review: `([0-9a-f]{64})`", (ROOT/"evidence/c0_review/ACCEPTANCE.md").read_text())
out["c0_acceptance_bound"] = m is not None and m[1] == sha((ROOT / "evidence/c0_review/results.json").read_bytes())
out["c0_results_sha256"] = sha((ROOT / "evidence/c0_review/results.json").read_bytes())
out["gates"] = r["gates"]; out["hypotheses"] = r["hypotheses"]
print(json.dumps(out, indent=1))
Path(__file__).with_suffix('.out.json').write_text(json.dumps(out, indent=1) + '\n')
