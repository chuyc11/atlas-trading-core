from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, seed_repeatability_outputs
from tests.a_share_owner_dashboard_test_utils import write_json, write_text
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import artifact_paths


def seed_build_output_dashboard_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_repeatability_outputs(paths, as_of_date)
    from trading_core.equity_build_repeatability.repeatability_audit import audit_a_share_build_repeatability

    audit_a_share_build_repeatability(as_of_date=as_of_date, paths=paths)
    dash = paths.data_dir / "equity_owner_dashboard" / "daily" / as_of_date
    for name in [
        "dashboard_config",
        "executive_status_card",
        "data_freshness_card",
        "workflow_status_card",
        "research_output_card",
        "warning_and_blocker_card",
        "artifact_navigation_index",
        "dashboard_source_trace",
        "dashboard_boundary_check",
        "dashboard_manifest",
        "dashboard_summary",
    ]:
        write_json(dash / f"{name}.json", {"target_version": "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard", "overall_passed": True, "warnings": [], "source_workflow_mode": "validate_existing_artifacts"})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_dashboard_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    refresh = paths.data_dir / "equity_data_refresh" / "daily" / as_of_date
    write_json(refresh / "data_refresh_summary.json", {"overall_passed": True, "warnings": []})
    for name in ["dataset_schema_validation", "dataset_freshness_validation", "dataset_coverage_summary", "data_refresh_boundary_check"]:
        write_json(refresh / f"{name}.json", {"overall_passed": True})
    write_json(paths.data_dir / "equity_selection" / "daily" / as_of_date / "candidate_generation_summary.json", {"overall_passed": True, "candidate_count": 10})
    write_json(paths.data_dir / "equity_portfolios" / "daily" / as_of_date / "portfolio_manifest.json", {"overall_passed": True, "portfolio_count": 3})
    write_json(paths.data_dir / "equity_benchmarks" / "daily" / as_of_date / "benchmark_summary.json", {"overall_passed": True, "benchmark_count": 3})
    write_json(paths.data_dir / "equity_performance" / "daily" / as_of_date / "performance_summary.json", {"overall_passed": True, "observation_count": 1})
    write_json(paths.data_dir / "equity_attribution" / "daily" / as_of_date / "attribution_summary.json", {"overall_passed": True})
    write_json(paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date / "current_day_summary.json", {"overall_passed": True, "warnings": []})
    write_json(paths.data_dir / "equity_briefings" / "daily" / as_of_date / "daily_stock_selection_briefing.json", {"overall_passed": True})
    write_json(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "tracking_summary.json", {"overall_passed": True})


def seed_build_output_dashboard_outputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_build_output_dashboard_inputs(paths, as_of_date)
    from trading_core.equity_build_output_dashboard.build_output_dashboard_builder import build_a_share_build_output_owner_dashboard

    build_a_share_build_output_owner_dashboard(as_of_date=as_of_date, paths=paths)
    write_text(artifact_paths(paths, as_of_date)["build_output_owner_dashboard_report"], "report")
