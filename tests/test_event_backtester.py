from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.storage.jsonl_store import write_jsonl


def test_event_backtester_runs(sample_workspace) -> None:
    summary = run_event_backtest("2026-06-23", "2026-06-24", sample_workspace)
    assert summary["days"] == 2
    assert "no future-dated file" in summary["pit_note"]
    assert summary["execution_model"].startswith("T day generates")
    assert summary["daily"][0]["trade_count"] == 0
    assert summary["daily"][1]["trade_count"] == 1


def test_event_backtester_settles_t_plus_one_before_next_day_sell(sample_workspace) -> None:
    data_dir = sample_workspace / "work" / "global-briefing" / "data"
    write_jsonl(
        data_dir / "macro_signals-2026-06-24.jsonl",
        [
            {
                "macro_signal_id": "MACRO-20260624-SELL",
                "date": "2026-06-24",
                "region": "CHINA",
                "theme": "risk_reduction",
                "scenario": "Exit broad ETF exposure",
                "confidence": "high",
                "affected_assets": ["510300.SH"],
                "side": "SELL",
                "risk_flags": [],
                "status": "open",
            }
        ],
    )

    summary = run_event_backtest("2026-06-23", "2026-06-25", sample_workspace)
    day1, day2, day3 = summary["daily"]

    assert day1["generated_signal_count"] == 1
    assert day2["trade_count"] == 1
    assert day2["trades"][0]["side"] == "BUY"
    assert day2["positions"][0]["quantity"] == 1200
    assert day2["positions"][0]["pending_t1_quantity"] == 1200
    assert day2["positions"][0]["available_quantity"] == 0

    assert day3["trade_count"] == 1
    assert day3["trades"][0]["side"] == "SELL"
    assert day3["trades"][0]["filled_quantity"] == 1100
    assert day3["trades"][0]["commission"] == 5.0
    assert day3["trades"][0]["tax"] > 0
    assert day3["cash"] > day2["cash"]
    assert day3["positions"][0]["quantity"] == 100
    assert day3["positions"][0]["pending_t1_quantity"] == 0
    assert day3["positions"][0]["available_quantity"] == 100
