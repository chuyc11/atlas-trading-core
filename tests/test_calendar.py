import pytest

from trading_core.calendar.trading_calendar import calendar_status, is_trading_day, next_trading_day, previous_trading_day, require_a_share_calendar


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
        "2026-10-09,true\n"
        "2026-10-10,true\n",
        encoding="utf-8",
    )

    assert calendar_status("2026-10-01", "A_SHARE", calendar_path=calendar)["status"] == "calendar_file"
    assert not is_trading_day("2026-10-01", "A_SHARE", calendar_path=calendar)
    assert is_trading_day("2026-10-09", "A_SHARE", calendar_path=calendar)
    assert is_trading_day("2026-10-10", "A_SHARE", calendar_path=calendar)


def test_formal_a_share_calendar_gate_fails_closed_without_calendar(tmp_path) -> None:
    missing = require_a_share_calendar(calendar_path=tmp_path / "missing.csv")
    assert missing["passed"] is False
    assert missing["status"] == "missing_calendar"
    assert "weekday fallback" in missing["warning"]


def test_formal_a_share_calendar_gate_accepts_external_calendar(tmp_path) -> None:
    calendar = tmp_path / "a_share_calendar.csv"
    calendar.write_text("date,is_trading_day\n2026-10-01,false\n2026-10-10,true\n", encoding="utf-8")

    result = require_a_share_calendar(calendar_path=calendar)

    assert result["passed"] is True
    assert result["status"] == "calendar_file"
    assert result["trading_day_count"] == 1
    assert result["closed_day_count"] == 1
