"""Read-only S4 observer analysis. No imports from, or execution of, combat code.

Run: python3 evidence/tactical_composition_demo/astelia_cpp/s4_fire_efficiency_v1/analyze.py
All selected raw/request hashes are checked before parsing any trace. Outputs are
owned JSON only; original probe evidence and raw files are never written.
"""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import statistics
import time

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
REPO = CPP.parents[2]
SOURCE = CPP / "s4_collective_probe_v1"
CELLS = (("P5", "regular"), ("P7", "regular"), ("P5", "novice"))
BINS = (0, 10, 20, 30, 60, 150.1)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def ratio(n, d):
    return n / d if d else None


def distribution(values):
    return dict(n=len(values), mean=statistics.mean(values) if values else None,
                median=statistics.median(values) if values else None,
                min=min(values) if values else None, max=max(values) if values else None)


def bin_index(t):
    return next(i for i in range(len(BINS)-1) if BINS[i] <= t < BINS[i+1])


def distance(a, b):
    return math.hypot(a[3]-b[3], a[4]-b[4])


def analyze(fight):
    counters = [collections.Counter(), collections.Counter()]
    bins = [[collections.Counter() for _ in range(len(BINS)-1)] for _ in (0, 1)]
    initial = None
    previous = None
    terminal = None
    last_step = -1
    launches = []
    pending = collections.defaultdict(list)
    deaths = []
    death_times = {}
    move_state = {}
    displacement_state = {}
    displacement_waiting = {}
    displacement_gaps = [[], []]
    starts = [[], []]
    waiting = {}
    gaps = [[], []]
    resets = [[], []]
    last_launch = {}
    interlaunch = [[], []]
    prep_switches = [[], []]
    with gzip.open(SOURCE / "raw" / (fight["id"] + ".jsonl.gz"), "rt") as f:
        for line in f:
            row = json.loads(line)
            if not row.get("observerV1"):
                if "collectiveProbe" not in row:
                    terminal = row
                continue
            assert row["step"] == last_step + 1
            last_step = row["step"]
            current = {u[0]: u for u in row["units"]}
            if previous is None:
                initial = current
                assert [sum(u[1] == side and u[2] == 2 for u in initial.values()) for side in (0, 1)] == [10, 10]
                previous = row
                continue
            before = {u[0]: u for u in previous["units"]}
            dt = row["t"] - previous["t"]
            assert abs(dt - 1/30) < 1e-10
            k = bin_index(previous["t"])
            actions = {a[0]: a for a in row["actions"]}
            released = set()
            for launch in row["launches"]:
                source, target, side = launch[:3]
                assert initial[source][2] == 2 and not launch[9] and not launch[8]
                assert source in before and abs(launch[5]-row["t"]) < 1e-9
                target_unit = initial.get(target)
                assert target_unit is not None and target_unit[1] != side
                item = dict(source=source, target=target, side=side, born=launch[5],
                            at=launch[6], gun_target=target_unit[2] == 2,
                            launch_bin=bin_index(launch[5]), hits=set(), target_hit=False,
                            gun_damage=0, switched_before_impact=False)
                launches.append(item)
                pending[source].append(item)
                released.add(source)
                if source in last_launch:
                    interlaunch[side].append(row["t"]-last_launch[source])
                last_launch[source] = row["t"]
            # Damage precedes post-step separation. Exact victim/killer coordinates
            # exist; all other centres at this instant are absent from the stream.
            for d in row["damage"]:
                if d["dealt"] > 0 and d["targetRole"] == "artillery":
                    victim_side = d["targetTeam"]
                    label = "incoming_damage_" + str(d["sourceTeam"]) + "_" + d["sourceRole"]
                    counters[victim_side][label] += d["dealt"]
                    if d["sourceRole"] == "artillery":
                        due = [s for s in pending[d["source"]] if -1e-9 <= d["t"]-s["at"] <= dt+1e-7]
                        assert len(due) == 1, (fight["id"], "ambiguous shell", d, due)
                        s = due[0]
                        if victim_side != s["side"]:
                            s["hits"].add(d["target"])
                            s["target_hit"] |= d["target"] == s["target"]
                            s["gun_damage"] += d["dealt"]
                if d["died"]:
                    assert d["target"] in before
                    assert d["target"] not in death_times
                    death_times[d["target"]] = d["t"]
                    if d["targetTeam"] == 0 and d["targetRole"] == "artillery":
                        death = dict(unit=d["target"], t=d["t"], x=d["targetX"], y=d["targetY"],
                                     killer=d["killer"], killer_team=d["sourceTeam"], killer_role=d["sourceRole"],
                                     killer_distance_exact=d["distance"],
                                     nearest_at_death_exact=None,
                                     snapshot_age_s=dt)
                        for role, name in ((2, "gun"), (1, "ranged")):
                            candidates = [u for u in before.values() if u[1] == 1 and u[2] == role]
                            best = min(candidates, key=lambda u: (math.hypot(u[3]-d["targetX"], u[4]-d["targetY"]), u[0]), default=None)
                            death["nearest_enemy_"+name+"_previous_snapshot"] = (
                                dict(id=best[0], distance=math.hypot(best[3]-d["targetX"], best[4]-d["targetY"]),
                                     surface_gap=math.hypot(best[3]-d["targetX"], best[4]-d["targetY"])-best[6]-before[d["target"]][6],
                                     min_range=best[8], range=best[7]) if best else None)
                        deaths.append(death)
            enemies = [[u for u in before.values() if u[1] != side] for side in (0, 1)]
            for uid, u in before.items():
                if u[2] != 2:
                    continue
                side = u[1]
                c = counters[side]
                b = bins[side][k]
                c["living_ticks"] += 1
                b["living_ticks"] += 1
                in_range = any(u[8] <= distance(u, e) <= u[7] for e in enemies[side])
                gun_range = any(e[2] == 2 and u[8] <= distance(u, e) <= u[7] for e in enemies[side])
                c["any_target_range_ticks"] += in_range
                c["gun_target_range_ticks"] += gun_range
                b["any_target_range_ticks"] += in_range
                b["gun_target_range_ticks"] += gun_range
                c["windup_ticks"] += u[12] > 0
                b["windup_ticks"] += u[12] > 0
                c["launch_ticks"] += uid in released
                b["launch_ticks"] += uid in released
                a = actions.get(uid)
                assert a is not None, (fight["id"], "missing decision", uid)
                command = bool(a[8] and a[5] > 0 and math.hypot(a[3]-u[3], a[4]-u[4]) > a[6]+1e-9)
                c["move_command_ticks"] += command
                c["command_range_ticks"] += command and in_range
                c["hold_range_ticks"] += not command and in_range
                c["command_launch_ticks"] += command and uid in released
                c["hold_launch_ticks"] += not command and uid in released
                c["command_launch_range_ticks"] += command and in_range and uid in released
                c["hold_launch_range_ticks"] += not command and in_range and uid in released
                b["move_command_ticks"] += command
                b["command_range_ticks"] += command and in_range
                b["hold_range_ticks"] += not command and in_range
                b["command_launch_ticks"] += command and uid in released
                b["hold_launch_ticks"] += not command and uid in released
                b["command_launch_range_ticks"] += command and in_range and uid in released
                b["hold_launch_range_ticks"] += not command and in_range and uid in released
                started = command and not move_state.get(uid, False)
                if started:
                    start = dict(unit=uid, t=row["t"], in_range=in_range, prep_before=u[12],
                                 previous_launch_age_s=row["t"]-last_launch[uid] if uid in last_launch else None)
                    starts[side].append(start)
                    if uid in waiting:
                        gaps[side].append(dict(**waiting.pop(uid), status="censored_by_next_move_start", end=row["t"], gap_s=None))
                    waiting[uid] = start
                move_state[uid] = command
                if uid in waiting and uid in released:
                    start = waiting.pop(uid)
                    gaps[side].append(dict(**start, status="observed", end=row["t"], gap_s=row["t"]-start["t"]))
                v = current.get(uid)
                if v is not None:
                    moving = distance(u, v) > 1e-6
                    displaced_start = moving and not displacement_state.get(uid, False)
                    displacement_state[uid] = moving
                    if displaced_start:
                        ds = dict(unit=uid, t=row["t"], in_range=in_range, prep_before=u[12])
                        if uid in displacement_waiting:
                            displacement_gaps[side].append(dict(**displacement_waiting.pop(uid), status="censored_by_next_movement_start", end=row["t"], gap_s=None))
                        displacement_waiting[uid] = ds
                    if uid in displacement_waiting and uid in released:
                        ds = displacement_waiting.pop(uid)
                        displacement_gaps[side].append(dict(**ds, status="observed", end=row["t"], gap_s=row["t"]-ds["t"]))
                    c["movement_known_ticks"] += 1
                    c["moving_ticks"] += moving
                    c["moving_launch_ticks"] += moving and uid in released
                    c["stationary_launch_ticks"] += not moving and uid in released
                    b["movement_known_ticks"] += 1
                    b["moving_ticks"] += moving
                    changed = a[2] != (u[13] or 0)
                    c["target_switches"] += changed
                    if changed and u[12] > 0:
                        prep_switches[side].append(dict(unit=uid, t=row["t"], from_target=u[13], to_target=a[2],
                                                       prep_before=u[12], prep_after=v[12], launched=uid in released))
                    if u[12] > 0 and v[12] < u[12]-1e-9 and uid not in released:
                        resets[side].append(dict(unit=uid, t=row["t"], prep_before=u[12], prep_after=v[12],
                                                move_command=command, movement_start=started, displaced=moving,
                                                displacement_start=displaced_start,
                                                target_switch=changed, target=a[2], decision_in_reach=a[12]))
                else:
                    c["death_interval_ticks"] += 1
                    if uid in waiting:
                        gaps[side].append(dict(**waiting.pop(uid), status="censored_by_death", end=row["t"], gap_s=None))
                    if uid in displacement_waiting:
                        displacement_gaps[side].append(dict(**displacement_waiting.pop(uid), status="censored_by_death", end=row["t"], gap_s=None))
                for s in pending[uid]:
                    if previous["t"] < s["at"] and a[2] != s["target"]:
                        s["switched_before_impact"] = True
            previous = row
    assert terminal == fight["summary"]
    for uid, start in waiting.items():
        gaps[initial[uid][1]].append(dict(**start, status="censored_by_end", end=terminal["t"], gap_s=None))
    for uid, ds in displacement_waiting.items():
        displacement_gaps[initial[uid][1]].append(dict(**ds, status="censored_by_end", end=terminal["t"], gap_s=None))
    for s in launches:
        side = s["side"]
        c = counters[side]
        b = bins[side][s["launch_bin"]]
        labels = ["launches", "gun_launches" if s["gun_target"] else "other_launches"]
        victim_label = "gun_target_shell_gun_victims" if s["gun_target"] else "other_target_shell_gun_victims"
        damage_label = "gun_target_shell_gun_damage" if s["gun_target"] else "other_target_shell_gun_damage"
        for dest in (c, b):
            dest[victim_label] += len(s["hits"])
            dest[damage_label] += s["gun_damage"]
            dest["shells_hitting_"+str(len(s["hits"]))+"_guns"] += 1
        if s["gun_target"]:
            labels.extend(["gun_launches_hit_any_gun"] if s["hits"] else [])
            labels.extend(["gun_launches_hit_intended_gun"] if s["target_hit"] else [])
            labels.extend(["gun_launches_airborne_at_end"] if s["at"] > terminal["t"] else [])
            if s["target"] in death_times and death_times[s["target"]] < s["at"]-1e-9:
                labels.append("gun_launches_target_dead_before_scheduled_impact")
                if not s["hits"]:
                    labels.append("gun_launches_no_gun_hit_target_dead_before_scheduled_impact")
        elif s["hits"]:
            labels.append("other_launches_hit_gun")
        if s["switched_before_impact"]:
            labels.append("launches_with_airborne_target_switch")
            if s["gun_target"]:
                labels.append("gun_launches_with_airborne_target_switch")
                if s["hits"]:
                    labels.append("gun_launches_with_airborne_target_switch_hit")
        for label in labels:
            c[label] += 1
            b[label] += 1
    assert len(deaths) == 10-terminal["artilleryAlive"][0]
    for side in (0, 1):
        assert counters[side]["launch_ticks"] == counters[side]["launches"]
        assert counters[side]["living_ticks"]/30 <= 10*terminal["t"]+1e-7
        assert counters[side]["gun_launches"]+counters[side]["other_launches"] == counters[side]["launches"]
        c = counters[side]
        enemy = counters[1-side]
        assert math.isclose(c["gun_target_shell_gun_damage"]+c["other_target_shell_gun_damage"],
                            enemy["incoming_damage_"+str(side)+"_artillery"], abs_tol=1e-7)
    return dict(id=fight["id"], arm=fight["arm"], head=fight["head"], cluster=fight["cluster"],
                orientation=fight["orientation"], duration_s=terminal["t"],
                end_guns=terminal["artilleryAlive"], sides=[dict(c) for c in counters],
                time_bins=[[dict(b) for b in side] for side in bins], deaths=deaths,
                move_launch_gaps=gaps, displacement_launch_gaps=displacement_gaps, windup_resets_without_launch=resets,
                target_switches_during_windup=prep_switches, interlaunch_gaps_s=interlaunch)


def side_metrics(c):
    c = collections.Counter(c)
    n = c["living_ticks"]
    return dict(counts=dict(c), living_gun_seconds=n/30,
                launches_per_living_gun_second=ratio(c["launches"], n/30),
                moving_fraction_known=ratio(c["moving_ticks"], c["movement_known_ticks"]),
                movement_coverage_fraction=ratio(c["movement_known_ticks"], n),
                move_command_fraction=ratio(c["move_command_ticks"], n),
                any_target_in_range_fraction=ratio(c["any_target_range_ticks"], n),
                gun_target_in_range_fraction=ratio(c["gun_target_range_ticks"], n),
                windup_fraction=ratio(c["windup_ticks"], n),
                firing_launch_interval_fraction=ratio(c["launch_ticks"], n),
                ready_but_not_firing=None,
                command_launches_per_gun_second=ratio(c["command_launch_ticks"], c["move_command_ticks"]/30),
                hold_launches_per_gun_second=ratio(c["hold_launch_ticks"], (n-c["move_command_ticks"])/30),
                command_range_launches_per_gun_second=ratio(c["command_launch_range_ticks"], c["command_range_ticks"]/30),
                hold_range_launches_per_gun_second=ratio(c["hold_launch_range_ticks"], c["hold_range_ticks"]/30),
                gun_launch_share=ratio(c["gun_launches"], c["launches"]),
                gun_launch_hit_any_gun_rate=ratio(c["gun_launches_hit_any_gun"], c["gun_launches"]),
                gun_launch_hit_intended_gun_rate=ratio(c["gun_launches_hit_intended_gun"], c["gun_launches"]))


def aggregate(rows):
    result = []
    for arm, head in CELLS:
        subset = [r for r in rows if (r["arm"], r["head"]) == (arm, head)]
        assert len(subset) == 20
        sides = []
        for side in (0, 1):
            c = collections.Counter()
            for r in subset:
                c.update(r["sides"][side])
            m = side_metrics(c)
            gaps = [g for r in subset for g in r["move_launch_gaps"][side]]
            resets = [g for r in subset for g in r["windup_resets_without_launch"][side]]
            switches = [g for r in subset for g in r["target_switches_during_windup"][side]]
            dg = [g for r in subset for g in r["displacement_launch_gaps"][side]]
            m.update(move_starts=len(gaps), move_gap_status_counts=dict(collections.Counter(g["status"] for g in gaps)),
                     move_start_to_launch_s=distribution([g["gap_s"] for g in gaps if g["gap_s"] is not None]),
                     in_range_move_start_to_launch_s=distribution([g["gap_s"] for g in gaps if g["gap_s"] is not None and g["in_range"]]),
                     interlaunch_gaps_s=distribution([g for r in subset for g in r["interlaunch_gaps_s"][side]]),
                     windup_resets_without_launch=len(resets),
                     resets_with_move_command=sum(g["move_command"] for g in resets),
                     resets_at_move_start=sum(g["movement_start"] for g in resets),
                     resets_at_displacement_start=sum(g["displacement_start"] for g in resets),
                     resets_with_target_switch=sum(g["target_switch"] for g in resets),
                     switches_during_windup=len(switches),
                     switches_during_windup_with_launch=sum(g["launched"] for g in switches),
                     launches_lost_to_target_switch=None)
            m.update(displacement_starts=len(dg), displacement_gap_status_counts=dict(collections.Counter(g["status"] for g in dg)),
                     displacement_start_to_launch_s=distribution([g["gap_s"] for g in dg if g["gap_s"] is not None]),
                     in_range_displacement_start_to_launch_s=distribution([g["gap_s"] for g in dg if g["gap_s"] is not None and g["in_range"]]))
            m["time_bins"] = []
            for i in range(len(BINS)-1):
                bc = collections.Counter()
                for r in subset:
                    bc.update(r["time_bins"][side][i])
                m["time_bins"].append(dict(from_s=BINS[i], to_s=min(150, BINS[i+1]), **side_metrics(bc)))
            sides.append(m)
        deaths = [dict(fight=r["id"], **d) for r in subset for d in r["deaths"]]
        death_summary = dict(n=len(deaths), death_time_s=distribution([d["t"] for d in deaths]),
                             killers=dict(collections.Counter(str(d["killer_team"])+"_"+d["killer_role"] for d in deaths)))
        for name in ("gun", "ranged"):
            field = "nearest_enemy_"+name+"_previous_snapshot"
            ds = [d[field]["distance"] for d in deaths if d[field] is not None]
            death_summary[name+"_distance_previous_snapshot"] = distribution(ds)
            death_summary[name+"_in_native_band_previous_snapshot"] = sum(
                d[field] is not None and (d[field]["min_range"] <= d[field]["distance"] <= d[field]["range"]
                                         if name == "gun" else d[field]["surface_gap"] <= d[field]["range"])
                for d in deaths)
        result.append(dict(arm=arm, head=head, fights=20, sides=sides,
                           enemy_guns_destroyed=sum(10-r["end_guns"][1] for r in subset),
                           own_guns_lost=len(deaths), death_summary=death_summary))
    return result


def main():
    start = time.monotonic()
    manifest = json.loads((SOURCE / "RAW_FILES_LOCAL.json").read_text())
    fights = json.loads((SOURCE / "FIGHTS.json").read_text())
    fights = [r for r in fights if (r["arm"], r["head"]) in CELLS]
    assert len(fights) == 60
    assert {(r["arm"], r["head"], r["cluster"], r["orientation"]) for r in fights} == {
        (a, h, c, o) for a, h in CELLS for c in range(10) for o in (0, 1)}
    manifest_by_path = {r["path"]: r for r in manifest["files"]}
    verified = []
    # Complete this entire loop before opening any gzip stream.
    for r in fights:
        for suffix in (".jsonl.gz", "_request.json"):
            key = "raw/"+r["id"]+suffix
            entry = manifest_by_path[key]
            path = SOURCE / key
            assert path.stat().st_size == entry["bytes"] and sha(path) == entry["sha256"], key
            assert entry["sha256"] == r["raw_sha256" if suffix == ".jsonl.gz" else "request_sha256"]
            verified.append(entry)
        request = json.loads((SOURCE / "raw" / (r["id"]+"_request.json")).read_text())
        opts = request["options"]
        assert opts["dt"] == 1/30 and opts["duration"] == 150 and opts["rules"] == "game"
        assert opts["ai"][0]["controller"] == r["arm"]
    declaration = json.loads((SOURCE / "DECLARATION.json").read_text())
    pins = {}
    for name in ("host_observer_v1.cpp", "observer_v1_combat_rules.cpp", "observer_v1.cpp", "combat.cpp"):
        path = CPP / "src/native" / name
        key = str(path.relative_to(REPO))
        expected = declaration["protected"][key]
        assert sha(path) == expected
        pins[key] = expected
    print("Verified all 60 raw traces, 60 requests and 4 schema/semantics sources before analysis.", flush=True)
    rows = []
    for r in fights:
        rows.append(analyze(r))
        if len(rows) % 5 == 0:
            print(json.dumps(dict(analyzed=len(rows), elapsed_s=time.monotonic()-start)), flush=True)
    aggregates = aggregate(rows)
    prior = json.loads((SOURCE / "COMPACT.json").read_text())
    for row in aggregates:
        old = next(r for r in prior["rows"] if r["arm"] == row["arm"] and r["head"] == row["head"])
        own = row["sides"][0]["counts"]
        assert own["gun_launches"] == old["shells_fired_at_enemy_guns"]
        assert own["gun_launches_hit_any_gun"] == old["shell_hits_on_enemy_guns"]
        assert row["own_guns_lost"] == old["own_gun_losses"]
        assert row["enemy_guns_destroyed"] == old["enemy_guns_destroyed"]
    write("COMPACT.json", dict(status="PARTIAL", coverage="60/60 selected stored fights; requested unavailable fields explicitly null",
                              schema_version=1, bins_s=BINS, aggregates=aggregates, fights=rows))
    write("VERIFICATION.json", dict(status="PASS", script_sha256=sha(pathlib.Path(__file__)),
                                   input_manifest_sha256=sha(SOURCE / "RAW_FILES_LOCAL.json"),
                                   fights_sha256=sha(SOURCE / "FIGHTS.json"), original_compact_sha256=sha(SOURCE / "COMPACT.json"),
                                   schema_source_pins=pins, verified_input_files=verified,
                                   all_traces_contiguous_30Hz=True, unique_shell_damage_attribution=True,
                                   previous_gun_launch_hit_casualty_counts_reconciled=True,
                                   elapsed_s=time.monotonic()-start))


if __name__ == "__main__":
    main()
