from trading_core.equity_owner_evidence_backed_reevaluation_prep.next_execution_plan import build_next_gate_reevaluation_execution_plan


def test_next_gate_reevaluation_execution_plan_branches_without_executing():
    blocked = build_next_gate_reevaluation_execution_plan(eligibility={"ready_for_controlled_gate_reevaluation": False, "blocking_reasons": ["missing"]})
    assert blocked["next_action"] == "final_blocked_closeout_or_further_evidence_collection"
    assert blocked["reevaluation_executed"] is False
    ready = build_next_gate_reevaluation_execution_plan(eligibility={"ready_for_controlled_gate_reevaluation": True, "blocking_reasons": []})
    assert ready["next_action"] == "execute_controlled_gate_reevaluation"
    assert ready["v0_8_19_executes_gate"] is False

