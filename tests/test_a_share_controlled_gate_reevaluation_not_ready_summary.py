from trading_core.equity_owner_controlled_gate_reevaluation.not_ready_summary import build_not_ready_reason_summary


def test_controlled_gate_reevaluation_not_ready_summary_counts_reasons():
    summary = build_not_ready_reason_summary(guard={"block_reasons": ["a", "b"], "evidence_available_count": 0, "verified_by_audit_only_count": 0, "completed_count": 0})
    assert summary["not_ready"] is True
    assert summary["reason_count"] == 2
    assert summary["recommended_follow_up"] == "collect_real_recovery_evidence_before_any_future_gate_reevaluation"

