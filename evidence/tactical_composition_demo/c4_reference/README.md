# C4 reference values for the S3 controller port

`c4_reference_states.json` holds the accepted C4 element law (`geomind/c4_model.py`, sha256 `4fafc161…59d33`, the frozen hash in `STATUS.json`) evaluated on 5 fixed
states, each under 3 variants (intact, J=0, K=0):
- the neighbour sets;
- the right-hand side (x_dot, th_dot);
- one RK4 step at dt 0.02.

Made by `make_c4_reference.py`, which only reads the frozen module. The cases:
- three random states (N = 6, 24, 50);
- edge cases: an isolated element, two coincident elements, an exact distance tie;
- a crowded state with more than 8 neighbours inside the radius.

**The S3 acceptance check (a):** the C++ controller's law, given these states with no enemies and no damage input, reproduces every value to 1e-9.
