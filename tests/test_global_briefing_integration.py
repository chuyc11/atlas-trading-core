from pathlib import Path

from trading_core.daily_run import run_daily
import pytest

pytestmark = pytest.mark.smoke


def test_missing_global_briefing_files_do_not_crash(workspace_with_calendar: Path) -> None:
    result = run_daily("2026-06-25", workspace_with_calendar)
    assert "missing macro_signals for 2026-06-25" in result["limitations"]
    assert result["signals"][0]["side"] == "HOLD"
