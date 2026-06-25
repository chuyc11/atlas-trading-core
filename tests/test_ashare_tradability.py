from trading_core.execution.ashare_tradability import evaluate_tradability


def test_ashare_tradability_fail_closed_rules() -> None:
    assert evaluate_tradability("tradable", "BUY").allowed
    assert evaluate_tradability("tradable", "SELL").allowed
    assert not evaluate_tradability("suspended", "BUY").allowed
    assert not evaluate_tradability("suspended", "SELL").allowed
    assert not evaluate_tradability("missing_price", "BUY", price_available=False).allowed
    assert not evaluate_tradability("limit_up", "BUY").allowed
    assert evaluate_tradability("limit_up", "SELL").allowed
    assert not evaluate_tradability("limit_down", "SELL").allowed
    assert evaluate_tradability("limit_down", "BUY").allowed
    assert not evaluate_tradability("st_flagged", "BUY").allowed
    assert not evaluate_tradability("new_listing_restricted", "BUY").allowed
    assert not evaluate_tradability("unknown_status", "BUY").allowed
    assert not evaluate_tradability("tradable", "BUY", status_date="2024-01-04", execution_date="2024-01-03").allowed

