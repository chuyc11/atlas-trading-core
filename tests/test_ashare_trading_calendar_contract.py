from pathlib import Path

from global_briefing_test_utils import assert_no_protected_paths
from planning_test_utils import make_planning_paths
from trading_core.execution.trading_calendar_contract import build_trading_calendar_contract, default_calendar


def test_calendar_contract_core_rules(tmp_path: Path) -> None:
    paths = make_planning_paths(tmp_path)
    cal = default_calendar()
    assert cal.is_trading_day("2024-01-02", "SSE")
    assert cal.is_trading_day("2024-01-02", "SZSE")
    assert cal.is_trading_day("2024-01-02", "HKEX")
    assert not cal.is_trading_day("2024-01-06", "SSE")
    assert not cal.is_trading_day("2024-10-01", "SSE")
    assert cal.next_trading_day("2024-01-05", "SSE") == "2024-01-08"
    assert cal.next_trading_day("2024-09-30", "SSE") == "2024-10-02"
    assert cal.previous_trading_day("2024-01-08", "SSE") == "2024-01-05"
    assert cal.is_trading_day("2024-07-01", "SSE") and not cal.is_trading_day("2024-07-01", "HKEX")
    result = build_trading_calendar_contract(paths=paths)
    assert result["weekday_assumption_forbidden"] is True
    assert_no_protected_paths(paths)

