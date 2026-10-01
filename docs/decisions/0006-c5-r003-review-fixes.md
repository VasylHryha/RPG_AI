# 0006: C5 R003 fixes the four findings of the R002 review

Date: 2026-10-02. Implementer: Claude. Trigger: Codex's independent review of R002, CHANGES_REQUIRED (`evidence/c5_r002_review_codex/INDEPENDENT_REVIEW.md`). The review also confirmed that R002's recorded verdicts (H-M level 2 and H-C first transition, both INCONCLUSIVE) follow the registered rules. Before any change, F2 and F3 were reproduced, and F1 and F4 were confirmed in the code.

## Findings and fixes

- **F1 (high): the composite never became an upper-facing unit.**
  - *The defect:* no level-2 `ResonatorState` was built or stored, so the interface that C6 must consume did not exist.
  - *The fix:* `c5_units.compose_state` builds the parent from its children's published states only, with the same fields. Children carry measured rates and their own validity. The parent's ports are the child ports on the hull of all child ports (the same hull rule as one level down).
  - *Storage:* every accepted group stores `level2_state` and `children_states`. The `level2_interface` endpoint and gate require exactly one valid parent per accepted candidate.
  - *Contracts:* the parent's shape, recursion to level 3, consumption by the coarse law, the count check, and an unweighted centroid with children of different sizes.
- **F2 (medium): the distinctness proxy missed crossing hulls.**
  - *The defect:* the vertex-in-hull fraction scored 0 for two hexagons sharing 93% of their area.
  - *The fix:* criterion 6 uses the hull-area overlap from exact convex clipping, with the threshold unchanged at 0.2.
  - *Development basis:* overlap 99th percentile 0.100, maximum 0.132 (a touching, accepted group).
  - *Contract:* the reviewer's hexagons, run through the real `unit_validity`, now fail criterion 6.
- **F3 (low): exact ties let the coarse neighbour rule take more than k.**
  - *The fix:* a stable sort takes exactly k candidates, own neighbours first, then applies the radius.
  - *Contract:* the reviewer's tie case gives n_p = 8 and excludes the cross port.
- **F4 (low): harvest sources could be shared across level-2 worlds.**
  - *The fix:* source-isolated assignment. Every template of one harvest world goes to a single level-2 world, and templates that do not fit are discarded. Sources are stored per world, and the harvest ratio rises from 1.3 to 1.5.
  - *Contracts:* the reviewer's split case, both through `assign_templates` and through `build_worlds`.

Contracts: 46. Mutants: 52, all detected locally.

## Unchanged

- **Settings:** placement radius, rate spread, T, the 0.2 overlap threshold, detector and effect thresholds, doses, baselines, endpoint rules, truth tables and the number of worlds.
- **Not tuned:** nothing was tuned on R001 or R002 final worlds.
- **History:** R001 and R002 evidence and the R002 review are preserved as committed.
- **Seeds:** R003 runs on fresh final entropy.
