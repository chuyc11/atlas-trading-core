from trading_core.execution.fill_price_model import resolve_fill_price


def test_fill_price_model_rejects_missing_and_future_price() -> None:
    assert resolve_fill_price({"date": "2024-01-03", "price": 10}, "BUY", execution_date="2024-01-03")["accepted"]
    assert not resolve_fill_price(None, "BUY", execution_date="2024-01-03")["accepted"]
    assert not resolve_fill_price({"date": "2024-01-04", "price": 10}, "BUY", execution_date="2024-01-03")["accepted"]

