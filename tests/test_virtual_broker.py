from trading_core.accounting.account import Account
from trading_core.broker.matching_engine import match_order
from trading_core.broker.virtual_broker import process_signals, signal_to_order


def test_virtual_broker_creates_order_trade_and_updates_account() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    signal = {
        "signal_id": "S1",
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "LONG",
        "target_weight": 0.05,
    }
    price = {"price": 4.0, "quality": "fresh"}
    order = signal_to_order(signal, "2026-06-23", account, price)
    assert order["quantity"] == 1200
    orders, trades = process_signals([signal], "2026-06-23", account, {"510300.SH": price})
    assert orders[0]["status"] == "submitted"
    assert trades[0]["status"] == "filled"
    assert account.positions["510300.SH"].quantity == 1200


def test_virtual_broker_rejects_suspended_limit_and_capacity_constrained_orders() -> None:
    signal = {
        "signal_id": "S1",
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "LONG",
        "target_weight": 0.05,
    }

    suspended = signal_to_order(signal, "2026-06-23", Account("CHINA_PAPER", cash=100000), {"price": 4.0, "quality": "fresh", "is_suspended": True})
    assert suspended["status"] == "rejected"
    assert suspended["risk_reason_code"] == "security_suspended"

    limit_up = signal_to_order(signal, "2026-06-23", Account("CHINA_PAPER", cash=100000), {"price": 4.4, "previous_close": 4.0, "quality": "fresh"})
    assert limit_up["status"] == "rejected"
    assert limit_up["risk_reason_code"] == "buy_blocked_at_limit_up"

    capacity = signal_to_order(signal, "2026-06-23", Account("CHINA_PAPER", cash=100000), {"price": 4.0, "quality": "fresh", "volume": 500})
    assert capacity["status"] == "rejected"
    assert capacity["risk_reason_code"] == "volume_capacity_exceeded"


def test_virtual_broker_capacity_is_cumulative_for_same_symbol_same_day() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    base_signal = {
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "LONG",
        "target_weight": 0.005,
    }
    price = {"price": 4.0, "quality": "fresh", "volume": 1500}

    orders, trades = process_signals(
        [
            {**base_signal, "signal_id": "BUY1"},
            {**base_signal, "signal_id": "BUY2"},
        ],
        "2026-06-23",
        account,
        {"510300.SH": price},
    )

    assert orders[0]["status"] == "submitted"
    assert trades[0]["filled_quantity"] == 100
    assert orders[1]["status"] == "rejected"
    assert orders[1]["risk_reason_code"] == "volume_capacity_exceeded"
    assert len(trades) == 1


def test_t_plus_one_blocks_same_day_sell_then_allows_after_settlement() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    buy_signal = {
        "signal_id": "BUY1",
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "LONG",
        "target_weight": 0.05,
    }
    sell_signal = {**buy_signal, "signal_id": "SELL1", "side": "SELL"}
    price = {"price": 4.0, "quality": "fresh", "volume": 100000}

    _, buy_trades = process_signals([buy_signal], "2026-06-23", account, {"510300.SH": price})
    assert account.positions["510300.SH"].pending_t1_quantity == 1200
    assert account.positions["510300.SH"].available_quantity == 0
    same_day_orders, same_day_trades = process_signals([sell_signal], "2026-06-23", account, {"510300.SH": price})
    account.settle_t_plus_one("2026-06-24")
    settled_orders, settled_trades = process_signals([sell_signal], "2026-06-24", account, {"510300.SH": price})

    assert buy_trades[0]["side"] == "BUY"
    assert same_day_orders[0]["status"] == "rejected"
    assert same_day_orders[0]["risk_reason_code"] == "sell_quantity_exceeds_available_position"
    assert same_day_trades == []
    assert settled_orders[0]["status"] == "submitted"
    assert settled_trades[0]["side"] == "SELL"


def test_sell_quantity_over_available_is_rejected() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    buy_signal = {
        "signal_id": "BUY1",
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "LONG",
        "target_weight": 0.05,
    }
    sell_signal = {**buy_signal, "signal_id": "SELL2", "side": "SELL", "target_weight": 0.10}
    price = {"price": 4.0, "quality": "fresh", "volume": 100000}

    process_signals([buy_signal], "2026-06-23", account, {"510300.SH": price})
    account.settle_t_plus_one("2026-06-24")
    orders, trades = process_signals([sell_signal], "2026-06-24", account, {"510300.SH": price})

    assert orders[0]["status"] == "rejected"
    assert orders[0]["risk_reason_code"] == "sell_quantity_exceeds_available_position"
    assert trades == []
    assert account.positions["510300.SH"].quantity == 1200
    assert account.positions["510300.SH"].available_quantity == 1200


def test_matching_engine_rejects_a_share_market_constraint_bypass() -> None:
    order = {
        "order_id": "ORD-BYPASS",
        "date": "2026-06-23",
        "account_id": "CHINA_PAPER",
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "BUY",
        "quantity": 100,
    }

    missing_row = match_order(order, 4.0)
    suspended = match_order(order, 4.0, {"price": 4.0, "is_suspended": True})
    zero_volume = match_order(order, 4.0, {"price": 4.0, "volume": 0})
    limit_up = match_order(order, 4.4, {"price": 4.4, "previous_close": 4.0, "volume": 100000})

    assert missing_row["status"] == "rejected"
    assert missing_row["risk_reason_code"] == "missing_market_constraints"
    assert suspended["risk_reason_code"] == "security_suspended"
    assert zero_volume["risk_reason_code"] == "zero_volume_suspension"
    assert limit_up["risk_reason_code"] == "buy_blocked_at_limit_up"
