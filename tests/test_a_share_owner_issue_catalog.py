from trading_core.equity_owner_remediation.issue_catalog import build_issue_catalog


def test_issue_catalog_generates_warnings_and_unknowns():
    catalog = build_issue_catalog(
        as_of_date="2026-06-26",
        payloads={"warning_trend_snapshot": {"current_warning_codes": ["daily_basic:required_field_all_null", "new_unknown"]}},
    )
    codes = {issue["issue_code"]: issue for issue in catalog["issues"]}
    assert codes["daily_basic:required_field_all_null"]["known_non_blocking"] is True
    assert codes["new_unknown"]["explicitly_classified_unknown"] is True
