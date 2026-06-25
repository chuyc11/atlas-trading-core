from trading_core.execution.cash_position_invariants import check_cash_position_invariants


def test_cash_position_invariants() -> None:
    assert check_cash_position_invariants({"cash": 1, "positions": [{"quantity": 100, "available_quantity": 50}]})["passed"]
    assert not check_cash_position_invariants({"cash": -1, "positions": []})["passed"]
    assert not check_cash_position_invariants({"cash": 1, "positions": [{"symbol": "X", "quantity": 1, "available_quantity": 2}]})["passed"]
    assert not check_cash_position_invariants({"cash": 1, "positions": [{"symbol": "X", "quantity": -1, "available_quantity": 0}]})["passed"]

