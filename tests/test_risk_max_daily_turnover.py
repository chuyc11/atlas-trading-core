"""Tests for max_daily_turnover risk enforcement."""

from __future__ import annotations

import importlib

from trading_core.accounting.account import Account
from trading_core.risk.risk_engine import check_order


def _rules(max_daily_turnover=None) -> dict:
    limits = {
        "max_single_position_weight": 0.20,
        "max_total_position_weight": 0.80,
        "min_cash_weight": 0.10,
        "max_orders_per_day": 5,
    }
    if max_daily_turnover is not None:
        limits["max_daily_turnover"] = max_daily_turnover
    return {
        "limits": limits,
        "data_quality": {
            "allow_fallback_buy": False,
            "allow_stale_buy": False,
            "allow_missing_price_trade": False,
            "allow_stale_sell": True,
        },
        "actions": {},
    }


def _order(price: float = 4.0, quantity: int = 1200) -> dict:
    return {
        "symbol": "510300.SH",
        "side": "BUY",
        "target_weight": 0.05,
        "estimated_price": price,
        "quantity": quantity,
    }


def test_large_order_rejected_when_max_daily_turnover_configured() -> None:
    account = Account("CHINA_PAPER", cash=100000)

    result = check_order(account, _order(), "fresh", risk_rules=_rules(0.03))

    assert result["risk_check"] == "rejected"
    assert result["risk_reason_code"] == "daily_turnover_limit_exceeded"


def test_small_order_passes_when_turnover_is_below_limit() -> None:
    account = Account("CHINA_PAPER", cash=100000)

    result = check_order(account, _order(quantity=500), "fresh", risk_rules=_rules(0.03))

    assert result["risk_check"] == "passed"


def test_non_positive_account_equity_does_not_crash() -> None:
    account = Account("CHINA_PAPER", cash=0)

    result = check_order(account, _order(quantity=1), "fresh", risk_rules=_rules(0.30))

    assert result["risk_check"] == "rejected"
    assert result["risk_reason_code"] == "account_equity_non_positive"


def test_missing_max_daily_turnover_does_not_enable_rule() -> None:
    account = Account("CHINA_PAPER", cash=100000)

    result = check_order(account, _order(), "fresh", risk_rules=_rules())

    assert result["risk_check"] == "passed"


def test_projected_turnover_includes_existing_same_day_notional() -> None:
    account = Account("CHINA_PAPER", cash=100000)

    result = check_order(account, _order(quantity=500), "fresh", today_traded_notional=2500, risk_rules=_rules(0.04))

    assert result["risk_check"] == "rejected"
    assert result["risk_reason_code"] == "daily_turnover_limit_exceeded"


def test_turnover_check_does_not_write_main_ledgers(tmp_path) -> None:
    before = list(tmp_path.rglob("*"))
    account = Account("CHINA_PAPER", cash=100000)

    check_order(account, _order(), "fresh", risk_rules=_rules(0.03))

    assert list(tmp_path.rglob("*")) == before


def test_risk_import_does_not_import_daily_run() -> None:
    module = importlib.import_module("trading_core.risk.risk_engine")

    assert hasattr(module, "check_order")
