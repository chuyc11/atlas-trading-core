from trading_core.broker.cost_model import calculate_trade_cost, slippage_price
from trading_core.broker.market_rules import get_market_rule


def test_trade_cost_includes_commission_tax_and_slippage() -> None:
    rule = get_market_rule("A_SHARE")
    assert slippage_price(4.0, "BUY", rule) > 4.0
    buy = calculate_trade_cost(4.0, 100, "BUY", "A_SHARE")
    sell = calculate_trade_cost(4.0, 100, "SELL", "A_SHARE")
    assert buy.commission == 5.0
    assert sell.tax > 0
    assert buy.net_amount > buy.gross_amount
    assert sell.net_amount < sell.gross_amount
