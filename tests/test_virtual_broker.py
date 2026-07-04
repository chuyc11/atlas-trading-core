from trading_core.accounting.account import Account
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
