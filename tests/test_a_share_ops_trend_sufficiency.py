from trading_core.equity_ops_history.trend_sufficiency import build_ops_trend_sufficiency


def test_ops_trend_sufficiency_does_not_fabricate_history():
    result = build_ops_trend_sufficiency("2026-06-26", 1, 5, 20)
    assert result["trend_analysis_available"] is False
    assert result["baseline_status"] == "insufficient_history"
    assert result["synthetic_history_used"] is False
    assert result["future_dates_used"] is False

