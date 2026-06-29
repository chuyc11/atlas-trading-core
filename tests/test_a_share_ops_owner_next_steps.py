from trading_core.equity_ops_center.owner_next_steps import build_ops_owner_next_steps


def test_ops_owner_next_steps_exclude_trade_actions():
    steps = build_ops_owner_next_steps(as_of_date="2026-06-26", health_score={"blocking_issue_count": 0}, action_summary={"top_owner_actions": ["检查 audit"], "wait_for_history_count": 1})
    text = " ".join(str(value) for value in steps.values()).lower()
    assert "buy" not in text
    assert "sell" not in text
    assert "connect broker" not in text
