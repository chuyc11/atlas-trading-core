import pytest

from trading_core.calendar.trading_calendar import calendar_status, is_trading_day, next_trading_day, previous_trading_day, require_a_share_calendar
from trading_core.storage.file_paths import project_paths

pytestmark = pytest.mark.smoke


def test_weekday_calendar_fallback_warns_and_supports_strict_mode(tmp_path) -> None:
    missing = tmp_path / "missing.csv"
    status = calendar_status("2026-06-23", "A_SHARE", calendar_path=missing)
    assert status["status"] == "degraded"
    assert "weekday fallback" in status["warning"]
    with pytest.raises(RuntimeError, match="calendar file unavailable"):
        is_trading_day("2026-06-23", "A_SHARE", calendar_path=missing, allow_degraded=False)
    with pytest.warns(RuntimeWarning, match="calendar file unavailable"):
        assert is_trading_day("2026-06-23", "A_SHARE", calendar_path=missing)
    assert next_trading_day("2026-06-19", calendar_path=missing) == "2026-06-22"
    assert previous_trading_day("2026-06-22", calendar_path=missing) == "2026-06-19"


def test_default_a_share_calendar_is_discovered_from_project_data() -> None:
    assert calendar_status("2026-07-16", "A_SHARE")["status"] == "calendar_file"
    assert is_trading_day("2026-07-16", "A_SHARE")


def test_explicit_project_paths_do_not_fall_back_to_shared_workspace_calendar(tmp_path) -> None:
    isolated_paths = project_paths(tmp_path)

    status = calendar_status("2026-01-02", "A_SHARE", paths=isolated_paths)
    gate = require_a_share_calendar(paths=isolated_paths)

    assert status["status"] == "degraded"
    assert status["is_trading_day"] is True
    assert gate["passed"] is False
    assert gate["status"] == "missing_calendar"


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


def test_formal_a_share_calendar_gate_rejects_expired_or_short_coverage(tmp_path) -> None:
    calendar = tmp_path / "a_share_calendar.csv"
    calendar.write_text(
        "date,is_trading_day\n"
        "2026-07-30,true\n"
        "2026-07-31,true\n",
        encoding="utf-8",
    )

    expired = require_a_share_calendar(
        calendar_path=calendar,
        as_of_date="2026-08-03",
    )
    short = require_a_share_calendar(
        calendar_path=calendar,
        as_of_date="2026-07-30",
        minimum_forward_days=30,
    )

    assert expired["passed"] is False
    assert expired["status"] == "calendar_coverage_insufficient"
    assert "does not cover" in expired["warning"]
    assert short["passed"] is False
    assert "at least 30" in short["warning"]


def test_next_trading_day_fails_when_loaded_calendar_lacks_required_date(tmp_path) -> None:
    calendar = tmp_path / "a_share_calendar.csv"
    calendar.write_text("date,is_trading_day\n2026-10-01,false\n", encoding="utf-8")
    with pytest.raises(ValueError, match="is absent"):
        next_trading_day("2026-10-01", calendar_path=calendar)
