# RRG v0.1 — Mathematical Core and First Experiments

## 1. Goal

We want the smallest mathematical system that implements the sentence:

\[
\boxed{
\text{geometry determines allowed modes,
and modes determine/maintain geometry}
}
\]

and then tests whether:

\[
\boxed{
\text{stable lower-level resonators}
\rightarrow
\text{stable higher-level resonators}
}
\]

using the **same equation family after coarse-graining**.

If every level needs a new manually invented rule, the central RRG claim fails.

---

## 2. Minimal state of one unit

For unit \(i\), begin with:

\[
R_i=
(\mathbf x_i,z_i)
\]

where:

\[
z_i=A_i e^{i\theta_i}
\]

and:

- \(\mathbf x_i\) = spatial position / geometric state,
- \(A_i\) = oscillation/state amplitude,
- \(\theta_i\) = phase,
- \(\omega_i\) = natural frequency.

We may later add:

- orientation,
- internal topology,
- multiple modes,
- discrete identity,
- conserved charges,
- spin-like variables,
- local energy stores.

Do not add them in the first model unless required.

---

## 3. One interaction should control both geometry and phase

A minimal pair interaction:

\[
\boxed{
V_{ij}(r_{ij},\Delta\theta_{ij})
=
U(r_{ij})
-
J(r_{ij})\cos(\Delta\theta_{ij})
}
\]

where:

\[
r_{ij}=|\mathbf x_i-\mathbf x_j|
\]

and:

\[
\Delta\theta_{ij}=\theta_i-\theta_j.
\]

Interpretation:

- \(U(r)\) provides short-range exclusion plus a preferred geometric range;
- \(J(r)\) controls phase-sensitive coupling;
- \(\cos(\Delta\theta)\) makes geometry depend on phase compatibility.

This gives the closed relation:

\[
\boxed{
r\rightarrow\text{phase coupling}
\quad\text{and}\quad
\Delta\theta\rightarrow\text{spatial force}
}
\]

This is conceptually related to swarmalator systems, where spatial and phase dynamics co-evolve.

---

## 4. Spatial equation

An inertial version:

\[
\boxed{
m_i\ddot{\mathbf x}_i
+
\gamma_x\dot{\mathbf x}_i
=
-\nabla_{\mathbf x_i}
\sum_{j\neq i}
V_{ij}
+
\boldsymbol\xi_i(t)
}
\]

where:

- \(m_i\) = effective inertia,
- \(\gamma_x\) = damping,
- \(\boldsymbol\xi_i\) = optional noise/perturbation.

For the first simulation an overdamped model may be simpler:

\[
\boxed{
\dot{\mathbf x}_i
=
-\mu_x
\nabla_{\mathbf x_i}
\sum_{j\neq i}V_{ij}
}
\]

This avoids unnecessary inertial complexity.

---

## 5. Phase equation

A direct potential-gradient form:

\[
\boxed{
\dot\theta_i
=
\omega_i
-
\mu_\theta
\frac{\partial}{\partial\theta_i}
\sum_{j\neq i}V_{ij}
+
\eta_i(t)
}
\]

which yields a Kuramoto-like phase term.

Equivalently:

\[
\dot\theta_i=
\omega_i
+
\sum_{j\neq i}
K(r_{ij})
\sin(\theta_j-\theta_i)
+
\eta_i(t)
\]

for an appropriate \(K(r)\).

Thus:

\[
\boxed{
\text{geometry controls synchronization}
}
\]

while the spatial equation gives:

\[
\boxed{
\text{synchronization controls geometry}
}
\]

---

## 6. Optional amplitude dynamics

If amplitude must evolve, use a Stuart–Landau normal form:

\[
\boxed{
\dot z_i
=
(\alpha_i+i\omega_i-\beta_i|z_i|^2)z_i
+
\sum_j K_{ij}(G)(z_j-z_i)
}
\]

This naturally provides stable oscillation amplitude when \(\alpha_i>0\).

It is a better second-stage model than manually fixing all amplitudes.

---

## 7. Geometry as a graph as well as position

Physical position alone may be insufficient.

Define adaptive edge strength:

\[
g_{ij}\in[0,1].
\]

Let effective interaction be:

\[
K_{ij}
=
g_{ij}K(r_{ij}).
\]

Then let the graph adapt:

\[
\boxed{
\dot g_{ij}
=
\eta_g
\left[
C_{ij}(R)-g_{ij}
\right]
}
\]

where \(C_{ij}\) measures compatibility.

A first compatibility function:

\[
C_{ij}
=
\sigma
\left[
a\cos(\theta_i-\theta_j)
-b(r_{ij}-r_0)^2
+cA_iA_j
\right]
\]

with sigmoid \(\sigma\).

This gives a literal dynamic graph:

\[
\boxed{
\text{mode changes topology}
\leftrightarrow
\text{topology changes mode}
}
\]

---

## 8. Geometry determines modes

For a fixed weighted graph \(G\), define its graph Laplacian:

\[
L=D-W
\]

where \(W=[g_{ij}]\) and \(D\) is the degree matrix.

Linear collective modes satisfy:

\[
\boxed{
Lu_k=\lambda_k u_k
}
\]

For many oscillator networks:

\[
\omega_k^2\propto\lambda_k.
\]

Thus the graph/geometry produces an allowed collective spectrum:

\[
\boxed{
G\rightarrow\{u_k,\omega_k\}.
}
\]

This is the mathematical form of “shape is a resonator”.

---

## 9. Mode determines geometry

Because:

\[
V_{ij}=V(r_{ij},\Delta\theta_{ij})
\]

the active phase pattern changes the force/relationship network.

Therefore:

\[
\boxed{
M\rightarrow G'.
}
\]

A self-consistent stable resonator is a pair:

\[
\boxed{
R^*=(G^*,M^*)
}
\]

for which evolution keeps the system in the same organized class.

---

## 10. Stability condition

### 10.1 Fixed-point case

Let the full state be:

\[
X=(\mathbf x_1,\ldots,\theta_1,\ldots,g_{ij},\ldots).
\]

Dynamics:

\[
\dot X=F(X).
\]

A fixed organized state \(X^*\) satisfies:

\[
F(X^*)=0.
\]

Linearize:

\[
\delta\dot X=J(X^*)\delta X.
\]

Local stability requires:

\[
\boxed{
\mathrm{Re}(\lambda_k(J))<0
}
\]

for all non-symmetry modes.

### 10.2 Periodic resonator

If the system reproduces its organization every period \(T\):

\[
X(t+T)\approx X(t),
\]

use Floquet multipliers.

Stability requires nontrivial multipliers to lie inside the unit circle.

### 10.3 Attractor formulation

More generally, define a persistent region \(\mathcal A\) such that perturbed trajectories return to or remain near \(\mathcal A\).

This lets RRG include:

- fixed structures,
- oscillatory structures,
- rotating structures,
- quasiperiodic systems,
- more complicated bounded attractors.

---

## 11. What counts as a new resonator?

For a cluster \(C\), compute phase coherence:

\[
\boxed{
\rho_C=
\left|
\frac{1}{|C|}
\sum_{i\in C}e^{i\theta_i}
\right|
}
\]

but phase coherence alone is not enough.

Define a persistence score:

\[
P_C=
w_1\rho_C
+w_2S_{\text{geometry}}
+w_3S_{\text{return}}
+w_4S_{\text{lifetime}}
-w_5S_{\text{fragmentation}}.
\]

A cluster becomes a candidate higher-level resonator only when:

1. membership remains sufficiently stable,
2. geometry remains within a bounded equivalence class,
3. collective phase/mode is measurable,
4. it survives perturbations,
5. it persists for many internal cycles.

Thresholds are experimental parameters in v0.1 and must later be replaced by scale-free criteria if possible.

---

## 12. Coarse-graining a stable cluster

For cluster \(C\):

\[
\boxed{
Z_C=
\frac{\sum_{i\in C}w_i z_i}
{\sum_{i\in C}w_i}
}
\]

Collective amplitude:

\[
A_C=|Z_C|.
\]

Collective phase:

\[
\Theta_C=\arg Z_C.
\]

Collective frequency:

\[
\boxed{
\Omega_C=
\frac{d\Theta_C}{dt}.
}
\]

Collective position:

\[
\boxed{
\mathbf X_C=
\frac{\sum_{i\in C}m_i\mathbf x_i}
{\sum_{i\in C}m_i}
}
\]

or another conserved-weight center.

Inter-cluster edge:

\[
\boxed{
g_{CD}
=
\mathcal A
\left(
\{g_{ij}: i\in C,\;j\in D\}
\right)
}
\]

where \(\mathcal A\) is an aggregation operator derived from flux/coupling, not chosen solely for convenience.

Now:

\[
R_C=(\mathbf X_C,Z_C,g_{C*},\ldots)
\]

becomes one effective node.

---

## 13. The central RRG recursion test

Let microscopic evolution be:

\[
\Phi_t.
\]

Let coarse-graining be:

\[
\mathcal R.
\]

RRG seeks approximate closure:

\[
\boxed{
\mathcal R\circ\Phi_t
\approx
\Phi'_t\circ\mathcal R
}
\]

where \(\Phi'_t\) belongs to the **same equation family** as \(\Phi_t\), with renormalized parameters:

\[
\lambda\rightarrow\lambda'.
\]

In plain language:

> evolve the small structures and then zoom out

should approximately agree with:

> zoom out first and evolve the larger structures using the same kind of rule.

This is the most important mathematical test in RRG v0.1.

---

## 14. Variation: same lower units, different higher structures

The model must permit:

\[
\{R_i\}
\rightarrow
R_A,\;R_B,\;R_C,\ldots
\]

depending on:

- count,
- geometry,
- order,
- connectivity,
- phase arrangement,
- energy,
- boundary conditions,
- external environment.

This is essential.

Otherwise the model produces only one repetitive crystal-like structure and cannot explore higher complexity.

---

## 15. Energy

For conservative components, define:

\[
E=
\sum_i \frac12m_i|\dot{\mathbf x}_i|^2
+
\sum_i E_{\text{osc},i}
+
\sum_{i<j}V_{ij}.
\]

For open/dissipative systems:

\[
\boxed{
\frac{dE}{dt}
=
P_{\text{in}}
-
P_{\text{diss}}
}
\]

A passively stable structure may sit in a bound state without continuous external power.

An actively maintained structure may require:

\[
P_{\text{in}}>0.
\]

This distinction is essential before modelling life.

---

## 16. A possible “resonant closure” functional

We want one scalar diagnostic for how well mode and geometry mutually support one another.

Define schematically:

\[
\boxed{
\mathcal Q(R)
=
-\alpha\|\dot G-\mathcal F_G(M,G)\|^2
-\beta\|\dot M-\mathcal F_M(G,M)\|^2
-\gamma E_{\text{escape}}
+\delta P_{\text{return}}
}
\]

High \(\mathcal Q\) means:

- geometry evolves consistently with the mode,
- mode evolves consistently with geometry,
- perturbations tend to return,
- escape/fragmentation is difficult.

This is not yet a law of nature.

It is a useful simulation diagnostic.

A later theory should derive stability directly from the governing action/dynamics rather than optimizing \(\mathcal Q\) by hand.

---

## 17. First computational experiment

### 17.1 Setup

- 256–2048 units
- 2D continuous space initially
- heterogeneous \(\omega_i\)
- random initial phases
- random positions
- one universal pair interaction \(V(r,\Delta\theta)\)
- optional adaptive \(g_{ij}\)
- damping + controlled noise
- no predefined clusters

### 17.2 Phase A — Can multiple stable shapes emerge?

Measure:

- number of persistent clusters,
- distinct geometry classes,
- mode spectra,
- perturbation recovery,
- lifetimes.

Success means more than one stable attractor appears from the same lower-level laws.

### 17.3 Phase B — Promote stable clusters

Automatically coarse-grain clusters that pass stability criteria.

Do **not** manually assign identities.

### 17.4 Phase C — Apply same equation family

Treat supernodes as the new units.

Run again.

### 17.5 Phase D — Seek third level

Attempt:

\[
R_0\rightarrow R_1\rightarrow R_2\rightarrow R_3.
\]

The hierarchy must not be predeclared.

---

## 18. Metrics

### Persistence

\[
T_{\text{life}}/\tau_{\text{internal}}
\]

How many internal cycles does a structure survive?

### Coherence

\[
\rho_C
\]

### Perturbation recovery

Distance back to attractor after standardized disturbance.

### Compression ratio

\[
\frac{\text{number of lower degrees of freedom}}
{\text{number of effective higher degrees of freedom}}
\]

### Timescale separation

\[
\frac{\tau_{n+1}}{\tau_n}
\]

### Recursive closure error

\[
\boxed{
\epsilon_R
=
\left\|
\mathcal R(\Phi_t(X))
-
\Phi'_t(\mathcal R(X))
\right\|
}
\]

This is perhaps the most important metric.

If \(\epsilon_R\) remains small across multiple levels after parameter rescaling, RRG gains real mathematical support.

---

## 19. Strong failure conditions

The first simulation should count as failure if:

1. stable structures only appear after manually specifying cluster geometry;
2. every stable structure is essentially identical and no combinatorial variation appears;
3. promoted supernodes require a completely unrelated equation;
4. coarse-graining destroys predictive power;
5. stable higher levels cannot survive perturbations;
6. hierarchy depth is entirely controlled by manually chosen thresholds;
7. apparent “recursion” disappears when units/noise/initial conditions are varied.

These are useful failures.

---

## 20. Second experiment: primitive replication

Only after recursive stable geometry works.

Add:

- finite resources,
- local energy source,
- components that can bind/unbind,
- structures capable of catalyzing compatible assembly.

Ask whether a persistent geometry can increase the probability of creating another similar geometry:

\[
R+\text{resources}
\rightarrow
R+R'.
\]

Do not hard-code DNA-style copying.

Measure whether geometry-assisted self-templating can emerge.

This links RRG with autocatalytic-set research.

---

## 21. Third experiment: RRG AI toy model

Build a simple 2D world with:

- moving objects,
- collisions,
- hidden object identity,
- goals,
- changing relationships.

Compare equal-resource:

1. small Transformer,
2. RNN,
3. graph neural network,
4. RRG recursive dynamic network.

RRG network rules:

- local dynamic nodes,
- adaptive graph,
- phase/timescale variables,
- persistent clusters promoted automatically,
- temporary synchronization for task relevance,
- same recursive update family across levels.

Compare:

- sample efficiency,
- parameter count,
- memory,
- generalization to unseen combinations,
- long-horizon prediction,
- robustness to perturbations,
- computational cost.

---

## 22. Physics program after the toy model

Only if recursive closure works generically:

1. test whether known inverse-distance interactions can emerge;
2. test local symmetries;
3. test conservation laws;
4. test continuum/field limit;
5. test Lorentz-compatible dynamics;
6. test whether gauge-like redundancy emerges;
7. compare with quantum field behavior;
8. test whether an effective metric/gravity-like regime can appear.

Do not retrofit these properties one by one unless the extension is independently motivated.

---

## 23. Closest mathematical/scientific frameworks

RRG should explicitly build on rather than ignore:

- normal-mode / spectral theory,
- coupled resonator theory,
- Kuramoto synchronization,
- swarmalators,
- Stuart–Landau oscillators,
- adaptive networks,
- Synergetics,
- dynamical systems / attractors,
- renormalization group,
- effective field theory,
- graph spectral theory,
- autocatalytic-set theory,
- neural manifolds.

The potential novelty is **their recursive unification into one geometry↔mode promotion rule**, not the invention of these individual mathematical tools.

---

## 24. Minimal mathematical summary

At scale \(n\):

\[
R_n=(G_n,M_n).
\]

Evolution:

\[
\dot R_n=F(R_n;\lambda_n).
\]

Stable resonant geometry:

\[
R_n\in\mathcal A_n
\]

for an attractor/persistent set \(\mathcal A_n\).

Coarse-grain stable cluster:

\[
R_{n+1}=\mathcal R(\{R_n\}).
\]

Recursive closure requirement:

\[
\boxed{
\mathcal R\circ F_{\lambda_n}
\approx
F_{\lambda_{n+1}}\circ\mathcal R.
}
\]

This single condition is the mathematical heart of RRG v0.1.

If it survives nontrivial simulations and known physical constraints, the framework becomes much more than an analogy.

If it does not, we revise or reject the universal-recursion claim.

---

# v0.1a Addendum — Minimal \(\Gamma\) with Scale-Activated Interaction Channels

## 25. Why the previous minimal model was not enough

The pair potential \(V(r,\Delta\theta)\) is useful for a toy simulation, but it cannot realistically encode multiple force sectors, symmetry breaking, confinement, emergent composite fields, gravity-like geometry, and different effective laws at different scales.

For the deeper RRG formulation, use a **scale-dependent effective action**.

## 26. Abstract minimal RRG effective action

Let:

\[
R=(D,\Psi)
\]

where:

- \(D\) is the geometry/spectral operator,
- \(\Psi\) is the active state/mode content.

Use:

\[
\boxed{
\Gamma_k[D,\Psi]
=
\Gamma_{\mathrm{geom},k}[D]
+
\langle\Psi,\mathcal K_k(D)\Psi\rangle
+
U_k[\Psi]
+
\sum_\alpha g_\alpha(k)\mathcal O_\alpha[D,\Psi]
}
\]

Interpretation:

- \(\Gamma_{\mathrm{geom},k}[D]\): cost/dynamics of geometry itself.
- \(\langle\Psi,\mathcal K_k(D)\Psi\rangle\): modes allowed by that geometry.
- \(U_k[\Psi]\): nonlinear self-interaction needed for multiple stable branches.
- \(g_\alpha(k)\mathcal O_\alpha\): interaction channels allowed by the current symmetries/constraints.

This is the smallest abstract form that can contain geometry, spectrum, nonlinear stability, multiple interaction channels, and scale dependence.

## 27. Geometry↔mode closure

Self-consistency requires:

\[
\boxed{\frac{\delta\Gamma_k}{\delta\Psi}=0}
\]

\[
\boxed{\frac{\delta\Gamma_k}{\delta D}=0}
\]

The first gives the allowed state/mode on the current geometry. The second gives the geometry compatible with the active state/mode.

## 28. Force and frequency emerge from the same effective action

Let \(q\) be a collective geometric coordinate. Then:

\[
\boxed{F_q=-\frac{\partial\Gamma_k}{\partial q}}
\]

A stable geometry satisfies:

\[
\boxed{\frac{\partial\Gamma_k}{\partial q}=0}
\]

Near a stable state:

\[
\Gamma_k(q)\approx\Gamma_k(q_*)+\frac12(q-q_*)^T H_k(q-q_*)
\]

with:

\[
\boxed{H_k=\frac{\partial^2\Gamma_k}{\partial q^2}}
\]

Normal modes satisfy:

\[
\boxed{H_k u_n=\lambda_n u_n}
\]

After accounting for the kinetic metric/mass matrix \(M_q\):

\[
\boxed{\omega_n^2=\operatorname{eig}(M_q^{-1}H_k)}
\]

Therefore stable geometry, restoring interaction, and resonant frequencies are three properties of the same local effective-action landscape:

\[
\boxed{\Gamma_k\Rightarrow\{G_k,F_k,\Omega_k\}}
\]

## 29. Latent interaction channels

Write:

\[
\boxed{\Gamma_k=\Gamma_{0,k}+\sum_\alpha g_\alpha(k)\mathcal O_\alpha}
\]

Scale changes the couplings:

\[
\boxed{k\frac{dg_\alpha}{dk}=\beta_\alpha(\{g\})}
\]

An interaction channel can therefore be negligible at one scale and important at another.

This mathematically captures the intuition that an interaction may be “available” but only become dynamically visible/dominant once the scale, geometry, and mode structure make its coupling relevant.

## 30. When a new geometry appears

A new collective structure often appears when a fluctuation channel becomes soft/unstable.

Let \(\Gamma_k^{(2)}\) be the second functional derivative. In channel \(\alpha\), suppose:

\[
\boxed{\lambda_{\min}^{(\alpha)}(k)\rightarrow0}
\]

Then fluctuations in that mode become large. If the eigenvalue changes sign:

\[
\lambda_{\min}^{(\alpha)}<0
\]

the old state is unstable and the system reorganizes. A new order parameter/composite field can acquire:

\[
\boxed{\langle\Phi_\alpha\rangle\neq0}
\]

This is the mathematical version of:

\[
\boxed{
\text{old geometry}
\rightarrow
\text{soft resonant mode}
\rightarrow
\text{reorganization}
\rightarrow
\text{new stable geometry}
}
\]

## 31. Functional RG supplies the scale evolution

Use:

\[
\boxed{
k\partial_k\Gamma_k
=
\frac12\operatorname{STr}
\left[(\Gamma_k^{(2)}+R_k)^{-1}k\partial_kR_k\right]
}
\]

This integrates out progressively shorter/faster fluctuations and produces the larger-scale effective action.

When a long-lived composite mode appears, promote it to an explicit field/node and continue the flow.

## 32. The RRG recursion with interaction channels

At scale \(n\):

\[
\Gamma_n\Rightarrow(G_n,M_n,\{g_{\alpha,n}\}).
\]

A collective channel becomes stable:

\[
\lambda_{\min}^{(\alpha)}\rightarrow0\rightarrow\Phi_\alpha\neq0.
\]

That produces a new effective object \(R_{n+1}\). Coarse-grain:

\[
\Gamma_n\rightarrow\Gamma_{n+1}.
\]

Then:

\[
\Gamma_{n+1}\Rightarrow(G_{n+1},M_{n+1},\{g_{\alpha,n+1}\}).
\]

So:

\[
\boxed{
\Gamma_n
\rightarrow
\text{stable resonant geometry}
\rightarrow
\text{composite promotion}
\rightarrow
\Gamma_{n+1}
\rightarrow\cdots
}
\]

## 33. Relation to known forces

RRG should treat known forces as constraints/examples, not pre-assigned layers.

- **Strong interaction:** QCD coupling is strongly scale dependent; quarks/gluons are useful high-energy variables, hadrons useful low-energy composites.
- **Electroweak:** the Higgs vacuum changes the effective low-energy spectrum; massive \(W/Z\), massless photon, hence very different ranges.
- **Electromagnetism:** long-range massless photon sector; neutral matter can strongly screen/cancel electric effects at large scales.
- **Gravity:** present at all known scales but dominant for large astronomical systems. Whether it emerges as a collective spin-2/geometric channel remains open.

A 2026 FRG study demonstrates that dynamical tensor composite fields with an Einstein-Hilbert-like quadratic structure can emerge in prototype microscopic models. This shows mathematical possibility, not a derivation of real gravity from RRG.

## 34. Immediate mathematical target

Use at least two competing channels:

\[
\Gamma_k=\Gamma_{\rm base}+g_1(k)\mathcal O_1+g_2(k)\mathcal O_2+U_k.
\]

Desired behavior:

1. At high scale, neither channel forms a stable composite.
2. Under RG, \(g_1\) becomes relevant.
3. Stable resonator \(R_1\) forms.
4. Promote \(R_1\) to an effective node/field.
5. Continue RG.
6. At a larger scale, \(g_2\) or a newly generated composite channel becomes relevant.
7. Stable resonator \(R_2\) forms.
8. The same geometry–force–frequency relation remains valid.

If this occurs for multiple levels without hand-authoring each transition, it directly tests the distinctive RRG claim.


---

# v0.1b Addendum — Background-Dependent Recursive Action

## 35. Add the evolving background

The effective action should depend not only on scale \(k\) but on a background/environment \(B(t)\):

\[
\boxed{
\Gamma_k[D,\Psi;B(t)]
}
\]

A minimal decomposition is:

\[
\boxed{
\Gamma_k
=
\Gamma_{\mathrm{geom},k}[D;B]
+
\langle\Psi,\mathcal K_k(D;B)\Psi\rangle
+
U_k[\Psi;B]
+
\sum_\alpha g_\alpha(k,B)\mathcal O_\alpha[D,\Psi;B].
}
\]

The background can change which stationary solutions and interaction channels are stable.

## 36. Background-dependent stable set

Define:

\[
\boxed{
\mathcal S_{k,B}
=
\left\{
R=(D,\Psi):
\frac{\delta\Gamma_k}{\delta R}=0,
\;\sigma(\Gamma_k^{(2)})\;\text{is stable}
\right\}.
}
\]

As \(B\) evolves:

\[
\boxed{
\mathcal S_{k,B_1}\neq\mathcal S_{k,B_2}
}
\]

can occur even though the underlying functional form remains the same.

This gives the theory a mathematically precise notion of “previously inaccessible geometry becomes possible”.

## 37. A scale is an effective resonant regime

For a persistent collective mode \(R_n\), define characteristic quantities:

\[
\boxed{
\mathcal L_n=
\{L_n,\tau_n,\Omega_n,\{g_{\alpha,n}\},B_n\}.
}
\]

A new scale exists when:

1. a collective mode is long lived compared with its internal timescale,
2. a reduced set of variables predicts its interactions with bounded error,
3. the coarse-grained action closes approximately within the same functional family.

This makes “scale” an emergent modelling regime rather than merely a length interval.

## 38. Revised RRG closure condition

Let \(\Phi_{k,B}^t\) denote evolution under \(\Gamma_k[\cdot;B]\), and let \(\mathcal R\) coarse-grain a stable collective structure.

RRG seeks:

\[
\boxed{
\mathcal R\!\left(\Phi_{k,B}^t(R)\right)
\approx
\Phi_{k',B'}^t\!\left(\mathcal R(R)\right)
}
\]

with \(\Phi_{k',B'}\) generated by the **same class of effective action**, but with renormalized couplings and possibly a new background produced by the higher-level structure.

The full recursion is therefore:

\[
\boxed{
(\Gamma_n,B_n)
\rightarrow
R_n
\rightarrow
\mathcal R
\rightarrow
(\Gamma_{n+1},B_{n+1})
\rightarrow
R_{n+1}.
}
\]

## 39. Geometry, force, and mode remain one local object

For collective coordinates \(q\):

\[
\boxed{
\frac{\partial\Gamma}{\partial q}=0
}
\]

defines a stationary geometry,

\[
\boxed{
F_q=-\frac{\partial\Gamma}{\partial q}
}

defines the restoring/driving interaction, and

\[
\boxed{
\omega_n^2
=
\operatorname{eig}\!\left(M_q^{-1}\frac{\partial^2\Gamma}{\partial q^2}\right)
}
\]

defines the local collective mode spectrum.

Thus RRG's core statement is represented mathematically as:

\[
\boxed{
\Gamma_k
\Rightarrow
\{G_k,F_k,M_k\}
}
\]

rather than treating geometry, force, and frequency as independent primitives.

## 40. Next concrete calculation

Construct the smallest explicit \(\Gamma_k\) with:

- one background parameter \(B\) that changes slowly,
- two competing interaction channels \(g_1\mathcal O_1\) and \(g_2\mathcal O_2\),
- nonlinear terms that permit several stable branches,
- a calculable fluctuation spectrum,
- an RG/coarse-graining step.

Required outcome:

1. At \(B=B_0\), only lower-level resonators are stable.
2. As \(B\) or \(k\) changes, a collective mode softens.
3. A new stable resonator forms without being specified in advance.
4. That resonator is promoted to an effective field/node.
5. The same action family then produces a second transition.

This is now the minimum mathematical experiment that tests the combined RRG claims of geometry–mode closure, background selection, and recursive scale formation.

