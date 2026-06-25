from trading_core.execution.ashare_lot_rules import validate_order_quantity


def test_ashare_lot_rules() -> None:
    assert validate_order_quantity("BUY", 100)["accepted"]
    assert not validate_order_quantity("BUY", 50)["accepted"]
    assert not validate_order_quantity("BUY", 150)["accepted"]
    assert validate_order_quantity("SELL", 50, position_quantity=150, available_quantity=150)["accepted"]
    assert not validate_order_quantity("SELL", 200, position_quantity=150, available_quantity=150)["accepted"]
    assert not validate_order_quantity("SELL", 100, position_quantity=150, available_quantity=50)["accepted"]

