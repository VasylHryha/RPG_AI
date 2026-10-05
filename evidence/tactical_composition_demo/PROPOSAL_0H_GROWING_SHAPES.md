# Proposal 0h, revision 2: shapes that grow and die in a shared medium (DRAFT for the owner; nothing built or run)

Exploratory line under decision 0028. It comes from the owner's direction of 2026-10-05:
- build from the simplest shapes to complex ones;
- parts connect only when together they beat apart and the combination is stable;
- atomic shapes are crystallized on tiny tasks;
- **"we should allow it grow and die, that's the main thing, and have clear conditions for it"**.

Revision 1 (`6c6cbe0`) is replaced. The changes and their causes are in section 10.

## 1. The three statements

| | This proposal |
|---|---|
| **What the pieces are made of** | Elements running the C4 law (position, phase, natural rate; in-phase elements attract, neighbours sync), living in **one shared medium**: the background, as in C6. |
| **How structure forms** | Elements are **born and die** by the conditions in section 3. Shapes are groups that lock (C4/C5 detection). Shapes connect **through the medium** when their bands match, and the connection stays only if it is stable (and, as a labelled addition, useful). Nothing is wired by hand. |
| **Closest known methods, and what differs** | Growing neural gas, cascade-correlation, NEAT, dynamically expandable networks, progressive networks, oscillator networks (AKOrN), communication through coherence. What differs: birth and death driven by **resonance** (novelty, strain, locking), structure carried by a **shared background** the shapes change (the RRG background, as in C6), and bonds by band match plus stability. |

## 2. What comes from the theory and what is added (so that no result is read as more than it is)

| Element | Source |
|---|---|
| C4 law; groups lock and publish an interface; the same law at every level; resonance shapes geometry; stability selects | **theory and accepted C4/C5** (decision 0007) |
| Structure transforms the background, which grows the next structure | **RRG v0.2.1** (B → R → B); requires C6's medium |
| Birth by novelty and by strain; death of unlocked elements | **derived** from resonance and stability (section 3) |
| **Task reward and usefulness** | **added** (machine learning and neuroscience), labelled; it is tested against "stability only" |
| Direction carried as phase, frequency bands as types | **design choice** (fits the spirit; not dictated by the theory) |
| Atomic tasks | **chosen by the drafter** (a hand-made split, a known weakness) |
| A cost per element and per coupling; changing goals | **borrowed** from modularity research |

## 3. Birth and death: the main mechanism, with exact conditions

**Measured quantities** (computed by the runner and logged):
- **Lock** L(i, j): the phase-locking value of elements i and j over a window W (1 = perfectly locked, 0 = unrelated).
- An element's **lock** L(i): the largest L(i, j) over its neighbours and over the input sites in range.
- **Strain** S(i): the bimodality of the phases its coupling partners pull it toward, from a two-cluster circular fit (0 = one direction, 1 = two opposite directions, equally strong).
- **Utility** U(i): the change in task score when element i is silenced for one evaluation block. Computed only for elements alive longer than one growth period.
- **Cost:** c_e per element plus c_c per active coupling, subtracted from the score.

**Birth (each rule is checked once per growth period):**

| Rule | Condition | Birth |
|---|---|---|
| **B1 Novelty** | an input site drives a band and phase to which no element within reach has lock ≥ L_on, for at least T_nov | one element at that site, natural rate at the band's centre, phase at the input phase |
| **B2 Strain split** | S(i) ≥ S_split and L(i) < L_on for at least T_split | element i divides into two, at the two cluster phases, offset by a small fixed distance |
| **B3 Need** (labelled addition, active only in the reward arm) | the task error accumulated at a state region exceeds E_need for at least T_need, with no birth there in the last T_need | one element there, tuned to the inputs present |

**Death:**

| Rule | Condition |
|---|---|
| **D1 Unlocked** | L(i) < L_off for at least T_death: it synchronizes with nothing |
| **D2 Useless** (only in the reward arm) | abs(U(i)) < ε_U in each of K consecutive checks |
| **D3 Budget** | the total cost exceeds the budget C_max: remove the element with the lowest lock (stability arm) or the lowest utility (reward arm) |

**Order and timescales** (the level ledger, section 5):
- activity (beats) runs on the fast scale τ_a;
- reshaping (positions and couplings, by the C4 law) runs on τ_g ≥ 10 τ_a;
- birth and death are checked every τ_l ≥ 10 τ_g.

Within one check, deaths come first, then births. A newborn element is protected from death for T_protect.

All thresholds are fixed in the design before development: L_on > L_off (a hysteresis gap, so that an element is not born and killed at the same level), S_split, T_nov, T_split, T_death, T_need, E_need, ε_U, K, c_e, c_c, C_max, T_protect, and a hard cap N_max. Development may only report them as attainable, not tune them per task.

## 4. Two arms that test the theory against the addition

| Arm | Selection | Birth and death rules |
|---|---|---|
| **Stability** (the theory alone) | what locks and recovers persists | B1, B2, D1, D3 by lock |
| **Stability + reward** (labelled addition) | locks during good outcomes strengthen (three-factor rule), and usefulness also counts | B1, B2, B3, D1, D2, D3 by utility |

Yardsticks:
- a fixed-size medium of the same final size, trained the same way;
- the same medium trained by gradient through its dynamics (AKOrN-like);
- a normal neural network of equal parameter count.

## 5. Level, size and timescale ledger (required by AGENTS.md and the principle-first rule)

| Level | Unit | Size | Own timescale | What it publishes upward |
|---|---|---|---|---|
| 0 | element | 1 | τ_a (beat) | phase, natural rate |
| 1 | atomic shape (a locked group) | measured | collective period, expected ≥ 3 τ_a (C5 measured a 3.4× separation) | collective phase, band, ports (C5 interface fields) |
| 2 | combined shape (locked atoms through the medium) | measured | slower again, measured | the same fields, one level up |

Checks:
- each level's timescale is measured on its own clock;
- no check mixes levels;
- descendant reads stay on the evaluator side.

## 6. Language, bonds and tasks

- **The language:** direction as phase, strength as amplitude, memory as a held phase, kinds of signal as frequency bands. The band layout is fixed before running.
- **Bonds between shapes:** they form only **through the medium** between band-matched shapes. A bond stays if it recovers from kicks (stability) and, in the reward arm only, if the joint result beats the parts alone and side by side without the bond.
- **Atomic tasks in a small 2D world**, rotated rather than trained one after the other (changing goals):
  - perceive (point at the right enemy);
  - move (reach a point or keep a distance);
  - remember (keep pointing after the enemy vanishes);
  - choose (pick one target).
- **Then combined tasks:**
  - chase and kite;
  - pursuit out of sight;
  - focus fire.

  The Astelia bench comes only after level 2 works.

## 7. Predictions that can fail

| ID | Prediction | Check |
|---|---|---|
| **G0 growth is driven by need** | births happen at novel inputs and strained elements, not uniformly | against a control with births at random places and times at the same rate |
| **G0' growth stops** | the element count levels off once the tasks are solved | it does not grow without bound under the cost |
| **G1 atoms form** | locked groups appear that do each atomic task to a registered score and pass the recovery test | |
| **G2 selective bonds** | bonds through the medium form between band-matched shapes and persist only where stable (and useful in the reward arm) | against random bonding |
| **G3 growing is cheaper** | a grown medium reaches the combined-task scores in fewer episodes and with fewer elements | than the fixed-size medium and the neural network |
| **G4 reuse** | the same locked atom serves at least two combined shapes unchanged | |
| **G5 no forgetting** | the atoms still pass their tasks after level 2 forms | |
| **G6 the theory alone** | the stability arm meets G0, G0', G1, G2 and G5 without reward | if only the reward arm works, the result says usefulness had to be added |

## 7b. Roadmap: bootstrap a library of atoms, then grow combinations (the owner's step-by-step request, 2026-10-05)

| Step | What | In theory terms | Done when |
|---|---|---|---|
| 0. The background | C6 medium in typed C++ (revision R007) | B0 | equivalent to the Python model; much faster |
| 1. Bootstrap atoms | A fresh medium is fed one simple task's input rhythms (perceive, move, remember, choose). Elements are born and die by section 3. The stable groups that do the task are the atoms | frequency → resonance → resonator (R0) | each atom passes its task score and the recovery test, and stays below a size cap |
| 2. Lock and define | Each atom's inside is locked. Its **identity card** is recorded: input band, output band, collective rhythm, size, stability, task score. It goes into the **library** | a resonator publishes its interface (C5) | a copied atom passes the same checks in a fresh medium (reusable) |
| 3. Seed a new background | Library atoms are copied into a new medium that has free space for growth | R0 transforms B0 into B1 | the atoms still pass after placement |
| 4. Grow combinations | A harder task is fed. Atoms bond through the medium (band match plus stability, plus usefulness in the reward arm), and elements are born only where coverage is missing | B1 grows R1: self-recreation, new options, new geometry | the combined task is passed in fewer episodes than learning from scratch |
| 5. Lock and repeat | Stable combinations are locked as level-2 shapes and added to the library. They seed the next medium for full game tasks | R1 → B2 → R2 (recursion) | each level is bigger and slower (the ledger, section 5) |
| 6. Into the game | Level-2 or level-3 shapes control units on the Astelia bench (S2 plug) | the AI | it plays against the frozen scripted ladder |

Only the tasks are chosen by the drafter. Atoms, bonds and growth are produced by the rules of section 3 and the bond conditions. Steps 1-2 are the bootstrap: after them, the library is relied on as given (reused, never retrained), and every later level is built on it.

## 7c. Types and copies, duplicates and shared building blocks (the owner, 2026-10-05: parts can be unlimited, recombined again and again; a complex shape may contain two duplicate smaller shapes, or shapes built from similar basic shapes)

- **The library holds types; the medium holds instances.** Placing a type creates an instance. Any number of instances of one type may sit in a medium, and **one combined shape may contain several instances of the same type** (as water contains two H).
- **Identical instances can take different roles.** C4 permits stable phase offsets inside a locked group, including anti-phase. Two instances of one type may lock at an offset and divide the work. This is tested (G7), not assumed.
- **The "same shape?" check:** before a new stable shape enters the library, it is compared with every entry: the identity card within registered tolerances **and** the same behaviour on its task panel. A match is recorded as a reuse of the existing type, not a new type.
- **The composition record:** for every combined type, the library records which types it contains and how many of each. This is the "periodic table plus molecules" record.
- **Unlimited but paid for:** parts may recombine without limit. The element and coupling cost (section 3) and the sameness check keep library growth tied to need.

| ID | Prediction | Check |
|---|---|---|
| **G7 duplicates** | when a task needs it (for example advance-and-cover), combinations with two or more instances of one type form, and the instances take differentiated roles (a stable phase offset and different action statistics) rather than redundant ones | against the same task with only one instance allowed |
| **G8 shared building blocks** | a small set of types appears in many combined types, and the rate of new types entering the library falls as more tasks are learned | across tasks, in training order |

## 8. Dependencies and order

1. **C6 first:** its medium must exist and run fast (the C++ port, revision R007). 0h builds on that medium.
2. Then:
   - an 0h design with every threshold fixed;
   - a Codex review;
   - development (G0 and G1 first, with a stop row if births do not track novelty and strain);
   - registration, owner approval naming the specification, and one recorded run.

Nothing runs before the owner's approval.

## 9. Related work, to read before the design is frozen

- growing neural gas (Fritzke 1995);
- cascade-correlation (Fahlman and Lebiere 1990);
- NEAT (Stanley and Miikkulainen 2002);
- dynamically expandable networks (Yoon et al. 2018);
- progressive networks (Rusu et al. 2016);
- AKOrN (Miyato et al. 2025);
- grokking circuits (Nanda et al. 2023);
- modularity under varying goals (Kashtan and Alon 2005) and connection cost (Clune, Mouret and Lipson 2013);
- communication through coherence (Fries);
- complementary learning systems (McClelland, McNaughton and O'Reilly 1995).

## 10. Changes from revision 1, and causes

| Change | Cause |
|---|---|
| Shapes live in one shared medium, and bonds form through it | Revision 1 wired shapes port to port, which leaves out the RRG background transformation |
| Stability is the main selection; reward is a labelled addition and is tested against stability alone (G6) | Revision 1 let reward decide, which tests machine learning, not the theory |
| A level, size and timescale ledger | It was missing (AGENTS.md, principle-first rule) |
| Borrowed elements marked (section 2) | So that results are not read as proving more than they do |
| Growth and death, with exact conditions, as the main mechanism | The owner's direction |
