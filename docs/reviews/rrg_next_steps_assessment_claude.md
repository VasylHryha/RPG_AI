# Assessment of "RRG — Proper Next Steps / Execution Instructions" (2026-10-07)

**Author:** Claude (claude-opus-5-5), the drafter. **Date:** 2026-10-07.
**Source:** `~/Downloads/RRG_NEXT_STEPS_EXECUTION_INSTRUCTIONS_2026-10-07.md`. It reviewed `main` at `446215f`, before this session's commits.
**The owner's framing:** a second point of view, to mine for better solutions and real blockers. It is not an instruction to follow in full.

## 1. Adopted

| Point | Why | Where |
|---|---|---|
| The O pin is a **benchmark**, not the law | it moves the output instead of solving the connection; it remains the strongest exploratory result (8/10) | plan A6s; the W6 question is closed for the pin |
| **Success means signal, not reach:** the grown connection keeps a measurable input-dependent response | F5's A and B are input-dependent only on average; per-site causal response is unmeasured | telemetry at O: an input-perturbation response per site |
| Telemetry is observer-only, with an on/off byte-identity test, implemented by Codex | my traces are scratch code; their reproduction check is necessary but not sufficient | plan A6w |
| **Benchmarks on the fresh keys:** the base law and the pin run alongside the selected law (descriptive, not gating) | if the new law is no more reliable than the placement prior, we must know before development | §19.7 addition with the next revision |
| **One principal change per revision** | attributable results | the V3 pilot (two changes) was dropped from the queue; V1 alone is the candidate |
| **0g v7 trigger:** real elimination wins against regular **and** clearly better than P5 | stricter than my §19.4 reading (≥ 7/10 guns destroyed), and matches the owner's criterion | §19.4 reading amended after the probe finishes |
| No heavy 0h and 0g runs at the same time; C6 maintenance only | the machine is shared (load 100–140 from other projects) | standing rule |

## 2. Where I think the document is wrong or incomplete

**2.1 The taxonomy misses the cause we actually observed: removal by a death rule.**
- **What the traces show (A6v):** in both traced failures of chain bonds + screening, the budget rule D3 deleted an element of the live root→O chain. The passing run had no D3 removals. Evidence: `growing_shapes_review_claude/rev711_diag/medium_variants/signal_loss/`.
- **This is class I (an internal break), but not by bond strain.** The document's remedy for I, bond hysteresis ("hard to form, easy to keep"), would not prevent it.
- **The deeper defect:** D3 removes the lowest-lock element, on the premise that low lock means "least organized". **Any law that raises locking (bonds do: locks about 0.9999) removes that premise.** The choice then becomes effectively arbitrary with respect to function.
- **The principled fix** comes from the 0h proposal's own rule, "keep only where they help and hold": prune by service, not by lock. The minimal form is V1, under which the budget never removes an element on a live root→O path.
- **Proposed:** add class **D (removal by a death or budget rule)** to the taxonomy.

**2.2 Break versus repair.**
- The document asks for a connection that is "continuously connected". A self-recreating medium will break links (deaths, noise, remodelling). **What matters is break → repair.**
- In the traced failures there are two stages:
  - the break (D3);
  - the **non-repair**: O's leftover piece closed into a saturated three-element ring, which screening makes inert, and births were then refused on cost.
- **Proposed:** classify each failure by its break cause **and** its non-repair cause, and report the repair-time distribution. The F5 gate already tolerates repaired breaks, because it averages E over checkpoints.

**2.3 Ports are not strictly "after" the connection.**
- The document defers ports until after development. But **bounded port degree and protection may be part of how one connection becomes reliable.** In our traces, O's two bonds let the closed ring form.
- **Proposed:** port **rules** (degree, protection) are admissible as connection mechanisms, one at a time. The full port interface, the router and composition wait, as the document says.

**2.4 The economics of the strict gate (a practical blocker).**
- Every one of 10 runs must pass:
  - a law with a true per-run pass rate of 0.9 passes the whole gate with probability 0.9¹⁰ ≈ 0.35;
  - at 0.8, ≈ 0.11.
- Each attempt spends five fresh key sets and about 1–4 h.
- **Proposed entry condition (a prerequisite, not a relaxation):** a candidate law first passes all 10 exploratory runs (5 key sets × 2 starts). Only then are the fresh keys spent.

**2.5 Stage the telemetry.**
- The document's B1 list is large: per-hop PLV, cross-correlation, readout contributions. The two traced failures were classified from **topology alone** (paths, bonds, deaths).
- **Proposed:**
  - **stage 1:** topology and lifecycle telemetry for all failures (root attachment, path, first lost edge and its cause, bond and death events, the fragment at O);
  - **stage 2:** phase-propagation metrics, only where stage 1 finds an intact path with a lost signal (class P).

**2.6 The development run's design predates the medium change.**
- The 48-training protocol (rev 6/7) assumed the 7.11 law. A law with bonds, screening and service-based pruning changes the deaths, the budget and control M's matched births.
- Batch D must explicitly re-check M/U matching under the new death rule, not only list it.

## 3. Resulting order (Track A)

1. A6v: the V1 pilot (path-protected budget) on the exploratory keys. **Running.**
2. A6w: Codex builds the stage-1 observer telemetry (on/off identity). It classifies all screening failures and the V1 failures by break cause and non-repair cause.
3. **One** revision from that classification, with Codex design and implementation review.
4. The exploratory entry condition: 10/10.
5. §19.7 fresh-key gate, with the base law and the pin as benchmarks.
6. Cost projection, then the owner's approval of the development run.
