# What we did, 6–7 October 2026 (night and morning)

**Author:** Claude (claude-opus-5-5), with Codex (GPT-6) as implementer and cross-family reviewer.
**Goal:** a different AI foundation (growing oscillator shapes, RRG) that beats Astelia's scripted AI in our tactical game.
**Scope:** everything since the 7.11 fixtures ran (about 23:00, 6 October) up to about 11:00, 7 October.
- **The step plan:** `docs/PLAN_CURRENT.md`.
- **Ideas:** `docs/IDEAS_AND_ROADMAP.md`.
- Nothing has been pushed. Every result below is committed locally.

## 1. Your decisions and ideas this session

| When | Your words | What it changed |
|---|---|---|
| morning | "surviving doesn't count as a win… you survive better if you efficiently kill enemies" | 0g's success criterion is now an **elimination win**: enemy destroyed before the timeout, with our units alive. A timeout is never a win. `DESIGN_0G.md` §19 |
| morning | the O pin "can not be decision — confirm with tests and explain… do research" | The O pin was tested on 5 seed sets with controls and backed by research (section 3) |
| morning | "c6 yes use faster math then" | Decision 0032: C6 adopts the inexact math (section 4) |
| morning | ports: "one connection in and out"; a router choosing the shape | Roadmap: ports, and routing by resonance |
| morning | a shape that does one job is one node, with things inside at a different scale | Roadmap: recursion (C5/C6) |
| morning | "inside stable and organized, connections at input and output" | Roadmap: interior and port roles |
| morning | different scales need different interactions, like the four forces (your table) | Roadmap: saturating "strong" bonds, screened "electromagnetic" cohesion, weak "gravity" pull, with experiments (section 3) |
| morning | a third dimension? | Judged no help for the connection problem (3D swarmalators form balls). Kept as an idea if springs fail |

## 2. 0g: beating the scripted AI

| Step | Result | Evidence |
|---|---|---|
| **v5 development** (night) | resonator against regular −6.03, novice +5.60. NOT_READY | `astelia_cpp/S4_V5_DEVELOPMENT_REPORT.md` |
| **v5 trace diagnostic** | the resonator's phase never settles (locked < 0.5% of the time); about 25 large reversals per unit-minute against morale's about 1; it dies in gun bands | `astelia_cpp/S4_V5_TRACE_DIAGNOSTIC.md` |
| **v6 design** (an amplitude-and-phase, Stuart-Landau resonator) | three Codex review rounds, then approved | `DESIGN_0G.md` §18, 18.1, 18.2 |
| **v6 development** (attempt 2; attempt 1 stopped on a cache schema) | against regular **+8.03**, but 198/200 timeouts. A survivor-score tie with morale. **Not a win under your criterion** | `astelia_cpp/S4_V6_DEVELOPMENT_REPORT_ATTEMPT2.md` |
| **Kill telemetry and gun-assault diagnostic** | **0/20 elimination wins against regular for every arm.** Enemy guns die only to artillery; assaults on guns fail; enemy artillery makes 81% of our deaths | `astelia_cpp/S4_GUN_ASSAULT_DIAGNOSTIC.md` |
| **Volley probe** (synchronized volleys and nets) | 0/20 against regular. **Key fact: our shells aimed at regular guns hit 99%, but we aim only about 14 per fight** (about 1.4 hits per gun; about 12 kill one) | `astelia_cpp/S4_VOLLEY_PROBE.md`, DESIGN_0G §19.2 |
| **Focus-fire probe** | committed, focused guns rout **novice 20/20** and kill 3.4 of 10 regular guns, but **lose the whole battery** to regular's screened line (enemy artillery and direct units) | `astelia_cpp/S4_FOCUS_PROBE.md`, DESIGN_0G §19.3 |

**Where 0g stands:** no arm has won a single fight against regular yet.
- **What the problem is:** a coordination problem. The guns must commit **together**, with a direct-unit screen, so the enemy line cannot pick them off.
- **Next:** a scripted collective-commitment probe, then the RRG version (target-group synchrony, K_t).

## 3. 0h: growing shapes, the connection problem

**In simple terms:**
- We can make shapes, and a connection that is already built carries the signal well.
- **What we cannot yet do is grow a connection from a shape to the output and keep it.**
- Each cell moves toward the average of its 8 nearest neighbours, so everything clumps like a water drop, and a growing link to O snaps back.
- In the literature this is the swarmalator "compact disc" effect; Merks 2008 describes cells that "aggregate into large, round clusters".

| Step | Result | Evidence |
|---|---|---|
| **7.11 fixtures** | empty start FAIL; seeded start PASS | `growing_shapes/runner/REV711_FIXTURE_REPORT.md` |
| **Diagnosis** (three revisions, two Codex rechecks) | in the empty start the closing link breaks within seconds, because the tip is pulled back at 0.3–0.6 m.u./s; the edge is lost by coefficient decay; not a phase problem; O placement swaps alone did not separate the starts | `rev711_diag/REV711_F5I_DIAGNOSIS.md` |
| **Root-relative O pin (C2)** | on the validated pilot assay (it reproduces the fixture exactly), both starts meet the F5 thresholds | `REV711_F5I_DIAGNOSIS.md` §8 |
| **Revision 7.12 design (C2)** | Codex APPROVE_WITH_NOTES | `DESIGN_0H_REV7.md` §19, 19.6 |
| **Validation, at your request** (5 seed sets, controls) | **C2 8/10 against the centre pin's 3/10**; opposite and perpendicular pins 3/6 (like the centre); **F5 flips from seed to seed, so one key per start is unreliable**. Codex recheck: CHANGES_REQUIRED on wording and the multi-key gate (fixes pending) | `rev711_diag/validation_712/OPIN_VALIDATION_REPORT.md`, `docs/reviews/tactical_0h_opin_validation_recheck_codex.md` |
| **Research** (two memos) | the pin is a **placement effect**, not new bridging. Chain-forming systems use contact inhibition, saturating bonds, guidance fields or flow reinforcement | `rev711_diag/OPIN_RESEARCH_MEMO.md`, `CHAIN_GROWTH_RESEARCH_MEMO.md` |
| **Medium-law experiments** (scratch) | bonds on every pair 1/10; chain bonds (at most 2) 5/10; **chain bonds + partial screening 6/10, the best medium-only result**; chain bonds + pin 8/10; weak pull (0.1) 4/10 (paths everywhere, weak signal); strong pull (0.3) 0/10. **The variants now always reach O; the remaining failure is keeping the signal from the roots to O** | `rev711_diag/medium_variants/README.md` |

**Where 0h stands:** the O pin works (8/10) but is a placement trick. Chain bonds with partial screening (6/10) are the best medium change; it always reaches O, but sometimes loses the signal from the roots.
- **Next:** why the signal is lost (the chain detaching from the roots, or crowding at O), then combine the best medium rule with the multi-key test.
- **Then:** fix the validation-report wording and the multi-key F5 gate (Codex R1–R6), and choose the 7.12 content with you.

## 4. C6: the faster engine

| Step | Result | Evidence |
|---|---|---|
| **Inexact-math impact study** (three Codex rounds) | in 10 stored worlds no decision or outcome changed (77,342 decisions, 4.3 M pair tests); about −25% CPU; future-panel risk not quantified | `evidence/c6_option_b/inexact_study/INEXACT_IMPACT_REPORT_R3.md` |
| **Adoption** (decision 0032) | **ADOPTED:** the 4 reference worlds pass the new contract; new references generated; **−23.9% CPU**; the exact kernel stays selectable; macOS build pinned | `evidence/c6_option_b/ADOPTION_0032_CONTINUATION.md` |

C6 itself stays BLOCKED / R006 STOP until its own owner-approved steps.

## 5. Visuals

The **Growing Shapes Atlas** (https://claude.ai/artifact/6t2LXndFvARKLjGRRa6gWx) shows recorded runs, with cells coloured by shape, strong links and the path to O, plus the planned ports-and-nodes architecture. It has three scenarios: the centre pin, the root-relative pin and the seeded start.

## 6. Process notes (lessons)

- **Overclaiming, caught twice by Codex:** "O must be surrounded"; "direction matters" stated as fact. Claims are now narrowed to what the runs show.
- **Instrumentation bug:** a per-step recorder copied into recovery clones advanced the live run, and one pilot was invalidated. Fixed by a live-only, class-level recorder with a clone-isolation check.
- **The pin guard worked:** pilots refused to run after the design file changed. They were run in a worktree at the reviewed identity, not by weakening the guard.
- **Shared git index:** a commit of mine swept Codex's staged files into it (disclosed by Codex). Commits now use explicit paths.
- **Machine load:** too many parallel pilots pushed the load average past 200. Batches are kept smaller now.

## 7. Open decisions for you

1. **0h:** after the screening and weak-pull results, which way do we go?
   - adopt the O pin (honestly labelled a placement prior, 8/10);
   - push the medium change (bonds, screening, a weak pull);
   - combine them.
2. **0h:** the multi-key F5 gate. Codex recommends five fresh key sets, with every key passing in each start.
3. **0g:** a scripted collective-commitment probe, then the v7 design. I'll proceed unless you prefer otherwise.
