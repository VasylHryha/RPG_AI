# Addendum to the two-body pilot report (2026-10-03)

Additive. `REPORT.md`, `SPEC.json`, `pilot.py`, `run/` and `posthoc/` are unchanged, and no verdict is changed. The pilot remains an owner-requested
exploratory record, **not C6 evidence**; C6 stays BLOCKED / R006 STOP. This addendum follows a recheck by four same-family (Claude) subagent audits; it is a
self-audit, not a cross-family review. Numbers marked "audit" were recomputed by a subagent from the stored runs and not re-derived by me.

## 1. The unit-table post-hoc result that `REPORT.md` omits

`posthoc/posthoc_unit_table.py` (commit `b7397e6`; output `posthoc/posthoc_unit_table.json`; descriptive, not predeclared) tabulates the stored units. It is
the only basis for the sentence in `tactical_composition_demo/MOTIVATION.md` that the model has no way for a unit's shape to set its frequency.

| Level | Units | Elements | Intrinsic frequency | Own collective rate (median; range) | Correlation of size, radius with rate |
|---|---|---|---|---|---|
| 1 | 80 | 6 to 16 | exactly 0 for every unit and element | 0.0; about 1e-11 at most | size vs rate 0.08; radius vs rate 0.09 |
| 2 | stored level-2 groups | 28 to 64 | small, nonzero (mean magnitude up to 0.017) | -0.00045; -0.016 to +0.017 | size vs rate -0.16; radius vs rate -0.13 |

Reading: at level 1 every unit has frequency zero, so nothing about a unit's geometry can determine its frequency. At level 2 the rates are small and not
explained by size or radius (absolute correlation below 0.17). A shape-to-frequency link would have to be added to the element law; it is not present in the
C4 law this pilot used. This is a statement about the stored units only.

## 2. Wording in `REPORT.md` that the data do not fully support

| Statement | Better reading | Source |
|---|---|---|
| P1 and P3 REFUTED, with P3 "push 0.302" and "push much weaker at level 2" | The specification pools gaps 0.6, 1.2 and 2.0, and the gaps with no interaction dilute the fractions. At gap 0.6 alone the push criterion is met by 90.6% of level-2 pairs (29 of 32) and 100% of level-1 pairs. P1 is diluted by gap 1.2 in the same way. The recorded verdicts follow the pre-registered pooling. | audit |
| "approach and phase rates are zero to machine precision at gaps 1.2 and above, at both levels" | The phase rates are about 1e-9 to 1e-15. The approach slope is not zero: at level 1 it is -0.0041 at gaps 1.2 to 2.8 (exactly 0 at gap 4.5); at level 2 it is -0.00056 at every gap including 4.5, equal to the decoupled control. For gaps 1.2 and 2.0, 37.5% of level-1 pairs meet P3(a)'s push criterion. | audit |
| "R shrinks from 3.09 to 2.64 (median)" | Pooled over initial-offset cases. Anti-phase pairs grow from 3.09 to 3.39. | audit |
| "near-misses" and "a modest margin" (level-3 recovery) | The median pattern error is 0.21 rad in pass 1 and 0.13 rad in pass 2 against the 0.1 threshold: about 2 times in pass 1. Both medians are taken over candidates that already failed, so they exceed the threshold by construction. This is a hypothesis from stored data, not a test. | audit |
| (omitted) | `PARTS_DAMAGED` occurred in 28% (natural offset) and 34% (half-pi offset) of the short level-2 runs at gap 0.6. | audit |
| "They do not fuse" (and `MOTIVATION.md`) | Pairs only, at the gaps tried. Five-group worlds, where the earlier merging was seen, were not tested. | `REPORT.md` limits |

## 3. What this does not change

The two-body pilot cannot say whether level 3 can form under another law, and it assigns no C6 verdict. The own-level normalization in the post-hoc analyses is
mine, chosen after seeing the data. The independent-reproduction status is: raw runs and hash identities are committed; a rerun needs the gitignored,
macOS-specific `build/c6/element_law.dylib` (`tools/build_c6.py` builds it; reproducing the recorded dylib hash is unverified).
