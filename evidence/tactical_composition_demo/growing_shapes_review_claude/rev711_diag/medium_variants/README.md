PILOTS (no verdict): medium-law variants for the connection problem, on scratch copies of the 7.11 code. Best medium-only result: chain bonds plus partial screening, 6/10 (pin 8/10, original 3/10)

# Medium-law variants: can growth build and hold a link to O?

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**Why:** the owner asked to research and test different approaches to the connection problem. The evidence trail is in:
- `../REV711_F5I_DIAGNOSIS.md` (the diagnosis);
- `../CHAIN_GROWTH_RESEARCH_MEMO.md` (the research);
- `../validation_712/` (the O-pin tests).

**How these ran:**
- **Scratch copies of the reviewed 7.11 code** (`kernel_pilot*` in the session scratchpad). Each one changes only the native motion law in `rev7_medium.cpp`; the patches are here.
- **The identity gate is stubbed** in the scratch harness (`pilot_common_scratch.py`), because the native law is deliberately different.
- **The same F5 A/B/E estimator as `../pilot_common.py`,** which reproduces the 7.11 fixture exactly on the unchanged law. It includes the 160-decision guard.
- **The same key sets as `../validation_712`:** key set 0 = the fixture keys; 1–4 = the alternative keys and worlds 13,000,000+.
- **Gate shape:** A ≥ 0.3, B ≥ 0.3, max E ≥ 0.5 per run (descriptive).
- **Binaries:** listed in `SCRATCH_BINARIES.txt`. Bond v1's binary was `14b942a3…5ee9`; its source is in `bond_v1.patch`.

## Results (5 key sets × 2 starts)

| Variant (patch) | What changes in the motion law | (i) empty | (ii) seeded | Total | What happened |
|---|---|---|---|---|---|
| 7.11 law, origin pin (control, `../validation_712`) | — | 2/5 | 1/5 | **3/10** | the tip retracts; the cluster face settles 1.5–2.4 from O |
| C2 root-relative O pin (control, `../validation_712`) | placement only | 5/5 | 3/5 | **8/10** | the cluster face reaches O |
| **Bond v1** (`bond_v1.patch`) | every strong pair gets a spring, rest 0.45; unbonded pairs only exclusion | 1/5 | 0/5 | **1/10** | the whole cluster contracts like a gel; tips are still held back by about 7 springs |
| **Bond v2** (`bond_v2.patch`) | springs only to each cell's **2 nearest** strong partners (chains), rest 0.556; unbonded pairs only exclusion | 2/5 | 3/5 | **5/10** | **cells always reach O** (nearest distance exactly 0.556, the bond length), but in half the runs the response vanishes (A, B about 0.05): the part at O detaches from the driven cells |
| **Bond v2 + C2 pin** (`bond_v2.patch` + `../pilot_c2_opin.py`) | as bond v2, O pinned toward the first root | 5/5 | 3/5 | **8/10** | the same as the pin alone; the bonds add nothing on top of the pin |
| **Bond v2 + guidance G = 0.3** (`bond_v2_guide_G0.3.patch`) | plus a constant pull of 0.3 m.u./s toward O on every cell | 0/5 | 0/5 | **0/10** | far too strong: every cell collapses onto O (distance about 0) and the sensors are abandoned, so there is no response |
| **Bond v2 + guidance G = 0.1** (`bond_v2_guide_G0.1.patch`) | a 0.1 m.u./s pull | 0/5 | 4/5 | **4/10** | paths to O exist in **all** 10 runs (max E 0.7–0.8), but cells pile up on O (nearest about 0.1) and the response is weak (A 0.05–0.45): the crowd at O swamps the signal |
| **Bond v2 + partial screening** (`bond_v2_screening.patch`) | saturated cells (2 bonds) exert and feel no cohesion; free cells keep the swarmalator law | 3/5 | 3/5 | **6/10** | **the best medium-only result so far.** Cells reach O in every run (nearest exactly 0.556, the bond length); 4 runs still lose the signal (A about 0.03–0.2) |

**What we learn so far:**
- **Saturation matters,** as for the strong force: chain bonds (at most 2) beat bonding everything (5/10 against 1/10).
- **Bonds let growth reach and hold O,** but they do not keep the whole sensor-to-O chain connected.
- **The pin is still the strongest single factor.**
- **Screening adds a little:** 5/10 → 6/10. It is the best medium-only rule, but still below the pin (8/10).
- **A global pull must be weak, and even then it over-crowds O:** 0.3 destroys the structure; 0.1 builds paths everywhere but swamps the signal.
- **The common failure of the medium variants is no longer reaching O. It is keeping the signal from the driven cells to O.** That points to the chain's connection back to the roots, and to signal quality at O, not to reach.
- **The owner's frame:** scale-separated interactions (four-forces analogy: saturating "strong" bonds, screened "electromagnetic" cohesion, weak "gravity"). See `docs/IDEAS_AND_ROADMAP.md`.

**Limits:**
- One run per key set and start, so these are single realizations.
- Scratch code, not reviewed.
- No verdict.
- Raw traces stay in the session scratchpad and are not kept. The logs here carry the per-run summary and the assay numbers.
