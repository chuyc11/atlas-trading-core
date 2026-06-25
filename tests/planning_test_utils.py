from __future__ import annotations

from pathlib import Path

from global_briefing_test_utils import make_paths, write_json, write_text


def make_planning_paths(tmp_path: Path):
    paths = make_paths(tmp_path)
    seed_planning_repo(paths)
    return paths


def seed_planning_repo(paths) -> None:
    for path in [
        "src/trading_core/calendar/__init__.py",
        "src/trading_core/data/price_dataset_merge.py",
        "src/trading_core/global_briefing/isolated_replay_execution.py",
        "src/trading_core/broker/market_rules.py",
        "src/trading_core/broker/cost_model.py",
        "src/trading_core/accounting/__init__.py",
        "src/trading_core/daily_run.py",
        "src/trading_core/reports/__init__.py",
        "src/trading_core/benchmarks/__init__.py",
        "src/trading_core/strategy/__init__.py",
        "src/trading_core/experiments/promotion_simulation.py",
        "src/trading_core/global_briefing/isolated_replay_adapter_audit.py",
        "tests/test_calendar.py",
        "tests/test_historical_data_downloaders.py",
        "tests/test_price_dataset_merge.py",
        "tests/test_point_in_time.py",
        "tests/test_isolated_replay_execution.py",
        "tests/test_market_rules.py",
        "tests/test_cost_model.py",
        "tests/test_accounting.py",
        "tests/test_consistency_checker.py",
        "tests/test_end_to_end_daily_run.py",
        "tests/test_dry_run_validation_report.py",
        "tests/test_benchmark_engine.py",
        "tests/test_strategy_comparison.py",
        "tests/test_day0_readiness_audit.py",
        "tests/test_isolated_replay_adapter_audit.py",
        "tests/test_promotion_simulation.py",
        "tests/test_forward_dry_run_operating_calendar.py",
    ]:
        write_text(paths.project_root / path, "# fixture\n")
    for path in [
        "docs/PROJECT_PLAN.md",
        "docs/RUNBOOK.md",
        "docs/SAFETY_BOUNDARY.md",
        "docs/FORWARD_DRY_RUN_DAY0_READINESS.md",
        "README.md",
        "RELEASE_NOTES.md",
        "VERSION",
    ]:
        write_text(paths.project_root / path, "fixture\n")
    write_json(paths.data_dir / "system" / "historical_data_quality_audit.json", {"overall_passed": True})
    write_json(paths.data_dir / "system" / "day0_accepted_warning_register.json", {"blocking_count": 0})
    write_json(paths.data_dir / "system" / "forward_dry_run_operating_calendar.json", {"calendar_status": "template_only"})
    write_text(paths.outputs_dir / "audit" / "DAY0_READINESS_AUDIT.md", "day0 audit\n")
    write_text(paths.outputs_dir / "system" / "FORWARD_DRY_RUN_OPERATING_CALENDAR.md", "calendar\n")


def build_planning_stack(paths) -> None:
    from trading_core.planning.artifact_coverage_scanner import build_artifact_coverage_scan
    from trading_core.planning.day1_blocker_classifier import classify_day1_blockers
    from trading_core.planning.mvp_gap_classifier import classify_mvp_gaps
    from trading_core.planning.mvp_requirement_map import build_mvp_requirement_map
    from trading_core.planning.next_work_register import build_next_work_register
    from trading_core.planning.plan_checklist_extractor import build_plan_checklist

    build_plan_checklist(paths=paths)
    build_mvp_requirement_map(paths=paths)
    build_artifact_coverage_scan(paths=paths)
    classify_mvp_gaps(paths=paths)
    classify_day1_blockers(paths=paths)
    build_next_work_register(paths=paths)

