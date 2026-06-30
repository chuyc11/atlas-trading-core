from trading_core.equity_owner_daily_pack_history.boundary_trends import build_boundary_trend_baseline


def test_boundary_trend_clean():
    trend = build_boundary_trend_baseline(as_of_date="2026-06-26", records=[{"boundary_clean": True}], boundary_check={"overall_passed": True, "blocking_reasons": []})
    assert trend["boundary_trend_clean"] is True
