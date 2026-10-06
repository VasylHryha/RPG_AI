"""False-positive guards for the partial-development reconstruction."""
import pytest
from s4_v4_partial_audit import require_complete_orientations, require_tuning_shape, endpoint_coverage


def test_missing_orientation_cannot_count_as_complete():
    require_complete_orientations({'candidate': {'battle': {False, True}}})
    with pytest.raises(ValueError, match='missing orientation'):
        require_complete_orientations({'candidate': {'battle': {False}}})


def test_incomplete_generations_do_not_satisfy_full_arm_budget():
    require_tuning_shape('C', 'pushpull', 13)
    for stage, arm, count in [('A', 'pushpull', 13), ('C', 'morale', 13), ('C', 'pushpull', 16)]:
        with pytest.raises(ValueError, match='generation count'):
            require_tuning_shape(stage, arm, count)


def test_completed_tuning_cannot_imply_c_validation():
    rows=endpoint_coverage()
    assert all(v['status']=='not_run' and v['reason'] for k,v in rows.items() if k.startswith('C|'))
    assert all(v['status']=='evaluated' and v['clusters']==100 for k,v in rows.items() if not k.startswith('C|'))
