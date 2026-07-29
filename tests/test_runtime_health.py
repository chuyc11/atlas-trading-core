from __future__ import annotations

from pathlib import Path

from trading_core.daily_run import run_daily
from trading_core.runtime.health import load_health, summarize_health
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import write_json


def test_run_daily_generates_runtime_health(sample_workspace: Path) -> None:
    result = run_daily("2026-06-23", sample_workspace)
    health = result["health"]

    assert health["date"] == "2026-06-23"
    assert health["run_id"].startswith("RUN-")
    assert health["macro_signals_count"] == 1
    assert health["orders_count"] == 1
    assert health["benchmark_count"] >= 1
    assert health["attribution_status"] == "ok"
    assert load_health("2026-06-23", project_paths(sample_workspace))["run_id"] == health["run_id"]


def test_missing_macro_signals_warns_without_crashing(workspace_with_calendar: Path) -> None:
    data = workspace_with_calendar / "work" / "global-briefing" / "data"
    data.mkdir(parents=True)
    write_json(
        data / "china-market-snapshot-2026-06-23.json",
        {"items": [{"symbol": "510300.SH", "price": 4.0, "previous_close": 4.0, "data_status": "ok"}]},
    )

    result = run_daily("2026-06-23", workspace_with_calendar)
    assert "missing macro_signals for 2026-06-23" in result["health"]["warnings"]
    assert result["health"]["errors"] == []


def test_missing_price_snapshot_warns_without_crashing(workspace_with_calendar: Path) -> None:
    result = run_daily("2026-06-23", workspace_with_calendar)
    assert any("missing China market snapshot" in warning for warning in result["health"]["warnings"])
    assert result["health"]["missing_prices_count"] >= 1
    assert result["health"]["errors"] == []


def test_summarize_health_aggregates_multiple_days(sample_workspace: Path) -> None:
    run_daily("2026-06-23", sample_workspace)
    run_daily("2026-06-24", sample_workspace)
    summary = summarize_health("2026-06-23", "2026-06-24", project_paths(sample_workspace))

    assert summary["total_run_days"] == 2
    assert summary["success_days"] == 2
    assert summary["failed_days"] == 0
    assert summary["total_orders_count"] >= 1
    assert "missing_input_count" in summary
