from trading_core.equity_owner_evidence_backed_reevaluation_prep.eligibility_decision import build_controlled_reevaluation_eligibility_decision


def test_controlled_reevaluation_eligibility_decision_not_eligible_when_gap_blocks():
    decision = build_controlled_reevaluation_eligibility_decision(
        sufficiency={"ready_for_controlled_gate_reevaluation": True, "blocking_reasons": []},
        gap_decision={"blocks_controlled_gate_reevaluation": True},
    )
    assert decision["ready_for_controlled_gate_reevaluation"] is False
    assert decision["eligibility_decision"] == "not_eligible"
    assert decision["reevaluation_executed"] is False

