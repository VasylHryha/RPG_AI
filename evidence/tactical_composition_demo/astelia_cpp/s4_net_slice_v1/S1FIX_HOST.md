# S1FIX host rerun

Owner-authorized development pilot repair, following design rev 3 and decisions 0035–0037. All original S1 evidence, inventory, raw, native build and source files remain unchanged. No sandbox fights, fits, S2 panel or outcome entropy. This revision drops the unexercised two-gun cells and keeps D2-10/M2-10. The prospective support/oracle changes and counted root causes are in `S1_WRAPPER_DIAGNOSIS.md`. Review and disposition live in `S1FIX_RECHECK.md`; PLAN_CURRENT.md is untouched under the owner's instruction.

Fresh pilot maximum: 20 pairs/cell = 80 arm-fights. Initial extent: 10 pairs/cell = 40. The first five pairs in each cell form the **20 arm-fight timing sample**, already included in that initial extent. Do not repeat sample fights. Seeds/entropy are independent of the initial pilot, including its unrun reserved extensions, and all historical seeds found by the existing workspace inventory exclusion procedure. `S1FIX_PILOT_SEED_EXCLUSIONS.json` excludes all 40 fresh paired seeds from future training/validation/outcome pools. Keep the original exclusion file too.

Manifests bind code, binary, immutable seed inventories and approved design commit identity. They never hash-pin living design/plan/spec documents or mutable cap bytes. The actual owner cap is checked live at every launch. Every physical attempt uses process ownership discovery plus the historical collection/training locks. Failed attempts consume the cap and remain preserved; no automatic retry. Stop on a failed discovery, native error, RSS/disk/cap admission or malformed log.

The current `S1FIX_BUILD.json` and `_local/s1fix/native/s1fix_host` are the new native build. `admit` verifies them without running a fight. The final native build measured 10.63 s on this machine, and use `s1fix_build.py build` only when that build is genuinely absent; the builder refuses a present record. Original binaries/objects are verified read-only. Fixture RPC explicitly uses `--fixture`; `--collect` is the separate host-only fight path.

Exact commands, from the repository root:

```sh
cd /Users/new/RiderProjects/ai_RPG_test
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
PYTHON="$SLICE/_local/mlenv/bin/python"
"$PYTHON" "$SLICE/s1fix_build.py" admit
"$PYTHON" "$SLICE/s1fix_pilot.py" seal
"$PYTHON" "$SLICE/s1fix_pilot.py" sample
"$PYTHON" "$SLICE/s1fix_pilot.py" project
```

`admit`/`seal`: seconds. `seal` revalidates the prepared inventory and returns it; it never replaces it. **Unverified initial sample estimate: 20–40 s.** The old mixed-cell sample measured 0.838 s mean / 1.828 s maximum per fight; both retained ten-gun cells are heavier than the dropped cells. Changes to support/reaction can alter fight length. Read the new PROJECTION.json and tell the owner the maximum-extent estimate before collection. The formula is charged time plus `2 × sample maximum × remaining maximum arm-fights`. It is a planning margin, not a proven runtime bound; timeouts enforce the live cap. Measured RSS/disk admission covers the full 80-fight extent. Collection/extension rechecks sample receipt hashes, current charge/remaining extent, observed wall/RSS/disk maxima, live cap and full remaining disk reserve before each new physical attempt. Admission checks are append-only; the original projection is preserved.

After projection returns `ADMITTED`:

```sh
"$PYTHON" "$SLICE/s1fix_pilot.py" collect
"$PYTHON" "$SLICE/s1fix_pilot.py" report
```

Initial 40 arm-fights including sample: **rough estimate 45–90 s**, refresh from `initial_40_fights_projected_seconds` before collection. Maximum 80-fight extent: roughly **2–4 min** before a new measured projection; no assumption of restored full-army utility. Report reads hashed receipts and takes seconds. New reports are `S1FIX_PILOT_INITIAL.json/.md`; the initial S1 report is never overwritten. Fixture support success is not an empirical fresh-pilot rate. Before admission require zero target/aim-lock differences, >=95% supported release rows, residual validity, adequate multi-gun/physical response and unchanged moving raw-miss/MDE/coverage stops. Read autonomous-bound/rejected-command counters alongside snap support.

A coverage/detectability extension is allowed only for named unresolved cells with no lock/residual/snap/miss failure, never to chase a favorable effect:

```sh
"$PYTHON" "$SLICE/s1fix_pilot.py" extend --cells D2-10 M2-10
"$PYTHON" "$SLICE/s1fix_pilot.py" report --cells D2-10 M2-10
```

Only name cells that qualify under the prior report. New extended report preserves the initial one. The 20-pair limit includes every sample and failed physical attempt. Commit the compact reports plus raw pilot evidence or its complete hashed inventory before further S2 work. The pilot remains development evidence, with no tactical utility or RRG claim.

Local focused verification passed 23 tests in 16.27 s; native support replay covered 5,453 old release rows with zero bad snaps and explicit physical-bound counters. No local fight was run. Two earlier fixture failures and their source hashes remain preserved.

The separate reviewer found one medium resource-admission gap; it is fixed and the corrected-source reread passed. Final admission-focused verification passed 8 tests in 0.20 s. The unchanged native wrapper retains its previous 23-test and 5,453-row support evidence.

The prepared inventory is published as `S1FIX_INVENTORY.json` (SHA256 `f06e39fabbb01a3d08e3993af5bf02264d71939f62a26d31b0694973f018cfec`), alongside the matching local seal. It contains 40 distinct paired seeds disjoint from all 80 initial reserved pilot seeds and records 5,134 historical exclusion sources. There are zero fresh physical attempts. `UNCOMMITTED_S1FIX.txt` lists only changed delivery paths, without a heading.
