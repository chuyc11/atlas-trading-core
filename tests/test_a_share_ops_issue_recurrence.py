from trading_core.equity_ops_history.issue_recurrence import build_ops_issue_recurrence_baseline


def test_ops_issue_recurrence_preserves_known_non_blocking():
    baseline = build_ops_issue_recurrence_baseline(as_of_date="2026-06-26", issue_summary={"remediation_issues": [{"issue_code": "I1", "known_non_blocking": True}]}, records=[{}], minimum_required_observations=5)
    assert baseline["items"][0]["recurrence_status"] == "known_non_blocking"

