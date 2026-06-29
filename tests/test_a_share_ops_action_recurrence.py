from trading_core.equity_ops_history.action_recurrence import build_ops_action_recurrence_baseline


def test_ops_action_recurrence_is_manual_and_not_trade_related():
    baseline = build_ops_action_recurrence_baseline(as_of_date="2026-06-26", action_checklist={"top_owner_actions": ["检查 warning"]}, records=[{}])
    item = baseline["items"][0]
    assert item["automatic_action_allowed"] is False
    assert item["trade_related"] is False
    assert item["broker_related"] is False
    assert item["order_related"] is False

