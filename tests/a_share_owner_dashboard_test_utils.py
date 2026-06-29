import json
from pathlib import Path

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_workflows.workflow_config import workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths


AS_OF_DATE = "2026-06-26"


def make_paths(tmp_path: Path) -> ProjectPaths:
    project_root = tmp_path / "work" / "trading-core"
    (project_root / "data").mkdir(parents=True)
    (project_root / "outputs").mkdir()
    return ProjectPaths(tmp_path)


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, text: str = "report") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_owner_dashboard_inputs(paths: ProjectPaths, as_of_date: str = AS_OF_DATE) -> None:
    seed_current_day(paths, as_of_date)
    seed_data_refresh(paths, as_of_date)
    seed_workflow(paths, as_of_date)
    seed_briefing_tracking_and_analytics(paths, as_of_date)
    seed_candidates(paths, as_of_date)


def seed_current_day(paths: ProjectPaths, as_of_date: str) -> None:
    artifacts = current_day_artifact_paths(paths, as_of_date)
    write_json(
        artifacts["current_day_run_manifest"],
        {
            "target_version": "v0.8.1-a-share-current-day-research-workflow-runner",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": ["workflow:portfolio tracking has limited first-day performance history"],
            "resolved_as_of_date": as_of_date,
            "recommended_next_version": "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard",
        },
    )
    write_json(artifacts["current_day_summary"], {"overall_passed": True, "warnings": []})
    write_json(artifacts["current_day_workflow_execution"], {"workflow_mode": "validate_existing_artifacts", "command": "run-a-share-daily-research-workflow"})
    write_json(
        artifacts["current_day_audit_json"],
        {"overall_passed": True, "blocking_reasons": [], "warnings": ["current_day_warning"], "resolved_as_of_date": as_of_date},
    )
    write_text(artifacts["current_day_summary_report"], "current day report")


def seed_data_refresh(paths: ProjectPaths, as_of_date: str) -> None:
    artifacts = data_refresh_artifact_paths(paths, as_of_date)
    write_json(
        artifacts["data_refresh_audit_json"],
        {
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": ["daily_basic:required_field_all_null"],
            "validation_checks": {
                "critical_datasets_available": True,
                "schema_validation_passed": True,
                "freshness_validation_passed": True,
                "coverage_validation_passed": True,
            },
        },
    )
    write_json(artifacts["data_refresh_summary"], {"dataset_status": {"daily_price": "passed"}, "warnings": []})
    write_json(artifacts["dataset_freshness_validation"], {"freshness_validation_status": "passed"})
    write_json(artifacts["dataset_coverage_summary"], {"coverage_validation_status": "passed"})
    write_json(artifacts["data_gap_report"], {"gaps": []})
    write_json(
        artifacts["provider_health_check"],
        {
            "providers": [
                {"provider_id": "local_file_provider", "enabled": True, "current_attempt_status": "available", "fallback_used": False, "supports_required_dataset": True, "local_source_available": True},
                {"provider_id": "eastmoney_public_provider", "enabled": False, "current_attempt_status": "disabled_or_unavailable", "fallback_used": False},
                {"provider_id": "akshare_provider", "enabled": False, "current_attempt_status": "disabled_or_unavailable", "fallback_used": False},
            ]
        },
    )


def seed_workflow(paths: ProjectPaths, as_of_date: str) -> None:
    artifacts = workflow_artifact_paths(paths, as_of_date)
    write_json(artifacts["workflow_summary"], {"overall_passed": True, "warnings": []})
    write_json(artifacts["workflow_audit_json"], {"overall_passed": True, "blocking_reasons": [], "warnings": ["workflow_warning"]})
    write_json(artifacts["workflow_run_manifest"], {"overall_passed": True})
    write_json(
        artifacts["workflow_stage_manifest"],
        {"stages": [{"stage_id": "briefing", "stage_name": "briefing", "status": "passed", "warnings": []}]},
    )


def seed_briefing_tracking_and_analytics(paths: ProjectPaths, as_of_date: str) -> None:
    write_json(paths.data_dir / "equity_briefings" / "daily" / as_of_date / "daily_stock_selection_briefing.json", {"warnings": []})
    write_text(paths.outputs_dir / "equity_briefings" / "daily" / as_of_date / "DAILY_STOCK_SELECTION_BRIEFING.md")
    write_json(paths.data_dir / "equity_data_quality" / "a_share_daily_stock_selection_briefing_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    write_json(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "tracking_summary.json", {"warnings": ["tracking_warning"], "performance_not_yet_observed": True})
    write_json(
        paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_nav_snapshot.json",
        {"portfolios": {"core": {"portfolio_id": "core", "portfolio_nav": 1.0, "holding_count": 2, "cash_balance": 0.0, "gross_exposure": 1.0}}},
    )
    write_json(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_exposure_snapshot.json", {"largest_weights": []})
    write_text(paths.outputs_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md")
    write_json(paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    write_json(paths.data_dir / "equity_benchmarks" / "daily" / as_of_date / "benchmark_summary.json", {"warnings": [], "benchmark_availability": {"CSI300": {"available": True}}, "first_day_initialization": True})
    write_text(paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date / "A_SHARE_BENCHMARK_SUMMARY.md")
    write_json(paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    write_json(paths.data_dir / "equity_performance" / "daily" / as_of_date / "performance_summary.json", {"portfolio_observation_count": 1, "minimum_required_observations": 2, "sufficient_history": False, "warnings": ["limited_history"]})
    write_text(paths.outputs_dir / "equity_performance" / "daily" / as_of_date / "A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md")
    write_json(paths.data_dir / "equity_data_quality" / "a_share_multi_day_performance_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    write_json(paths.data_dir / "equity_attribution" / "daily" / as_of_date / "attribution_summary.json", {"limited_history": True, "structural_diagnostics_available": True, "realized_performance_attribution_available": False, "warnings": ["limited_history"]})
    write_text(paths.outputs_dir / "equity_attribution" / "daily" / as_of_date / "A_SHARE_ATTRIBUTION_SUMMARY.md")
    write_json(paths.data_dir / "equity_data_quality" / "a_share_performance_attribution_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})


def seed_candidates(paths: ProjectPaths, as_of_date: str) -> None:
    base = paths.data_dir / "equity_selection" / "daily" / as_of_date
    rows = [{"symbol": "000001.SZ"}, {"symbol": "000002.SZ"}]
    for name in ["long_candidates", "mid_candidates", "short_candidates", "extended_watch_pool", "multi_horizon_candidates", "risk_downgraded_candidates"]:
        write_json(base / f"{name}.json", rows)
