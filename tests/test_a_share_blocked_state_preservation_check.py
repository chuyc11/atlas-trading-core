from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_blocked_state_preservation_check_preserves_blocked_decision(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    check = recovery_data(paths, "blocked_state_preservation_check.json")
    assert check["source_gate_decision"] == "blocked"
    assert check["blocked_gate_decision_preserved"] is True
    assert check["recovery_plan_changes_gate_decision"] is False
