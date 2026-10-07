PARTIAL

Amendment-1 exploratory ECOF/ECOR × starts i/ii × keys0–4;20 on runs plus two off controls. No scientific verdict or A7 authorization.

Integrity: {'ECOF': 'PASS', 'ECOR': 'PASS'}. Verification errors: [].

Exact declared RD3 pooled sites3–6 baseline: 0.08601377266387726; doubling target: 0.17202754532775452.

| Arm | Status | Empty passes/runs | Seeded passes/runs | Pooled sites3–6 | Reading |
|---|---|---|---|---|---|
| RD3 | DONE | {'passes': 5, 'runs': 5} | {'passes': 3, 'runs': 5} | 0.08601377266387726 | CONTROL |
| COVA | DONE | {'passes': 5, 'runs': 5} | {'passes': 5, 'runs': 5} | 0.12255927475592747 | DESCRIPTIVE |
| COVB | DONE | {'passes': 5, 'runs': 5} | {'passes': 4, 'runs': 5} | 0.13642346582984657 | DESCRIPTIVE |
| ECOF | DONE | {'passes': 5, 'runs': 5} | {'passes': 3, 'runs': 5} | 0.08601377266387726 | DESCRIPTIVE |
| ECOR | INCOMPLETE | {'passes': 0, 'runs': 5} | {'passes': 0, 'runs': 3} | 0.056244635193133045 | INCOMPLETE |

Pooling sums active_served_steps / active_steps over sites3–6 and all ten on runs. Coverage improves requires the exact doubling target, >=4/5 empty passes, all ten runs and that arm’s on/off summary+trajectory identity and clone isolation. Regression requires <=3/5 empty passes with the same completeness/integrity gates. Missing runs never count as failures.

| Arm/site | Pooled active served fraction |
|---|---|
| RD3/0 | 0.4913194444444444 |
| RD3/1 | 0.6017830882352941 |
| RD3/2 | 0.33109848484848486 |
| RD3/3 | 0.18893979057591623 |
| RD3/4 | 0.0193853021978022 |
| RD3/5 | 0.05787292817679558 |
| RD3/6 | 0.07105061349693252 |
| RD3/7 | 0.3861257530120482 |
| COVA/0 | 0.4127923976608187 |
| COVA/1 | 0.38235294117647056 |
| COVA/2 | 0.4485227272727273 |
| COVA/3 | 0.31223821989528794 |
| COVA/4 | 0.12506868131868132 |
| COVA/5 | 0.013173342541436464 |
| COVA/6 | 0.01896088957055215 |
| COVA/7 | 0.0316453313253012 |
| COVB/0 | 0.5085526315789474 |
| COVB/1 | 0.602389705882353 |
| COVB/2 | 0.4617613636363636 |
| COVB/3 | 0.3327715968586387 |
| COVB/4 | 0.05729739010989011 |
| COVB/5 | 0.05828729281767956 |
| COVB/6 | 0.08146088957055214 |
| COVB/7 | 0.39819277108433737 |
| ECOF/0 | 0.4913194444444444 |
| ECOF/1 | 0.6017830882352941 |
| ECOF/2 | 0.33109848484848486 |
| ECOF/3 | 0.18893979057591623 |
| ECOF/4 | 0.0193853021978022 |
| ECOF/5 | 0.05787292817679558 |
| ECOF/6 | 0.07105061349693252 |
| ECOF/7 | 0.3861257530120482 |
| ECOR/0 | 0.2359318181818182 |
| ECOR/1 | 0.33193181818181816 |
| ECOR/2 | 0.25007183908045977 |
| ECOR/3 | 0.16028814935064936 |
| ECOR/4 | 0.012940436241610738 |
| ECOR/5 | 0.023741467576791807 |
| ECOR/6 | 0.020089285714285716 |
| ECOR/7 | 0.12502376425855513 |

Per-run gate shape (A>=.3, B>=.3, max(E)>=.5); empty and seeded are separate:

| Arm/start/key | A | B | E | Pass |
|---|---|---|---|---|
| RD3/i/0 | 0.980103167564469 | 1.1109559049957511 | [0.0, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| RD3/i/1 | 1.450507188964859 | 1.3794314081835557 | [0.5, 0.7, 0.8, 0.052500000000000005, 0.0, 0.0, 0.0, 0.0] | True |
| RD3/i/2 | 1.4116205544021823 | 1.2277011373959636 | [0.5, 0.7, 0.04583333333333333, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| RD3/i/3 | 1.4208028674096502 | 1.0220814327837138 | [0.5, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| RD3/i/4 | 1.4686823230970532 | 1.358475754521448 | [0.5, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| RD3/ii/0 | 1.2405333185086787 | 1.0859656932809232 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6, 0.7] | True |
| RD3/ii/1 | 1.3849957611484873 | 1.1215296763997529 | [0.5, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.7] | True |
| RD3/ii/2 | 0.4140048174063415 | 0.5522032541848246 | [0.0, 0.23333333333333334, 0.26666666666666666, 0.2, 0.08874999999999998, 0.0, 0.0, 0.0] | False |
| RD3/ii/3 | 0.19704779553951146 | 0.13701651551759758 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| RD3/ii/4 | 1.4137570397167176 | 1.2062399590689061 | [0.5, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| COVA/i/0 | 0.9876859892520463 | 1.1184413714063122 | [0.0, 0.7, 0.8, 0.6, 0.00020833333333333335, 0.0, 0.0, 0.0] | True |
| COVA/i/1 | 1.444181635089438 | 1.3787238147849823 | [0.5, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| COVA/i/2 | 0.6090296776434044 | 0.38282905274881224 | [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| COVA/i/3 | 1.232422510520728 | 1.5393077654025478 | [0.0, 0.0, 0.8, 0.6, 0.7, 0.0, 0.0, 0.0] | True |
| COVA/i/4 | 1.4620634518419469 | 1.3565459840080505 | [0.5, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| COVA/ii/0 | 0.9948141476695118 | 1.0282014155065944 | [0.0, 0.0, 0.8, 0.6, 0.7, 0.0, 0.0, 0.0] | True |
| COVA/ii/1 | 0.8562163180820495 | 0.9514916953376156 | [0.5, 0.0, 0.0, 0.0, 0.4666666666666667, 0.3333333333333333, 0.4, 0.0] | True |
| COVA/ii/2 | 1.082087009942695 | 1.2862821943923142 | [0.0, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| COVA/ii/3 | 0.6874068754694377 | 0.9027126286625421 | [0.0, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| COVA/ii/4 | 0.9581092230461529 | 0.6069798377494491 | [0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| COVB/i/0 | 0.9750172047701072 | 1.101655643054214 | [0.0, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| COVB/i/1 | 1.4821436642547865 | 1.3646454351972106 | [0.5, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| COVB/i/2 | 1.3723886730644184 | 1.2195714780393299 | [0.5, 0.7, 0.728125, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| COVB/i/3 | 1.3659293562187158 | 1.2733351792772825 | [0.5, 0.7, 0.8, 0.6, 0.0, 0.0, 0.03895833333333333, 0.7] | True |
| COVB/i/4 | 1.4531350702822732 | 1.2885272672273407 | [0.5, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0, 0.31229166666666663] | True |
| COVB/ii/0 | 1.1760093764690107 | 1.0689844543191958 | [0.3333333333333333, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6, 0.7] | True |
| COVB/ii/1 | 1.1879977570491453 | 1.1718684206160057 | [0.5, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.7] | True |
| COVB/ii/2 | 0.4888220768286046 | 0.6270937889798034 | [0.0, 0.23333333333333334, 0.26666666666666666, 0.2, 0.07875, 0.0725, 0.0, 0.0] | False |
| COVB/ii/3 | 1.2203326152557623 | 1.4174929177413786 | [0.0, 0.08791666666666667, 0.8, 0.6, 0.7, 0.0, 0.0, 0.0] | True |
| COVB/ii/4 | 1.417734752081994 | 1.2106572072160517 | [0.5, 0.7, 0.0, 0.0, 0.0029166666666666664, 0.0020833333333333333, 0.0025, 0.7] | True |
| ECOF/i/0 | 0.980103167564469 | 1.1109559049957511 | [0.0, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.0] | True |
| ECOF/i/1 | 1.450507188964859 | 1.3794314081835557 | [0.5, 0.7, 0.8, 0.052500000000000005, 0.0, 0.0, 0.0, 0.0] | True |
| ECOF/i/2 | 1.4116205544021823 | 1.2277011373959636 | [0.5, 0.7, 0.04583333333333333, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| ECOF/i/3 | 1.4208028674096502 | 1.0220814327837138 | [0.5, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| ECOF/i/4 | 1.4686823230970532 | 1.358475754521448 | [0.5, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0] | True |
| ECOF/ii/0 | 1.2405333185086787 | 1.0859656932809232 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.6, 0.7] | True |
| ECOF/ii/1 | 1.3849957611484873 | 1.1215296763997529 | [0.5, 0.7, 0.8, 0.6, 0.0, 0.0, 0.0, 0.7] | True |
| ECOF/ii/2 | 0.4140048174063415 | 0.5522032541848246 | [0.0, 0.23333333333333334, 0.26666666666666666, 0.2, 0.08874999999999998, 0.0, 0.0, 0.0] | False |
| ECOF/ii/3 | 0.19704779553951146 | 0.13701651551759758 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOF/ii/4 | 1.4137570397167176 | 1.2062399590689061 | [0.5, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7] | True |
| ECOR/i/0 | 0.02421323403878322 | 0.01765937727008434 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/i/1 | 0.591502123935775 | 0.5274874482048808 | [0.13083333333333333, 0.14395833333333333, 0.15458333333333332, 0.0006250000000000001, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/i/2 | 0.22401789646940384 | 0.13466487658845103 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/i/3 | 0.04699438407296317 | 0.03470047004034812 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/i/4 | 0.5909740157958258 | 0.7233066746743345 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/ii/0 | 0.24326063404237316 | 0.18995986990867733 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/ii/1 | 0.46701257212763747 | 0.27977081263453235 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |
| ECOR/ii/2 | 0.05645380593799198 | 0.07787106215308025 | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] | False |

Class allocation at fixed5s post-boundary snapshots (equal weights across complete runs):

| Arm/class | Mean bodies | Mean pair cost | Mean total cost |
|---|---|---|---|
| RD3/critical | 1.0081250000000002 | 0.4458125 | 1.4539374999999999 |
| RD3/redundant | 11.774375000000003 | 5.744906249999999 | 17.519281250000002 |
| RD3/front | 20.835 | 8.126156250000012 | 28.961156250000023 |
| RD3/orphan | 0.19375 | 0.054749999999999986 | 0.24850000000000003 |
| COVA/critical | 0.6187500000000001 | 0.24540625 | 0.8641562499999995 |
| COVA/redundant | 9.693124999999998 | 4.583968749999997 | 14.277093749999995 |
| COVA/front | 22.904999999999998 | 9.450437500000028 | 32.35543750000003 |
| COVA/orphan | 0.08249999999999999 | 0.015875000000000004 | 0.09837500000000002 |
| COVB/critical | 1.2625 | 0.5624374999999999 | 1.8249375 |
| COVB/redundant | 14.976875000000001 | 7.209812500000014 | 22.186687500000016 |
| COVB/front | 17.338749999999997 | 6.648000000000008 | 23.986750000000008 |
| COVB/orphan | 0.12625 | 0.03424999999999998 | 0.1605000000000001 |
| ECOF/critical | 1.0081250000000002 | 0.4458125 | 1.4539374999999999 |
| ECOF/redundant | 11.774375000000003 | 5.744906249999999 | 17.519281250000002 |
| ECOF/front | 20.835 | 8.126156250000012 | 28.961156250000023 |
| ECOF/orphan | 0.19375 | 0.054749999999999986 | 0.24850000000000003 |
| ECOR/critical | 0.72734375 | 0.31910156250000005 | 1.0464453125000002 |
| ECOR/redundant | 5.5679687499999995 | 2.724999999999997 | 8.29296875 |
| ECOR/front | 26.079687500000002 | 10.75335937500005 | 36.83304687500006 |
| ECOR/orphan | 0.9765624999999999 | 0.27496093749999995 | 1.2515234375000006 |

Allocation is ordinary N+.1 per ordinary undirected held pair, split .05 per endpoint. O and incident pairs are exempt. All-site effective-root classification separates critical, redundant, forward-reachable fronts and root-unreachable orphans; idle sites count. Cost allocations conserve, but are not marginal deletion savings. JSON contains each time series (t0 separately), all eight per-run fractions and both starts.

| Arm | D5 removals | Triggered checks | Trials / failures | No candidates / no passing | Prospective wall / CPU seconds |
|---|---|---|---|---|---|
| ECOF | {} | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| ECOR | {'D5r': 53} | 183 | 53 / 0 | 130 / 0 | 0.1645645850002211 / 0.061050000000108184 |

Prospective failure fraction uses candidate trials as denominator; check-level no-candidate/no-passing/below-trigger counts are separate. Time is the pure prospective graph rebuild, not total observer/worker overhead. D5f_none and removal site/class/age/lock/tip are in JSON. Reserve56 is a trigger only; one removal need not restore cost<=56.

| Arm/start/key | First actual candidate cost refusal t | Current cost | Candidate insertion cost |
|---|---|---|---|
| ECOF/i/0 | 400.0 | 62.8 | 64.1 |
| ECOF/i/1 | 400.0 | 62.7 | 64.2 |
| ECOF/i/2 | 420.0 | 63.5 | 65.3 |
| ECOF/i/3 | 400.0 | 63.8 | 65.2 |
| ECOF/i/4 | 420.0 | 63.3 | 64.9 |
| ECOF/ii/0 | 360.0 | 63.1 | 64.5 |
| ECOF/ii/1 | 340.0 | 63.2 | 64.3 |
| ECOF/ii/2 | 380.0 | 64.0 | 65.3 |
| ECOF/ii/3 | 400.0 | 63.3 | 65.1 |
| ECOF/ii/4 | 320.0 | 63.6 | 65.3 |
| ECOR/i/0 | 440.0 | 63.0 | 64.5 |
| ECOR/i/1 | 400.0 | 63.400000000000006 | 65.0 |
| ECOR/i/2 | 440.0 | 63.6 | 65.2 |
| ECOR/i/3 | 420.0 | 62.8 | 64.3 |
| ECOR/i/4 | 440.0 | 63.1 | 64.7 |
| ECOR/ii/0 | 360.0 | 62.8 | 64.4 |
| ECOR/ii/1 | 360.0 | 63.0 | 64.9 |
| ECOR/ii/2 | 400.0 | 63.1 | 65.0 |

The first-refusal table records actual feasible-candidate admission time and current/prospective cost, before later removals/births. Propagated resource stops are not new candidate measurements. Historical first-refusal boundaries are sampled in COVERAGE_DIAGNOSTIC; historical mass-series cost is sampled, so it cannot substitute for an exact first-candidate cost. Context samples remain labelled historical.

| Arm | Break labels | Non-repair labels |
|---|---|---|
| RD3 | {'D3': 0, 'D1': 0, 'D4': 0, 'G-dist': 69, 'G-deg': 0, 'R': 0, 'X': 17} | {'S': 17, 'C': 33, 'N': 1, 'G': 0, 'X': 2, 'legacy_B': 17} |
| COVA | {'D3': 0, 'D1': 0, 'D4': 0, 'G-dist': 10, 'G-deg': 0, 'R': 0, 'X': 7} | {'S': 6, 'C': 16, 'N': 0, 'B': 11, 'G': 0, 'X': 0} |
| COVB | {'D3': 0, 'D1': 0, 'D4': 0, 'G-dist': 90, 'G-deg': 0, 'R': 0, 'X': 37} | {'S': 25, 'C': 38, 'N': 2, 'B': 21, 'G': 0, 'X': 4} |
| ECOF | {'D3': 0, 'D1': 0, 'D4': 0, 'D5f': 0, 'D5r': 0, 'G-dist': 69, 'G-deg': 0, 'R': 0, 'X': 17} | {'S': 17, 'C': 33, 'N': 1, 'B': 16, 'G': 0, 'X': 2} |
| ECOR | {'D3': 0, 'D1': 0, 'D4': 0, 'D5f': 0, 'D5r': 0, 'G-dist': 90, 'G-deg': 0, 'R': 0, 'X': 18} | {'S': 47, 'C': 54, 'N': 1, 'B': 32, 'G': 0, 'X': 1} |

Revised B records post-birth gaps for pre-transition open outages, excluding restoring terminals and restoring gaps from non-repair evidence; restoration samples remain with zero duration weight. New outages inherit no earlier birth. RD3 retains legacy_B, separately from revised B. C and B are global observations, N names the site; D5 attribution includes loss after neighbor/degree rewiring and is observed removal context, not causal proof. Full outages retain break candidates and restoration evidence in JSON.

ECOF deficit/stall histories are kernel-owned, clone-copied and growth-end only; finite-current guard implements newly gained roots and infinity pauses. D5f follows D1/D4 before D3; its reset can become20 at the same check’s end if still stalled. ECOR follows D3 before births and vetoes candidates using a pure all-site graph rebuild. Output-first, pointer, quotas and RD3 remain inherited; neither economy arm includes coverage ordering or recycle.

Scheduler cap5400s, <=10 workers, conservative remaining-job projection includes both off controls. Verified completed slots are reused; any started/incomplete slot is never rerun. Process-access failure stops execution. Caffeinate surrounds execution; each worker shares the deadline. Every attempt retains its ticket and timing: {"status":"PARTIAL","projection_seconds":4372.95988575,"workers":10,"reused":["ECOF_i_k0_on","ECOF_i_k1_on","ECOF_i_k2_on","ECOF_i_k3_on","ECOF_i_k4_on","ECOF_ii_k0_on","ECOF_ii_k1_on","ECOR_i_k0_on","ECOF_i_k0_off","ECOR_i_k0_off"],"stop_reason":"projection 6255.6s exceeds 5400s; stop launching","elapsed_seconds":2011.138375583,"awake_seconds":2011.138377083}

Historical conservative projection is3987.979s at10 workers, above the fixed cap. A new full schedule must stop before launch until Claude resolves the owner’s runtime decision; code never raises the cap. This report never executes pilots. No native trajectory identity is claimed until Claude’s full on/off pairs complete.

Commands: ECONOMY_USAGE.md. Raw files remain in _local/economy with size/SHA256; source/build/dependency pins exclude PLAN_CURRENT.md, DESIGN_0G.md and DESIGN_0H_REV7.md. Existing SCR/V1/RD3 and coverage summaries/receipts are unchanged. Recheck tracking is in docs/reviews/tactical_0h_economy_implementation_recheck_codex.md, under the owner’s prohibition on editing PLAN_CURRENT.md.
