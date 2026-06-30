from trading_core.equity_owner_controlled_gate_reevaluation.controlled_decision import build_controlled_reevaluation_decision


def test_controlled_gate_reevaluation_decision_skipped_not_ready():
    decision = build_controlled_reevaluation_decision(skip_decision={"reevaluation_skipped": True, "reevaluation_skip_reason": "not_ready"})
    assert decision["decision"] == "skipped_not_ready"
    assert decision["gate_reevaluation_executed"] is False
    assert decision["new_gate_decision_generated"] is False

