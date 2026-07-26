import hashlib

from tests.a_share_gated_build_test_utils import seed_gated_build_outputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths as make_paths, write_json, write_text
from trading_core.equity_build_repeatability.repeatability_config import (
    REPEATABILITY_BOUNDARY,
    REPEATABILITY_FILES,
    REPEATABILITY_REPORTS,
    TARGET_VERSION,
    repeatability_artifact_paths,
)


def seed_repeatability_outputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_gated_build_outputs(paths, as_of_date)
    artifacts = repeatability_artifact_paths(paths, as_of_date)
    base = {"target_version": TARGET_VERSION, "as_of_date": as_of_date}
    source_path = paths.data_dir / "equity_data_quality" / "a_share_gated_build_from_existing_data_audit.json"
    for key in REPEATABILITY_FILES:
        write_json(artifacts[key], {**base, "id": key})
    write_json(artifacts["repeatability_config"], {**base, "config_id": "A-SHARE-BUILD-REPEATABILITY-CONFIG", "workflow_mode": "build_from_existing_data"})
    write_json(artifacts["repeatability_input_availability"], {**base, "overall_passed": True, "gated_build_audit_passed": True})
    write_json(artifacts["repeatability_date_alignment"], {**base, "overall_passed": True})
    write_json(artifacts["protected_path_pre_run_snapshot"], {**base, "entries": []})
    write_json(artifacts["protected_path_post_run_snapshot"], {**base, "entries": []})
    write_json(
        artifacts["protected_path_modification_check"],
        {
            **base,
            "preexisting_protected_paths_allowed": True,
            "protected_path_modifications_detected": False,
            "new_protected_paths_created": [],
            "protected_files_modified": [],
            "protected_files_created": [],
            "protected_files_deleted": [],
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
        },
    )
    write_json(artifacts["repeat_build_execution_plan"], {**base, "workflow_mode": "build_from_existing_data", "command_allowed": True})
    write_json(
        artifacts["repeat_build_execution_record"],
        {
            **base,
            "workflow_mode": "build_from_existing_data",
            "command_executed": True,
            "workflow_audit_overall_passed": True,
            "old_run_daily_called": False,
            "run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
            "real_account_data_read": False,
        },
    )
    write_json(artifacts["repeat_build_workflow_result"], {**base, "workflow_mode": "build_from_existing_data", "workflow_audit_overall_passed": True})
    write_json(artifacts["first_build_artifact_snapshot"], {**base, "artifact_count": 1, "entries": []})
    write_json(artifacts["second_build_artifact_snapshot"], {**base, "artifact_count": 1, "entries": []})
    write_json(
        artifacts["build_vs_build_comparison"],
        {
            **base,
            "comparison_completed": True,
            "business_output_drift_count": 0,
            "timestamp_only_drift_count": 1,
            "metadata_hash_drift_count": 1,
            "missing_required_artifact_count": 0,
            "boundary_drift": False,
            "protected_path_drift": False,
            "source_trace_drift": False,
            "blocking_reasons": [],
        },
    )
    write_json(artifacts["repeatability_drift_summary"], {**base, "overall_status": "passed", "blocking_reasons": []})
    write_json(artifacts["deterministic_field_normalization"], {**base, "normalization_applied": True})
    write_json(artifacts["repeatability_warning_comparison"], {**base, "new_warnings": []})
    write_json(
        artifacts["repeatability_source_trace"],
        {
            **base,
            "source_trace_complete": True,
            "forbidden_generated_sources": [],
            "entries": [
                {
                    "artifact_id": "gated_build_audit",
                    "required": True,
                    "path": str(source_path.relative_to(paths.project_root)).replace("\\", "/"),
                    "exists": True,
                    "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                }
            ],
        },
    )
    write_json(
        artifacts["repeatability_boundary_check"],
        {
            **base,
            **REPEATABILITY_BOUNDARY,
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "forbidden_artifacts_present": [],
            "forbidden_wording_positive_hits": [],
        },
    )
    write_json(
        artifacts["repeatability_manifest"],
        {
            **base,
            "manifest_id": "A-SHARE-BUILD-REPEATABILITY-MANIFEST",
            "workflow_mode": "build_from_existing_data",
            "repeat_build_execution_performed": True,
            "second_build_audit_passed": True,
            "comparison_completed": True,
            "business_output_drift_count": 0,
            "missing_required_artifact_count": 0,
            "boundary_drift": False,
            "protected_path_drift": False,
            "source_trace_missing": False,
            "blocking_reasons": [],
            "warnings": [],
            "recommended_next_version": "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh",
        },
    )
    write_json(artifacts["repeatability_summary"], {**base, "overall_passed": True})
    for key in REPEATABILITY_REPORTS:
        write_text(artifacts[key], "report")
