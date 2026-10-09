# Ordinary movement toolbox

Decision 0039 applies: these functions enumerate points. They do not select a
target, movement, fire, hold, advance, participation activation, P16 mode or
safety winner. The learned scorer and pointer retain those decisions. Labels,
oracle counters, complex states, pair modes and previous teacher commands never
enter these functions. Only current public unit positions/velocities/physics and
the public-prefix one-second velocity are used. No controller is invoked.

Let actor position be p, body radius r, speed s, weapon range R and minimum
range L. All positions, distances and offsets below are in pixels; velocity is
pixels/second. Define D(x)=x/||x||, with D(0)=(1,0), C the arena rectangle clamp,
and C_r the body rectangle clamp. Units are sorted by persistent ID. Nearest
entities minimize (Euclidean distance, ID); this identifies a geometric origin,
never a target assignment. Existing candidate order is preserved as a prefix.

| Family | Formula and enumeration |
|---|---|
| Body-aware range point | For every enemy e, project p to the annulus about e with [L,R] for artillery and [0,R+r+r_e] otherwise, intersected with the body rectangle. |
| Anchor point | For every enemy e, `e + max(L,R-12) D(p-e)`, for artillery. All enemies are supplied; no focus, splash-value rank, reach filter or anchor winner is chosen. |
| Gun spacing | `S = sum_{friendly artillery g != actor} max(0,60-||p-g||) D(p-g)`. At coincidence use (-1,0) if actor ID < gun ID, otherwise (1,0). Supply each anchor both without and with S; also supply p+S. |
| Escort | For ranged actors, let g be the nearest friendly gun. Supply `C(g+60 D(e-g))` for every enemy e, and the same point directed toward the arithmetic centroid of enemy artillery. No 400 px threat selector, P16 activation or fallback hierarchy is used. Each direction retains its enemy source; the centroid retains the gun source. |
| Approach waypoint | For every enemy e, `p+200 D(e-p)`. This computes a waypoint only; no advance instruction is issued. |
| Velocity continuation | For instantaneous public velocity v and public-prefix smoothed velocity V, supply `p+200 D(v)` / `p+200 D(V)` and `p+v*1s` / `p+V*1s`. Zero velocity supplies p, rather than an invented +x continuation. |
| Local repulsion | p+S above (artillery only); other roles use the same 60 px overlap sum over all friends. No attraction, target preference or complex-mode law is copied. |
| Directional waypoints | 64 fixed equally spaced directions at radius 200 about p. Maximum chord error on this circle is `400 sin(pi/128)=9.81649 px`. Arena/body clamp cannot increase this error. |
| Engagement-ring points | 64 fixed equally spaced directions about the nearest enemy, at its body-aware outer engagement radius, and also its inner radius when positive. Error is `2*radius*sin(pi/128)` (15.7064 px at radius 320). This is a finite vocabulary, not a guarantee for arbitrary larger ranges. |
| Unconditional band image | For each escort, anchor, spacing-resolved anchor, approach, continuation and local-repulsion q, additionally supply `C_r(e + clamp(||q-e||,lo,hi) D(q-e))` about the nearest enemy. Retain q too. At q=e, use D(p-e). This computes the radial band image even if q already participates elsewhere; no participation decision or legal-target selection is copied. Fixed rings already enumerate boundary directions and need no band image. |
| Hold | Existing p candidate remains available for every frame, including empty enemy banks. |

Each raw new point is arena-clamped, each band image is body-clamped. Computation
of the band image uses the original raw point before the final arena clamp;
escort's explicit C occurs first, matching its documented geometry. The runtime
still applies its existing body clamp after the learned residual and N2 drift.

The preserved vocabulary has at most 576 points. New points have at most 64
body-aware bands + 128 approach/images + 256 artillery anchors/images + 8
continuations/images + 2 repulsion/images + 192 directional/ring points = 650,
so artillery has at most 1226. Ranged escorts add at most 130 instead of 256
anchors. MAX_MOVE=1280 supplies fixed padding with no truncation. MAX_AIM=194
and residual bounds (aim 12, movement 24 per axis) remain unchanged.

Descriptors have 26 entries. Existing types 0–10 and numerical fields 11–17
retain their meanings. New one-hot types: 18 escort, 19 anchor, 20 spaced anchor,
21 waypoint, 22 continuation, 23 band image, 24 repulsion, 25 angular point.
Every candidate has its own point, features, mask and source token. Raw and
projected variants are separately scored; the network can choose either.
The seven numerical fields are still serialized at indices 11:18, with type and
source alongside them. Python/native MLP widths, normalization by sqrt(FEATURES),
source pointers, padding and flat-head slices derive from the shared constants.

No irreducible private-input movement is established by rev2: O reconstructs its
state from the full public prefix. Its v6 complex-mode steering is not copied
into a tool. Remaining misses must be reported as vocabulary approximation or
insufficient public-history representation, unless an actual missing input is
proved. The existing bounded learned residual remains ±24 px per axis. If that
cannot represent a measured remaining class, propose a separately bounded
history-conditioned residual extension with a predeclared pixel envelope and
native/Python parity, then rerun unchanged 90% admission. Do not lower the gate.
