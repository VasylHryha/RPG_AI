"""Offline analysis contracts. Fixtures contain no worlds, policies or entropy."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from evidence.tactical_composition_demo.growing_shapes.runner import recheck_development as audit


class RecheckContracts(unittest.TestCase):
    def test_strict_reach_and_empty_distinct_from_cancellation(self):
        self.assertEqual(audit.geometry([[2., 0., 0., 3., 1.]])['readout_weight'], 0.)
        self.assertEqual(audit.geometry([[1.999, 0., 0., 3., 1.]])['copy_time_coherence'], 1.)
        value = audit.geometry([[1., 0., 0., 3., 1.], [-1., 0., audit.math.pi, 3., 1.]])
        self.assertGreater(value['readout_weight'], 0.)
        self.assertTrue(value['copy_time_abstain'])

    def test_drive_reach_is_strict_and_not_readout_reach(self):
        value = audit.geometry([[4., 0., 0., 3., 1.]])
        self.assertEqual(value['potential_driven_members'], 1)
        self.assertEqual(value['readout_members'], 0)
        self.assertEqual(audit.geometry([[100., 0., 0., 3., 1.]])['potential_driven_members'], 0)

    def test_floor_and_random_are_separate_comparisons(self):
        value = audit.score_summary([-.1, 0., .1, .2, .3], .2)
        self.assertEqual(value['above_floor'], 1)
        self.assertEqual(value['equal_floor'], 1)
        self.assertEqual(value['above_calibrated_random'], 3)
        self.assertEqual(value['above_both'], 1)
        self.assertEqual(audit.score_summary([-.05], -.1)['above_both'], 0)

    def test_nonfinite_and_empty_samples_refused(self):
        for value in ([], [float('nan')], [float('inf')]):
            with self.assertRaises(ValueError):
                audit.score_summary(value, 0.)
        with self.assertRaises(ValueError):
            audit.geometry([[0., 0., float('nan'), 3., 1.]])

    def test_ledger_hashes_and_selected_events(self):
        rows = [dict(time=25600., rule='B1_rejected', ids=[], values={'reason': 'cost'}, cost=64.),
                dict(time=20., rule='B1', ids=[24], values={'site': 2}, cost=24.),
                dict(time=40., rule='control_drop', ids=[], values={'reason': 'terminal'}, cost=64.)]
        raw = b''.join(json.dumps(r, separators=(',', ':')).encode() + b'\n' for r in rows)
        root = audit.HERE / '_build'
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='offline-recheck-test-', dir=root) as directory:
            path = Path(directory) / 'events.jsonl.gz'
            path.write_bytes(gzip.compress(raw))
            receipt = dict(retained_path='fixture/events.jsonl.gz', archive_bytes=path.stat().st_size,
                archive_sha256=audit.sha(path), decoded_bytes=len(raw), records=3,
                decoded_sha256=hashlib.sha256(raw).hexdigest())
            value = audit.audit_ledger(path, receipt)
            self.assertEqual(value['late_rejection_reasons'], {'cost': 1})
            self.assertEqual(value['drop_reasons'], {'terminal': 1})
            self.assertEqual(value['birth_sites'], {'2': 1})
            for key, replacement in [('decoded_sha256', '0' * 64), ('records', 2), ('decoded_bytes', 0),
                                     ('archive_sha256', '0' * 64)]:
                with self.assertRaises(ValueError):
                    audit.audit_ledger(path, dict(receipt, **{key: replacement}))

    def test_artifact_identity_changes_with_content(self):
        first = {'members': [[1., 0., 0., 3., 1.]], 'constants_version': 'fixture'}
        second = dict(first, members=[[1., 0., .1, 3., 1.]])
        self.assertNotEqual(audit.content_hash(first), audit.content_hash(second))


if __name__ == '__main__':
    unittest.main()
