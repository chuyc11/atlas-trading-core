from trading_core.accounting.account import Account
from trading_core.risk.risk_engine import check_order


def test_risk_engine_rejects_data_and_position_breaches() -> None:
    account = Account("CHINA_PAPER", cash=100000)
    order = {
        "symbol": "510300.SH",
        "side": "BUY",
        "target_weight": 0.05,
        "estimated_price": 4.0,
        "quantity": 1200,
    }
    assert check_order(account, order, "fresh")["risk_check"] == "passed"
    assert check_order(account, order, "missing")["risk_check"] == "rejected"
    assert check_order(account, {**order, "target_weight": 0.5}, "fresh")["risk_check"] == "rejected"
