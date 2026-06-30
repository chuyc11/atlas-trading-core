from trading_core.equity_owner_daily_pack_history.safe_action_trends import build_safe_action_trend_baseline


def test_safe_action_trend_rejects_trade_action():
    trend = build_safe_action_trend_baseline(as_of_date="2026-06-26", records=[], safe_action_digest={"items": [{"safe_action_type": "place_order"}]}, sufficiency={"trend_analysis_available": False})
    assert trend["safe_actions_not_trade_related"] is False
    assert trend["forbidden_safe_action_hits"]
