from trading_core.equity_ops_center.issue_summary import build_ops_issue_summary


def test_ops_issue_summary_carries_remediation_counts():
    summary = build_ops_issue_summary(
        as_of_date="2026-06-26",
        payloads={"remediation_manifest": {"issue_count": 17, "blocking_issue_count": 0, "warning_issue_count": 10, "known_non_blocking_issue_count": 5}, "issue_catalog": {"issues": []}},
    )
    assert summary["issue_count"] == 17
    assert summary["warning_issue_count"] == 10
    assert summary["known_non_blocking_issue_count"] == 5
