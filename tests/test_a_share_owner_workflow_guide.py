from trading_core.equity_owner_remediation.workflow_guide import build_workflow_remediation_guide


def test_workflow_guide_generated():
    guide = build_workflow_remediation_guide("2026-06-26")
    assert "workflow_issue" in guide["applicable_issue_categories"]
    assert any("current-day" in step for step in guide["safe_diagnostic_steps"])
