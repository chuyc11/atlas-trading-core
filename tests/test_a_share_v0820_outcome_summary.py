from trading_core.equity_owner_v0820_gate_outcome.outcome_summary import build_owner_outcome_summary


def test_v0820_outcome_summary_records_closeout_truth():
    summary = build_owner_outcome_summary(
        branch={"selected_branch": "final_blocked_closeout", "controlled_reevaluation_allowed": False},
        controlled={"controlled_reevaluation_executed": False, "new_controlled_readiness_score_generated": False, "new_controlled_gate_decision_generated": False, "owner_operationally_acceptable": False},
        closeout={"final_blocked_closeout_generated": True},
        availability={"source_gate_decision": "blocked", "previous_readiness_score": 54, "minimum_owner_readiness_score": 75},
    )
    assert summary["selected_branch"] == "final_blocked_closeout"
    assert summary["final_blocked_closeout_generated"] is True
    assert summary["new_controlled_gate_decision_generated"] is False

