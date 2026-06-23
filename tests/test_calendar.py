from trading_core.calendar.trading_calendar import is_trading_day, next_trading_day, previous_trading_day


def test_weekday_calendar_fallback() -> None:
    assert is_trading_day("2026-06-23", "A_SHARE")
    assert not is_trading_day("2026-06-20", "A_SHARE")
    assert next_trading_day("2026-06-19") == "2026-06-22"
    assert previous_trading_day("2026-06-22") == "2026-06-19"
