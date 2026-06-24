"""Tests for v0.5 weekly research reporting."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.reports.research_common import snapshot_diff, snapshot_protected
from trading_core.reports.weekly_research_report import build_weekly_research_report
from trading_core.storage.file_paths import ProjectPaths


@pytest.fixture
def report_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project_root = workspace / "work" / "trading-core"
    for directory in ["data/orders", "data/trades", "data/portfolios", "data/shadow", "data/experiments", "outputs/daily"]:
        (project_root / directory).mkdir(parents=True)
    return ProjectPaths(workspace_root=workspace)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_weekly_report_generates_json_and_markdown(report_paths: ProjectPaths) -> None:
    (report_paths.data_dir / "orders" / "orders-2026-06-17.jsonl").write_text('{"id":"o1"}\n', encoding="utf-8")
    (report_paths.data_dir / "trades" / "trades-2026-06-17.jsonl").write_text('{"id":"t1"}\n', encoding="utf-8")
    _write_json(report_paths.data_dir / "portfolios" / "portfolio-2026-06-17.json", {"equity": 1000})
    (report_paths.outputs_dir / "daily" / "virtual-trading-report-2026-06-17.md").write_text("# Daily", encoding="utf-8")
    _write_json(
        report_paths.data_dir / "shadow" / "ml_shadow_leaderboard-test.json",
        {"model_id": "MLSHADOW-test", "prediction_count": 10, "signal_count": 2, "shadow_recommendation": "watch"},
    )
    _write_json(report_paths.data_dir / "experiments" / "parameter_sweep-EXP-test.json", {"experiment_id": "EXP-test"})
    _write_json(report_paths.data_dir / "experiments" / "strategy_comparison-CMP-test.json", {"comparison_id": "CMP-test"})
    _write_json(report_paths.data_dir / "experiments" / "promotion_simulation-SIM-test.json", {"simulation_id": "SIM-test"})
    _write_json(report_paths.data_dir / "experiments" / "mistake_pattern_library.json", {"patterns": [{"pattern_type": "overfit", "severity": "medium", "evidence_count": 2}]})

    before = snapshot_protected(report_paths)
    result = build_weekly_research_report("2026-06-17", "2026-06-23", True, True, True, report_paths)
    after = snapshot_protected(report_paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["trading"]["orders"] == 1
    assert result["trading"]["trades"] == 1
    assert result["ml_shadow"]["recommendation"] == "watch"
    assert result["experiments"]["parameter_sweeps"] == 1
    assert snapshot_diff(before, after) == []
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "not an admission gate" in report
    assert "not forward 30d dry-run" in report
    assert "no orders/trades/portfolio/accounts written" in report


def test_weekly_report_missing_optional_inputs_warns(report_paths: ProjectPaths) -> None:
    result = build_weekly_research_report("2026-06-17", "2026-06-23", True, True, True, report_paths)

    assert "ML shadow leaderboard missing." in result["warnings"]
    assert result["ml_shadow"]["available"] is False
    assert result["boundary"]["run_daily_called"] is False


def test_weekly_research_cli_smoke(report_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: report_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    exit_code = cli.main(["weekly-research-report", "--start-date", "2026-06-17", "--end-date", "2026-06-23"])

    assert exit_code == 0
    assert (report_paths.outputs_dir / "reports" / "WEEKLY_RESEARCH_REPORT-2026-06-17-2026-06-23.md").exists()
