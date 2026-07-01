from trading_core.equity_owner_v0820_gate_outcome.controlled_reevaluation import build_controlled_gate_reevaluation_outcome


def test_v0820_controlled_reevaluation_refuses_when_branch_not_selected_and_runs_when_selected():
    refused = build_controlled_gate_reevaluation_outcome(branch={"selected_branch": "final_blocked_closeout"}, availability={"previous_readiness_score": 54, "minimum_owner_readiness_score": 75})
    assert refused["controlled_reevaluation_executed"] is False
    assert refused["branch_not_selected"] is True
    executed = build_controlled_gate_reevaluation_outcome(branch={"selected_branch": "controlled_gate_reevaluation"}, availability={"previous_readiness_score": 80, "minimum_owner_readiness_score": 75})
    assert executed["controlled_reevaluation_executed"] is True
    assert executed["new_controlled_gate_decision"] == "owner_operationally_acceptable"

