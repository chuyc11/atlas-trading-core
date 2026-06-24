from __future__ import annotations

import pytest
from trading_core.accounting.account import Account
from trading_core.risk.risk_engine import check_order, load_risk_rules
from trading_core.broker.market_rules import get_market_rule


def test_gap_max_daily_turnover_remediated() -> None:
    # v0.5.1 remediation: max_daily_turnover exists in config and is enforced by check_order.
    rules = load_risk_rules()
    assert "max_daily_turnover" in rules["limits"]

    account = Account("CHINA_PAPER", cash=100000)
    order = {
        "symbol": "510300.SH",
        "side": "BUY",
        "target_weight": 0.05,
        "estimated_price": 4.0,
        "quantity": 1200,
    }

    custom_rules = {
        "limits": {
            "max_single_position_weight": 0.20,
            "max_total_position_weight": 0.80,
            "min_cash_weight": 0.10,
            "max_daily_turnover": 0.0001,
            "max_orders_per_day": 5,
        },
        "data_quality": rules["data_quality"],
    }
    result = check_order(account, order, "fresh", risk_rules=custom_rules)
    assert result["risk_check"] == "rejected"
    assert result["risk_reason_code"] == "daily_turnover_limit_exceeded"


def test_gap_hk_board_lots() -> None:
    # Verify that HK market rule hardcodes lot_size=1 which does not match real board lots (e.g. 500 or 1000)
    hk_rule = get_market_rule("HK")
    assert hk_rule.lot_size == 1


def test_gap_timezone_asia_shanghai_remediated() -> None:
    from trading_core.config_loader import load_config
    settings = load_config("settings.yaml")
    assert settings.get("project_timezone") == "Asia/Shanghai"
