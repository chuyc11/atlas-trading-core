from trading_core.equity_owner_remediation.priority_summary import build_remediation_priority_summary


def test_priority_summary_buckets():
    catalog = {
        "issue_count": 4,
        "issues": [
            {"issue_code": "BOUNDARY_VIOLATION", "blocking": True, "category": "boundary_issue", "severity": "critical"},
            {"issue_code": "PROVIDER_HEALTH_DEGRADED", "blocking": False, "category": "provider_issue", "severity": "warning"},
            {"issue_code": "known", "blocking": False, "category": "known_non_blocking_issue", "severity": "known_non_blocking", "known_non_blocking": True},
            {"issue_code": "insufficient_history_for_trends", "blocking": False, "category": "insufficient_history_issue", "severity": "known_non_blocking"},
        ],
    }
    summary = build_remediation_priority_summary(as_of_date="2026-06-26", issue_catalog=catalog)
    assert summary["blocking_issue_count"] == 1
    assert summary["warning_issue_count"] == 1
    assert summary["known_non_blocking_issue_count"] == 1
    assert summary["wait_for_history_issue_count"] == 1
