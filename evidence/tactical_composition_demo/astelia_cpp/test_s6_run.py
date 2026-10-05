"""0g runner tests: fake root/identities only; synthetic executable host only."""
import copy
from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
module_spec = importlib.util.spec_from_file_location("s6_runner_under_test", HERE / "s6_run.py")
s6 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(s6)
FAKE_ROOT = "000102030405060708090a0b0c0d0e0f"


@pytest.fixture(autouse=True)
def forbid_real_root(monkeypatch):
    derive = s6.derive_seed

    def guarded(root, namespace, index):
        assert root == FAKE_ROOT, "Tests may only derive the fake root"
        return derive(root, namespace, index)

    monkeypatch.setattr(s6, "derive_seed", guarded)
    popen = s6.subprocess.Popen

    def stub_only(command, *args, **kwargs):
        binary = Path(command[0])
        assert "fake_repo" in binary.parts, "Tests may only launch a fake-repository stub"
        assert binary.read_text().startswith("#!" + sys.executable + "\n" + STUB)
        return popen(command, *args, **kwargs)

    monkeypatch.setattr(s6.subprocess, "Popen", stub_only)


@pytest.fixture
def spec():
    value = json.loads((HERE.parent / "SPEC_0G.json").read_text())
    # Never pass the on-disk judging root to any runner operation.
    value["seeds"]["judging_root_hex"] = FAKE_ROOT
    return value


STUB = r'''
import json, os, pathlib, sys, time
mode = pathlib.Path(__file__).with_suffix('.mode').read_text().strip()
log = pathlib.Path(__file__).with_suffix('.requests')
output = pathlib.Path(__file__).parents[1] / 's6_run'
identity = output / 'identity.json'
schedule = json.loads((output / 'schedule.json').read_text())
assert identity.is_file(), 'identity must precede worker launch'
batch = None
returns = 0
for line in sys.stdin:
    assert identity.is_file(), 'identity must precede the first fight'
    request = json.loads(line)
    key = next(row['key'] for row in schedule if row['request'] == request)
    current = (key[0], key[1] if key[0] == 'HEAD' else None, key[2], key[4])
    batch = batch or current
    assert current == batch, 'worker mixed clusters/blocks/arms/panels'
    attempts = [json.loads(line) for line in (output / 'attempts.jsonl').read_text().split('\n')[:-1]]
    assert any(row['key'] == key and row['request'] == request for row in attempts), 'send before attempt'
    arm = request['options']['ai'][0]['controller']
    panel = 'HEAD' if 'level' in request['options']['ai'][1] else 'POOL'
    with log.open('a') as f:
        f.write(json.dumps(request) + '\n')
    if mode == 'strict_template':
        assert set(request) == {'trace', 'debug', 'mode', 's3', 'diagnostics', 'opponent', 'options'}
        assert 'request_template_note' not in request and 'comment' not in request
    if mode.startswith('late_') and arm == 'morale' and panel == 'POOL' and key[2] == 0 and returns == 1:
        if mode == 'late_timeout':
            time.sleep(2)
        elif mode == 'late_malformed':
            print('{bad json', flush=True)
            continue
        elif mode == 'late_missing':
            sys.exit(0)
    if mode == 'timeout' and arm == 'resonator' and panel == 'HEAD':
        time.sleep(2)
    if mode == 'error' and arm == 'resonator' and panel == 'HEAD':
        print(json.dumps({'error':'synthetic error'}), flush=True)
        continue
    if mode == 'missing' and arm == 'resonator' and panel == 'HEAD':
        sys.exit(0)
    if mode == 'malformed' and arm == 'resonator' and panel == 'HEAD':
        print('{bad json', flush=True)
        continue
    if mode == 'nonzero' and arm == 'nearest':
        sys.exit(7)
    if mode == 'nonzero_required' and arm == 'resonator' and panel == 'POOL':
        sys.exit(7)
    failure = mode == 'controller' and arm == 'resonator' and panel == 'HEAD'
    score = {'resonator': 10, 'morale': 0, 'pushpull': 1, 'nearest': -2}[arm]
    summary = dict(survivors=20 + score, enemySurvivors=20, t=150,
        crossTeamDealt=[100, 50], crossTeamTaken=[30, 40],
        friendlyDealt=[3, 2], friendlyTaken=[4, 1],
        controllerStatus='controller_failure' if failure else 'completed',
        controllerFailures=[1 if failure else 0, 0])
    if mode == 'nan' and arm == 'resonator' and panel == 'HEAD':
        summary['survivors'] = float('nan')
    if request['diagnostics']:
        print(json.dumps(dict(diagnostics=True, second=1, t=1, sides=[])), flush=True)
    print(json.dumps(summary), flush=True)
    returns += 1
    if mode == 'duplicate' and arm == 'nearest':
        print(json.dumps(summary), flush=True)
if mode == 'late_nonzero' and arm == 'morale' and panel == 'POOL' and key[2] == 0:
    sys.exit(9)
if mode == 'shutdown_timeout' and arm == 'morale' and panel == 'POOL' and key[2] == 0:
    time.sleep(2)
'''


def rebind(fake):
    """Refresh fake registration/review/auth hashes after a fixture edit."""
    s6.dump(fake["spec_path"], fake["spec"])
    digest = s6.sha256(fake["spec_path"])
    fake["review"].parent.mkdir(parents=True, exist_ok=True)
    fake["review"].write_text("APPROVE_WITH_NOTES\nReviewer family: Codex\nSPEC_0G.json sha256 " + digest + "\n")
    s6.dump(fake["auth"], dict(spec_sha256=digest, delta_approved=True, n_approved=True,
                               s6_authorized=True, owner_words="Synthetic test approval", date="test-only"))


@pytest.fixture
def fake(tmp_path, spec):
    repo = tmp_path / "fake_repo"
    base = repo / "evidence/tactical_composition_demo"
    cpp = base / "astelia_cpp"
    build = cpp / "build"
    build.mkdir(parents=True)
    binary = build / "astelia_native"
    binary.write_text("#!" + sys.executable + "\n" + STUB)
    binary.chmod(0o755)
    binary.with_suffix(".mode").write_text("normal")
    manifest = base / spec["engine"]["build_manifest"]
    s6.dump(manifest, {"binary_sha256": s6.sha256(binary)})
    # Keep revision 4's registered paths; replace only artifact identities.
    spec["engine"]["binary_sha256"] = s6.sha256(binary)
    spec["engine"]["build_manifest_sha256"] = s6.sha256(manifest)
    # Tiny synthetic panel for subprocess integration, not real judging entropy.
    for ns in spec["seeds"]["namespaces"]:
        spec["seeds"]["namespaces"][ns] = "i = 0..1 (2 synthetic units)"
    s6.dump(cpp / "S4_SEED_LEDGER.json", {
        "ranges": {"A": {"tuning": [1000, 1002], "validation": [1010, 1011]}},
        "final_C_head_validation": [1020, 1021], "anomaly": [1030, 1031]})
    amended = cpp / "s4_amended_development/s4_seeds.json"
    amended.parent.mkdir()
    s6.dump(amended, {"uses": [{"seed": 2000}, {"seed": 2001}]})
    value = dict(repo=repo, base=base, cpp=cpp, binary=binary, manifest=manifest, spec=spec,
                 spec_path=base / "SPEC_0G.json", output=cpp / "s6_run",
                 review=repo / spec["gates"]["codex_review"].split(":", 1)[0],
                 auth=cpp / "S6_AUTHORIZATION.json", amended=amended)
    rebind(value)
    return value


def synthetic_summary(S=10, **changes):
    row = dict(survivors=20 + max(S, 0), enemySurvivors=20 + max(-S, 0), t=150,
               crossTeamDealt=[100, 50], crossTeamTaken=[30, 40], friendlyDealt=[3, 2],
               friendlyTaken=[4, 1], controllerStatus="completed", controllerFailures=[0, 0])
    row.update(changes)
    return row


def schedule_data(spec, scoring=None):
    # No seed derivation is needed for statistical tests.
    seeds = {ns: list(range(50000, 50000 + n)) for ns, n in s6.namespace_sizes(spec).items()}
    schedule = s6.scheduled_keys(spec, seeds)
    scoring = scoring or (lambda k: {"resonator": 10, "morale": 0, "pushpull": 1, "nearest": -2}[k[4]])
    rows = [s6.fight_record(spec, key, s6.request_for(spec, seeds, key), synthetic_summary(scoring(key)))
            for key in schedule]
    return seeds, schedule, rows


def check_coverage(result):
    assert set(result["endpoint_coverage"]) == {"P1", "P2", "P3"}
    for endpoint in result["endpoint_coverage"].values():
        assert endpoint["status"] in ("evaluated", "not_run")
        assert endpoint["verdict"] in ("SUPPORTED", "REFUTED", "INDETERMINATE")
        if endpoint["status"] == "evaluated":
            assert endpoint["value"] is not None and endpoint["bounds"] is not None
        else:
            assert endpoint["reason"]


def test_seed_byte_example():
    # Written out by hand: 16 root bytes, ASCII TEST=54 45 53 54,
    # uint64 big-endian i=1 is 00 00 00 00 00 00 00 01.
    # SHA256 of 000102030405060708090a0b0c0d0e0f544553540000000000000001
    # = 68d88620d4953e488a2a15fd8e46932a652cd088113696ffbba25c8468d1cfff.
    assert s6.derive_seed(FAKE_ROOT, "TEST", 1) == 0x68D88620
    assert s6.derive_seed(FAKE_ROOT, "TEST", 0) != 0x68D88620
    with pytest.raises(UnicodeEncodeError):
        s6.derive_seed(FAKE_ROOT, "é", 0)


def test_registered_schedule_and_diagnostics(spec):
    seeds, schedule, rows = schedule_data(spec)
    assert len(schedule) == 6464 and len(set(schedule)) == 6464
    assert sum(k[0] == "HEAD" for k in schedule) == 1600
    batches = s6.scheduled_batches(schedule)
    assert len(batches) == 928
    assert sum(len(batch) == 2 for batch in batches) == 800
    assert sum(len(batch) == 38 for batch in batches) == 128
    assert {key for batch in batches for key in batch} == set(schedule)
    assert sum(map(len, batches)) == len(schedule)
    for batch in batches:
        assert len({(k[0], k[1] if k[0] == "HEAD" else None, k[2], k[4]) for k in batch}) == 1
    diagnostic = [r for r in rows if r["request"]["diagnostics"]]
    assert len(diagnostic) == 57
    assert all(r["key"][0] == "POOL" and r["key"][2] in (0, 1, 2)
               and r["key"][3] is False and r["key"][4] == "resonator" for r in diagnostic)
    # The registered shared POOL seed is identical across every arm/doctrine/orientation.
    for i in (0, 31):
        assert {r["request"]["options"]["seed"] for r in rows
                if r["key"][0] == "POOL" and r["key"][2] == i} == {seeds["POOL"][i]}
    result = s6.evaluate(spec, schedule, rows)
    assert result["P1_subtests"]["novice"]["bounds"]["n"] == 100
    assert result["P1_subtests"]["regular"]["bounds"]["n"] == 100
    assert result["endpoint_coverage"]["P2"]["bounds"]["n"] == 32
    assert result["endpoint_coverage"]["P3"]["bounds"]["n"] == 32
    check_coverage(result)


@pytest.mark.parametrize("panel", ["HEAD", "POOL"])
def test_requests_every_field(spec, panel):
    seeds = {ns: [50000 + i for i in range(n)] for ns, n in s6.namespace_sizes(spec).items()}
    opponents = (["novice", "regular"] if panel == "HEAD"
                 else spec["opponents"]["pool"]["doctrines_in_order"])
    for opponent in opponents:
        for arm in ("resonator", "morale", "pushpull", "nearest"):
            for orientation in (False, True):
                for i in (0, 3):
                    key = (panel, opponent, i, orientation, arm)
                    actual = s6.request_for(spec, seeds, key)
                    profile = (spec["opponents"]["head"][opponent] if panel == "HEAD"
                               else spec["opponents"]["pool"]["profile_for_every_doctrine"])
                    expected = {
                        "trace": False, "debug": False, "mode": "alone", "s3": True,
                        "diagnostics": panel == "POOL" and arm == "resonator" and i == 0 and not orientation,
                        "opponent": "alone" if panel == "HEAD" else opponent,
                        "options": {"rules": "game", "scenario": "mirror", "sandboxAbilities": False,
                                    "perception": False, "duration": 150, "dt": 0.03333333333333333,
                                    "army": {"melee": 10, "ranged": 30, "artillery": 10},
                                    "seed": 50000 + i, "swapSides": orientation,
                                    "ai": [spec["arms"][panel.lower()][arm], profile]}}
                    assert actual == expected
                    # Returned requests own every nested dictionary/list.
                    actual["options"]["ai"][0]["params"]["unexpected"] = 1
                    assert "unexpected" not in spec["arms"][panel.lower()][arm]["params"]


@pytest.mark.parametrize("gate", ["delta_approved", "n_approved", "s6_authorized"])
@pytest.mark.parametrize("invalid", [False, 1, None])
def test_owner_gate_refuses_before_seed_derivation(fake, monkeypatch, gate, invalid):
    auth = s6.read_json(fake["auth"])
    auth[gate] = invalid
    s6.dump(fake["auth"], auth)
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Gate refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match=gate):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("record", ["review", "auth", "ledger"])
def test_missing_gate_or_ledger(fake, record):
    path = fake["cpp"] / "S4_SEED_LEDGER.json" if record == "ledger" else fake[record]
    path.unlink()
    with pytest.raises(s6.Refusal):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("first", ["CHANGES_REQUIRED", "APPROVE_WITH_NOTES extra", "", "SUPPORTED"])
def test_review_first_line_refusal(fake, first):
    fake["review"].write_text(first + "\n" + s6.sha256(fake["spec_path"]))
    with pytest.raises(s6.Refusal, match="review"):
        s6.preflight(fake["spec_path"], fake["repo"])


@pytest.mark.parametrize("record", ["review", "auth"])
def test_gate_wrong_spec_hash(fake, record):
    if record == "review":
        fake["review"].write_text("APPROVE\n" + "0" * 64)
    else:
        auth = s6.read_json(fake["auth"])
        auth["spec_sha256"] = "0" * 64
        s6.dump(fake["auth"], auth)
    with pytest.raises(s6.Refusal, match="sha256"):
        s6.preflight(fake["spec_path"], fake["repo"])


def test_unregistered_approving_review_cannot_replace_named_rejection(fake, monkeypatch):
    alternate = fake["review"].with_name("tactical_0g_spec_review_codex_r3.md")
    alternate.write_text("APPROVE\n" + s6.sha256(fake["spec_path"]))
    fake["review"].write_text("CHANGES_REQUIRED\n" + "0" * 64)
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Review refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match="review"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


def test_review_path_is_registered_not_inferred(fake, monkeypatch):
    original = fake["review"]
    review = original.with_name("declared_review.md")
    fake["spec"]["gates"]["codex_review"] = (
        "docs/reviews/declared_review.md: first line APPROVE or APPROVE_WITH_NOTES, "
        "and it names this file's sha256")
    fake["review"] = review
    rebind(fake)
    original.write_text("CHANGES_REQUIRED\n" + s6.sha256(fake["spec_path"]))
    _, _, _, identity = s6.preflight(fake["spec_path"], fake["repo"])
    assert identity["review_sha256"] == s6.sha256(review)
    review.unlink()
    original.write_text("APPROVE\n" + s6.sha256(fake["spec_path"]))
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Review refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match="Preflight record invalid"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("field", ["owner_words", "date"])
def test_authorization_provenance_required(fake, field):
    auth = s6.read_json(fake["auth"])
    del auth[field]
    s6.dump(fake["auth"], auth)
    with pytest.raises(s6.Refusal, match="owner_words and date"):
        s6.preflight(fake["spec_path"], fake["repo"])


@pytest.mark.parametrize("artifact", ["binary", "manifest"])
def test_binary_and_manifest_hash_refusal(fake, monkeypatch, artifact):
    with fake[artifact].open("a") as stream:
        stream.write("\nmodified\n")
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Hash refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match="sha256 mismatch"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


def test_manifest_binary_binding(fake):
    s6.dump(fake["manifest"], {"binary_sha256": "0" * 64})
    fake["spec"]["engine"]["build_manifest_sha256"] = s6.sha256(fake["manifest"])
    rebind(fake)
    with pytest.raises(s6.Refusal, match="admitted binary"):
        s6.preflight(fake["spec_path"], fake["repo"])


def test_manifest_path_is_registered_not_inferred(fake, monkeypatch):
    manifest = fake["base"] / "declared_manifest.json"
    fake["manifest"].rename(manifest)
    fake["spec"]["engine"]["build_manifest"] = "declared_manifest.json"
    rebind(fake)
    _, _, _, identity = s6.preflight(fake["spec_path"], fake["repo"])
    assert identity["manifest_sha256"] == s6.sha256(manifest)
    manifest.unlink()
    # A valid sibling manifest cannot substitute for the registered missing file.
    s6.dump(fake["manifest"], {"binary_sha256": s6.sha256(fake["binary"])})
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Path refusal must precede seeds"))
    with pytest.raises(s6.Refusal):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


def test_manifest_path_explanation_is_literal_and_refuses(fake, monkeypatch):
    # Regression for revision 3's defective path: never strip prose or infer a file.
    fake["spec"]["engine"]["build_manifest"] += (
        " (its binary_sha256 field must equal engine.binary_sha256)")
    rebind(fake)
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Path refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match="Preflight record invalid"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


def test_revision4_registered_paths_and_identities(fake):
    spec = fake["spec"]
    assert spec["revision"] == 4
    assert spec["gates"]["codex_review"].split(":", 1)[0] == (
        "docs/reviews/tactical_0g_spec_review_codex_r4.md")
    assert spec["engine"]["build_manifest"] == "astelia_cpp/build/astelia_native.build.json"
    admitted, binary, _, identity = s6.preflight(fake["spec_path"], fake["repo"])
    assert admitted == spec and binary == fake["binary"]
    assert identity["revision"] == 4
    assert identity["spec_sha256"] == s6.sha256(fake["spec_path"])
    assert identity["binary_sha256"] == spec["engine"]["binary_sha256"]
    assert identity["manifest_sha256"] == spec["engine"]["build_manifest_sha256"]
    assert identity["review_sha256"] == s6.sha256(fake["review"])


@pytest.mark.parametrize("record,field", [("gates", "codex_review"), ("engine", "build_manifest")])
def test_missing_registered_path_refuses_before_seeds(fake, monkeypatch, record, field):
    del fake["spec"][record][field]
    rebind(fake)
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Path refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match=field):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("revision", [1, 2, 3, 5])
def test_other_revisions_refused(fake, revision):
    fake["spec"]["revision"] = revision
    rebind(fake)
    with pytest.raises(s6.Refusal, match="revision 4"):
        s6.preflight(fake["spec_path"], fake["repo"])


def test_registered_host_timeouts(spec):
    assert spec["failures"]["host"]["per_fight_timeout_seconds"] == 120
    assert spec["failures"]["host"]["worker_shutdown_timeout_seconds"] == 30


def test_cli_has_no_host_timeout_override(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["s6_run.py", "--host-timeout", "120"])
    monkeypatch.setattr(s6, "run", lambda *a, **k: pytest.fail("Unsupported flag must precede run"))
    with pytest.raises(SystemExit) as exc:
        s6.main()
    assert exc.value.code == 2


@pytest.mark.parametrize("field", ["per_fight_timeout_seconds", "worker_shutdown_timeout_seconds"])
@pytest.mark.parametrize("value", [0, -1, True, "120", None])
def test_invalid_registered_host_timeout_refused_before_seeds(fake, monkeypatch, field, value):
    fake["spec"]["failures"]["host"][field] = value
    rebind(fake)
    monkeypatch.setattr(s6, "derive_seed", lambda *a: pytest.fail("Timeout refusal must precede seeds"))
    with pytest.raises(s6.Refusal, match="registered host timeout"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("first", ["APPROVE", "APPROVE_WITH_NOTES"])
def test_both_approving_gate_verdicts(fake, first):
    fake["review"].write_text(first + "\nSpec sha256: " + s6.sha256(fake["spec_path"]))
    _, _, seeds, _ = s6.preflight(fake["spec_path"], fake["repo"])
    assert sum(map(len, seeds.values())) == 6


def test_duplicate_scheduled_key_refused_before_latch(fake):
    fake["spec"]["panels"]["HEAD"]["orientations"] = [False, False]
    rebind(fake)
    with pytest.raises(s6.Refusal, match="Duplicate scheduled key"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("cross_namespace", [False, True])
def test_seed_duplicate_preflight(fake, monkeypatch, cross_namespace):
    sizes = s6.namespace_sizes(fake["spec"])
    offsets = {ns: (j + 1) * 100000 for j, ns in enumerate(sizes)}
    if cross_namespace:
        offsets["P1_regular"] = offsets["P1_novice"]
    monkeypatch.setattr(s6, "derive_seed", lambda root, ns, i: offsets[ns] + (i if cross_namespace else 0))
    with pytest.raises(s6.Refusal, match="Duplicate"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


@pytest.mark.parametrize("seed", [101, 102, 301, 303, 701, 704, 811, 813,
                                   2026100500, 2026100529, 2026100700, 2026100729,
                                   1000, 1002, 1010, 1011, 1020, 1021, 1030, 1031, 2000, 2001])
def test_development_overlap_each_source(fake, monkeypatch, seed):
    monkeypatch.setattr(s6, "derive_seed", lambda *a: seed)
    with pytest.raises(s6.Refusal, match="overlap"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert not fake["output"].exists()


def test_preflight_all_seeds_and_latch(fake, monkeypatch):
    fake["spec"]["seeds"]["namespaces"] = {
        "P1_novice": "i = 0..99 (100 clusters)", "P1_regular": "i = 0..99 (100 clusters)",
        "POOL": "i = 0..31 (32 seed blocks)"}
    rebind(fake)
    _, _, seeds, identity = s6.preflight(fake["spec_path"], fake["repo"])
    assert sum(map(len, seeds.values())) == 232
    assert len(set(v for values in seeds.values() for v in values)) == 232
    assert identity["root"] == FAKE_ROOT
    fake["output"].mkdir()
    sentinel = fake["output"] / "KEEP"
    sentinel.write_text("one-shot")
    monkeypatch.setattr(s6.subprocess, "Popen", lambda *a, **k: pytest.fail("Latch must precede host"))
    with pytest.raises(s6.Refusal, match="latch"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert sentinel.read_text() == "one-shot"
    assert list(fake["output"].iterdir()) == [sentinel]


@pytest.mark.parametrize("alpha", [Fraction(1, 400), Fraction(1, 1200), Fraction(1, 2400)])
def test_t_quantiles_against_closed_forms(alpha):
    # Student t(df=1) is Cauchy; df=2 has an algebraic CDF.
    assert s6.t_critical(alpha, 1) == pytest.approx(1 / math.tan(math.pi * float(alpha)), rel=2e-11)
    p = 1 - 2 * float(alpha)
    expected = math.sqrt(2) * p / math.sqrt(1 - p * p)
    assert s6.t_critical(alpha, 2) == pytest.approx(expected, rel=2e-11)


@pytest.mark.parametrize("df", [31, 99])
@pytest.mark.parametrize("alpha", [Fraction(1, 400), Fraction(1, 1200), Fraction(1, 2400)])
def test_registered_t_quantiles_by_independent_integration(df, alpha):
    # Independently integrate the t density with composite Simpson quadrature.
    critical = s6.t_critical(alpha, df)
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    steps, total = 4000, 0.0
    width = critical / steps
    for i in range(steps + 1):
        density = c * (1 + (i * width) ** 2 / df) ** (-(df + 1) / 2)
        total += density * (1 if i in (0, steps) else 4 if i % 2 else 2)
    tail = 0.5 - total * width / 3
    assert tail == pytest.approx(float(alpha), abs=2e-12)


def test_bounds_sample_sd_exact_alpha_and_zero_variance(monkeypatch):
    calls = []

    def critical(alpha, df):
        calls.append((alpha, df))
        return 2

    monkeypatch.setattr(s6, "t_critical", critical)
    result = s6.bounds([1, 3], Fraction(1, 400), Fraction(1, 2400))
    assert result["value"] == 2 and result["sd"] == pytest.approx(math.sqrt(2))
    assert result["lower"] == pytest.approx(0) and result["upper"] == pytest.approx(4)
    assert calls == [(Fraction(1, 400), 1), (Fraction(1, 2400), 1)]
    calls.clear()
    result = s6.bounds([4] * 32, "1/400", "1/1200")
    assert result["lower"] == result["upper"] == result["value"] == 4
    assert calls == []


@pytest.mark.parametrize("lower,upper,margin,want", [
    (4, 5, 4, "INDETERMINATE"), (4.001, 5, 4, "SUPPORTED"),
    (-2, 0, 4, "INDETERMINATE"), (-2, -.001, 4, "REFUTED"),
    (0, 1, 0, "INDETERMINATE"), (.001, 1, 0, "SUPPORTED")])
def test_strict_verdict_comparisons(lower, upper, margin, want):
    assert s6.verdict({"lower": lower, "upper": upper}, margin) == want


@pytest.mark.parametrize("novice,regular,want", [
    (10, 10, "SUPPORTED"), (10, 0, "INDETERMINATE"), (0, 10, "INDETERMINATE"),
    (0, 0, "INDETERMINATE"), (-1, 10, "REFUTED"), (10, -1, "REFUTED"),
    (0, -1, "REFUTED"), (-1, -1, "REFUTED")])
def test_p1_intersection_union_and_union_refutation(fake, novice, regular, want):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec, lambda k: novice if k[0] == "HEAD" and k[1] == "novice"
                                   else regular if k[0] == "HEAD" else 10 if k[4] == "resonator" else 0)
    result = s6.evaluate(spec, keys, rows)
    assert result["endpoint_coverage"]["P1"]["verdict"] == want
    for level in ("novice", "regular"):
        bound = result["P1_subtests"][level]["bounds"]
        assert bound["support_alpha"] == "1/400" and bound["refutation_alpha"] == "1/2400"
    check_coverage(result)


@pytest.mark.parametrize("endpoint,baseline", [("P2", "morale"), ("P3", "pushpull")])
@pytest.mark.parametrize("difference,want", [(5, "SUPPORTED"), (-1, "REFUTED"),
                                             (4, "INDETERMINATE"), (0, "INDETERMINATE")])
def test_p2_p3_verdicts(fake, endpoint, baseline, difference, want):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec, lambda k: 10 if k[4] == "resonator"
                                   else 10 - difference if k[4] == baseline else 0)
    result = s6.evaluate(spec, keys, list(reversed(rows)))
    value = result["endpoint_coverage"][endpoint]
    assert value["value"] == difference and value["verdict"] == want
    assert value["bounds"]["support_alpha"] == "1/400"
    assert value["bounds"]["refutation_alpha"] == "1/1200"
    check_coverage(result)


def test_pairing_orientations_equal_doctrines_and_blocks(fake):
    spec = fake["spec"]
    doctrines = spec["opponents"]["pool"]["doctrines_in_order"]

    def values(k):
        if k[0] == "HEAD":
            return 2 + 2 * int(k[3]) + 4 * k[2]
        if k[4] != "resonator":
            return 0
        return doctrines.index(k[1]) + 2 * int(k[3]) + 4 * k[2]

    _, keys, rows = schedule_data(spec, values)
    result = s6.evaluate(spec, keys, rows[::2] + rows[1::2])
    assert result["P1_subtests"]["novice"]["clusters"] == [3, 7]
    for endpoint in ("P2", "P3"):
        assert result["endpoint_coverage"][endpoint]["blocks"] == [10, 14]
        assert result["endpoint_coverage"][endpoint]["bounds"]["n"] == 2


@pytest.mark.parametrize("failure_kind", ["controllerStatus", "controllerFailures", "technical", "missing",
                                           "duplicate", "schedule_missing", "schedule_duplicate"])
@pytest.mark.parametrize("panel,arm,affected", [
    ("POOL", "morale", ("P2",)), ("POOL", "pushpull", ("P3",)),
    ("POOL", "resonator", ("P2", "P3")), ("HEAD", "resonator", ("P1",))])
def test_required_failure_no_partial_averaging(fake, failure_kind, panel, arm, affected):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec)
    target = next(r for r in rows if r["key"][0] == panel and r["key"][4] == arm)
    if failure_kind in ("controllerStatus", "controllerFailures"):
        summary = copy.deepcopy(target["summary"])
        summary[failure_kind] = "controller_failure" if failure_kind == "controllerStatus" else [1, 0]
        replacement = s6.fight_record(spec, target["key"], target["request"], summary)
        rows[rows.index(target)] = replacement
    elif failure_kind == "technical":
        rows[rows.index(target)] = s6.fight_record(spec, target["key"], target["request"], failure="native error")
    elif failure_kind == "missing":
        rows.remove(target)
    elif failure_kind == "duplicate":
        rows.append(copy.deepcopy(target))
    elif failure_kind == "schedule_missing":
        keys.remove(tuple(target["key"]))
    else:
        keys.append(tuple(target["key"]))
    result = s6.evaluate(spec, keys, rows)
    for name, endpoint in result["endpoint_coverage"].items():
        if name in affected:
            assert endpoint["verdict"] == "INDETERMINATE"
            assert endpoint["value"] is None and endpoint["bounds"] is None
            assert endpoint["failures"] and all(f["reason"] for f in endpoint["failures"])
        else:
            assert endpoint["verdict"] == "SUPPORTED"
    assert next(t for t in result["descriptive_tables"] if t["arm"] == arm
                and t["panel"] == panel)["mean_S"] is None
    check_coverage(result)


def test_partial_head_cluster_and_failed_p1_level_cannot_refute_joint(fake):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec, lambda k: -10 if k[0] == "HEAD" and k[1] == "regular" else 10)
    target = next(r for r in rows if r["key"][0] == "HEAD" and r["key"][1] == "novice"
                  and r["key"][4] == "resonator")
    rows.remove(target)
    result = s6.evaluate(spec, keys, rows)
    assert result["P1_subtests"]["novice"]["value"] is None
    assert result["P1_subtests"]["regular"]["verdict"] == "REFUTED"
    assert result["endpoint_coverage"]["P1"]["verdict"] == "INDETERMINATE"
    assert all(result["endpoint_coverage"][p]["status"] == "evaluated" for p in ("P2", "P3"))


@pytest.mark.parametrize("panel,arm", [("HEAD", "morale"), ("HEAD", "pushpull"),
                                       ("HEAD", "nearest"), ("POOL", "nearest")])
def test_descriptive_failures_veto_nothing(fake, panel, arm):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec)
    for index, row in enumerate(rows):
        if row["key"][0] == panel and row["key"][4] == arm:
            rows[index] = s6.fight_record(spec, row["key"], row["request"], failure="descriptive only")
    result = s6.evaluate(spec, keys, rows)
    assert all(e["verdict"] == "SUPPORTED" for e in result["endpoint_coverage"].values())


@pytest.mark.parametrize("changes", [{"survivors": float("nan")}, {"t": float("inf")},
    {"crossTeamTaken": [float("nan"), 0]}, {"controllerFailures": []}, {"survivors": "3"},
    {"friendlyTaken": None}, {"controllerStatus": None}, {"survivors": 1.5},
    {"extra": {"nonfinite": float("inf")}}])
def test_malformed_nonfinite_summary(fake, changes):
    record = s6.fight_record(fake["spec"], ("HEAD", "novice", 0, False, "resonator"), {},
                             synthetic_summary(**changes))
    assert record["status"] == "technical_failure" and record["reason"]
    json.dumps(record, allow_nan=False)


def test_s_d_timeout_and_controller_rule(spec):
    scores, failure = s6.score_summary(spec, synthetic_summary(S=-3))
    assert failure is None and scores == {"S": -3, "D": 70, "friendly_dealt": 3,
                                         "friendly_taken": 4, "timeout": True}
    boundary = 150 - spec["request_template"]["options"]["dt"] / 2
    assert s6.score_summary(spec, synthetic_summary(t=boundary))[0]["timeout"] is True
    assert s6.score_summary(spec, synthetic_summary(t=boundary - .000001))[0]["timeout"] is False
    assert s6.score_summary(spec, synthetic_summary(survivors=0))[0]["timeout"] is False
    assert s6.score_summary(spec, synthetic_summary(controllerFailures=[0, 1]))[1] is None
    assert s6.score_summary(spec, synthetic_summary(controllerStatus="controller_failure"))[1] == "controller_failure"


def test_complete_stub_run(fake):
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    disk = s6.read_json(fake["output"] / "results.json")
    assert result == disk
    assert all(e["verdict"] == "SUPPORTED" for e in result["endpoint_coverage"].values())
    rows = [json.loads(line) for line in (fake["output"] / "fights.jsonl").read_text().splitlines()]
    attempts = [json.loads(line) for line in (fake["output"] / "attempts.jsonl").read_text().splitlines()]
    assert len(rows) == len(attempts) == 336
    assert all(r["kind"] == "fight" for r in rows)
    assert all(r["kind"] == "attempt" for r in attempts)
    assert result["recorded_fights"] == result["attempted_fights"] == 336
    assert {tuple(r["key"]): r["request"] for r in rows} == {
        tuple(r["key"]): r["request"] for r in attempts}
    assert len({tuple(r["key"]) for r in rows}) == 336
    assert all(r["status"] == "completed" for r in rows)
    panels = [r["key"][0] for r in rows]
    assert panels == sorted(panels)
    assert sum(bool(r["diagnostics"]) for r in rows) == 38
    identity = s6.read_json(fake["output"] / "identity.json")
    assert identity["root"] == FAKE_ROOT
    assert identity["spec_sha256"] == s6.sha256(fake["spec_path"])
    assert identity["binary_sha256"] == s6.sha256(fake["binary"])
    assert identity["host"] == fake["spec"]["failures"]["host"]
    schedule = s6.read_json(fake["output"] / "schedule.json")
    seeds = identity["seeds"]
    assert schedule == [{"key": list(key), "request": s6.request_for(fake["spec"], seeds, key)}
                        for key in s6.scheduled_keys(fake["spec"], seeds)]
    assert len(schedule) == 336
    check_coverage(disk)


@pytest.mark.parametrize("mode,reason", [("controller", "controller_failure"), ("error", "native error"),
    ("nan", "non-finite"), ("malformed", "technical_failure"), ("timeout", "host timeout"),
    ("missing", "missing")])
def test_stub_failures_p1_does_not_stop_pool(fake, mode, reason):
    fake["binary"].with_suffix(".mode").write_text(mode)
    if mode == "timeout":
        fake["spec"]["failures"]["host"]["per_fight_timeout_seconds"] = .1
        rebind(fake)
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    p1 = result["endpoint_coverage"]["P1"]
    assert p1["verdict"] == "INDETERMINATE" and reason in json.dumps(p1)
    assert result["endpoint_coverage"]["P2"]["verdict"] == "SUPPORTED"
    assert result["endpoint_coverage"]["P3"]["verdict"] == "SUPPORTED"
    assert (fake["output"] / "results.json").is_file()
    check_coverage(result)


@pytest.mark.parametrize("mode", ["nonzero", "duplicate"])
def test_stub_descriptive_process_failure_independent(fake, mode):
    fake["binary"].with_suffix(".mode").write_text(mode)
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    assert all(e["verdict"] == "SUPPORTED" for e in result["endpoint_coverage"].values())
    events = [json.loads(line) for line in (fake["output"] / "fights.jsonl").read_text().splitlines()]
    assert any(e["kind"] == "process_failure" for e in events)


@pytest.mark.parametrize("mode,affected", [("nonzero_required", ("P2", "P3")),
                                          ("late_nonzero", ("P2",))])
def test_required_nonzero_exit_invalidates_only_dependent_endpoints(fake, mode, affected):
    fake["binary"].with_suffix(".mode").write_text(mode)
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    for name, endpoint in result["endpoint_coverage"].items():
        assert endpoint["verdict"] == ("INDETERMINATE" if name in affected else "SUPPORTED")
    check_coverage(result)


def test_native_template_excludes_explanatory_note(fake):
    fake["binary"].with_suffix(".mode").write_text("strict_template")
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    assert all(e["verdict"] == "SUPPORTED" for e in result["endpoint_coverage"].values())
    schedule = s6.read_json(fake["output"] / "schedule.json")
    assert "request_template_note" in fake["spec"]
    assert all(set(row["request"]) == set(fake["spec"]["request_template"]) for row in schedule)
    check_coverage(result)


@pytest.mark.parametrize("mode,reason", [
    ("late_nonzero", "nonzero native exit"), ("late_timeout", "host timeout"),
    ("late_malformed", "Expecting property"), ("late_missing", "missing summary"),
    ("shutdown_timeout", "worker shutdown timeout")])
def test_host_fault_invalidates_whole_block_including_prior_valid_returns(fake, mode, reason):
    fake["binary"].with_suffix(".mode").write_text(mode)
    host = fake["spec"]["failures"]["host"]
    host["per_fight_timeout_seconds"] = .3
    host["worker_shutdown_timeout_seconds"] = .1
    rebind(fake)
    result = s6.run(fake["spec_path"], fake["repo"], workers=4)
    coverage = result["endpoint_coverage"]
    assert coverage["P1"]["verdict"] == coverage["P3"]["verdict"] == "SUPPORTED"
    p2 = coverage["P2"]
    assert p2["verdict"] == "INDETERMINATE" and p2["bounds"] is None
    assert len(p2["failures"]) == 38
    assert {tuple(f["key"])[2:] for f in p2["failures"]} == {
        (0, orientation, "morale") for orientation in (False, True)}
    events = [json.loads(line) for line in (fake["output"] / "fights.jsonl").read_text().splitlines()]
    prior_valid = [e for e in events if e["kind"] == "fight" and e["status"] == "completed"
                   and e["key"][0] == "POOL" and e["key"][2] == 0 and e["key"][4] == "morale"]
    assert prior_valid, "Fault must follow an already returned valid summary"
    faults = [e for e in events if e["kind"] == "process_failure" and reason in e["reason"]]
    assert faults
    assert all(len(e["keys"]) == 38 and all(k[0] == "POOL" and k[2] == 0 and k[4] == "morale"
                                         for k in e["keys"]) for e in faults)
    assert result["identity"]["host"] == host
    check_coverage(result)


@pytest.mark.parametrize("fault,reason", [
    ("unmatched", "unmatched attempt"), ("duplicate", "duplicate attempted"),
    ("absent", "without attempt"), ("mismatch", "request mismatch")])
def test_attempt_return_pairing_invalidates_dependent_endpoint(fake, fault, reason):
    spec = fake["spec"]
    _, keys, rows = schedule_data(spec)
    attempts = [{"kind": "attempt", "key": row["key"], "request": copy.deepcopy(row["request"])}
                for row in rows]
    index = next(i for i, row in enumerate(rows) if row["key"][0] == "POOL"
                 and row["key"][4] == "pushpull")
    if fault == "unmatched":
        rows.pop(index)
    elif fault == "duplicate":
        attempts.append(copy.deepcopy(attempts[index]))
    elif fault == "absent":
        attempts.pop(index)
    else:
        attempts[index]["request"]["options"]["seed"] += 1
    result = s6.evaluate(spec, keys, rows, attempts=attempts)
    p3 = result["endpoint_coverage"]["P3"]
    assert p3["verdict"] == "INDETERMINATE" and p3["value"] is None and p3["bounds"] is None
    assert reason in json.dumps(p3)
    assert all(result["endpoint_coverage"][p]["verdict"] == "SUPPORTED" for p in ("P1", "P2"))


def test_interruption_after_attempt_retains_invalid_unmatched_request(fake, monkeypatch):
    original = s6.native_batch

    def interrupted(binary, spec, seeds, keys, journal, attempts, stop):
        if keys[0][0] == "HEAD" and keys[0][4] == "resonator":
            key = keys[0]
            attempts.append({"kind": "attempt", "key": list(key),
                             "request": s6.request_for(spec, seeds, key)})
            raise KeyboardInterrupt("synthetic interruption after journaling")
        return original(binary, spec, seeds, keys, journal, attempts, stop)

    monkeypatch.setattr(s6, "native_batch", interrupted)
    result = s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert result["run_status"] == "interrupted"
    assert "unmatched attempt" in json.dumps(result["endpoint_coverage"]["P1"])
    assert (fake["output"] / "attempts.jsonl").read_text()
    assert (fake["output"] / "schedule.json").is_file()
    check_coverage(s6.read_json(fake["output"] / "results.json"))


def test_interrupted_run_keeps_latch_and_all_endpoint_coverage(fake, monkeypatch):
    def interrupted(*args):
        raise KeyboardInterrupt("synthetic interruption")

    monkeypatch.setattr(s6, "native_batch", interrupted)
    result = s6.run(fake["spec_path"], fake["repo"], workers=1)
    assert result["run_status"] == "interrupted"
    assert "KeyboardInterrupt" in result["interruption_reason"]
    assert all(e["verdict"] == "INDETERMINATE" for e in result["endpoint_coverage"].values())
    check_coverage(s6.read_json(fake["output"] / "results.json"))
    assert (fake["output"] / "identity.json").is_file()
    assert (fake["output"] / "fights.jsonl").is_file()
    assert (fake["output"] / "attempts.jsonl").is_file()
    assert (fake["output"] / "schedule.json").is_file()
    with pytest.raises(s6.Refusal, match="latch"):
        s6.run(fake["spec_path"], fake["repo"], workers=1)
