from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_daily_dir, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_daily_workflow_integration_generates_manifest_and_monitoring(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    daily = v11_json(paths, "v11_daily_workflow_integration_result")

    assert result["daily_workflow_integrated"] is True
    assert daily["benchmark_coverage_status_updated"] is True
    assert daily["simulated_performance_attribution_updated"] is True
    assert daily["run_manifest_generated"] is True
    assert daily["monitoring_checks_run"] is True


def test_v11_dry_run_does_not_pollute_formal_artifacts(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True, dry_run=True)

    assert result["overall_passed"] is True
    assert not v11_daily_dir(paths).exists()
    assert v11_json(paths, "v11_owner_ops_platform_result", dry_run=True)["dry_run"] is True


def test_v11_non_trading_day_safe_skip(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, as_of_date="2026-07-04", simulation_only=True)
    daily = v11_json(paths, "v11_daily_workflow_integration_result", as_of_date="2026-07-04")

    assert result["overall_passed"] is True
    assert daily["non_trading_day_safe_skip"] is True
    assert daily["workflow_status"] == "safe_skip_non_trading_day"
