from trading_core.equity_owner_remediation.dashboard_guide import build_dashboard_remediation_guide


def test_dashboard_guide_generated():
    guide = build_dashboard_remediation_guide("2026-06-26")
    assert "dashboard_issue" in guide["applicable_issue_categories"]
    assert guide["safe_cli_checks"]
