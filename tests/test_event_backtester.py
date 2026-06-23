from trading_core.backtest.event_backtester import run_event_backtest


def test_event_backtester_runs(sample_workspace) -> None:
    summary = run_event_backtest("2026-06-23", "2026-06-24", sample_workspace)
    assert summary["days"] == 2
    assert "no future-dated file" in summary["pit_note"]
    assert summary["execution_model"].startswith("T day generates")
    assert summary["daily"][0]["trade_count"] == 0
    assert summary["daily"][1]["trade_count"] == 1
