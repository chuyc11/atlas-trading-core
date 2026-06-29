from trading_core.equity_owner_remediation.monitoring_guide import build_monitoring_remediation_guide


def test_monitoring_guide_generated():
    guide = build_monitoring_remediation_guide("2026-06-26")
    assert "monitoring_issue" in guide["applicable_issue_categories"]
    assert "insufficient_history_issue" in guide["applicable_issue_categories"]
