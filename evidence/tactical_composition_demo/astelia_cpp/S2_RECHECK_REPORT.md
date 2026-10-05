READY

Owner-requested adversarial recheck of S2 at `65c7dab4d9196a4d58cbee084122879b95598493`, 2026-10-05. Four concrete defects were repaired, and the complete engineering batch passed on the repaired build. Status is **REVIEW_READY for independent Claude review**, not independently accepted. Scope remains decision 0028 and the three authorized registry entries; no tuning, new controller arm, AI experiment, or scientific status change occurred.

The fresh receipt is [s2_plug_recheck_r1/S2_RECEIPT.json](s2_plug_recheck_r1/S2_RECEIPT.json), SHA256 `12b0322d2e4709fe6ec3c1f456c8a75c028d5296ba97f77d03c4a415403c0a09`. Tested native binary: `7262f414463fcbcd584912ed9af48315b9bcc75316f27845959c6042348fba1a`. [ARTIFACTS.json](s2_plug_recheck_r1/ARTIFACTS.json) binds the receipt, logs, request/result files, and three copied build manifests; its SHA256 is `b9383c31b5967848a79c126e6a5ffe7749382c27c4bac7cde9646a8c3f671b89`.

## Defects and repairs

| Finding | Caller evidence and consequence | Repair and negative coverage |
|---|---|---|
| Archive checker skipped duplicate logical bindings | Original `pack_s2.py --check` skipped a row when its archive path had already been seen. A later logical name could claim a different raw or packed hash without being checked. Empty or omitted outputs also had no coverage gate. Packing used receipt paths directly for writes/deletions. | Cache decoded archive identities, then compare **every** logical row's packed hash, raw hash, and byte count. Require nonempty coverage equal to the pinned prepack receipt and preserve each prepack raw identity. Check aggregate metadata; reject traversal, noncanonical paths, and symlinks. Validate all gzip sources before writing, recheck them before deletion, and atomically replace metadata. Eighteen tiny storage tests include swapped bindings, corrupt archives, omissions, duplicate-row changes, unsafe paths, symlinks, and unchanged inputs after rejection. These are storage-identity checks, not a defense against consistently forged receipts. |
| Special player silently used the wrong weapon path | `World::create` creates a `Role::Player` on skirmish side 1. The original external bridge mapped it to Direct, while its actual movement/weapon logic is `playerBrain`, reached through `Release::Player` in `combat.cpp`. `gamePrep` returns for zero windup, which this body has. Using Direct suppresses its normal combat; using Player would replace the external controller's decisions with that brain. | Reject nearest/hold control of this body before unit allocation; reject it in the direct narrow bridge too. Two host tests require explicit rejection, two retain ordinary side-0 control and privileged player passthrough. Native contracts verify rejection leaves unit storage unchanged. Observing an enemy player remains supported. This is an explicit compatibility limit pending a separate player adapter. |
| Native profile export discarded controller selection | `api.h::buildProfile` returned all legacy profile components but had no controller member. A caller retrieving the typed profile lost the external controller identity. | Add `ControllerProfile controller` to `Profile` and copy it from the selected side. Native contract checks nearest and the uncontrolled side's empty selection. |
| Null controller clone silently switched branch control | `World::copyAuthorityFrom` accepted a null result from a present controller's `clone()`. Branch decision dispatch then fell back to `decideUnit` despite the disabled pack. The three registered implementations clone correctly; the defect concerned the public custom-controller lifecycle contract. | Throw on a missing clone instead of changing branch policy. An instrumented hold fixture returns null, verifies rejection without advancing parent state, then verifies a subsequent fork succeeds. It is an unregistered contract fixture, not a new combat arm. |

The first-tick check was also strengthened: it requires exactly one decision for every expected living opponent unit before comparing values and order. Empty or incomplete lists cannot pass merely by being equal.

## Fresh verification

All code and test edits were finished before running the batch. The suite and each engineering stage ran once; no successful fight batch was repeated for documentation or packaging.

| Check | Repaired-build result |
|---|---|
| Tests | **193 passed**, including all original 158 checks, the prior 13 S2 tests, four new host cases, and eighteen archive tests. Pytest reported **179.79 s**; whole test invocation **180.09 s**, empty stderr. Native contract assertions include profile retention, null-clone rejection/recovery, and special-player rejection. |
| Observation fence and validation | Exact field list, negative World compilation and positive control, copied snapshot, callback order, damage/identity tests, numeric and target validation passed. |
| ASan/UBSan | Controller contracts passed, exit 0 and empty stderr; instrumented build/run **35.04 s**. |
| No-controller behavior | **80/80** reference requests reproduce the admitted pre-S2 binary byte for byte and the original S2 capture. Both binaries execute freshly. |
| Passthrough | **228/228** complete trace/summary pairs match, **114 per controlled side**. Every pool opponent, novice/regular/elite-fast, both field orientations, game rules. **137,028 frames per arm**. Each newly executed stream also matches its original S2 capture. |
| Opposite-side first tick | **38/38** complete side-1 decision lists match built-in with nearest on side 0, both field orientations. Coverage is now checked before equality. |
| Nearest completion and determinism | **114** complete fights; **114** reversed-order repeats in fresh processes match byte for byte. Both sets reproduce the original captures. |
| Cost | Fresh built-in/nearest/nearest/built-in samples on the same 50 qualification contexts: nearest/built-in **0.8372606464**, below **1.2**. Mean elapsed per fight: built-in **39.402 ms**, nearest **32.990 ms**. Each sample executes 50 fights with zero cache hits; work counts and system load are retained. |
| Stored evidence | All original **542 logical streams / 310 unique archives** verified against every mapping and the prepack receipt before reuse. Fresh receipt covers the same 542 logical captures. |

Cost remains the requested whole-fight comparison. Built-in samples execute 30,000 steps / 2,798,891 unit actions, nearest 29,910 / 2,670,672. The result does not measure isolated adapter overhead at equal work or tactical quality. The first-tick result covers the requested fixed opponent pool; later decisions can differ because the opponent faces a different world. Privileged passthrough still preserves full built-in planning/internal decisions as documented in the initial report.

## Evidence preservation and reproduction

The original `s2_plug_r1/` and `s2_plug_r2/` files remain unchanged. Original completed receipt SHA256 remains `1ae077ba28cdf5e9b13adc8d097457640846cd9defc15d5945b4ce782a13bb29`.

The recheck executes every request again. After execution it hashes the newly produced stdout and reuses a verified original archive only for identical bytes. All 542 captures happened to match existing stored streams, including cost summaries; the new wall/CPU/load timings are separate fresh measurements. There is no execution cache. This keeps the additional evidence under 1 MiB while retaining exact stdout through the committed original archives.

For each fresh output entry, `archive_receipt.receipt` names a receipt relative to this directory and `archive_receipt.sha256` pins its bytes. Resolve the entry's `path` relative to that receipt's directory, verify the packed SHA256, decompress with `lzma.decompress`, then verify `raw_sha256` and `raw_bytes`. An entry without `archive_receipt` is local to the fresh evidence directory. Historical identities describe the build that produced their receipt; they are not substituted for current build identities.

Read-only original archive verification:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/pack_s2.py evidence/tactical_composition_demo/astelia_cpp/s2_plug_r2 --check
```

The completed recheck command was:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/verify_s2.py --output evidence/tactical_composition_demo/astelia_cpp/s2_plug_recheck_r1 --recheck-of evidence/tactical_composition_demo/astelia_cpp/s2_plug_r2
```

It refuses an existing output directory. Do not rerun the successful batch to inspect evidence. The engineering seeds are deterministic regression fixtures, not a scientific panel.

Changed paths are confined to this S2 directory: `src/native/api.h`, `world.cpp`, `controller_bridge.cpp`; native and Python controller contracts; `pack_s2.py`, `test_s2_evidence.py`, `verify_s2.py`; current-truth report/README updates; and the new recheck evidence. Accepted GeoMind sources, milestone state, historical qualification, and original S2 receipts are untouched.

Remaining gate: independent Claude review of the repaired source and bound evidence, including acceptance of the explicit player-body limitation and privileged passthrough exception. This recheck does not self-accept S2 or authorize a later controller session.
