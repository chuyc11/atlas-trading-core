from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_execution_preservation_checks(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    blocked = execution_data(paths, "blocked_state_preservation_check.json")
    threshold = execution_data(paths, "threshold_preservation_check.json")
    waiver = execution_data(paths, "waiver_preservation_check.json")
    assert blocked["source_gate_decision"] == "blocked"
    assert blocked["gate_reevaluation_executed"] is False
    assert threshold["threshold_lowered"] is False
    assert waiver["auto_waiver_allowed"] is False
    assert waiver["manual_waiver_approval_recorded"] is False
