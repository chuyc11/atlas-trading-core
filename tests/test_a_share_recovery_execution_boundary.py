from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_execution_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    boundary = execution_data(paths, "recovery_execution_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["recovery_execution_used_as_trade_instruction"] is False
