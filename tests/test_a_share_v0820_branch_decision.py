from trading_core.equity_owner_v0820_gate_outcome.branch_decision import build_branch_decision


def _availability(**updates):
    payload = {
        "source_gate_decision": "blocked",
        "source_gate_decision_preserved": True,
        "v0819_ready_for_controlled_gate_reevaluation": True,
        "v0819_eligibility_decision": "eligible",
        "reevaluation_input_package_generated": True,
        "remaining_gap_count": 0,
        "blocking_gap_count": 0,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
    }
    payload.update(updates)
    return payload


def test_v0820_branch_decision_selects_controlled_or_closeout():
    controlled = build_branch_decision(availability=_availability())
    assert controlled["selected_branch"] == "controlled_gate_reevaluation"
    blocked = build_branch_decision(availability=_availability(v0819_ready_for_controlled_gate_reevaluation=False, v0819_eligibility_decision="not_eligible", blocking_gap_count=5))
    assert blocked["selected_branch"] == "final_blocked_closeout"
    assert blocked["final_blocked_closeout_required"] is True

