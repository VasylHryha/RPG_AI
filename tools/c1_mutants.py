"""Mutation definitions for the C1 suite (versioned tooling, not evidence).

Copied from the R005 list recorded in evidence/c1_claude_review/mutation_checks.py.
Update this file, never the recorded evidence script, when C1 code changes.
Each entry is (file, exact original text, replacement); the pattern must occur once.
"""

MUTANTS = {'frame_shift_sign_flipped': ('geomind/incremental.py', 'dx = self._edx[k] - (self._x[t] - self._x[s])', 'dx = (self._x[t] - self._x[s]) - self._edx[k]'),
 'certificate_skips_neighbors_of_moved_nodes': ('geomind/incremental.py', '                        certify.add(other)\n', '                        pass\n'),
 'certificate_skips_freed_anchors': ('geomind/incremental.py', 'tx.dirty = endpoints | set(new_ids) | freed', 'tx.dirty = endpoints | set(new_ids)'),
 'certificate_skips_translated_nodes': ('geomind/incremental.py', 'certify = set(tx.dirty) | tx.translated', 'certify = set(tx.dirty)'),
 'rounding_bound_removed': ('geomind/incremental.py', '            upper = magnitude + bound\n', '            upper = magnitude\n'),
 'anchor_change_not_restored': ('geomind/incremental.py',
                                '                if frame == root and best == self._anchor[root]:\n                    continue',
                                '                if frame == root:\n                    continue'),
 'largest_frame_kept_instead_of_anchor_frame': ('geomind/incremental.py',
                                                '            root = self._comp[best]\n',
                                                '            root = min(group, key=lambda c: (-len(self._members[c]), self._names[previous_anchors[c]]))\n'),
 'degree_overflow_unchecked': ('geomind/incremental.py', '            if not (math.isfinite(self._deg[s]) and math.isfinite(self._deg[t])):', '            if False:'),
 'energy_bound_unchecked': ('geomind/incremental.py', '            if not energy_bound <= ENERGY_LIMIT:', '            if False:'),
 'relation_map_copied': ('geomind/incremental.py', '        fresh = {}\n', '        fresh = {}\n        _copy = dict(self._relation_map)\n'),
 'validation_after_charge': ('geomind/incremental.py',
                             '            self._validate_delta(added_nodes, added_edges, added_relations)\n'
                             '            tx.spend(input_records + len(added_nodes) + len(added_edges) + len(added_relations), "input_records")',
                             '            tx.spend(input_records + len(added_nodes) + len(added_edges) + len(added_relations), "input_records")\n'
                             '            self._validate_delta(added_nodes, added_edges, added_relations)'),
 'rollback_skips_coordinates': ('geomind/incremental.py',
                                '        for node, (x, y) in self.coordinates.items():\n            state._x[node], state._y[node] = x, y',
                                '        for node, (x, y) in self.coordinates.items():\n            pass'),
 'rollback_skips_journal': ('geomind/incremental.py', '        for undo in reversed(self.journal):', '        for undo in ():'),
 'degree_list_unsorted': ('geomind/incremental.py', '            insort(self._src_w[s], item)', '            self._src_w[s].append(item)'),
 'anchor_tie_break_flipped': ('geomind/incremental.py', 'self._names[a] < self._names[b])', 'self._names[a] > self._names[b])'),
 'translation_not_charged': ('geomind/incremental.py', 'tx.spend(len(members), "translation_writes")', 'pass'),
 'local_reads_not_charged': ('geomind/incremental.py',
                             '                    tx.spend(len(incident), "local_edge_reads")\n                    touched.update(incident)',
                             '                    touched.update(incident)'),
 'budget_never_enforced': ('geomind/incremental.py', 'if self.trace["charged_operations"] + count > self.budget:', 'if False:'),
 'fallback_cap_never_enforced': ('geomind/incremental.py', 'if self.trace["fallback_operations"] + count > self.fallback_budget:', 'if False:'),
 'fallback_skips_final_certificate': ('geomind/incremental.py', 'bad, energy = self._certify(everyone, alpha, tx.spend_fallback, trace)', 'bad, energy = [], 0.0'),
 'duplicate_removal_allowed': ('geomind/incremental.py', 'if old_counts - new_counts:', 'if set(old_counts) - set(new_counts):'),
 'frozen_apply_allowed': ('geomind/incremental.py',
                          '"""Atomically apply one additive delta; refusals undo every change."""\n        if self._frozen:',
                          '"""Atomically apply one additive delta; refusals undo every change."""\n        if False:'),
 'relation_redefinition_allowed': ('geomind/incremental.py', 'name in self._relation_map or name in fresh or', 'name in fresh or'),
 'forced_certificate_step_removed': ('geomind/incremental.py', '                    elif quiet:\n', '                    if quiet:\n'),
 'local_quiet_ignores_update_tolerance': ('geomind/incremental.py', ' and alpha * magnitude < utol\n', '\n'),
 'local_norm_guard_removed': ('geomind/incremental.py', '        if not math.isfinite(magnitude):\n            raise ValueError("Nonfinite local force norm")', '        pass'),
 'reference_rhs_sign_flipped': ('geomind/c1_reference.py',
                                'rhs[i] -= w * np.asarray(d)\n            rhs[j] += w * np.asarray(d)',
                                'rhs[i] += w * np.asarray(d)\n            rhs[j] -= w * np.asarray(d)'),
 'baseline_translation_sign_flipped': ('geomind/c1_reference.py',
                                       'moving, keep, sx, sy = a, b, xt - xs - e.offset[0], yt - ys - e.offset[1]',
                                       'moving, keep, sx, sy = a, b, e.offset[0] - (xt - xs), e.offset[1] - (yt - ys)'),
 'evaluator_energy_gate_removed': ('geomind/run_c1.py', '\n                          and finite_number(energy_gap) and energy_gap <= manifest["energy_tolerance"])', ')'),
 'evaluator_status_equality_ignored': ('geomind/run_c1.py', 'statuses_equal &= a.status == b.status', 'statuses_equal &= True'),
 'evaluator_baseline_gate_removed': ('geomind/run_c1.py', 'old.export() == saved and baseline_ok', 'old.export() == saved'),
 'endpoint_time_rule_removed': ('geomind/run_c1.py', ' and time_ratio <= e["time_locality_max_ratio"])', ')')}

# Guards that another tested guard compensates for (see FOCUSED_CHECKS.md).
KNOWN_BACKSTOPS = {"energy_bound_unchecked", "forced_certificate_step_removed",
                   "local_quiet_ignores_update_tolerance", "local_norm_guard_removed"}
# Mutants expected to make the suite run forever; only these may be detected by timeout.
EXPECTED_TIMEOUTS = {"budget_never_enforced"}
