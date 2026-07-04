from trading_core.execution.virtual_execution_engine import execute_virtual_order, settle_available_shares


def test_virtual_execution_engine_scenarios() -> None:
    state = {"cash": 100000.0, "positions": {}}
    buy, trade = execute_virtual_order({"order_id": "O1", "execution_date": "2024-01-03", "symbol": "510300.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, state, {"date": "2024-01-03", "price": 10, "status": "tradable"})
    assert buy["status"] == "filled"
    assert trade and trade["commission"] > 0
    assert state["cash"] >= 0
    same_day_sell, _ = execute_virtual_order({"order_id": "O2", "execution_date": "2024-01-03", "symbol": "510300.SH", "market": "A_SHARE", "side": "SELL", "quantity": 100}, state, {"date": "2024-01-03", "price": 10, "status": "tradable"})
    assert same_day_sell["status"] == "rejected"
    settle_available_shares(state, "2024-01-04")
    sell, sell_trade = execute_virtual_order({"order_id": "O3", "execution_date": "2024-01-04", "symbol": "510300.SH", "market": "A_SHARE", "side": "SELL", "quantity": 100}, state, {"date": "2024-01-04", "price": 10, "status": "tradable"})
    assert sell["status"] == "filled"
    assert sell_trade
    for status, side in [("suspended", "BUY"), ("limit_up", "BUY"), ("limit_down", "SELL")]:
        order, _ = execute_virtual_order({"order_id": status, "execution_date": "2024-01-04", "symbol": "510500.SH", "market": "A_SHARE", "side": side, "quantity": 100}, state, {"date": "2024-01-04", "price": 10, "status": status})
        assert order["status"] == "rejected"
        assert order["reject_reason"]
    zero_volume, _ = execute_virtual_order({"order_id": "zero-volume", "execution_date": "2024-01-04", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, state, {"date": "2024-01-04", "price": 10, "status": "tradable", "volume": 0})
    capacity, _ = execute_virtual_order({"order_id": "capacity", "execution_date": "2024-01-04", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, state, {"date": "2024-01-04", "price": 10, "status": "tradable", "volume": 500})
    price_limit, _ = execute_virtual_order({"order_id": "price-limit", "execution_date": "2024-01-04", "symbol": "510500.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, state, {"date": "2024-01-04", "price": 11, "previous_close": 10, "status": "tradable", "volume": 100000})
    assert zero_volume["reject_reason"] == "zero_volume_suspension"
    assert capacity["reject_reason"] == "volume_capacity_exceeded"
    assert price_limit["reject_reason"] == "buy_blocked_at_limit_up"
    poor_state = {"cash": 1.0, "positions": {}}
    order, _ = execute_virtual_order({"order_id": "cash", "execution_date": "2024-01-04", "symbol": "510300.SH", "market": "A_SHARE", "side": "BUY", "quantity": 100}, poor_state, {"date": "2024-01-04", "price": 10, "status": "tradable"})
    assert order["status"] == "rejected"
