# NS1 deliverable 1

Read CONTRACT.md first. New-file implementation only; no training, teacher collection or fights in this delivery. Native fixture RPC defaults to observation/decoder/forward/phase/teacher/sequence operations. `--collect` is an explicit future physical-run switch and was never invoked here. The model exports produced by tests are **untrained fixture weights**, not policies suitable for play.

From the repository root:

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
UV_CACHE_DIR="$SLICE/_local/uv-cache" uv venv --python 3.11.15 "$SLICE/_local/mlenv"
UV_CACHE_DIR="$SLICE/_local/uv-cache" python3 "$SLICE/setup_env.py"
python3 "$SLICE/build.py"
"$SLICE/_local/mlenv/bin/python" "$SLICE/verify_focused.py"
```

Online installation initially failed DNS in this sandbox. The delivered `_local/mlenv` was instead populated with isolated exact distribution copies from existing read-only package sources using `setup_env.py --offline-source ...`. ENVIRONMENT.json contains the distribution versions, bytes and tree identities. requirements.lock seals exact transitive runtime/test versions. No Torch/MPS/CUDA operation, optimizer update or workspace environment change occurs on setup. Online recreation on this macOS arm64 host uses the commands above; Linux would require a separate CPU wheel lock rather than accepting PyPI's CUDA extras.

BUILD.json binds native code and reused admitted objects. Generated overlays stay in `_local/build`; build.py reconstructs them without altering ancestors. Tests generate `_local/*fixture_weights.json`; NATIVE_FIXTURES.json records short isolated native seam decisions and acknowledgements, not full fights or a teacher dataset. TESTS.json and logs preserve the final focused batch; failed build/test attempts are retained separately if present.

Claude next reviews CONTRACT.md against every R2 finding, source/fixture parity, neutral gun dispatch, teacher action support and chronological join, exact cast hooks, gradient/state and ablation paths, proposed resource/margin rules, and the findings/disposition. Cross-family review is still required before data execution. STATUS.json and accepted experiments are untouched.

**Next step is the teacher-data projection, not collection:**

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
python3 "$SLICE/project.py" --output "$SLICE/TEACHER_DATA_PROJECTION.json"
```

This produces expected/hard row, byte, memory and symbolic CPU budgets without allocating draws, collecting labels, training or fighting. Claude then reviews the projection and declares a bounded real-path timing/collection plan with whole-group split inventory, fresh entropy exclusion, admitted native binary/model/teacher hashes and resource permission if required by the one-hour rule. Only a subsequently authorized run may call `_local/build/net_host --collect` with `requests.drill(...)`; a collection executor, dataset packing and trainer remain the next deliverable. Never feed reporting draws to fitting/DAgger. Long native jobs must not run concurrently with source edits.

The owner's same-family recheck and disposition are tracked locally in PLAN.md because this user's new-files-only scope forbids editing/staging docs/PLAN_CURRENT.md. PLAN_CURRENT_APPEND.md is a paste-ready tracking entry for the authorized document owner, not staged plan work.
