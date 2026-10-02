ACCEPT_WITH_NOTE
Reviewer family: Claude
Reviewer model: claude-opus-5-5
Reviewed: C6 step 1 (the C++ element-law engine), implemented by Codex (gpt-6). Uncommitted working tree,
committed after this review: native/c6/element_law.cpp, geomind/c6_native.py, tools/build_c6.py,
tests/test_c6.py, and the .gitignore entry for build/.

Date: 2026-10-02. This is an intermediate code review of one implementation step under proposal §10. It is not
the evidence review, which follows the recorded panel.

## What was checked

- **No hidden fallback.** `geomind/c6_native.simulate` calls `c6_simulate` in `build/c6/element_law.dylib` through
  ctypes. It never calls `c4_model.simulate`. It imports only `Batch` and `Params` from the frozen model, read-only.
- **The kernel mirrors `c4_model` term by term.** It covers:
  - neighbour selection by std::hypot with stable index tie-breaking and the strict `<` radius mask;
  - the radial and phase terms, including `distance_weighted`;
  - the frozen-topology path, which recomputes r from current positions;
  - neighbours held for each RK4 step;
  - sampling and non-finite detection.

  It also reproduces NumPy's eight-lane pairwise summation, which explains the exact agreement.
- **The toolchain pin (G10).** The build refuses a different compiler identification line or different flags, and
  writes BUILD.json with source and binary hashes. The tests verify that record against the actual files.
- **Frozen files untouched.** `git status` shows only the new files and the one-line .gitignore change.
  `tools/accepted_freeze.py` passes at commit.

## Re-run by the reviewer

- `.venv/bin/python -m pytest -q tests/test_c6.py`: 41 passed in 1.35 s.
  - Check 1: 0 index and 0 mask mismatches over 1,000 states.
  - Checks 2 and 3: maximum differences of 0.0.
- A timing comparison on random arrays: 4 worlds, 200 free steps (neighbours recomputed each step), no
  experiment entropy.

| N | NumPy ms/world-step | C++ ms/world-step | Speedup | max \|Δx\|, max \|Δθ\| |
|---|---|---|---|---|
| 55 | 0.210 | 0.077 | 2.7× | 0, 0 |
| 190 | 2.443 | 0.607 | 4.0× | 0, 0 |
| 250 | 3.826 | 0.705 | 5.4× | 0, 0 |

The engine is bit-identical to the reference on these runs, including free neighbour switching at level-3 sizes.

## Note for the next step (low; not blocking)

The committed contracts use N ≤ 120 for check 1 and N = 12–17 for checks 2–3. Add one realistic-size contract:
N ≈ 250, a few hundred free steps, bit-identical or within the registered tolerances. That way the realistic-size
coverage shown above becomes part of the everyday suite. The design gate's check 4 still applies unchanged.
