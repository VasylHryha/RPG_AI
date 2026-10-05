# Proposal 0h: growing shapes, from atomic skills to combined skills (DRAFT for the owner; nothing built or run)

Exploratory line under decision 0028. It comes from the owner's direction of 2026-10-05:
- AI should be built from shapes, from the simplest to the complex;
- parts connect only when together they do better than apart, and stay connected when the combination is stable;
- each atomic shape is crystallized on a tiny task (move, spatial recognition, memory, …), and what one shape produces is what the next consumes.

**The claim boundary**, to be kept:
- first test exactly that, in a small 2D world;
- no claim about general AI, scale, the brain, or novelty over the related work listed in section 8.

## 1. The three statements every experiment makes

| | This proposal |
|---|---|
| **What the pieces are made of** | Small media running the C4 element law: position, phase, natural rate; in-phase elements attract, neighbours sync. Their geometry (positions, rates, couplings) is **learned** (section 4). |
| **How connections form** | By the three bond conditions (section 3): a connection is possible only between matching frequency bands; it stays only if the joint result beats the parts and the joint shape is stable under kicks. No connection is wired by hand. |
| **Closest known methods, and what differs** | Cascade-correlation, progressive networks, neural module networks, options in hierarchical reinforcement learning, mixtures of experts, oscillator networks (AKOrN), communication through coherence (neuroscience). What differs: locked parts that publish a rhythm interface and **bond by band matching plus measured benefit and stability**, with no retraining of the parts' insides. Whether that works is the question. |

## 2. The common language: phase and frequency bands

Every shape receives and emits **rhythms**:
- **A direction in the plane is an angle, carried as a phase.**
- **Strength or distance** is an amplitude.
- **Memory** is a phase held after its input stops.
- **Different kinds of signal use different frequency bands.**

An output port emits in one band and an input port listens in one band. This makes type compatibility **band matching**, not a declared list. The band layout is fixed by the drafter for v0 and stated before any run; letting bands emerge is a later step.

## 3. The bond: when two shapes connect

A connection from shape A's output to shape B's input:
1. **can form** only if A's output band matches B's input band (the valence);
2. **stays** only if the joint result beats both (a) each shape alone on the combined task and (b) the two side by side without the connection (the benefit, measured on paired episodes with a registered margin);
3. **stays** only if the joint shape recovers from kicks: input noise, or an input dropped for a moment. This reuses the C4 recovery idea, with thresholds fixed before running.

A connection that fails condition 2 or 3 dissolves. Bonds are tried where they are possible and kept where they help and hold.

## 4. Learning a shape: resonance plus selection, and locking

- **Resonance:** inputs drive the phases of sensor elements, and elements that lock pull together and couple more strongly (the C4 law's own mode → geometry).
- **Selection:** a task reward decides which locks become permanent: locks during good outcomes strengthen, and locks during bad outcomes loosen (three-factor learning).
- **Yardstick variant:** the same medium trained by gradient through its smooth dynamics (AKOrN-like). This shows whether resonance plus selection can stand alone.
- **Locking (consolidation):** a shape is locked when its task score has stopped improving and it passes the stability test. Its inside then stops changing, and it publishes its interface (bands, ports).

## 5. Nature's four conditions, applied

| Condition (source) | In 0h |
|---|---|
| Changing related goals make networks modular (Kashtan and Alon 2005) | Atomic tasks are trained in rotation, not one at a time to the end |
| Connection cost makes networks modular (Clune, Mouret and Lipson 2013) | Every coupling has a cost in the score |
| Routing by synchrony (communication through coherence, Fries) | Shapes connect only through band-matched phase coupling |
| Staged consolidation (complementary learning systems) | Lock, then learn the next level on top |

## 6. The atomic shapes and the first combinations (a 2D world, small)

| Atomic shape | Consumes | Produces | Tiny crystallization task |
|---|---|---|---|
| Perceive | nearby positions | direction (phase) and distance (amplitude) of the most relevant enemy | point at the right enemy |
| Move | a direction plus approach or avoid | a step | reach a point; keep a distance |
| Remember | a direction | the same direction held over time | keep pointing where an enemy was after it vanishes |
| Choose | several directions | one selected direction | pick the nearest or weakest |

**Level 2 combinations:**
- perceive → move: chase or kite;
- perceive → remember → move: pursuit out of sight;
- perceive → choose → move: focus fire.

**Level 3:** combinations of level-2 shapes in game-like fights. The world is a small purpose-built 2D task suite first. The Astelia bench is used only after level 2 works.

## 7. Predictions that can fail (measured against two yardsticks: one medium of equal total size trained from scratch, and a normal neural network of equal parameter count)

- **G1, atoms form:** each atomic shape reaches a registered task score and passes the stability test.
- **G2, bonds are selective:**
  - band-matched connections that help are kept;
  - mismatched or useless connections are not formed or dissolve;
  - checked against a control in which bonds form at random.
- **G3, growing is cheaper:** a level-2 shape built from locked atoms reaches the registered score in fewer training episodes than either yardstick learning the same task from scratch.
- **G4, reuse:** the same locked atom works inside at least two different level-2 shapes without changes to its inside.
- **G5, no forgetting:** after level 2 is learned, every atom still passes its own task.

Each can fail, and each failure says which part of the idea does not hold.

## 8. Related work, to be read before the design is frozen

- cascade-correlation (Fahlman and Lebiere 1990);
- progressive neural networks (Rusu et al. 2016);
- neural module networks;
- the options framework;
- lottery tickets (Frankle and Carbin 2019);
- the grokking circuits (Nanda et al. 2023);
- AKOrN (Miyato et al. 2025);
- modularity under varying goals (Kashtan and Alon 2005) and under connection cost (Clune, Mouret and Lipson 2013);
- communication through coherence (Fries);
- complementary learning systems (McClelland, McNaughton and O'Reilly 1995).

## 9. Order and approval

Owner approval of this proposal comes first. Then:
1. the band layout, the task suite, the learning rules and all thresholds written into a design;
2. a Codex review;
3. development: atoms first, with a stop row if G1 fails;
4. registration, the owner's approval naming the specification, and one recorded run.

Nothing in this proposal runs before the owner's approval. It sits alongside the C6 C++ port request and the running 0g v1 development.
