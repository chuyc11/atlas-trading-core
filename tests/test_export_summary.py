from __future__ import annotations

from pathlib import Path

from trading_core.daily_run import run_daily
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.storage.file_paths import project_paths


def test_run_daily_exports_trading_summary(sample_workspace: Path) -> None:
    result = run_daily("2026-06-23", sample_workspace)
    summary = result["trading_summary"]
    paths = project_paths(sample_workspace)

    assert summary["date"] == "2026-06-23"
    assert summary["total_asset"] == result["portfolio"]["total_asset"]
    assert summary["trades_count"] == len(result["trades"])
    assert paths.dated_json("exports", "trading_summary", "2026-06-23").exists()


def test_export_summary_missing_files_adds_limitations(tmp_path: Path) -> None:
    summary = export_trading_summary("2026-06-23", project_paths(tmp_path))

    assert "missing_portfolio" in summary["limitations"]
    assert "missing_benchmark" in summary["limitations"]
    assert "missing_attribution" in summary["limitations"]
    assert "missing_evolution" in summary["limitations"]
