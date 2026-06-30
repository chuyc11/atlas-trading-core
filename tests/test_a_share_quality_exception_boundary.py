from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    boundary = exception_data(paths, "quality_exception_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["quality_exception_used_as_trade_instruction"] is False
    assert boundary["broker_connected"] is False
