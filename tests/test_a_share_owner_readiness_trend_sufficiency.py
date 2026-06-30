from trading_core.equity_owner_daily_pack_history.trend_sufficiency import build_trend_sufficiency


def test_owner_readiness_trend_sufficiency_insufficient_history():
    suff = build_trend_sufficiency(as_of_date="2026-06-26", observation_count=1, minimum_required_observations=5, baseline_window_observations=20)
    assert suff["trend_analysis_available"] is False
    assert suff["readiness_trend_status"] == "insufficient_history"


def test_owner_readiness_trend_sufficiency_enough_history():
    suff = build_trend_sufficiency(as_of_date="2026-06-26", observation_count=5, minimum_required_observations=5, baseline_window_observations=20)
    assert suff["trend_analysis_available"] is True
    assert suff["readiness_trend_status"] == "available"
