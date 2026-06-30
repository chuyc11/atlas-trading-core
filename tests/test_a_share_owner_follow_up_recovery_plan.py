from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_owner_follow_up_recovery_plan_excludes_trading_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    plan = recovery_data(paths, "owner_follow_up_recovery_plan.json")
    assert plan["owner_follow_up_count"] > 0
    assert all(item["trade_related"] is False for item in plan["items"])
    assert all(item["broker_related"] is False for item in plan["items"])
    assert all(item["order_related"] is False for item in plan["items"])
