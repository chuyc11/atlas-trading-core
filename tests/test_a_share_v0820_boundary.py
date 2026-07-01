from tests.a_share_v0820_test_utils import make_paths, seed_v0820_outputs, v0820_data


def test_v0820_boundary_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_outputs(paths)
    boundary = v0820_data(paths, "v0820_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["old_run_daily_called"] is False
    assert boundary["v0820_outcome_used_as_trade_instruction"] is False

