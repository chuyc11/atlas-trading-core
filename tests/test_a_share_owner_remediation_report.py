from trading_core.equity_owner_remediation.remediation_report import render_data_guide, render_runbook, render_safe_action_checklist, render_workflow_guide


def test_remediation_reports_generated():
    payload = {
        "remediation_summary": {"as_of_date": "2026-06-26", "issue_count": 0, "automatic_action_count": 0},
        "remediation_priority_summary": {"priority_buckets": {}},
        "issue_catalog": {"issues": []},
        "safe_owner_action_checklist": {"items": []},
    }
    assert "今日修复总览" in render_runbook(payload)
    assert "Safe Action Checklist" in render_safe_action_checklist(payload)
    assert "data freshness issue handling" in render_data_guide(payload)
    assert "current-day run failure handling" in render_workflow_guide(payload)
