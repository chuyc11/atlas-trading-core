from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_operator_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    boundary = operator_data(paths, "operator_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["run_full_pytest"] is False
    assert boundary["operator_experience_used_as_trade_instruction"] is False
