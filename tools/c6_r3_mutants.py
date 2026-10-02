"""Semantic Arm-B mutants; executed only by the registered generic pipeline."""
MUTANTS={
 'nonzero_sham':('geomind/c6_r3_assay.py',"outbound=0. if condition=='no_backreaction' else 1.","outbound=1."),
 'masked_denominator':('native/c6_r3/background.cpp','double count=(double)ids.size();','double count=0.;for(int j:ids)count+=gate?gate[j]:1.;count=std::max(count,1.);'),
 'incoming_no_r_leaks':('native/c6_r3/background.cpp','(mode==1||mode==3)?0.:.8,mode==1?0.:1.,true,vx,vt,true,mode!=2);','mode==3?0.:.8,1.,true,vx,vt,true,mode!=2);'),
 'phase_sign':('native/c6_r3/background.cpp','std::sin(p);','std::sin(-p);'),
 'common_topology_ignored':('native/c6_r3/background.cpp','nearest(phase_origin+2*nb,i,reference_x,nb,false)','nearest(initial_x+2*nb,i,reference_x,nb,false)'),
 'replay_extends_future':('geomind/c6_r3_background.py','np.any(times > self.duration+1e-10)','False'),
 'causal_ablation_unchecked':('geomind/c6_r3_assay.py',"if abs(ablated) > max(q['vanish_absolute_tolerance'], q['vanish_fraction']*intact):",'if False:'),
 'no_r_contrast_omitted':('geomind/c6_r3_protocol.py','for control in CONTROLS:','for control in CONTROLS[-1:]:'),
 'publication_only_fake_bg':('geomind/c6_r3_protocol.py','bg=claim(bgverdicts);ps=claim(psverdicts)',"bg='SUPPORTED_WITHIN_SCOPE';ps=claim(psverdicts)"),
 'outcome_selected_ports':('geomind/c6_r3_assay.py','ports=(0,12)','ports=tuple(np.argsort(state[1][:self.nb])[-2:])'),
 'label_leakage':('geomind/c6_r3_assay.py','def find_candidates(xs, ths, thresholds):','def find_candidates(xs, ths, thresholds, condition=None):'),
 'second_turn_restage':('geomind/c6_r3_protocol.py',"return first if first is not None and first[2]['qualified'] else None",'return first'),
 'margin_ignored':('geomind/c6_r3_protocol.py',"if ci[0]>margin:return 'PASS'","if ci[0]>0:return 'PASS'"),
 'quorum_ignored':('geomind/c6_r3_protocol.py',"if ci is None or n<minimum:return 'INCONCLUSIVE'","if ci is None:return 'INCONCLUSIVE'"),
 'chain_bath_unchecked':('geomind/c6_r3_protocol.py',"l['first_after']==l['second_before'] and ",''),
 'chain_source_unchecked':('geomind/c6_r3_protocol.py',"l['first_episode_source']==l['second_source_input'] and ",''),
 'chain_quorum_ignored':('geomind/c6_r3_protocol.py',"if complete_chains<st['minimum_qualified_worlds']:",'if False:'),
 'source_pin_unchecked':('tools/c6_r3_design_gate.py',"if record.get('verification_status')!='VERIFIED' or problems:",'if False:'),
 'formed_numerics_ignored':('geomind/c6_r3_protocol.py',"all(c['passed'] for c in checks.values())","checks['initial']['passed']"),
}
KNOWN_BACKSTOPS=set()
EXPECTED_TIMEOUTS=set()
