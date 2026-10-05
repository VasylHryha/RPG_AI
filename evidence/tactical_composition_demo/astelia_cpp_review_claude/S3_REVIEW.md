APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: S3 controllers at commit `f23186a`, the design contract `DESIGN_0G.md` revision 3 (Codex's corrections in section 11), and the report `astelia_cpp/S3_CONTROLLERS_REPORT.md`
Receipt reviewed: `astelia_cpp/s3_controllers_r3/S3_RECEIPT.json`, sha256 `db56b3b9867e0ff70594291076c86c76c07bd8e9628b1a0f5d7df844b19562eb`
Date: 2026-10-05

## Verdict

The three controllers implement design revision 3 and may enter S4 development. This approves the engineering. It does not approve any tactical claim.

## What I checked

**Revision-3 design corrections** (section 11):
- the reference-algebra check is separated from the production ODE check;
- push-pull's hysteresis scale is defined;
- the diagnostic formulas are fixed;
- κ is dimensionless, with a fixed tanh normalization;
- empty-group semantics are defined.

They clarify the design rather than change its intent, and each records its cause. Accepted.

**The equations in the code** (`src/native/s3_controller.cpp`) against the design:
- The resonator phase is ω + P sin θ + K_t sin(ψ − θ) + K · mean e^{−r²} sin Δθ (`:52-54`). P > 0 pushes toward π, as specified.
- Morale is −λm − P + K_t(μ − m) + K · mean e^{−r²}(m_j − m_i) (`:53-54`).
- Pressure is κ(z_in − β z_out) (`:82`); the damage average uses q = e^{−dt/2} (`:76`).
- The preferred distance is f · range · (1 + w(1 − c)/2), with w = 0 for push-pull (`:92`).
- The enemy term G(1 − d/max(ρ, 0.01)) is averaged over up to 8 enemies, with ρ the gap for melee and direct and the centre distance for artillery (`:94`).

All match.

**My own fights** (fresh build of `f23186a`; review development seeds 2026100700-2026100729, never used by S3):

| Arm | vs novice (head-to-head, 10 seeds × 2 sides) | vs regular (the same) | vs the 19 doctrines (pool-default skills, 1 seed × 2 sides) |
|---|---|---|---|
| resonator (default knobs) | S −12.70, 0/20 won | −25.05, 0/20 | −4.11, 4/38 won |
| morale (default knobs) | −17.15, 0/20 | −5.75, 0/20 | −0.71, 5/38 |
| push-pull (default knobs) | −16.00, 0/20 | −33.60, 0/20 | −14.05, 0/38 |
| nearest | −15.40, 0/20 | −24.05, 0/20 | −9.42, 1/38 |

- There were zero controller failures in 196 fights, and the resonator replay is deterministic.
- **These are untuned midpoint knobs. They are development readings, not results.** With default knobs every arm loses head-to-head to novice and regular. S4 tuning has to find out whether
  any arm can beat them (the stop row in design section 10).

**Not rerun:** the 213 tests, the sanitizer, the C4 1e-9 fixtures and the 80/228 parity fixtures. I read the receipt but did not reproduce them.

## Notes for S4

1. **The runner cannot yet set the P2/P3 panel.** Design section 6 specifies the 19 doctrines with opponent skills = elite skills without `artyRollout`. `s3_runner.py` gives doctrine opponents
   their pool-default skills only. Add an explicit, fixed opponent-skill setting before the P2/P3 development runs.
2. **The morale arm against regular** (−5.75) is far better than against novice (−17.15), while the other arms do worse against regular. Look at a few fights before tuning, to check whether
   this is a real matchup effect or a configuration difference between the two levels (Codex's review finding 5: a level resets the formation).
3. **Zero natural rates in the default resonator** mean that this grid never exercised a rotating phase (the report says so). S4's bounds include non-zero ω.
4. **Codex's design review file** (`docs/reviews/tactical_0g_design_review_codex.md`) was untracked. It is committed with this review, unchanged.
