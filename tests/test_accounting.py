from trading_core.accounting.account import Account
from trading_core.accounting.valuation import value_account
from trading_core.broker.matching_engine import match_order
from trading_core.calendar.trading_calendar import next_trading_day
import pytest


def test_account_buy_t_plus_one_and_sell() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    buy_trade = {
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "BUY",
        "date": "2026-06-23",
        "filled_quantity": 1200,
        "filled_price": 4.0,
        "net_amount": 4805.0,
    }
    account.apply_trade(buy_trade)
    position = account.positions["510300.SH"]
    assert account.cash < 100000
    assert position.quantity == 1200
    assert position.available_quantity == 0
    account.settle_t_plus_one("2026-06-24")
    assert position.available_quantity == 1200
    account.apply_trade({**buy_trade, "side": "SELL", "date": "2026-06-24", "net_amount": 4790.0})
    assert account.cash > 99900
    assert position.quantity == 0


def test_account_settlement_is_lot_dated_and_symbol_scoped() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    account.apply_trade(
        {
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "BUY",
            "date": "2026-06-23",
            "filled_quantity": 300,
            "filled_price": 4.0,
            "net_amount": 1205.0,
            "settlement_date": "2026-06-24",
        }
    )
    account.apply_trade(
        {
            "symbol": "159915.SZ",
            "market": "A_SHARE",
            "side": "BUY",
            "date": "2026-06-23",
            "filled_quantity": 500,
            "filled_price": 2.0,
            "net_amount": 1005.0,
            "settlement_date": "2026-06-25",
        }
    )

    account.settle_t_plus_one("2026-06-24")

    assert account.positions["510300.SH"].available_quantity == 300
    assert account.positions["510300.SH"].pending_t1_quantity == 0
    assert account.positions["159915.SZ"].available_quantity == 0
    assert account.positions["159915.SZ"].pending_t1_quantity == 500


def test_account_settlement_skips_non_trading_days_and_crosses_holiday(tmp_path) -> None:
    calendar = tmp_path / "a_share_calendar.csv"
    calendar.write_text(
        "date,is_trading_day\n"
        "2026-09-30,true\n"
        "2026-10-01,false\n"
        "2026-10-02,false\n"
        "2026-10-05,false\n"
        "2026-10-06,false\n"
        "2026-10-07,false\n"
        "2026-10-08,false\n"
        "2026-10-09,true\n",
        encoding="utf-8",
    )
    account = Account("CHINA_PAPER", cash=100000)
    settlement_date = next_trading_day("2026-09-30", calendar_path=calendar)
    buy_trade = match_order(
        {
            "order_id": "ORD-HOLIDAY-BUY",
            "date": "2026-09-30",
            "account_id": "CHINA_PAPER",
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "BUY",
            "quantity": 100,
            "calendar_path": str(calendar),
        },
        4.0,
        {"price": 4.0, "volume": 100000},
    )
    account.apply_trade(buy_trade)

    assert settlement_date == "2026-10-09"
    assert account.positions["510300.SH"].pending_t1_lots[0]["settlement_date"] == "2026-10-09"
    account.settle_t_plus_one("2026-10-01", calendar_path=calendar)
    assert account.positions["510300.SH"].available_quantity == 0
    account.settle_t_plus_one("2026-10-09", calendar_path=calendar)
    assert account.positions["510300.SH"].available_quantity == 100
    assert account.positions["510300.SH"].pending_t1_quantity == 0


def test_account_settlement_requires_explicit_date() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    account.apply_trade(
        {
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "BUY",
            "date": "2026-06-23",
            "filled_quantity": 100,
            "filled_price": 4.0,
            "net_amount": 405.0,
            "settlement_date": "2026-06-24",
        }
    )

    with pytest.raises(ValueError, match="settlement_date_required"):
        account.settle_t_plus_one()

    position = account.positions["510300.SH"]
    assert position.available_quantity == 0
    assert position.pending_t1_quantity == 100


def test_account_apply_trade_rejects_direct_oversell_bypass() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    account.apply_trade(
        {
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "BUY",
            "date": "2026-06-23",
            "filled_quantity": 100,
            "filled_price": 4.0,
            "net_amount": 405.0,
            "settlement_date": "2026-06-24",
        }
    )

    with pytest.raises(ValueError, match="sell_trade_exceeds_available_quantity"):
        account.apply_trade(
            {
                "symbol": "510300.SH",
                "market": "A_SHARE",
                "side": "SELL",
                "date": "2026-06-23",
                "filled_quantity": 100,
                "filled_price": 4.0,
                "net_amount": 395.0,
            }
        )

    position = account.positions["510300.SH"]
    assert position.quantity == 100
    assert position.available_quantity == 0
    assert position.pending_t1_quantity == 100


def test_account_partial_sell_updates_available_cash_commission_and_tax() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    buy_trade = match_order(
        {
            "order_id": "ORD-BUY",
            "date": "2026-06-23",
            "account_id": "CHINA_PAPER",
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "BUY",
            "quantity": 1200,
        },
        4.0,
        {"price": 4.0, "volume": 100000},
    )
    account.apply_trade(buy_trade)
    account.settle_t_plus_one("2026-06-24")
    cash_after_buy = account.cash

    sell_trade = match_order(
        {
            "order_id": "ORD-SELL",
            "date": "2026-06-24",
            "account_id": "CHINA_PAPER",
            "symbol": "510300.SH",
            "market": "A_SHARE",
            "side": "SELL",
            "quantity": 500,
        },
        4.2,
        {"price": 4.2, "volume": 100000},
    )
    account.apply_trade(sell_trade)
    position = account.positions["510300.SH"]

    assert sell_trade["commission"] == 5.0
    assert sell_trade["tax"] > 0
    assert account.cash == round(cash_after_buy + sell_trade["net_amount"], 6)
    assert position.quantity == 700
    assert position.available_quantity == 700
    assert position.pending_t1_quantity == 0


def test_valuation_marks_prices() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    valuation = value_account(account, "2026-06-23", {}, 100000)
    assert valuation["total_asset"] == 100000
