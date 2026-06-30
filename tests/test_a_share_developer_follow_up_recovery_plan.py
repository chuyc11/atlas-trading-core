from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_developer_follow_up_recovery_plan_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    plan = recovery_data(paths, "developer_follow_up_recovery_plan.json")
    assert plan["follow_up_count"] == 1
    assert plan["items"][0]["status"] == "planned"
    assert plan["items"][0]["safe_audit_only_commands"]
