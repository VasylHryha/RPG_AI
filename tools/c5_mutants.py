"""C5 mutation definitions for tools/milestone_mutation.py: {name: (file, exact original text, replacement)}.

Each mutant is a plausible implementation error that the focused contracts in tests/test_c5.py must
detect. The frozen C4 files are covered by the C4 mutants and are not mutated here.
"""

MUTANTS = {
    "recovery_ignores_original": ("geomind/c5_detect.py", "float(min(original_to_control, original_to_kicked, control_to_kicked))",
                                  "float(control_to_kicked)"),
    "criterion6_dropped": ("geomind/c5_detect.py", '"6_parts_alive": bool(stats["parts_alive"])', '"6_parts_alive": True'),
    "port_overlap_unchecked": ("geomind/c5_detect.py", 'and r["port_overlap"] <= max_port_overlap', ""),
    "unit_lock_unchecked": ("geomind/c5_detect.py", 'and r["lock_std"] <= level1["lock_std"]', ""),
    "time_not_scaled": ("geomind/c5_detect.py", "t[key] = level1[key] * T", "t[key] = level1[key]"),
    "freq_tol_not_scaled": ("geomind/c5_detect.py", 't["freq_tol"] = level1["freq_tol"] / T', 't["freq_tol"] = level1["freq_tol"]'),
    "outcome_merged_first": ("geomind/c5_detect.py", '    if any(c["accepted"] for c in world_candidates):\n        return "FORMED"\n',
                             ""),
    "decoupling_leaks": ("geomind/c5_compose.py", "SEPARATION = 100.0", "SEPARATION = 1.0"),
    "shift_not_rigid": ("geomind/c5_compose.py", "        out[labels == u] += v\n", "        out[np.flatnonzero(labels == u)[:1]] += v\n"),
    "scale_wrong_factor": ("geomind/c5_compose.py", "(scale - 1.0) * (centroids[u] - group)", "scale * (centroids[u] - group)"),
    "rates_per_element": ("geomind/c5_compose.py", "oms.append(np.full(len(t[\"th\"]), rng.uniform(-delta, delta)))",
                          "oms.append(rng.uniform(-delta, delta, len(t[\"th\"])))"),
    "unit_phase_arithmetic_mean": ("geomind/c5_units.py", "raw = np.stack([circular_mean(ths[:, labels == u], axis=1) for u in units], axis=1)",
                                   "raw = np.stack([ths[:, labels == u].mean(1) for u in units], axis=1)"),
    "port_overlap_never": ("geomind/c5_units.py", "return bool((cross > 0).all() or (cross < 0).all())", "return False"),
    "coarse_never_flags": ("geomind/c5_coarse.py", "if invalid(cs, counts0, counts, theta0, theta):", "if False:"),
    "open_loop_flags_dropped": ("geomind/c5_coarse.py", "                flagged += 1\n", ""),
    "coarse_phase_sign": ("geomind/c5_coarse.py", "np.sin(dphi) * weight", "np.sin(-dphi) * weight"),
    "coarse_ignores_natural_rate": ("geomind/c5_coarse.py", "theta_dot = cs.natural + np.bincount", "theta_dot = 0.0 * cs.natural + np.bincount"),
    "margin_ignored": ("geomind/c5_experiment.py", '    if summary["ci"][0] > margin:', '    if summary["ci"][0] > 0:'),
    "coarse_pass_one_baseline": ("geomind/c5_experiment.py", 'if all(g["ci"][0] > 0 for g in gains):', 'if gains[0]["ci"][0] > 0:'),
    "coarse_fail_one_baseline": ("geomind/c5_experiment.py", 'if any(g["ci"][1] < 0 for g in gains):', 'if gains[0]["ci"][1] < 0:'),
    "coarse_drops_relaxation": ("geomind/c5_experiment.py", 'for b in ("no_transfer", "rigid_transfer", "relaxation")}', 'for b in ("no_transfer", "rigid_transfer")}'),
    "relaxation_ignores_tau": ("geomind/c5_experiment.py", "share = 1.0 - np.exp(-np.asarray(times) / tau)", "share = np.ones(len(times))"),
    "response_error_unnormalized": ("geomind/c5_experiment.py", "axis=-1) / L[others]", "axis=-1)"),
    "separation_fail_row": ("geomind/c5_experiment.py", 'if summary["ci"][1] < 1.0:', 'if summary["ci"][1] < 0.0:'),
    "separation_wrong_tau1": ("geomind/c5_experiment.py", 't1 = np.mean([w["tau1"][u] for u in g["units"]])', 't1 = np.mean(w["tau1"])'),
    "hc_ignores_separation": ("geomind/c5_experiment.py", '                   e["timescale_separation"]["verdict"])', '                   "PASS")'),
    "mg_dose_constant": ("geomind/c5_experiment.py", "    return float(value)\n", "    return 1.0\n"),
    "mg_uniform_allowed": ("geomind/c5_experiment.py", '    if kind != "rms":\n        raise', '    if False:\n        raise'),
    "downward_against_self": ("geomind/c5_experiment.py", 'off_d = wrap(thd[-1, ports] - circular_mean(thd[-1, members]))',
                              'off_d = wrap(thc[-1, ports] - circular_mean(thc[-1, members]))'),
    "control_vacuous_passes": ("geomind/c5_experiment.py", '"PASS" if tested else "NOT_TESTED"', '"PASS"'),
    "hm_ignores_formation": ("geomind/c5_experiment.py", 'elif e["formation_l2"]["verdict"] == "PASS" and causal', "elif causal"),
    "hm_ignores_dose": ("geomind/c5_experiment.py", 'and causal == ("PASS", "PASS", "PASS"):', 'and causal[:2] == ("PASS", "PASS"):'),
    "hc_formation_row_dropped": ("geomind/c5_experiment.py", "    if upper < 0.25:\n        h_c = \"NOT_SUPPORTED\"\n    elif",
                                 "    if False:\n        h_c = \"NOT_SUPPORTED\"\n    elif"),
    "hc_ignores_transfer": ("geomind/c5_experiment.py", 'composition = (e["downward_effect"]["verdict"], e["emergent_transfer"]["verdict"],',
                            'composition = (e["downward_effect"]["verdict"], "PASS",'),
    "formation_min_worlds_ignored": ("geomind/c5_experiment.py", 'rules["formation_min_fraction"] and formed >= min_worlds', 'rules["formation_min_fraction"]'),
    "effective_state_min_worlds_ignored": ("geomind/c5_experiment.py", '"INCONCLUSIVE" if formed < min_worlds or not errors', '"INCONCLUSIVE" if not errors'),
    "effective_frequency_unscaled": ("geomind/c5_experiment.py", '["state_error_frequency_level1"] / S["T"]', '["state_error_frequency_level1"]'),
    "ablation_against_intact_control": ("geomind/c5_experiment.py", '= v - gm_values[("control", cond)]', '= v - gm_values[("control", "intact")]'),
    "decoupled_transfer_not_decoupled": ("geomind/c5_experiment.py", '("decoupled_pulse", "intact", x0 + offsets, pulse_th)',
                                         '("decoupled_pulse", "intact", x0, pulse_th)'),
    "smoke_uses_final_seeds": ("geomind/run_c5.py", 'execute(manifest, manifest["seeds"]["development_entropy"], SMOKE_WORLDS)',
                               'execute(manifest, manifest["seeds"]["final_entropy"], SMOKE_WORLDS)'),
    "controls_gate_vacuous": ("geomind/run_c5.py", 'e["not_independent"]["verdict"] == "PASS" and e["not_a_clump_l2"]["verdict"] == "PASS"',
                              'e["not_independent"]["verdict"] != "FAIL" and e["not_a_clump_l2"]["verdict"] != "FAIL"'),
}

# Guards whose removal another tested guard compensates for; none are expected for C5.
KNOWN_BACKSTOPS = set()

# Mutants expected to run forever; none for C5.
EXPECTED_TIMEOUTS = set()
