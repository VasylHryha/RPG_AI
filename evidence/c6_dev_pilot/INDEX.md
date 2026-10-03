# Index of the C6 development pilots (none is evidence; C6 stays BLOCKED / R006 STOP)

`README.md` in this folder documents the first pilot (2026-10-02, entropy 44444) and holds its hash list; it is left unchanged. Later pilots live in subfolders.

| Folder | What | Run by | Authorization | Commits | Status |
|---|---|---|---|---|---|
| (top level: `c6_pilot.py`, `pilot_*.json`) | level-1/2 harvest and level-3 assembly pilot; the level-3 formation result is void (see `README.md`) | Claude | owner, during review of `experiments/c6_proposal.md` | see `README.md` | development record |
| `r4_sensitivity/` | one fixed 16-pair Q/H run against the GPT synthesis | Codex | owner approved on 3 October 2026 (stated in its README; no decision record) | `9d72c5a` spec, `e2a31cc` run | pilot record |
| `r4_sensitivity_recheck/` | audit of the Q/H pilot observations | Codex | no separate decision found | `628a00d` | audit record |
| `a_twobody/` | two-body force-map pilot: why level three stalls; do level-2 groups fuse | Claude | owner chat messages, recorded in decision 0028 **[R]** | `3173bab`, `5c10d57`, `b7397e6` | pilot record; wording corrections in `a_twobody/ADDENDUM.md` |

Scope and boundaries: `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`. The later composable-shapes demos (`evidence/geometric_composition_demo/`,
`evidence/tactical_composition_demo/`) are not C6 pilots and are not listed here.
