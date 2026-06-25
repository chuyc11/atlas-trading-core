from __future__ import annotations

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.full_historical_proxy_workflow import build_proxy_workflow_markdown, run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages
from trading_core.global_briefing.historical_warning_inventory import group_warning_messages


def test_repeated_replay_warnings_are_grouped_and_raw_count_preserved() -> None:
    messages = [
        *[f"target delta below lot size for 510300.SH on 2024-01-{day:02d}" for day in range(2, 9)],
        *[f"missing replay price for 159915.SZ on 2024-01-{day:02d}" for day in range(2, 9)],
        "future leakage detected in replay input",
    ]
    groups = group_warning_messages(messages)
    assert len(groups) < len(messages)
    assert any(group["category"] == "lot_size_constraint" and group["raw_count"] == 7 for group in groups)
    assert any(group["category"] == "missing_price" and group["severity"] == "high" for group in groups)
    assert any(group["category"] == "future_leakage" and group["severity"] == "high" for group in groups)
    markdown = build_proxy_workflow_markdown({"overall_status": "research_review_ready", "blocking_reasons": [], "raw_warning_count": len(messages), "grouped_warning_count": len(groups), "grouped_warnings": groups})
    assert "Grouped Warnings" in markdown
    assert "raw_count=7" in markdown


def test_proxy_workflow_cli_smoke_with_grouped_warning_fields(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    result = run_full_historical_proxy_replay(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert "raw_warning_count" in result
    assert "grouped_warnings" in result
    assert result["grouped_warning_count"] <= result["raw_warning_count"]
    assert result["boundary"]["main_ledger_written"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)

    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["run-full-historical-proxy-replay", "--start-date", "2024-01-02", "--end-date", "2024-01-08"]) == 0
