from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    boundary = v090_data(paths, "v090_boundary_check.json")
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["v090_rc_used_as_trade_instruction"] is False
