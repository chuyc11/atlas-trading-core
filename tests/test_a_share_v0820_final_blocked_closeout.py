from trading_core.equity_owner_v0820_gate_outcome.final_blocked_closeout import build_final_blocked_closeout


def test_v0820_final_blocked_closeout_generated_when_not_eligible():
    closeout = build_final_blocked_closeout(
        branch={"selected_branch": "final_blocked_closeout"},
        availability={"source_gate_decision": "blocked", "previous_readiness_score": 54, "minimum_owner_readiness_score": 75, "remaining_gap_count": 5, "blocking_gap_count": 5},
    )
    assert closeout["final_blocked_closeout_generated"] is True
    assert closeout["controlled_reevaluation_executed"] is False
    assert closeout["new_controlled_gate_decision_generated"] is False

