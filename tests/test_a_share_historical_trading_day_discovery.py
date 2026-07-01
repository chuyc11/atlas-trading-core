from tests.a_share_historical_backfill_test_utils import LOOKBACK_START, build_v097, historical_json, seed_v096_with_historical_inputs


def test_historical_trading_day_discovery_uses_bounded_lookback_and_excludes_weekends(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    build_v097(paths, monkeypatch)

    discovery = historical_json(paths, "historical_trading_day_discovery")

    assert discovery["historical_lookback_start"] == LOOKBACK_START
    assert discovery["lookback_before_2026_06_26_executed"] is True
    assert "2026-06-20" in discovery["non_trading_days"]
    assert "2026-06-21" in discovery["non_trading_days"]
    assert "2026-06-25" in discovery["candidate_backfill_days"]
    assert discovery["existing_eligible_days"] == ["2026-06-26", "2026-07-01"]
    assert discovery["discovery_passed"] is True
