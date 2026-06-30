from trading_core.equity_owner_daily_pack_history.owner_next_step_trends import build_owner_next_step_trend


def test_owner_next_step_trend_excludes_trade_decisions():
    trend = build_owner_next_step_trend(as_of_date="2026-06-26", records=[], checklist={"do_now": ["connect broker"], "review_today": ["check audit"]})
    assert trend["owner_next_steps_trade_instruction_free"] is False
    assert trend["blocked_trade_like_steps"] == ["connect broker"]
