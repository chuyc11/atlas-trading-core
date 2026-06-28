from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_tracking_test_utils import make_tracking_paths
from trading_core.equity_portfolio_tracking.tracking_inputs import load_tracking_inputs
from trading_core.equity_portfolio_tracking.valuation import build_valuation_prices, valuation_price_for_symbol


def test_valuation_prefers_adjusted_close(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    inputs = load_tracking_inputs(paths=paths, as_of_date=AS_OF_DATE)

    prices = build_valuation_prices(inputs)
    first_symbol = inputs.portfolios["long"][0]["symbol"]

    assert prices[first_symbol].price > 0
    assert prices[first_symbol].price_field == "adj_close"
    assert prices[first_symbol].to_dict()["valuation_price_policy"] == "adjusted_close_then_close"


def test_valuation_falls_back_to_close_when_adjusted_missing(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    inputs = load_tracking_inputs(paths=paths, as_of_date=AS_OF_DATE)
    symbol = inputs.portfolios["long"][0]["symbol"]
    adjusted_without_symbol = inputs.adjusted_prices[inputs.adjusted_prices["symbol"] != symbol]
    patched = inputs.__class__(**{**inputs.__dict__, "adjusted_prices": adjusted_without_symbol})

    price = valuation_price_for_symbol(patched, symbol)

    assert price.price > 0
    assert price.price_field == "close"
