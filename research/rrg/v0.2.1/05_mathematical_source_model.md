# 05 — Optional mathematical illustrations and scope corrections

**RRG v0.2.1 · 2 October 2026 · not a required foundation or a universal proof**

The public theory stands as an explanatory hypothesis with a catalogue of examples. This note is for readers who want to inspect some small calculations. It replaces the previous presentation of “seven theorems” as though their combination proved the source mechanism. The old document, figures and code are retained in `archive/`.

The calculations below are conditional statements about chosen equations. They do not establish that nature uses those equations, that a spatial pattern is a temporal resonator, or that a new physical level has emerged. Their main value is to make assumptions visible and keep illustrative mathematics from overstating the theory.

## 0. The smallest useful illustration: a resonator filters noise

For a **pre-existing** linear oscillator,

\[
m\ddot x+\gamma\dot x+kx=\eta(t),\qquad m,\gamma,k>0,
\]

assume a zero-mean input with covariance \(\langle\eta(t)\eta(t')\rangle=2D\delta(t-t')\). In a stationary Fourier description its displacement spectrum is

\[
S_x(\omega)=\frac{2D}{(k-m\omega^2)^2+\gamma^2\omega^2}.
\]

This follows by dividing the input spectrum by the squared magnitude of the response operator \(k-m\omega^2+i\gamma\omega\). The output is not white. A nonzero-frequency spectral peak occurs only when

\[
\omega_{\mathrm{peak}}^2=\frac{k}{m}-\frac{\gamma^2}{2m^2}>0.
\]

Thus noise can drive structured fluctuations without an externally prescribed sinusoidal signal. But the oscillator, its stiffness and its coupling were supplied. This does **not** derive the first resonator from noise, nor does a noisy resonant peak necessarily imply a phase-coherent self-oscillation. It is a component illustration for the proposed background–resonator relation.

## 1. Spatial mode selection in one specified equation

Take a real field on a one-dimensional periodic interval of length \(L\), with uniform frozen background \(B\):

\[
\partial_t u=r(B)u-[q(B)^2+\partial_x^2]^2u+\nu_3u^3-\nu_5u^5,
\qquad \nu_5>0.
\]

For a perturbation \(u\propto e^{\lambda t+ik_mx}\),

\[
k_m=\frac{2\pi m}{L},\qquad
\lambda_m=r(B)-[q(B)^2-k_m^2]^2.
\]

**Calculation.** Substitute the Fourier mode and use \(\partial_x^2u=-k_m^2u\); the cubic and quintic terms disappear at linear order around zero.

On a continuous wavenumber domain, the maximum growth rate is \(r(B)\), attained at \(|k|=q(B)\). On the stated finite periodic domain, the maximum is instead

\[
\lambda_{\max}=r(B)-\min_m[q(B)^2-k_m^2]^2.
\]

Consequently \(r(B)>0\) need not be sufficient for an allowed unstable mode when the preferred wavenumber is unavailable. The interval size and boundary conditions matter.

This real first-order equation illustrates **stationary pattern selection**. It does not, by that fact alone, generate a temporal resonator. Stability of nonlinear patterns is another question. If \(B\) varies spatially, operator ordering and derivatives of coefficients must be defined; the uniform-background dispersion relation cannot simply be reused. If stochastic forcing is added to a PDE, its covariance, domain and solution assumptions must also be stated.

The near-onset amplitude approximations in [06, E21](06_evidence_catalog.md#e21) and the date-qualified further reading F03 are relevant mathematical precedents, not proofs for every choice of the equation above.

## 2. A signed scalar order parameter can have two attracting magnitudes

Consider the independently specified ordinary differential equation

\[
\dot x=f(x)=\mu x+c_3x^3-c_5x^5,
\qquad x\in\mathbb R,\quad c_3,c_5>0.
\]

Here \(x\) is a **signed scalar order parameter**, not automatically the magnitude of a complex oscillation. This note does not derive it from the preceding PDE.

For

\[
-\frac{c_3^2}{4c_5}<\mu<0,
\]

let

\[
y_{\pm}=\frac{c_3\pm\sqrt{c_3^2+4c_5\mu}}{2c_5}.
\]

The equilibria are \(0\), \(\pm\sqrt{y_-}\), and \(\pm\sqrt{y_+}\). At zero, \(f'(0)=\mu<0\). At a nonzero equilibrium, using \(\mu+c_3y-c_5y^2=0\),

\[
f'(x)=2y(c_3-2c_5y).
\]

The smaller-magnitude branch is unstable and the larger-magnitude branch locally asymptotically stable. The origin is also locally asymptotically stable. These are elementary deterministic fixed-point results, not proof of a spatially localized or oscillatory structure. In the signed model there are **five** equilibria, rather than just three nonnegative amplitudes.

At \(\mu=-0.18\) and \(c_3=c_5=1\), the positive thresholds are approximately \(x_-=0.485206\) and \(x_+=0.874400\). The branch algebra in the earlier note was substantially correct; the interpretation as an already-proved resonator was too broad.

## 3. Noise causes transitions in both directions

Add one-dimensional Itô noise to that signed coordinate:

\[
dX=-V'(X)dt+\sqrt{2D}\,dW_t,\qquad
V(x)=-\frac{\mu x^2}{2}-\frac{c_3x^4}{4}+\frac{c_5x^6}{6},\quad D>0.
\]

For this confining potential on the real line, a normalized zero-current stationary density is

\[
p_*(x)=Z^{-1}e^{-V(x)/D}.
\]

**Check.** In the Fokker–Planck current \(J=-V'p-D\partial_xp\), substitution gives \(J=0\); the positive sixth-order leading term ensures integrability.

Noise can carry the system over a deterministic basin boundary. It can also take it **out** of the high-amplitude basin. Persistence is then a residence-time question, not permanent noiseless attraction. A small-noise barrier-crossing approximation has exponential dependence on \(\Delta V/D\), but prefactors and first-passage definitions require specified starting wells, absorbing boundaries and nondegenerate barriers. It is not an exact universal clock.

The old text mixed \(a=|A|\ge0\) with a signed additive-noise scalar equation. For an isotropic two-component complex-amplitude SDE with component noise \(\sqrt{2D}\), the radius acquires an Itô drift \(D/a\) away from the origin, and its stationary radial density includes the radial measure factor. One cannot silently use the signed-scalar formula for that radius.

A stochastic order parameter with finite-amplitude residence does not yet show a temporally coherent oscillator, growing domain or new background.

## 4. A background responds to an imposed constant intensity

For uniform variables, assume

\[
\tau_B\dot B=-(B-B_0)+\rho I_*,\qquad \tau_B>0,
\]

where **\(I_*\) is constant and supplied as an assumption**. The exact solution is

\[
B(t)=B_0+\rho I_*+[B(0)-B_0-\rho I_*]e^{-t/\tau_B}.
\]

With \(B(0)=B_0\), the limiting change is \(\Delta B=\rho I_*\). To reach a fraction \(0<p<1\) of that change takes \(-\tau_B\ln(1-p)\). This is a relaxation time for the chosen equation, not the total formation time of a next level.

If intensity actually depends on the evolving background, the equilibrium is **implicit**:

\[
B_*=B_0+\rho I_*(B_*).
\]

In a justified one-dimensional adiabatic reduction, its local linear growth rate is

\[
\frac{-1+\rho I_*'(B_*)}{\tau_B}.
\]

Positive intensity feedback can therefore destabilize rather than automatically settle the background. If intensity has its own dynamics, the coupled Jacobian must be examined instead. Resetting \(B_0\) manually after every “level” builds a discrete update into the model; it does not establish autonomous recursion.

## 5. A damped candidate mode can become unstable

Suppose a previously specified candidate mode has a linear coefficient

\[
\lambda(B)=r_{\mathrm{next}}+\alpha(B-B_0),\qquad r_{\mathrm{next}}<0.
\]

Under the constant-intensity assumption above, its asymptotic coefficient is positive when

\[
\alpha\rho I_*>-r_{\mathrm{next}}.
\]

This is algebraic substitution into **an assumed coupling**. The coefficient \(\alpha\), sign of the feedback, candidate mode and background equation were not derived from the source principle.

The correct interpretation is: *a linearly damped mode becomes linearly unstable*. A negative growth rate never meant the mode was physically impossible or incapable of being excited by noise or forcing. A positive growth rate does not establish nonlinear saturation, stable geometry, coherent resonance or a new effective unit. A finite-domain pattern model also requires the wavenumber-detuning penalty from section 1.

This may be a useful local mechanism to investigate, but it is not itself a proof of \(R_n\to R_{n+1}\).

## 6. Increasing length follows only from a specified scale response

For a differentiable preferred wavenumber \(q(B)>0\), define \(\ell(B)=2\pi/q(B)\). Then

\[
\ell'(B)=-\frac{2\pi q'(B)}{q(B)^2}.
\]

If \(q'<0\) throughout an interval and \(B\) increases across that interval, \(\ell\) increases. If \(q'>0\), the implication reverses. On a finite domain, the realized selected mode can change discretely and need not exactly follow this continuous preferred wavelength.

For the **chosen example** \(q(B)=q_0e^{-\sigma B}\), \(\sigma>0\),

\[
\frac{\ell(B+\Delta B)}{\ell(B)}=e^{\sigma\Delta B}.
\]

This identity does not derive the exponential choice. The earlier eight-level growth plot repeatedly supplied background increments; it was an illustration of those assumptions, not a simulated discovery of eight spontaneously arising physical levels.

A characteristic material wavelength is not the cosmological scale factor. A separate metric model would be required for that identification. Likewise, accelerated expansion and expansion are not synonymous. No cosmological conclusion follows from this wavelength calculation.

## 7. An error bound is not a proof that errors diverge

Assume, after specifying compatible maps, norms and time rescalings, that a nonnegative error sequence obeys

\[
e_{n+1}\le\varepsilon+Ke_n,\qquad e_0=0,\quad K,\varepsilon\ge0.
\]

Repeated substitution gives

\[
e_N\le\varepsilon\sum_{j=0}^{N-1}K^j.
\]

For \(K<1\), this yields the sufficient uniform bound \(e_N\le\varepsilon/(1-K)\). For \(K=1\), it gives \(e_N\le N\varepsilon\). For \(K>1\), the **upper bound** grows exponentially, but actual errors need not grow. The sequence \(e_n=0\) satisfies the inequality for every \(K\ge0\) and \(\varepsilon\ge0\).

Therefore a noncontractive bound neither disproves recursive behavior nor proves actual instability. Conversely, the existence of a contracting abstract inequality does not show that a physical coarse-graining satisfies it.

In the previous note, bounds for the higher-level flow alone were treated as sufficient to get this recurrence. A real multi-level comparison also needs control of reduction maps, state domains, normalization, parameter changes and aligned times. The recurrence is an explicit assumption here, not a derived general fact about RRG.

## 8. What is inserted, and what is obtained

| Illustration | Inserted | Obtained | Not obtained |
|---|---|---|---|
| Noise filter | Oscillator and white-noise input | Colored response spectrum | Origin of oscillator |
| Pattern spectrum | Equation, coefficients, domain | Linear spatial growth rates | Stable temporal resonance |
| Cubic–quintic order parameter | Nonlinear drift | Fixed-point branches and local stability | Derived geometry or PDE stability |
| Noisy scalar | Drift, noise and real state space | Stationary density | Permanent organization |
| Background relaxation | Intensity and response law | Conditional background change | Self-derived feedback law |
| Candidate-mode threshold | Next mode and its coupling | Change of linear stability | Existence of a new stable level |
| Scale example | Decreasing preferred wavenumber | Increasing preferred wavelength | Cosmic expansion or unlimited hierarchy |
| Error recurrence | Uniform comparison inequality | A conditional bound | Real physical closure or its failure |

These simple results may help someone develop a more complete model. They do not need to be promoted into a universal proof to be useful. Some further work may be possible; this audit has not attempted it.

## 9. Verification actually performed in this release

The standard-library script [checks/verify_small_results.py](checks/verify_small_results.py) checks fixed-point residuals and derivatives, the stationary-density current identity, finite-domain detuning, the relaxation equation, the implicit-background stability example, scale monotonicity and the error-bound counterexample. Results are written to [checks/verification_results.json](checks/verification_results.json).

These are deterministic algebra/numerical spot checks, not independent peer review, full stochastic simulations or formal machine-checked theorems. The earlier 32-cell research simulation and its claimed convergence checks are preserved but were not rerun in this audit.

## 10. A useful contribution can be smaller than a proof

A reader may identify a mistaken assumption, derive one actual geometry-dependent response, connect two steps in a measured system, or provide a counterexample. All are worthwhile. None requires accepting the entire framework first. The immediate public package remains the source-direction explanation plus [06 — Evidence catalogue](06_evidence_catalog.md).
