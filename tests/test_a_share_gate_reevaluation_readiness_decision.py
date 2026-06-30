from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_gate_reevaluation_readiness_decision_defaults_not_ready(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    decision = execution_data(paths, "gate_reevaluation_readiness_decision.json")
    assert decision["gate_reevaluation_readiness_decision"] == "not_ready"
    assert decision["ready_for_future_gate_reevaluation"] is False
    assert decision["gate_reevaluation_executed"] is False
