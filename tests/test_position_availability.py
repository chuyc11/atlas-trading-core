from trading_core.execution.position_availability import AvailabilityBook


def test_position_availability_t_plus_one() -> None:
    book = AvailabilityBook()
    settle = book.buy(100, "2024-01-02")
    assert book.position == 100
    assert book.available == 0
    assert settle == "2024-01-03"
    assert not book.sell(100)
    book.settle("2024-01-03")
    assert book.available == 100
    assert book.sell(100)

