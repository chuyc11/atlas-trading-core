from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    boundary = recovery_data(paths, "recovery_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["recovery_plan_used_as_trade_instruction"] is False
