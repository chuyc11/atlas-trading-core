from trading_core.equity_owner_controlled_gate_reevaluation.skip_decision import build_reevaluation_skip_decision


def test_controlled_gate_reevaluation_skip_decision_not_ready():
    skip = build_reevaluation_skip_decision(guard={"reevaluation_allowed": False, "block_reasons": ["x"]}, execution_plan={"execution_status": "not_executed"})
    assert skip["reevaluation_skipped"] is True
    assert skip["reevaluation_skip_reason"] == "not_ready"
    assert skip["owner_operationally_acceptable"] is False
    assert skip["new_gate_score_generated"] is False

