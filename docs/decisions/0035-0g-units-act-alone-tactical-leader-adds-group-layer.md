# 0035: 0g units act on their own; a tactical leader network adds a group layer on top

**Date:** 2026-10-08. **Decided by:** the owner ("units should be able to act on themselves - tactical leader adds extra smartness or group reaction"). **Recorded by:** Claude (claude-opus-5-5).
**Context:**
- The first trained networks (`d82b505`, `b5cc3cf`) and their cross-family recheck (`a919155`, H2) showed the aim head could not learn.
- The teacher's aim is a **group-level** volley plan: the copied planner assigns all ready guns' aim points together (`s4_net_slice_v1/teacher.cpp`).
- Each network gun decides alone and cannot see its slot. Identical observations then carry contradictory labels (left, centre or right), and the network collapses to the centre.
- The owner identified the cause: the teacher is a tactical AI that controls the group, while we trained unit-level networks.

## Decision

1. **Unit networks must be competent alone.**
   - Each unit learns move, dodge, range keeping, target and fire timing, plus **its own best single shot** for aim (per-gun labels, no group spread).
   - With no leader, units fight properly.
2. **A tactical leader network adds a group layer.**
   - It observes the whole group: guns, readiness and enemies.
   - It emits **commands** that units take as an extra input: volley slot or aim offset, hold/fire-together timing, and group reactions such as a shift away from incoming shells.
   - Units must remain valid when the command input is empty.
   - The leader is trained from the teacher planner at the planner's own level, so its labels are consistent.
3. **Measured separately.**
   - The arms are units alone and units plus leader, on the same paired fights.
   - The leader must earn its place by its added kills or saved deaths (decision 0034 axes).
4. **Plain and RRG in parallel at both levels.** At the unit level these are N1/N1r/N2. At the leader level: a plain set-attention leader, and an RRG level-2 group resonator, the parent element over its guns, with lawful up/down transmission (AGENTS.md normalization ledger).
5. **Closest known methods:** hierarchical commander/unit control (feudal and hierarchical RL; StarCraft micro agents), and communication policies (CommNet, BiCNet, TarMAC) for comparison. The RRG difference is that the leader is a resonator whose state is formed from its units' modes and feeds back to them.

## Consequences

- **Aim labels:** the stage-1 unit aim label changes to a per-gun label. The volley spread moves to the leader.
- **Re-collection and retraining:** teacher data is re-collected with both label levels (about 7 minutes) and the units are retrained.
- **Leader fixes ride along:** the fixes from recheck `a919155` (J confound, contested drills, seeds and data order, committed per-fight parity, per-run results files) go into the same build.
- **Timing:** the build starts after the running DAgger rounds finish (no code edits during a run).
