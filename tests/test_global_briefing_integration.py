from trading_core.daily_run import run_daily


def test_missing_global_briefing_files_do_not_crash(tmp_path) -> None:
    result = run_daily("2026-06-25", tmp_path)
    assert "missing macro_signals for 2026-06-25" in result["limitations"]
    assert result["signals"][0]["side"] == "HOLD"
