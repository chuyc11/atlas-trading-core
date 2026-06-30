from trading_core.equity_owner_controlled_gate_reevaluation.readiness_guard import build_reevaluation_readiness_guard


def test_controlled_gate_reevaluation_readiness_guard_blocks_not_ready():
    guard = build_reevaluation_readiness_guard(
        source_summary={"source_gate_decision": "blocked", "blocked_gate_decision_preserved": True},
        status_tracker={"task_count": 3, "completed_count": 0, "verified_by_audit_only_count": 0},
        evidence_registry={"evidence_available_count": 0},
        readiness_decision={"ready_for_future_gate_reevaluation": False},
        threshold={"threshold_lowered": False},
        waiver={"auto_waiver_allowed": False, "manual_waiver_approval_recorded": False},
    )
    assert guard["readiness_guard_passed"] is False
    assert guard["reevaluation_allowed"] is False
    assert "no_recovery_evidence_available" in guard["block_reasons"]
    assert guard["gate_reevaluation_executed"] is False

