# 0039: 0g "the network decides, exact functions compute"

**Date:** 2026-10-09 (~08:15). **Decided by:** the owner. The owner asked "can the AI network use some API to make it efficient, so it can reuse some efficient code... balance or combine what AI can do best and what some function or math equation can do - it also fits into RRG logic", then chose "Yes, prepare it now (Recommended)". **Recorded by:** Claude (claude-opus-5-5).

## Decision

1. **Learned heads choose; exact functions compute.** Learned policy heads may select among candidates computed by exact, pure geometric or physical functions, or parameterize them. The functions are:
   - the lead/intercept point for a moving target;
   - legal range-band projection;
   - splash coverage of an enemy set;
   - cluster centres;
   - the predicted dodge spot;
   - distance to safety behind friends;
   - threat estimates.

   This is known as parameterized actions or tool use.
2. **Tools compute; they never decide.** Whom to target, whether to fire or hold, and whether to advance, hold or fall back stay learned. A function that embeds a decision rule (react dodge, the V2 planner, P16) is a script, not a tool.
3. **Honest labels.** Results are reported as network+tools versus network-only, on the same paired fights (script-vs-RRG labelling rule).
4. **RRG fit.** The resonator or mode selects; the geometric substrate executes. A verified primitive becomes a reusable building block for the next level (recursion). The shape library becomes the network's toolbox.
5. **Use.** It is prepared now as stage B2 in new files, so running stage B training is untouched. It is used if stage B fights show aim or movement still failing. The diagnosis found artillery aim about 99.7% wrong even on training data.
6. **Also prepared: a learned-dodge arm** (owner question "can't we copy dodge with the network? why code?"). It is the same network with the shared react/dodge layer switched off, so its own movement must dodge, compared with the coded layer on the same fights. It runs after the networks can fight, so the two problems are not confounded.

## Addendum: tools are a bridge (owner, 2026-10-09 ~15:45)

Owner: "so we should use teacher tools only in case we can quickly or properly replace it with network". Agreed rule:

1. **Decisions are always learned.** Tools never decide (unchanged).
2. **A pure-math tool is temporary.** It stays only until the network can do its job equally well. Each tool gets a replacement test: the same network with the tool removed, trained to compute that part itself (first by distillation from the tool's outputs, then reward training), compared on the same paired fights (deaths, kills per own death, wins).
   - **If the network matches the tool,** the tool is removed.
   - **If it cannot, or only at disproportionate cost,** the tool stays as a calculator, and the measured gap is recorded.
3. **Order:**
   1. B2 first produces a competent network+tools fighter.
   2. Tools are then removed one at a time, starting with the coded react dodge (the learned-dodge arm is already built) and aim, while a working fighter is always kept.
