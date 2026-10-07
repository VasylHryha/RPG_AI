"""Focused scratch checks: pure graphs and fake native geometry, no pilot execution."""
import copy
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from service_graph import classify, ranked_choice, service_snapshot
from service_telemetry import break_labels, Observer
from kernel_builder.build_kernels import normal_patch
from execute_service_plan import process_check
from unittest.mock import patch


class Checks(unittest.TestCase):
    def test_alternative_routes_and_idle_critical_site(self):
        ids=[0,1,2,3,4]; incoming={0:{2,3},1:set(),2:{1},3:{1},4:set()}
        out,routes,lost,classes=classify(ids,incoming,{s:{1} if s==7 else set() for s in range(8)},{0})
        self.assertEqual(classes[1],'critical');self.assertEqual(classes[2],'redundant')
        self.assertEqual(classes[3],'redundant');self.assertEqual(classes[4],'non-service')
        self.assertEqual(lost[1],[7]);self.assertTrue(routes[7])
        s=dict(classes=classes,lost=lost)
        self.assertEqual(ranked_choice(s,[1,2,3,4],{1:0,2:.9,3:.9,4:1}),(4,[]))
        self.assertEqual(ranked_choice(s,[1,2,3],{1:0,2:.9,3:.9}),(2,[]))
        self.assertEqual(ranked_choice(s,[1],{1:.9}),(1,[7]))
        incoming[0].remove(2)
        _,_,lost,classes=classify(ids,incoming,{7:{1}},{0})
        self.assertEqual(classes[3],'critical');self.assertEqual(lost[3],[7])

    def test_native_selection_tie_uses_array_order_not_id(self):
        # id 9 precedes id 1 in native storage and is equidistant to receiver 0.
        es=[NS(id=0,x=0.,y=0.,silent=False),NS(id=9,x=1.,y=0.,silent=False),NS(id=1,x=-1.,y=0.,silent=False),NS(id=2,x=0.,y=1.,silent=False)]
        native=NS(elements=es,role=lambda i:'output' if i==0 else 'element',gain=lambda i:1.,policy=lambda:(8.,False,True),params=NS(K=1.),neighbors=lambda:([[1,2,3],[],[],[]],[[1,1,1],[],[],[]],None))
        graph=NS(incoming={0:{1,2,9},9:{0},1:{0},2:{0}})
        m=NS(native=native,drives=[],strong_influence=lambda:graph,step_index=200,birth_steps={i:0 for i in (0,9,1,2)})
        s=service_snapshot(m)
        self.assertEqual(s['selected'][0],[9,1]);self.assertEqual(s['degree'][0],3)
        self.assertEqual(s['active'],set());self.assertEqual(len(s['roots']),8)

    def test_crowding_uses_held_degree(self):
        before=dict(roots={0:{1}},outputs={0},outgoing={1:{0},0:set()},incoming={0:{1},1:set()},lost={1:[0]},
                    positions={1:(0.,0.),0:(1.,0.)},held={0:[1],1:[0]},scale=2.)
        after=copy.deepcopy(before);after['incoming'][0]=set();after['held'][0]=[1,2]
        self.assertEqual(break_labels(before,after,0)[0],'G-deg')
        after=copy.deepcopy(before);after['incoming'][0]=set();after['positions'][0]=(2.,0.)
        self.assertEqual(break_labels(before,after,0)[0],'G-dist')
        after=copy.deepcopy(before);after['incoming'][0]=set();after['positions'].pop(1)
        self.assertEqual(break_labels(before,after,0,dict(id=1,rule='D3'))[0],'D3')

    def test_pgrep_inaccessible_is_not_clear(self):
        with patch('execute_service_plan.subprocess.run',return_value=NS(returncode=3,stdout='',stderr='Cannot get process list')):
            self.assertEqual(process_check()['status'],'PROCESS_ACCESS_BLOCKED')
        with patch('execute_service_plan.subprocess.run',return_value=NS(returncode=1,stdout='',stderr='')):
            self.assertEqual(process_check()['status'],'CLEAR')

    def test_patch_context_is_exact(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'_local') as tmp:
            p=Path(tmp)/'source';d=Path(tmp)/'change';p.write_text('a\nb\n');d.write_text('1a2\n> c\n')
            normal_patch(p,d);self.assertEqual(p.read_text(),'a\nc\nb\n')
            d.write_text('1c1\n< WRONG\n---\n> x\n')
            with self.assertRaises(ValueError):normal_patch(p,d)

    def test_none_gap_is_infinite_not_zero(self):
        from collections import Counter
        for gaps, expected_b in (([None,None], True), ([None,2.], False), ([3.,2.], False), ([3.,3.], True)):
            with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'_local') as tmp:
                o=object.__new__(Observer);o.live=NS(step_index=8000);o.stream=open(Path(tmp)/'trace','w')
                item=dict(site=0,start=700.,end=None,duration=None,censored=False,break_cause='X',initial_gap=gaps[0],
                          samples=[dict(t=700.+i,gap=g,rootless_screened=False) for i,g in enumerate(gaps)],
                          requests=[dict(t=701.)],terminals=[dict(t=702.,outcome='accepted',birth_rule='B1')],internal_route_events=[])
                o.open={0:item};o.outages=[item];o.active=Counter();o.active_served=Counter();o.served=Counter();o.degree=Counter();o.steps=1
                o.removals=[];o.forced=[];o.decisions=[];o.growth_checks=[]
                r=o.finish();self.assertEqual('B' in r['outages'][0]['non_repair_labels'],expected_b)

    def test_censored_outage_and_earliest_nonrepair_tie(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'_local') as tmp:
            # Observer.finish consumes metadata, not native state, after run.close.
            o=object.__new__(Observer);o.live=NS(step_index=8000);o.stream=open(Path(tmp)/'trace','w')
            item=dict(site=0,start=700.,end=None,duration=None,censored=False,break_cause='D3',
                      samples=[dict(t=700.,gap=3.,rootless_screened=True),dict(t=720.,gap=3.,rootless_screened=True)],
                      requests=[],terminals=[],internal_route_events=[])
            o.open={0:item};o.outages=[item];o.active={0:1};o.active_served={};o.served={};o.degree={};o.steps=1
            # Use real Counter semantics required by finish.
            from collections import Counter
            o.active=Counter(o.active);o.active_served=Counter();o.served=Counter()
            o.removals=[];o.forced=[];o.decisions=[];o.growth_checks=[]
            r=o.finish();self.assertTrue(r['outages'][0]['censored']);self.assertEqual(r['maximum_outage'],100.)
            self.assertEqual(r['outages'][0]['non_repair_labels'],['N','S']);self.assertEqual(r['outages'][0]['primary_non_repair'],'X')


if __name__=='__main__': unittest.main()
