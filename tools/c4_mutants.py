"""C4 mutation definitions for tools/milestone_mutation.py: {name: (file, exact original text, replacement)}.

Each mutant is a plausible implementation error that the focused contracts in
tests/test_c4.py must detect.
"""

MUTANTS = {
    "mode_to_geometry_sign": ("geomind/c4_model.py", "batch.A * (1.0 + batch.J * np.cos(dth))", "batch.A * (1.0 - batch.J * np.cos(dth))"),
    "coupling_kernel": ("geomind/c4_model.py", "np.exp(-r * r)", "np.exp(-r)"),
    "neighbor_radius_ignored": ("geomind/c4_model.py", "axis=2) < batch.radius)", "axis=2) < 100 * batch.radius)"),
    "neighbor_skips_nearest": ("geomind/c4_model.py", 'kind="stable")[:, :, :k]', 'kind="stable")[:, :, 1:k + 1]'),
    "self_as_neighbor": ("geomind/c4_model.py", "r[:, np.arange(n), np.arange(n)] = np.inf", "r[:, np.arange(n), np.arange(n)] = 0.0"),
    "phase_coupling_sign": ("geomind/c4_model.py", "np.sin(dth) * mask", "np.sin(-dth) * mask"),
    "rk4_weights": ("geomind/c4_model.py", "2 * k2x + 2 * k3x + k4x", "2 * k2x + k3x + k4x"),
    "recovery_ignores_phase": ("geomind/c4_detect.py",
                               ' and stats["recovery_pattern_error"] <= t["pattern_tol"],', ","),
    "recovery_compares_to_itself": ("geomind/c4_detect.py",
                                    "members) - pair_differences(end_th[b], members)", "members) - pair_differences(end_th[worlds + n], members)"),
    "kick_not_zero_mean": ("geomind/c4_detect.py", "    dth -= dth.mean()\n    dth *= phase_rms", "    dth *= phase_rms"),
    "lock_mask_loose": ("geomind/c4_detect.py", "ths[:, :, None], 0) <= lock_std", "ths[:, :, None], 0) <= 10 * lock_std"),
    "membership_unchecked": ("geomind/c4_detect.py", 'stats["membership_jaccard"] >= t["membership_jaccard"]', "True"),
    "shape_unchecked": ("geomind/c4_detect.py", '"2_shape": stats["shape_cv"] <= t["shape_cv"]', '"2_shape": True'),
    "gm_not_scaled": ("geomind/c4_experiment.py", "centroid + scale * (x[members] - centroid)", "centroid + (x[members] - centroid)"),
    "mg_statistic_min": ("geomind/c4_experiment.py", "return float(max(radius_of_gyration", "return float(min(radius_of_gyration"),
    "causality_upper_bound": ("geomind/c4_experiment.py", 'if intact["ci"][0] <= 0:', 'if intact["ci"][1] <= 0:'),
    "wilson_centre": ("geomind/c4_experiment.py", "centre = (p + z * z / (2 * total))", "centre = (p + z * z / total)"),
    "hm_ignores_mg_failure": ("geomind/c4_experiment.py", '    if "FAIL" in causal:', '    if "FAIL" in causal[:1]:'),
    "effective_state_rule": ("geomind/c4_experiment.py", 'fraction >= rules["effective_state_min_fraction"]', "fraction >= 0.0"),
    "clump_gate_off": ("geomind/run_c4.py", 'all(evaluations[a]["not_a_clump"]["verdict"] != "FAIL" for a in ARMS)', "True"),
    "clump_gate_vacuous": ("geomind/run_c4.py", '\n                                    and evaluations["identical"]["not_a_clump"]["verdict"] == "PASS"),', "),"),
    "smoke_uses_final_seeds": ("geomind/run_c4.py", 'execute(manifest, manifest["seeds"]["development_entropy"], SMOKE_WORLDS)',
                               'execute(manifest, manifest["seeds"]["final_entropy"], SMOKE_WORLDS)'),
    "frozen_topology_ignored": ("geomind/c4_model.py", "idx = np.where(batch.frozen, phase_topology[0], idx)", "idx = idx"),
    "ablation_against_intact_control": ("geomind/c4_experiment.py", 'stats[(kind, n, f"control/{condition}", condition)]',
                                        'stats[(kind, n, "control/intact", "intact")]'),
    "dose_monotonicity_unchecked": ("geomind/c4_experiment.py", 'if all(a <= b for a, b in zip(means, means[1:])) and difference["ci"][0] > 0:',
                                    'if difference["ci"][0] > 0:'),
    "min_worlds_ignored": ("geomind/c4_experiment.py", ' or intact["n_worlds"] < min_worlds:', ":"),
    "hm_ignores_dose": ("geomind/c4_experiment.py", 'and causal == ("PASS", "PASS", "PASS"):', 'and causal[:2] == ("PASS", "PASS"):'),
    "hm_ignores_formation": ("geomind/c4_experiment.py", 'elif arm_eval["formation"]["verdict"] == "PASS" and causal', "elif causal"),
    "formation_fail_not_supported": ("geomind/c4_experiment.py", '    if "FAIL" in causal:', '    if "FAIL" in causal + (arm_eval["formation"]["verdict"],):'),
    "recovery_ignores_original": ("geomind/c4_detect.py", "float(min(original_to_control, original_to_kicked, control_to_kicked))",
                                  "float(control_to_kicked)"),
    "clump_vacuous_passes": ("geomind/c4_experiment.py", '"PASS" if clump["candidates"] else "NOT_TESTED"', '"PASS"'),
    "mg_dose_size": ("geomind/c4_experiment.py", 'probe_kick(rng, len(members), float(dose.split(":")[1]))',
                     'probe_kick(rng, len(members), 2 * float(dose.split(":")[1]))'),
}

# Guards whose removal another tested guard compensates for; none are expected for C4.
KNOWN_BACKSTOPS = set()

# Mutants expected to run forever; none for C4.
EXPECTED_TIMEOUTS = set()
