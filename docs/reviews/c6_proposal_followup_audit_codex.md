CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: gpt-6
Rechecked proposal commit: 5ac60a0
Proposal SHA-256: 853ad3f81eccca390090f75456d5bcd5ec941e3c5ccc111a12ff98e45e4e61cc
Prior re-check commit: 366bf1e
Prior re-check SHA-256: 20254f61f1310d548859cc3a5fc39b9052bd0c175550e53982cdb2f6516efe90

Date: 2026-10-02. This document records the second proposal follow-up and the owner's requested audit of that follow-up. It is an audit of the same review, not another independent evidence review. The prior committed report, `docs/reviews/c6_proposal_recheck_codex.md`, remains unchanged. Locations below refer to `experiments/c6_proposal.md` at 5ac60a0.

The two substantive findings remain: the broader F14 flat-null claim fails for unequal-size push probes, and the N5 finite grid does not bound the continuous censored-time domain. My original follow-up overstated the E2 input wording as a separate blocker; that conclusion is corrected below. D8 is executable with the response floor, but approving its numerical value remains the owner's decision. Claude owns proposal amendments and their self-audit. This report does not authorize implementation or change milestone status.

## Finding status after audit

| Finding | Status | Proposal lines | Evidence |
|---|---|---|---|
| F14 | PARTIALLY_RESOLVED | 294–305 | The specified equal-size oracle fixture cancels, but unequal-size push probes retain positive expected specificity in a flat linear system. |
| N1 | RESOLVED | 368–372, 415, 482–486, 707 | The inclusive 0.01 floor, below-floor reporting, eligible-excitation world means, ten-world minimum and development stop are explicit. |
| N2 | RESOLVED | 197, 347–350 | The dimensionless Jacobian, reference norm and near-zero convention remove the dimensional discrepancy. |
| N3 | RESOLVED | 203, 309 | Both descriptive censoring statements use the actual maximum formation horizon. |
| N4 | RESOLVED | 477, 704 | The binary stop covers censoring of every required development median: tau_1, tau_2 and tau_3. |
| N5 | PARTIALLY_RESOLVED | 157–159, 415, 479–485 | Grid extrema are executable and non-circular for the finite registered comparator family, but do not bound the continuous censored-time domain. |
| N6 | RESOLVED | 200, 291, 581 | Singleton pushes use a registered, grouping-independent nearest-neighbour spacing rather than singleton radius of gyration. |

## 1. F14: the requested fixture passes; the broader null claim fails

For the nine-element fixture with phases `(-2,-2,-2,0,0,0,2,2,2)`, all 36 balanced mixed alternatives, all nine sites and all 101 samples from 0 through 32 were evaluated for amplitudes 0.5 and 0.2. The original probe made 65,448 comparisons; maximum absolute contrast was `1.7347234759768071e-17`.

The cancellation is algebraically exact. Write q = exp(-t). Every unexcited element has response a(1-q)/9; the probed element's triple has mean response a(1-q)/9 + aq/3. Exactly two scored elements carry residual aq/3 under every partition. Initial phases cancel from the unwrapped paired response. Final residual wrapping does not change these small errors.

The independent audit additionally checked homogeneous and heterogeneous initial phases, amplitudes 0.2 and 0.5, C values 1.6, 3.2 and 6.4, and both ordinary and wrapped final residuals. Its 807,192 checks differed from the closed-form error by at most `4.85722573273506e-17`.

**Residual-bias counterexample.** At transition 3, take ten equally weighted rigid sub-parts with flat consensus of their displacements and no privileged higher grouping:

```text
Real:        {0,1,2}, {3,4,5}, {6,7,8,9}
Alternative: {1,4,8}, {2,5,9}, {0,3,6,7}
```

Give every sub-part the same primitive count. Use a complete sub-part contact graph. Both partitions preserve count profile (3,3,4), including primitive counts, and every fake part mixes real parts. Give sub-parts 0–5 published length 1 and sub-parts 6–9 length 2, hence registered push amplitudes 0.2 and 0.4. Probe sites are uniform and independent of grouping; no probe is chosen using these labels.

For a probe in a part containing m sub-parts, the perfect linear-summary membership decoder has position error, in common unit spacing,

```text
E_m(t) = |a| exp(-t) sqrt((m-1)/9) / m.
```

The alternative-minus-real error, averaged uniformly over every site, is `+0.0005118909186508314 × exp(-t)`. An explicit lift to 60 primitive elements, excluding all six members of the probed sub-part, independently reproduces this result. For example, at t=0.32 its contrast is `+0.0003717090976650683`.

All 1,890 admissible alternatives give positive expected contrasts: between `0.0002559454593254157 × exp(-t)` and `0.0010237818373016628 × exp(-t)`. An independent enumeration grouped them by the number of high-amplitude sub-parts moved out of the real four-member part: 216 move one, 864 move two, 720 move three and 90 move four. Moving such a sub-part to a triple increases its decoder error; the reciprocal move of a low-amplitude sub-part decreases error by less. Thus any selected twenty alternatives retain positive expected push contrast. Four uniform sites give that same expectation. Equal-amplitude pulses have zero uniform-site mean contrast, so averaging pulse and push reduces this bias without cancelling it.

This is a counterexample to the general flat-linear-system claim at line 295 and to an unqualified decoder/statistic neutrality claim. It is an analytic challenge, not proof that an actual C4 world or an unrun E1/E2 panel produces a particular verdict. It uses oracle summaries to isolate the scoring effect. The push channel does not involve phase wrapping.

**Smallest fix:** remove the probe-conditioned decoder bias before interpreting specificity. One candidate remedy is to constrain alternatives to preserve each probe's containing-part sub-part count and primitive count. Another is a registered null correction. The drafter must choose the rule, check its feasibility and preserve the modular positive fixture; neither remedy is accepted merely by being suggested here. **Blocks approval: yes.**

## 2. N5: finite-grid comparison is valid; continuous-domain bounds are unsupported

Taking minimum baseline error for PASS and maximum for FAIL is conservative within the registered finite comparator family. Evaluating both extrema is not circular fitting of a winning baseline. However, censoring establishes tau > T, not membership in `{T,2T,4T,8T,16T,32T,infinity}`. Registering that grid does not establish that it bounds the unknown measured time. The statement that censoring can never manufacture either verdict is therefore too strong.

**Lower-bound witness.** Take the exact response

```text
y(t) = (0.5/3) [1 - exp(-t/(1.5T))]
```

at the registered 101 equally spaced samples over [0,T]. A decay with tau=1.5T remains above 1/e at T, so calibration is censored. The baseline at that admissible time has zero error. The best grid baseline has error `0.01050760672339519`. A prediction obtained by scaling y slightly has error 0.001 and starts at zero, so it produces grid gain_lo `+0.00950760672339519` against true-time gain `-0.001`. Its normalized error is approximately 0.019695; the response floor and D8 ceiling do not remove this lower-bound problem.

**Upper-bound witness.** A deterministic 101-sample response vector constructed from exact exponential curves gives maximum grid error `0.9998072350042901` versus off-grid error `1.0000000000000002`. To reproduce it, let b_tau be the equal-share exponential baseline vector above, u=b_T, v=b_2T, z=b_1.5T, d=v-u, p=((z-u) dot d)/(d dot d), n=z-u-pd, and y=z-n/RMS(n). An intermediate model error makes grid gain_hi negative while the off-grid gain is positive. This invalidates the claimed continuous-domain upper bound; it does not alone prove a reversal of the complete endpoint verdict, which also includes other gains, world aggregation and the error ceiling.

**Smallest fix:** certify extrema over the continuous censored interval, or register an explicit inconclusive outcome where the needed bounds are unavailable. Alternatively, explicitly narrow the claim to the finite comparator family and remove the unknown-time guarantee. Specify which gain bounds readiness uses. **Blocks approval: yes for the current bound claim.**

A finite grid can be retained with certified approximation margins. For the scalar baseline b(t,u)=c[1-exp(-tu)], let u=1/tau in [0,1/T] and let c be the equal-share response amplitude. Reverse triangle inequality gives an error Lipschitz constant K=|c| RMS(t). If h is the covering radius of the registered grid in u, valid bounds are:

```text
lower_error = max(0, min_grid_error - K h)
upper_error = max_grid_error + K h
```

For the lower-bound witness and the current grid, h=0.025 when T=10, K=0.9646530752325189 and Kh=0.02411632688081297. The resulting interval is `[0, 0.0748914230370428]`, which contains the true zero error and prevents the false positive gain bound. A deterministic 1,001-point check agrees with the analytic bound; those sample checks are not the proof. The full phase-plus-position metric needs the corresponding normalized channel constants. The drafter must register the complete rule before it can replace the existing one.

## 3. Correction: E2 input wording is a clarification, not a separate proven blocker

My follow-up treated lines 294 and 351 as incompatible executable definitions and called this a separate blocker. That conclusion was overstated. The new overarching linear-input convention supplies a coherent interpretation: E2 takes the difference of the supplied synthetic linear-response input states.

If line 351 were instead implemented using fresh circular publication of both full snapshots, the heterogeneous fixture would give t=0 real error `0.08254533518937095`, alternative error `0.6319071936553043` and contrast `0.5493618584659334`. That is a diagnostic of violating the new input convention, not another demonstrated bias under the correctly applied amendment.

**Correction:** downgrade this item to an implementation clarification. Explicitly name the linear input constructor in E2 and synchronize the E1 input contract. Remove the obsolete decoder-offset contract at line 578 and align the mutant description at line 605. **Blocks approval separately: no.**

## 4. Low note: first-order equivalence is overstated

Lines 296 and 922 claim that arithmetic and circular responses agree to first order for coherent parts. For phases `(-0.4,0,0.4)`, coherence is `0.9473739960019234`. A central-member infinitesimal pulse has circular derivative `1/(1+2 cos(0.4)) = 0.35184978133245765`, whereas the arithmetic derivative is 1/3. Coherence alone does not establish equality.

**Smallest fix:** restrict exact equivalence to identical phases or a rigid whole-part kick, and describe near-synchronized equivalence as approximate. **Blocks approval: no.**

## D8 and ownership

The normalized-error ceiling works as an ordered rule with the new floor. It bounds mean relative error over eligible worlds and excitations, not every excitation or raw physical error. This review does not approve or reject the numerical value 0.5. The owner decides D8 and D1; the drafter owns the remaining proposal fixes and records their causes. No numeric quality score is assigned.

## Commands, artifacts and execution scope

Read-only inspection included the following commands and narrowed range/search variants:

```text
cat AGENTS.md
cat docs/reviews/c6_proposal_recheck_codex.md
git status --short
git rev-parse HEAD
git show 5ac60a0:experiments/c6_proposal.md | shasum -a 256
git show 366bf1e:docs/reviews/c6_proposal_recheck_codex.md | shasum -a 256
git diff 290b414 5ac60a0 -- experiments/c6_proposal.md
nl -ba experiments/c6_proposal.md
rg -n ... experiments/c6_proposal.md GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
sed -n ... geomind/c5_coarse.py geomind/c5_units.py geomind/c5_experiment.py
python3 -B /private/tmp/c6-followup-5ac60a0/probe.py
python3 -B /private/tmp/c6-followup-5ac60a0/review_audit.py
shasum -a 256 /private/tmp/c6-followup-5ac60a0/probe.py
shasum -a 256 /private/tmp/c6-followup-5ac60a0/review_audit.py
git diff --stat
```

Standard-library-only inline Python probes checked alternative enumeration, the upper-bound witness and the certified finite-grid margin. They were run outside project imports; the margin proof and results are recorded above. A quick external memory-registry search returned no relevant matches; no memory-derived fact was used.

| Scratch artifact | SHA-256 |
|---|---|
| `/private/tmp/c6-followup-5ac60a0/probe.py` | `7250cb00a5e875eeaa34071084ee9dedca45e7aea7d61bba88fac55b877f1a73` |
| `/private/tmp/c6-followup-5ac60a0/review_audit.py` | `531249e0a9ebfeb632ff2ca880d255edcf7d970e9a20d858db03e01c0ba083f9` |

The follow-up and self-audit each finished within the requested 15-minute cap. The scripts evaluate closed-form trajectories and algebra using the standard library. No project code, simulations, numerical integration, random values, seeds, project tests, smoke runs, panels, mutation probes, design gates or verification pipelines were executed. No proposal, status, code, accepted artifact or prior committed review was changed. The subsequent owner request authorizes creating this document; this new report is the only repository write.

The scratch paths are temporary. The independently written audit script is reproduced below so its core checks remain available with this report. Extract it to a scratch path outside the repository before running it under the proposal-phase rules.

## Reproducible independent audit script

```python
"""Independent review audit: closed forms only, no project imports or random values."""
import math
import itertools
import cmath

triples=((0,1,2),(3,4,5),(6,7,8))
partitions=tuple(tuple((i,a[i],b[i]) for i in range(3)) for a in itertools.permutations(range(3,6)) for b in itertools.permutations(range(6,9)))
def rms(v):return math.sqrt(math.fsum(x*x for x in v)/len(v))
def wrap(x):return math.atan2(math.sin(x),math.cos(x))
max_contrast=0.
checks=0
for magnitude in (0.,2.):
    initial=tuple((-magnitude,0.,magnitude)[i//3] for i in range(9))
    for cumulative_time in (1.6,3.2,6.4):
        for frame in range(101):
            t=frame*.1*cumulative_time
            q=math.exp(-t)
            for p in range(9):
                for amplitude in (.2,.5):
                    control=tuple(q*x for x in initial)
                    probed=tuple(amplitude/9+q*(x+amplitude*(i==p)-amplitude/9) for i,x in enumerate(initial))
                    response=tuple(a-b for a,b in zip(probed,control))
                    expected=abs(amplitude*q)/6
                    for grouping in (triples,)+partitions:
                        predicted={i:math.fsum(response[j] for j in part)/len(part) for part in grouping for i in part}
                        errors=tuple(predicted[i]-response[i] for i in range(9) if i!=p)
                        for measured in (rms(errors),rms(tuple(wrap(x) for x in errors))):
                            max_contrast=max(max_contrast,abs(measured-expected))
                            assert abs(measured-expected)<1e-12
                            checks+=1
print('Equal-triple homogeneous/heterogeneous, pulse/push, final wrapping, three C values:',checks,'checks; maximum deviation from closed-form error:',max_contrast)
# Explicit lift from ten equally populated rigid sub-parts to 60 primitive elements.
real=((0,1,2),(3,4,5),(6,7,8,9))
fake=((0,3,6,7),(1,4,8),(2,5,9))
primitive_count=6
for t in (0.,.32,1.,32.):
    q=math.exp(-t)
    contrasts=[]
    for probe in range(10):
        amount=.2 if probe<6 else .4
        responses=tuple(amount*(1-q)/10+amount*q*(child==probe) for child in range(10))
        values=[]
        for grouping in (real,fake):
            lift={child:math.fsum(responses[c] for c in part)/len(part) for part in grouping for child in part}
            residuals=tuple(lift[e//primitive_count]-responses[e//primitive_count] for e in range(60) if e//primitive_count!=probe)
            values.append(rms(residuals))
        contrasts.append(values[1]-values[0])
    mean=math.fsum(contrasts)/10
    formula=.04*q*(math.sqrt(2)/9-math.sqrt(3)/12)
    assert abs(mean-formula)<1e-15
    print('Explicit 60-element lift t=',t,'uniform-site push contrast=',mean)
# Count all admissible alternatives using a different split canonicalization.
labels=tuple(0 if i<3 else 1 if i<6 else 2 for i in range(10))
counts={}
for four in itertools.combinations(range(10),4):
    left=set(range(10))-set(four)
    smallest=min(left)
    for two in itertools.combinations(sorted(left-{smallest}),2):
        a=(smallest,)+two
        b=tuple(sorted(left-set(a)))
        parts=(four,a,b)
        if any(len({labels[i] for i in part})<2 for part in parts):continue
        moved=len(set(range(6,10))-set(four))
        counts[moved]=counts.get(moved,0)+1
assert sum(counts.values())==1890 and min(counts)>0
print('Admissible alternatives by high-amplitude sub-parts moved to triples:',counts)
# Registering a finite comparator family is not estimating a continuous censored tau.
limit=10.
true_tau=15.
times=tuple(i*.1 for i in range(101))
truth=tuple((.5/3)*(1-math.exp(-t/true_tau)) for t in times)
scale=1-.001/rms(truth)
prediction=tuple(scale*x for x in truth)
model_error=rms(tuple(a-b for a,b in zip(prediction,truth)))
grid=tuple(k*limit for k in (1,2,4,8,16,32))+(math.inf,)
grid_errors=tuple(rms(tuple((.5/3)*(1-math.exp(-t/tau))-y for t,y in zip(times,truth))) for tau in grid)
assert math.exp(-limit/true_tau)>1/math.e
assert min(grid_errors)>model_error>0
assert prediction[0]==truth[0]==0
print('PASS-bound witness: calibration censored=',True,'grid minimum=',min(grid_errors),'model error=',model_error,'actual tau baseline error=',0.)
# Central-pulse derivative of a circular mean: independently via resultant calculus.
angles=(-.4,0.,.4)
z=math.fsum(math.cos(x) for x in angles)+1j*math.fsum(math.sin(x) for x in angles)
derivative=(1j/z).imag
assert abs(derivative-1/(1+2*math.cos(.4)))<1e-15
print('Coherent-state circular central-pulse derivative=',derivative,'arithmetic derivative=',1/3)
print('Audit scope: algebra and exact trajectories only; no project code, simulations, or seeds.')
```
