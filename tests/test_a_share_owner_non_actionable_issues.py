from trading_core.equity_owner_remediation.non_actionable_issues import build_non_actionable_issue_list


def test_non_actionable_insufficient_history_issue_generated():
    result = build_non_actionable_issue_list(
        as_of_date="2026-06-26",
        payloads={"run_history_snapshot": {"run_history_observation_count": 1, "minimum_history_observations": 3}},
        issue_catalog={"issues": []},
    )
    assert any(item["issue_code"] == "insufficient_history_for_trends" for item in result["items"])
