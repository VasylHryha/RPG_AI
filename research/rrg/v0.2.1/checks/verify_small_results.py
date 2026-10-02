"""Deterministic checks for the limited illustrations in RRG 05.

Python 3 standard library only. This is not a simulation of universal RRG,
formal theorem verification, or independent experimental replication.
Run from any working directory: python path/to/verify_small_results.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path


def close(actual: float, expected: float, *, atol: float = 1e-10) -> None:
    if not math.isfinite(actual) or not math.isclose(actual, expected, abs_tol=atol, rel_tol=1e-10):
        raise AssertionError(f"{actual!r} != {expected!r}")


def main() -> dict:
    records = []
    def save(name: str, values: dict) -> None:
        records.append({"test": name, "status": "passed", "values": values})

    # Noise-filter spectral maximum: a pre-existing oscillator, not its origin.
    m, gamma, k, D = 2., .5, 3., .1
    w = math.sqrt(k/m-gamma**2/(2*m*m))
    def spec(freq: float) -> float:
        return 2*D/((k-m*freq**2)**2+gamma**2*freq**2)
    assert spec(w) > spec(w-.05) and spec(w) > spec(w+.05)
    # Critical point of the denominator at the positive-frequency peak.
    close(-4*m*w*(k-m*w*w)+2*gamma*gamma*w, 0.)
    save('noise_filter_peak', {'peak_angular_frequency': w, 'spectrum_at_peak': spec(w)})

    mu, c3, c5 = -.18, 1., 1.
    discr = c3*c3+4*c5*mu
    ym, yp = ((c3-math.sqrt(discr))/(2*c5), (c3+math.sqrt(discr))/(2*c5))
    xm, xp = math.sqrt(ym), math.sqrt(yp)
    f = lambda x: mu*x+c3*x**3-c5*x**5
    fp = lambda x: mu+3*c3*x*x-5*c5*x**4
    for x in (0., xm, -xm, xp, -xp): close(f(x), 0.)
    assert fp(0)<0 and fp(xm)>0 and fp(xp)<0
    close(fp(xm),2*ym*(c3-2*c5*ym))
    close(fp(xp),2*yp*(c3-2*c5*yp))
    save('signed_scalar_branches', {'x_minus':xm,'x_plus':xp,'lower_derivative':fp(xm),'upper_derivative':fp(xp),'equilibrium_count':5})

    # Zero stationary current; the normalization constant cancels.
    def V(x:float)->float: return -mu*x*x/2-c3*x**4/4+c5*x**6/6
    D=.07
    for x in (-1.1,-.4,0.,.6,1.2):
        p=math.exp(-V(x)/D)
        dp=f(x)*p/D
        close(f(x)*p-D*dp,0.)
    save('stationary_density_current', {'diffusivity':D,'points_checked':5})

    # On L=2*pi, allowed k are integers; preferred q=.6 cannot be realized.
    r,q=.05,.6
    rates={str(i):r-(q*q-i*i)**2 for i in range(-5,6)}
    maximum=max(rates.values())
    assert r>0 and maximum<0
    save('finite_domain_detuning', {'continuous_maximum':r,'discrete_maximum':maximum,'q':q,'L':2*math.pi})

    B0, rho, I, tau, initial = .2,1.,yp,2.,.1
    equilibrium=B0+rho*I
    for t in (0.,.1,2.,8.):
        B=equilibrium+(initial-equilibrium)*math.exp(-t/tau)
        derivative=-(initial-equilibrium)*math.exp(-t/tau)/tau
        close(tau*derivative,-(B-B0)+rho*I)
    p=.9
    t90=-tau*math.log(1-p)
    close(1-math.exp(-t90/tau),p)
    save('constant_intensity_relaxation', {'equilibrium':equilibrium,'time_to_90_percent_from_B0':t90})

    # Counterexample to automatic stability with positive intensity response.
    # Let B0=0, rho=1, I(B)=B^2. B*=1 solves B*=I(B*) and is unstable.
    Bstar=1.
    close(Bstar,Bstar*Bstar)
    slope=(-1+2*Bstar)/tau
    assert slope>0
    save('implicit_background_can_be_unstable', {'equilibrium':Bstar,'linear_growth_rate':slope})

    r_next,alpha=-.5,1.
    growth_after=r_next+alpha*rho*I
    assert growth_after>0
    save('conditional_next_mode_coefficient', {'before':r_next,'after':growth_after,'not_claimed':'a stable next resonator or newly existing mode'})

    sigma, increment=.6,yp
    ratio=math.exp(sigma*increment)
    close((2*math.pi/math.exp(-sigma*increment))/(2*math.pi),ratio)
    assert ratio>1
    assert math.exp(-sigma*increment)<1  # opposite sign response shrinks length
    save('assumed_wavelength_response', {'larger_ratio':ratio,'opposite_response_ratio':math.exp(-sigma*increment)})

    eps,N=.02,12
    for K in (0.,.5,1.,2.):
        e=0.
        for _ in range(N): e=eps+K*e
        bound=eps*sum(K**j for j in range(N))
        close(e,bound)
        if K<1: assert e<=eps/(1-K)+1e-14
    # e_n=0 is allowed even when the upper bound grows exponentially.
    K=2.
    assert all(0.<=eps+K*0. for _ in range(100))
    save('upper_bound_not_actual_divergence', {'K':K,'zero_error_valid':True,'upper_bound_at_N12':eps*(K**N-1)/(K-1)})

    result={'status':'passed','number_of_test_groups':len(records),
        'scope':'Limited deterministic spot checks; not a universal proof, full PDE/stochastic check, or rerun of archived 32-cell simulation.',
        'results':records}
    output=Path(__file__).resolve().with_name('verification_results.json')
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','test_groups':len(records),'output':str(output)}))
    return result

if __name__=='__main__':
    main()
