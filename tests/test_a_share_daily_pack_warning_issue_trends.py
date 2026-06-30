from trading_core.equity_owner_daily_pack_history.warning_issue_trends import build_warning_issue_trend_baseline


def test_warning_issue_trend_does_not_fabricate_repeated_status():
    trend = build_warning_issue_trend_baseline(as_of_date="2026-06-26", records=[{}], warning_digest={"warning_issues": [{"issue_code": "x"}], "warning_count": 1}, sufficiency={"trend_analysis_available": False})
    assert trend["repeated_items"] == []
    assert trend["no_fabricated_trends"] is True


def test_warning_issue_trend_repeated_with_enough_history():
    records = [{"warning_issue_codes": ["x"]}, {"warning_issue_codes": ["x"]}, {"warning_issue_codes": []}, {}, {}]
    trend = build_warning_issue_trend_baseline(as_of_date="2026-06-26", records=records, warning_digest={"warning_issues": [], "warning_count": 0}, sufficiency={"trend_analysis_available": True})
    assert trend["repeated_items"] == ["x"]
