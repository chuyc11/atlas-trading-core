from trading_core.accounting.account import Account
from trading_core.accounting.valuation import value_account


def test_account_buy_t_plus_one_and_sell() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    buy_trade = {
        "symbol": "510300.SH",
        "market": "A_SHARE",
        "side": "BUY",
        "filled_quantity": 1200,
        "filled_price": 4.0,
        "net_amount": 4805.0,
    }
    account.apply_trade(buy_trade)
    position = account.positions["510300.SH"]
    assert account.cash < 100000
    assert position.quantity == 1200
    assert position.available_quantity == 0
    account.settle_t_plus_one()
    assert position.available_quantity == 1200
    account.apply_trade({**buy_trade, "side": "SELL", "net_amount": 4790.0})
    assert account.cash > 99900
    assert position.quantity == 0


def test_valuation_marks_prices() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    valuation = value_account(account, "2026-06-23", {}, 100000)
    assert valuation["total_asset"] == 100000
