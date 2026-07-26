import hashlib

from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, write_json, write_text
from trading_core.equity_current_day_builds.gated_build_config import (
    GATED_BUILD_BOUNDARY,
    GATED_BUILD_FILES,
    GATED_BUILD_REPORTS,
    TARGET_VERSION,
    gated_build_artifact_paths,
)


def seed_gated_build_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    quality = paths.data_dir / "equity_data_quality"
    write_json(
        quality / "a_share_ops_history_baseline_audit.json",
        {"overall_passed": True, "blocking_reasons": [], "as_of_date": as_of_date, "trend_sufficiency": {"synthetic_history_used": False, "future_dates_used": False}},
    )
    write_json(quality / "a_share_daily_ops_center_audit.json", {"overall_passed": True, "blocking_reasons": [], "as_of_date": as_of_date})
    write_json(quality / "a_share_current_day_research_run_audit.json", {"overall_passed": True, "blocking_reasons": [], "as_of_date": as_of_date})
    write_json(
        quality / "a_share_daily_data_refresh_audit.json",
        {
            "overall_passed": True,
            "blocking_reasons": [],
            "as_of_date": as_of_date,
            "validation_checks": {
                "critical_datasets_available": True,
                "schema_validation_passed": True,
                "freshness_validation_passed": True,
                "coverage_validation_passed": True,
            },
        },
    )

    ops_history = paths.data_dir / "equity_ops_history" / "daily" / as_of_date
    for name in ["ops_trend_sufficiency", "ops_health_score_baseline", "ops_boundary_history_snapshot", "ops_history_manifest"]:
        write_json(ops_history / f"{name}.json", {"target_version": "v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines", "as_of_date": as_of_date})
    write_json(ops_history / "ops_history_boundary_check.json", {"overall_passed": True, "old_run_daily_called": False, "broker_connected": False, "real_orders_placed": False})

    ops_center = paths.data_dir / "equity_ops_center" / "daily" / as_of_date
    write_json(ops_center / "ops_health_score_card.json", {"score": 65})
    write_json(ops_center / "ops_manifest.json", {"blocking_issue_count": 0})
    for name in ["ops_module_status_matrix", "ops_issue_summary", "ops_action_summary", "ops_boundary_check"]:
        write_json(ops_center / f"{name}.json", {"overall_passed": True, "as_of_date": as_of_date})

    current_day = paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    for name in ["current_day_run_config", "current_day_readiness", "current_day_workflow_execution", "current_day_stage_manifest", "current_day_artifact_index", "current_day_boundary_check", "current_day_run_manifest"]:
        write_json(current_day / f"{name}.json", {"overall_passed": True, "as_of_date": as_of_date, "workflow_mode": "validate_existing_artifacts", "artifact_count": 1, "artifacts": [{"artifact_id": name}]})

    refresh = paths.data_dir / "equity_data_refresh" / "daily" / as_of_date
    for name in ["dataset_schema_validation", "dataset_freshness_validation", "dataset_coverage_summary", "data_refresh_boundary_check", "data_refresh_manifest"]:
        write_json(refresh / f"{name}.json", {"overall_passed": True, "as_of_date": as_of_date})


def seed_gated_build_outputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_gated_build_inputs(paths, as_of_date)
    artifacts = gated_build_artifact_paths(paths, as_of_date)
    base = {"target_version": TARGET_VERSION, "as_of_date": as_of_date}
    source_path = paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
    for key in GATED_BUILD_FILES:
        write_json(artifacts[key], {**base, "id": key})
    write_json(artifacts["preflight_gate"], {**base, "overall_passed": True})
    write_json(artifacts["gated_build_execution_record"], {**base, "workflow_mode": "build_from_existing_data", "command_executed": True, "workflow_audit_overall_passed": True, "old_run_daily_called": False})
    write_json(artifacts["build_from_existing_data_workflow_result"], {**base, "workflow_mode": "build_from_existing_data", "workflow_audit_overall_passed": True})
    write_json(artifacts["validate_vs_build_comparison"], {**base, "comparison_completed": True, "missing_required_artifacts": []})
    write_json(artifacts["artifact_drift_summary"], {**base, "drift_categories_found": [], "blocking_reasons": []})
    write_json(
        artifacts["gated_build_source_trace"],
        {
            **base,
            "source_trace_complete": True,
            "forbidden_path_hits": [],
            "entries": [
                {
                    "artifact_id": "ops_history_audit",
                    "required": True,
                    "path": str(source_path.relative_to(paths.project_root)).replace("\\", "/"),
                    "exists": True,
                    "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                }
            ],
        },
    )
    write_json(
        artifacts["gated_build_boundary_check"],
        {
            **base,
            **GATED_BUILD_BOUNDARY,
            "overall_passed": True,
            "public_network_refresh_run": False,
            "full_research_run": False,
            "forbidden_artifacts_present": [],
            "forbidden_wording_positive_hits": [],
        },
    )
    write_json(artifacts["gated_build_manifest"], {**base, "manifest_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-MANIFEST", "research_only": True, "recommended_next_version": "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability"})
    write_json(artifacts["gated_build_summary"], {**base, "overall_passed": True})
    write_json(
        paths.data_dir / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json",
        {
            **base,
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "recommended_next_version": "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability",
            "execution_checks": {"workflow_mode": "build_from_existing_data", "gated_build_execution_performed": True, "workflow_audit_passed": True, "old_run_daily_called": False},
            "comparison_checks": {"comparison_completed": True, "missing_required_artifacts": [], "boundary_drift": False, "source_trace_missing": False, "source_trace_hashes_match": True},
        },
    )
    for key in GATED_BUILD_REPORTS:
        write_text(artifacts[key], "report")
