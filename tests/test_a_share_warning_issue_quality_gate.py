from trading_core.equity_owner_readiness_gate.quality_gates import build_warning_issue_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_warning_issue_quality_gate_blocks_blockers():
    policy = build_owner_readiness_threshold_policy()
    gate = build_warning_issue_quality_gate(warning={"warning_count": 3, "blocking_count": 0}, policy=policy)
    assert gate["passed"] is True
    assert "warning_issue_items_present" in gate["warnings"]
    failed = build_warning_issue_quality_gate(warning={"warning_count": 1, "blocking_count": 1}, policy=policy)
    assert failed["passed"] is False
