import pytest

from trading_core.calendar.trading_calendar import calendar_status, is_trading_day, next_trading_day, previous_trading_day


def test_weekday_calendar_fallback_is_explicitly_degraded() -> None:
    status = calendar_status("2026-06-23", "A_SHARE")
    assert status["status"] == "degraded"
    assert "weekday fallback" in status["warning"]
    with pytest.warns(RuntimeWarning, match="calendar file unavailable"):
        assert is_trading_day("2026-06-23", "A_SHARE")
    assert not is_trading_day("2026-06-20", "A_SHARE")
    assert next_trading_day("2026-06-19") == "2026-06-22"
    assert previous_trading_day("2026-06-22") == "2026-06-19"


def test_a_share_calendar_uses_external_file_for_holidays(tmp_path) -> None:
    calendar = tmp_path / "a_share_calendar.csv"
    calendar.write_text(
        "date,is_trading_day\n"
        "2026-10-01,false\n"
        "2026-10-02,false\n"
        "2026-10-09,true\n",
        encoding="utf-8",
    )

    assert calendar_status("2026-10-01", "A_SHARE", calendar_path=calendar)["status"] == "calendar_file"
    assert not is_trading_day("2026-10-01", "A_SHARE", calendar_path=calendar)
    assert is_trading_day("2026-10-09", "A_SHARE", calendar_path=calendar)
