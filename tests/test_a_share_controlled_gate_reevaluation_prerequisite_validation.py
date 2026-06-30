from trading_core.equity_owner_controlled_gate_reevaluation.prerequisite_validation import build_reevaluation_prerequisite_validation


def test_controlled_gate_reevaluation_prerequisite_validation_records_skip_action():
    validation = build_reevaluation_prerequisite_validation(guard={"reevaluation_allowed": False, "readiness_guard_passed": False, "block_reasons": ["source_readiness_not_ready"]})
    assert validation["reevaluation_prerequisites_met"] is False
    assert validation["required_action"] == "record_skip_decision"
    assert validation["gate_reevaluation_executed"] is False

