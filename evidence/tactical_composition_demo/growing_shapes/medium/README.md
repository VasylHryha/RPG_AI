# 0h fast C4 medium

Exploratory engine implementation under decision 0028 item 17. Claude review is
pending. This folder contains no task experiment or learned parameters.

From this folder:

```sh
python3 build.py
../../../../.venv/bin/python -m pytest -q -x -o cache_dir=_build/pytest-cache test_medium.py
python3 benchmark.py
```

The native library and contract executable are placed in ignored `_build/`.
Build explicitly before importing: the wrapper never compiles on import.
The C++17 sources require only the standard library. The Python API requires
only the standard library; tests require pytest.

```python
from medium import Medium, Params, Drive

with Medium(seed=17, params=Params(window=32, min_samples=16)) as medium:
    element_id = medium.add(0, 0, phase=0, rate=0.1)
    medium.set_drives([Drive(1, 0, 0, 0, 0.1, 1, 1, 3)])
    medium.step(0.01, steps=10)
    amplitude, phase = medium.readout(0, 0, width=1, reach=3)
    state = medium.save()
    with medium.evaluation_without(element_id) as evaluation:
        evaluation.step(0.01, steps=10)
    with Medium.load(state) as restored:
        assert restored.save() == state
```

Coordinates, time and natural rates use accepted C4 units; phase is unwrapped
radians. Drives have caller-owned stable IDs separate from element IDs.
`Drive(id,x,y,phase,rate,strength,width,reach)` supplies the phase at step start,
the phase rate over that step, `K_in * strength`, Gaussian width and strict reach.
Set drives each step as needed; omitted sites are removed. The native integrator
advances drive phases through RK4 stages and to the end of the step.

`Params` retains accepted C4 defaults (including k=8, radius=3). `geometry_rate=1`
reproduces the accepted law. A runner may explicitly reduce it to impose slower
motion; that is a labelled extension, not exact accepted-law parity.
`window` counts samples; every `step` appends one. `observe` appends a sample
without advancing time and is intended for fixtures/external sampling. With
constant dt and no extra observe calls the window spans `(window-1)*dt`.
No PLV or strain is qualified until `min_samples` shared observations exist.

`Growth` requires **all** fields in `medium_c.h`; no growth thresholds are chosen
by the engine. `configure_growth` validates hysteresis/cap and resets timers.
Growth is explicitly triggered by `apply_growth_rules`, at most once per
`growth_period`; integration never changes structure automatically. Parameter
choices, exact formulas, ordering and the remaining drafter questions are in
[MEDIUM_REPORT.md](MEDIUM_REPORT.md).

`set_needs` accepts externally accumulated error and the runner's chosen input
phase/rate for each stable region. `set_utility` accepts externally computed
score loss on silence (`score_full-score_silenced`), only after age exceeds one
growth period. It is consumed once at the next growth check. The stability arm
ignores both reward hooks. `evaluation_without` clones the entire medium; the
original state is untouched. `silenced` temporarily silences on the same handle
and restores the flag even after an exception; use a clone when the evaluation
advances time and must not affect the original state.

Every successful add/remove/split is logged with time, rule, IDs and trigger
measurements. Split logs parent and both fresh child IDs. Element IDs never
reuse. Coupling diagnostics count directed element-to-element links plus active
drive-to-element links; readouts do not contribute a dynamical coupling cost.
`groups` uses C4's spatial rule and PLV connectivity; it is not the full accepted
C4 resonator/recovery qualification.

The v1 snapshot contains the complete medium, including RNG, samples, timers,
protection ages, reward data and event log. It uses explicit scalar fields, no
struct padding, in native byte order (same architecture required). `load` rejects
truncation, trailing bytes, wrong version and invalid operational fields. The C
API has no globals, returns handle-local errors, and bounds-checks output buffers.
Use one thread per handle; different handles share no state. ABI structs and
ownership are defined in [medium_c.h](medium_c.h).
