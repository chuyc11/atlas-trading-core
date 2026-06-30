from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_quality_improvement_target_policy_does_not_lower_threshold(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    policy = recovery_data(paths, "quality_improvement_target_policy.json")
    assert policy["target_owner_readiness_score"] >= 75
    assert policy["does_not_lower_v0813_gates"] is True
    assert policy["requires_broker_connection"] is False
