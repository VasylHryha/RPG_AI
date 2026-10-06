# History cleanup, 2026-10-06 (the owner's request: "keep only what matters", force push allowed)

## What changed

- **Removed from all of git history:** 361 raw bulk files, about 1.55 GB, all already compressed. They are:
  - Astelia replays (`*.jsonl.gz`, `*.replay.json.gz`) and their HTML renders;
  - the S2 plug stdout logs (`*.xz`);
  - C6 option B world dumps (`world.json.gz`);
  - trace and fight logs;
  - `PERF_RECHECK_EQUIVALENCE.json.gz` and `PERF_SMOKE.json.gz`.
- **Kept in git:** all code, reports, reviews, designs, decisions, result summaries, every `s4_seeds.json`, the 0h `REPORT.json.gz` library files, the viewer data (`viz_0g/replays_*.json`), and **all milestone evidence (C0–C6 R-series and design gates) unchanged.**
- **Where the removed bytes are:** the owner's disk, at the same paths, ignored through `evidence/.gitignore`. Each file's path, size, SHA256 and original git blob id are in `evidence/LARGE_FILES_OUTSIDE_GIT.json`. Verify a file with `shasum -a 256 <path>`.

  **Copy them to external storage**: a fresh clone does not have them.
- **The 0h raw ledgers** (about 14 GB) were never in `main`; see `growing_shapes/runner/development_20261006/LEDGERS_NOT_IN_GIT.md`.

## Commit identities

- **Unchanged:** the 174 commits before `Port frozen Astelia simulator to native C++ with reference evidence`, including every accepted milestone commit: C1 R006 `721249b`, C4 R003 `a774d44`, C5 R003 `92814d1`, and those pinned in `STATUS.json`.
- **Rewritten:** the 129 commits from that one onward. Contents and messages are identical except for the removed files.
- **Map:** old → new hashes are in `docs/HISTORY_CLEANUP_2026-10-06_MAP.tsv`. **Reports and reviews that cite one of those commits by hash mean the old hash; look it up in the map.**
- **The local safety copy:** branch `backup/main-before-cleanup-20261006` keeps the old history on this machine until the owner confirms. It is not pushed.

## Method

1. `git filter-branch --index-filter 'git rm --cached --ignore-unmatch --pathspec-from-file=…'`, run on a separate clone.
2. The cleaned branch was fetched back, and `git reset --mixed`, which leaves the working files untouched.
3. Force-pushed with a lease on the old remote head.

**Rule from now on:** raw bulk outputs (replays, dumps, logs, ledgers) stay out of git. Each file in git stays under 50 MB.
