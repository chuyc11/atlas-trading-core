from trading_core.equity_ops_history.warning_recurrence import build_ops_warning_recurrence_baseline


def test_ops_warning_recurrence_is_new_not_repeated_with_one_observation():
    baseline = build_ops_warning_recurrence_baseline(as_of_date="2026-06-26", issue_summary={"warning_issues": [{"issue_code": "W1"}]}, records=[{}], minimum_required_observations=5)
    assert baseline["items"][0]["recurrence_status"] == "new"

