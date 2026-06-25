from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, build_baseline_strategy_stack, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_pack_summary import build_baseline_strategy_pack_summary


def test_baseline_strategy_pack_summary(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths)
    result = build_baseline_strategy_pack_summary(start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["all_strategies_complete"] is True
    assert result["strategy_count"] == 3
    assert result["strategies_complete"] == 3
    assert result["promotion_triggered"] is False
    assert result["forward_dry_run_started"] is False
    assert result["run_daily_called"] is False
    assert result["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_baseline_strategy_pack_summary_warns_when_report_missing(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths)
    report = paths.data_dir / "strategies" / "reports" / f"baseline_strategy_report-equal_weight_etf_rotation-{TEST_START}-{TEST_END}.json"
    report.unlink()
    result = build_baseline_strategy_pack_summary(start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["all_strategies_complete"] is False
    assert result["warnings"] == ["equal_weight_etf_rotation report missing"]


def test_baseline_strategy_pack_summary_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths, start_date="2024-01-02", end_date="2024-12-31")
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["baseline-strategy-pack-summary"]) == 0

