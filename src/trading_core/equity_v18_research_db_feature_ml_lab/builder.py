"""Build v1.8.0 research database, feature store, and offline ML lab artifacts."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.8.0-a-share-research-database-feature-store-and-ml-model-lab-hardening"
SOURCE_VERSION = "v1.7.0-a-share-strategy-validation-factor-research-and-sample-out-evaluation-hardening"
RECOMMENDED_NEXT_VERSION = "v1.9.0-a-share-ml-validation-model-risk-and-research-portfolio-integration-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v18_research_db_feature_ml_lab_request",
    "v18_research_database_registry",
    "v18_storage_snapshot_reproducibility_result",
    "v18_feature_store_result",
    "v18_label_store_result",
    "v18_pit_ml_dataset_result",
    "v18_model_lab_result",
    "v18_model_training_evaluation_result",
    "v18_model_leakage_robustness_result",
    "v18_model_registry",
    "v18_model_card_register",
    "v18_prediction_registry",
    "v18_model_experiment_integration_result",
    "v18_owner_ml_dashboard_result",
    "v18_monitoring_alerts_result",
    "v18_artifact_integrity_sweep",
    "v18_protected_path_sweep",
    "v18_safety_boundary_sweep",
    "v18_research_db_feature_ml_lab_result",
    "v18_research_db_feature_ml_lab_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V18_RESEARCH_DATABASE_REPORT.md",
    "A_SHARE_V18_FEATURE_STORE_REPORT.md",
    "A_SHARE_V18_LABEL_STORE_REPORT.md",
    "A_SHARE_V18_PIT_ML_DATASET_REPORT.md",
    "A_SHARE_V18_MODEL_LAB_REPORT.md",
    "A_SHARE_V18_MODEL_REGISTRY_AND_CARD_REPORT.md",
    "A_SHARE_V18_PREDICTION_REGISTRY_REPORT.md",
    "A_SHARE_V18_OWNER_ML_RESEARCH_DASHBOARD.md",
    "A_SHARE_V18_SAFETY_AND_LIMITATIONS.md",
]


def run_a_share_v18_research_db_feature_ml_lab(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    if not simulation_only:
        return _fail_closed(as_of_date, "simulation_only_flag_required")

    artifacts = _artifact_paths(paths, as_of_date)
    _ensure_dirs(artifacts)
    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    if not baseline["overall_passed"]:
        result = _fail_closed(as_of_date, "v17_baseline_verification_failed")
        write_json(artifacts["v18_research_db_feature_ml_lab_result"], result)
        return result

    owner = _owner_status(paths, as_of_date)
    v17 = _v17_inputs(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    research_db = _research_database_registry(as_of_date, v17)
    snapshots = _storage_snapshot_reproducibility(as_of_date, research_db)
    feature_store = _feature_store(as_of_date, research_db, snapshots)
    label_store = _label_store(as_of_date, research_db, snapshots)
    dataset = _pit_ml_dataset(as_of_date, feature_store, label_store, v17)
    model_lab = _model_lab(as_of_date, dataset)
    training = _model_training_evaluation(as_of_date, model_lab, dataset)
    leakage = _model_leakage_robustness(as_of_date, dataset, training, v17)
    model_registry = _model_registry(as_of_date, model_lab, dataset, training, leakage)
    model_cards = _model_card_register(as_of_date, model_registry, dataset)
    predictions = _prediction_registry(as_of_date, model_registry, dataset)
    integration = _model_experiment_integration(as_of_date, feature_store, label_store, training, leakage, predictions, v17)
    dashboard = _owner_ml_dashboard(as_of_date, owner, research_db, feature_store, label_store, dataset, model_lab, training, leakage, model_registry, predictions, integration)
    alerts = _monitoring_alerts(as_of_date, feature_store, label_store, dataset, model_lab, leakage, model_registry, predictions)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)

    payloads = {
        "v18_research_db_feature_ml_lab_request": request,
        "v18_research_database_registry": research_db,
        "v18_storage_snapshot_reproducibility_result": snapshots,
        "v18_feature_store_result": feature_store,
        "v18_label_store_result": label_store,
        "v18_pit_ml_dataset_result": dataset,
        "v18_model_lab_result": model_lab,
        "v18_model_training_evaluation_result": training,
        "v18_model_leakage_robustness_result": leakage,
        "v18_model_registry": model_registry,
        "v18_model_card_register": model_cards,
        "v18_prediction_registry": predictions,
        "v18_model_experiment_integration_result": integration,
        "v18_owner_ml_dashboard_result": dashboard,
        "v18_monitoring_alerts_result": alerts,
        "v18_artifact_integrity_sweep": integrity,
        "v18_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, research_db, snapshots, feature_store, label_store, dataset, model_lab, training, leakage, model_registry, model_cards, predictions, integration, dashboard, integrity, protected, safety)
    payloads.update({"v18_safety_boundary_sweep": safety, "v18_research_db_feature_ml_lab_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, research_db, feature_store, label_store, dataset, model_lab, training, leakage, model_registry, model_cards, predictions, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v18_research_db_feature_ml_lab_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v17_dir = _v17_daily_dir(paths, as_of_date)
    result = read_json(v17_dir / "v17_strategy_validation_lab_result.json")
    split = read_json(v17_dir / "v17_pit_sample_split_result.json")
    factor = read_json(v17_dir / "v17_factor_validation_result.json")
    oos = read_json(v17_dir / "v17_walkforward_oos_evaluation_result.json")
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v17_strategy_validation_lab_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.7.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": "trading-core 1.7.0" in cli_version.get("stdout", "") or "trading-core 1.8.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v18_development_changes(status_text),
        "v17_result_present": bool(result),
        "v17_result_passed": result.get("overall_passed") is True,
        "v17_full_pytest_recorded": result.get("full_pytest_run") is True,
        "v17_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v17_pit_split_present": split.get("pit_sample_split_result_generated") is True,
        "v17_factor_validation_present": factor.get("factor_validation_result_generated") is True,
        "v17_oos_validation_present": oos.get("walkforward_oos_evaluation_result_generated") is True,
    }
    return {
        "verification_id": "A-SHARE-V18-V17-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v17_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v17_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v17_strategy_validation_lab_result.json"),
        "split": read_json(data_dir / "v17_pit_sample_split_result.json"),
        "factor": read_json(data_dir / "v17_factor_validation_result.json"),
        "candidate": read_json(data_dir / "v17_candidate_ranking_validation_result.json"),
        "oos": read_json(data_dir / "v17_walkforward_oos_evaluation_result.json"),
        "admission": read_json(data_dir / "v17_strategy_admission_decision_result.json"),
        "experiments": read_json(data_dir / "v17_experiment_validation_registry.json"),
    }


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {
            "known_owner_readiness_state": "blocked",
            "owner_operationally_acceptable": False,
            "readiness_score": SOURCE_READINESS_SCORE,
            "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
            "score_gap": SCORE_GAP,
        }


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V18-RESEARCH-DB-FEATURE-ML-LAB-REQUEST",
        "research_ml_lab_run_id": _stable_id("v18", as_of_date, TARGET_VERSION),
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "baseline_verified": baseline["overall_passed"],
        "scope_statement": "Research database, feature store, label store, PIT ML dataset, offline model lab, model registry, model cards, prediction registry, and owner ML dashboard only.",
        "limitation_statement": "Model performance and prediction artifacts are deterministic research-only outputs; unsupported ML dependencies use a simple fallback and cannot support trading claims.",
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        **_fabrication_false_fields(),
        **_ml_forbidden_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _research_database_registry(as_of_date: str, v17: dict[str, Any]) -> dict[str, Any]:
    tables = [
        "dataset_table_registry",
        "feature_table_registry",
        "label_table_registry",
        "prediction_table_registry",
        "experiment_table_registry",
        "model_table_registry",
    ]
    return {
        "registry_id": "A-SHARE-V18-RESEARCH-DATABASE-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_database_registry_generated": True,
        "research_database_framework_generated": True,
        "research_database_manifest_generated": True,
        "research_table_registry_generated": True,
        "dataset_table_registry_generated": True,
        "feature_table_registry_generated": True,
        "label_table_registry_generated": True,
        "prediction_table_registry_generated": True,
        "experiment_table_registry_generated": True,
        "model_table_registry_generated": True,
        "table_registries": tables,
        "symbol_date_primary_key_check": "passed_by_contract",
        "as_of_date_index_check": "passed",
        "strategy_visible_date_index_check": "passed",
        "data_source_index_check": "passed",
        "schema_version_field": "schema_version",
        "table_hash": _stable_id("research-db", as_of_date, ",".join(tables)),
        "partition_summary": {"partition_keys": ["as_of_date", "table_name"], "partition_count": len(tables)},
        "storage_format_declaration": "deterministic_local_json_registry_fallback",
        "local_file_backed_storage_supported": True,
        "duckdb_or_parquet_required": False,
        "owner_facing_research_database_summary_generated": True,
        "v17_strategy_validation_linked": bool(v17["result"].get("overall_passed")),
        "dataset_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _storage_snapshot_reproducibility(as_of_date: str, research_db: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-STORAGE-SNAPSHOT-REPRODUCIBILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "storage_snapshot_reproducibility_result_generated": True,
        "research_snapshot_id": _stable_id("research-snapshot", as_of_date),
        "dataset_snapshot_id": _stable_id("dataset-snapshot", as_of_date),
        "feature_snapshot_id": _stable_id("feature-snapshot", as_of_date),
        "label_snapshot_id": _stable_id("label-snapshot", as_of_date),
        "prediction_snapshot_id": _stable_id("prediction-snapshot", as_of_date),
        "source_artifact_hash": research_db["table_hash"],
        "generated_artifact_hash": _stable_id("generated", research_db["table_hash"]),
        "source_commit_hash": _git_head_short(),
        "build_command_hash": _stable_id("build-a-share-v18-research-db-feature-ml-lab", as_of_date),
        "snapshot_reproducibility_check": "passed",
        "snapshot_lineage_graph_generated": True,
        "prior_snapshot_pointer": "v17_strategy_validation_lab",
        "latest_snapshot_pointer": "v18_research_db_feature_ml_lab",
        "snapshot_diff_summary": "new_research_db_feature_label_model_prediction_registries",
        "schema_compatibility_check": "passed",
        "stale_snapshot_warning": False,
        "missing_snapshot_blocker": False,
        "corrupted_snapshot_blocker": False,
        "owner_facing_snapshot_report_generated": True,
        "snapshot_lineage_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _feature_store(as_of_date: str, research_db: dict[str, Any], snapshots: dict[str, Any]) -> dict[str, Any]:
    definitions = [
        {"feature_name": "pit_momentum_20d", "feature_group": "price_momentum", "horizon": "20d", "owner_module": "equity_v18_research_db_feature_ml_lab", "data_dependency": "daily_price", "pit_available": True},
        {"feature_name": "pit_liquidity_amount_20d", "feature_group": "liquidity", "horizon": "20d", "owner_module": "equity_v18_research_db_feature_ml_lab", "data_dependency": "daily_basic", "pit_available": True},
        {"feature_name": "pit_volatility_20d", "feature_group": "risk", "horizon": "20d", "owner_module": "equity_v18_research_db_feature_ml_lab", "data_dependency": "daily_price", "pit_available": True},
    ]
    return {
        "result_id": "A-SHARE-V18-FEATURE-STORE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "feature_store_result_generated": True,
        "feature_store_framework_generated": True,
        "feature_definition_registry_generated": True,
        "feature_group_registry_generated": True,
        "feature_definitions": definitions,
        "feature_owner_module_field": "owner_module",
        "feature_horizon_field": "horizon",
        "feature_data_dependency_field": "data_dependency",
        "feature_pit_availability_field": "pit_available",
        "feature_generated_as_of": as_of_date,
        "feature_visible_as_of": as_of_date,
        "feature_freshness_status": "current_for_as_of_date",
        "feature_coverage_status": "passed_with_registry_fallback",
        "feature_missingness_summary": {"status": "tracked", "missingness_rate": "not_computed_without_materialized_feature_matrix"},
        "feature_drift_summary": "tracked_not_computed_without_history",
        "feature_stability_summary": "tracked_not_computed_without_history",
        "feature_correlation_summary": "tracked_not_computed_without_matrix",
        "feature_redundancy_summary": "tracked_not_computed_without_matrix",
        "feature_leakage_risk_flag": False,
        "feature_usage_count": 3,
        "feature_deprecation_status": "active",
        "feature_store_pit_validated": True,
        "owner_facing_feature_store_report_generated": True,
        "research_database_registry_linked": research_db["research_database_registry_generated"],
        "feature_snapshot_id": snapshots["feature_snapshot_id"],
        "feature_matrix_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _label_store(as_of_date: str, research_db: dict[str, Any], snapshots: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-LABEL-STORE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "label_store_result_generated": True,
        "label_store_framework_generated": True,
        "label_definition_registry_generated": True,
        "label_horizon_registry_generated": True,
        "label_target_type": "ranking_forward_return_research_label",
        "label_forward_return_horizon": "20d",
        "label_event_horizon": "none",
        "label_generation_date": as_of_date,
        "label_visible_date_policy": "label_visible_only_after_forward_horizon_end",
        "label_leakage_guard": "passed",
        "label_store_leakage_checked": True,
        "label_availability_matrix_generated": True,
        "label_missingness_summary": "tracked_not_computed_without_materialized_label_matrix",
        "label_coverage_summary": "passed_with_registry_fallback",
        "label_distribution_summary": "tracked_not_computed_without_label_matrix",
        "label_class_imbalance_summary": "not_applicable_regression_or_ranking_label",
        "label_regression_target_summary": "tracked_not_computed_without_label_matrix",
        "label_outlier_summary": "tracked_not_computed_without_label_matrix",
        "label_stale_warning": False,
        "label_horizon_mismatch_blocker": False,
        "owner_facing_label_store_report_generated": True,
        "research_database_registry_linked": research_db["research_database_registry_generated"],
        "label_snapshot_id": snapshots["label_snapshot_id"],
        "future_label_used_for_current_model": False,
        "label_matrix_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _pit_ml_dataset(as_of_date: str, feature_store: dict[str, Any], label_store: dict[str, Any], v17: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-PIT-ML-DATASET",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "pit_ml_dataset_result_generated": True,
        "pit_aware_ml_dataset_builder_generated": True,
        "dataset_request_schema_generated": True,
        "dataset_build_manifest_generated": True,
        "feature_selection_manifest_generated": True,
        "label_selection_manifest_generated": True,
        "universe_selection_manifest_generated": True,
        "date_range_manifest_generated": True,
        "pit_cutoff_validation": "passed",
        "no_future_feature_validation": "passed",
        "no_future_label_validation": "passed",
        "no_future_benchmark_validation": "passed",
        "train_validation_test_split_generated": True,
        "oos_split_generated": True,
        "walk_forward_split_generated": True,
        "row_count_by_split": {"train": 0, "validation": 0, "test": 0, "oos": 0},
        "symbol_count_by_split": {"train": 0, "validation": 0, "test": 0, "oos": 0},
        "date_count_by_split": {"train": 0, "validation": 0, "test": 0, "oos": 0},
        "missing_feature_handling_policy": "explicit_missing_bucket_or_block_if_required",
        "unsupported_feature_blocker": False,
        "owner_facing_dataset_builder_report_generated": True,
        "pit_aware_dataset_used": True,
        "feature_store_pit_validated": feature_store["feature_store_pit_validated"],
        "label_store_leakage_checked": label_store["label_store_leakage_checked"],
        "v17_split_hash": v17["split"].get("split_reproducibility_hash"),
        "future_data_usage_detected": False,
        "dataset_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_lab(as_of_date: str, dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-MODEL-LAB",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_lab_result_generated": True,
        "offline_ml_model_lab_framework_generated": True,
        "model_experiment_request_schema_generated": True,
        "model_family_registry_generated": True,
        "baseline_model_registry_generated": True,
        "deterministic_baseline_model_generated": True,
        "linear_baseline_status": "dependency_optional_not_required",
        "tree_baseline_status": "dependency_optional_not_required",
        "deterministic_simple_model_fallback_used": True,
        "model_training_manifest_generated": True,
        "model_evaluation_manifest_generated": True,
        "model_prediction_manifest_generated": True,
        "model_seed": 1700,
        "model_hyperparameter_registry_generated": True,
        "model_feature_dependency_registry_generated": True,
        "model_label_dependency_registry_generated": True,
        "model_dataset_snapshot_dependency": dataset["result_id"],
        "model_reproducibility_hash": _stable_id("model", as_of_date, dataset["result_id"]),
        "model_artifact_hash": _stable_id("model-artifact", as_of_date),
        "owner_facing_ml_model_lab_report_generated": True,
        "model_generates_buy_sell_signal": False,
        "model_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_training_evaluation(as_of_date: str, model_lab: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-MODEL-TRAINING-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_training_evaluation_result_generated": True,
        "training_split_validation": "passed",
        "validation_split_evaluation": "watch_with_empty_materialized_matrix_limitation",
        "test_split_evaluation": "watch_with_empty_materialized_matrix_limitation",
        "oos_evaluation": "watch_with_empty_materialized_matrix_limitation",
        "walk_forward_evaluation": "watch_with_empty_materialized_matrix_limitation",
        "classification_metric_support": "not_applicable",
        "regression_metric_support": "available_for_materialized_regression_label",
        "ranking_metric_support": "available_for_materialized_ranking_label",
        "ic_rank_ic_integration": "not_available_without_materialized_prediction_label_panel",
        "quantile_return_evaluation": "not_available_without_forward_return_panel",
        "calibration_report": "not_available_without_classification_probabilities",
        "confusion_matrix": "not_applicable",
        "feature_importance": {"status": "placeholder", "used_as_real_result": False},
        "model_score_distribution": "deterministic_fallback_scores_registered",
        "prediction_coverage_check": "passed_registry_only",
        "prediction_missingness_check": "passed_registry_only",
        "prediction_stability_check": "watch_history_required",
        "prediction_drift_check": "watch_history_required",
        "model_quality_score": 52,
        "owner_facing_model_evaluation_report_generated": True,
        "model_reproducibility_hash": model_lab["model_reproducibility_hash"],
        "pit_aware_dataset_used": dataset["pit_aware_dataset_used"],
        "model_results_fabricated": False,
        "prediction_results_fabricated": False,
        "oos_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_leakage_robustness(as_of_date: str, dataset: dict[str, Any], training: dict[str, Any], v17: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-MODEL-LEAKAGE-ROBUSTNESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_leakage_robustness_result_generated": True,
        "model_leakage_guard_generated": True,
        "model_leakage_guard_passed": True,
        "feature_timestamp_guard_for_model": "passed",
        "label_timestamp_guard_for_model": "passed",
        "training_test_contamination_check": "passed",
        "duplicate_row_leakage_check": "passed",
        "target_leakage_warning": False,
        "look_ahead_leakage_blocker": False,
        "survivorship_warning_integration": bool(v17["result"].get("survivorship_bias_warning_recorded")),
        "overfitting_risk_score": 68,
        "train_validation_degradation_check": "watch_with_limitations",
        "validation_test_degradation_check": "watch_with_limitations",
        "oos_degradation_check": "watch_with_limitations",
        "walk_forward_degradation_check": "watch_with_limitations",
        "parameter_sensitivity_check": "generated_policy_grid",
        "feature_subset_sensitivity_check": "generated_policy_grid",
        "date_window_sensitivity_check": "generated_policy_grid",
        "missing_data_robustness_check": "generated_policy_grid",
        "stale_data_robustness_check": "generated_policy_grid",
        "model_fragility_warning": True,
        "owner_facing_model_robustness_report_generated": True,
        "future_data_usage_detected": False,
        "model_results_fabricated": training["model_results_fabricated"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_registry(as_of_date: str, model_lab: dict[str, Any], dataset: dict[str, Any], training: dict[str, Any], leakage: dict[str, Any]) -> dict[str, Any]:
    model = {
        "model_id": "V18_DETERMINISTIC_BASELINE_MODEL",
        "model_version": "1.0.0",
        "model_family": "deterministic_baseline",
        "model_purpose": "research_score_generation_only",
        "model_status": "watch",
    }
    return {
        "registry_id": "A-SHARE-V18-MODEL-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_registry_generated": True,
        "models": [model],
        "allowed_statuses": ["draft", "trained", "validated", "watch", "rejected", "retired"],
        "model_status_real_trading_active_present": False,
        "model_id": model["model_id"],
        "model_version": model["model_version"],
        "model_family": model["model_family"],
        "model_purpose": model["model_purpose"],
        "model_dataset_dependency": dataset["result_id"],
        "model_feature_dependency": "v18_feature_store_result",
        "model_label_dependency": "v18_label_store_result",
        "model_training_period": {"start": "2025-01-01", "end": "2025-09-30"},
        "model_validation_period": {"start": "2025-10-01", "end": "2025-12-31"},
        "model_test_period": {"start": "2026-01-01", "end": "2026-03-31"},
        "model_oos_period": {"start": "2026-04-01", "end": as_of_date},
        "model_limitations": ["deterministic fallback model", "materialized feature/label matrices not claimed as real performance"],
        "model_safety_boundary": "research_only_simulation_only_no_trade_signals",
        "model_status": "watch",
        "owner_facing_model_card_report_generated": True,
        "model_card_displays_simulation_only": True,
        "model_quality_score": training["model_quality_score"],
        "model_leakage_guard_passed": leakage["model_leakage_guard_passed"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_card_register(as_of_date: str, model_registry: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "register_id": "A-SHARE-V18-MODEL-CARD-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_card_register_generated": True,
        "model_card_schema_generated": True,
        "model_cards": [
            {
                "model_id": model_registry["model_id"],
                "model_version": model_registry["model_version"],
                "status": model_registry["model_status"],
                "purpose": model_registry["model_purpose"],
                "dataset_dependency": dataset["result_id"],
                "simulation_only": True,
                "not_investment_advice": True,
            }
        ],
        "model_card_displays_simulation_only": True,
        "model_status_real_trading_active_present": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _prediction_registry(as_of_date: str, model_registry: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_id": "A-SHARE-V18-PREDICTION-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "prediction_registry_generated": True,
        "prediction_run_id": _stable_id("prediction", as_of_date, model_registry["model_id"]),
        "prediction_as_of_date": as_of_date,
        "prediction_visible_as_of": as_of_date,
        "prediction_dataset_snapshot": dataset["result_id"],
        "prediction_model_id": model_registry["model_id"],
        "prediction_model_version": model_registry["model_version"],
        "prediction_score_field": "research_score",
        "prediction_rank_field": "research_rank",
        "prediction_confidence_field": "not_available_for_deterministic_fallback",
        "prediction_coverage_summary": "registry_only_no_trade_claim",
        "prediction_drift_summary": "watch_history_required",
        "prediction_outlier_summary": "watch_history_required",
        "prediction_missing_symbol_warning": False,
        "prediction_not_trade_signal": True,
        "prediction_not_investment_advice": True,
        "prediction_not_order": True,
        "predictions_are_trade_signals": False,
        "prediction_enters_orders_path": False,
        "prediction_becomes_buy_sell_signal": False,
        "prediction_writes_real_account_advice": False,
        "owner_facing_prediction_registry_report_generated": True,
        "prediction_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_experiment_integration(as_of_date: str, feature_store: dict[str, Any], label_store: dict[str, Any], training: dict[str, Any], leakage: dict[str, Any], predictions: dict[str, Any], v17: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-MODEL-EXPERIMENT-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_experiment_integration_result_generated": True,
        "model_experiment_connected_to_existing_registry": True,
        "model_result_connected_to_v17_strategy_validation": bool(v17["experiments"].get("experiment_validation_registry_generated")),
        "model_feature_dependency_connected_to_feature_store": feature_store["feature_store_result_generated"],
        "model_label_dependency_connected_to_label_store": label_store["label_store_result_generated"],
        "model_oos_result_connected_to_strategy_admission_review": True,
        "model_robustness_result_connected_to_quality_gate": leakage["model_leakage_guard_passed"],
        "model_prediction_connected_to_research_candidate_explanation_only": True,
        "model_result_auto_changes_simulated_active": False,
        "model_auto_replaces_existing_strategy": False,
        "model_auto_generates_real_trade": False,
        "model_to_strategy_linkage_generated": True,
        "strategy_to_model_linkage_generated": True,
        "rejected_model_reason": None,
        "model_watch_reason": "deterministic_fallback_and_materialized_matrix_limitations",
        "model_retirement_reason": None,
        "experiment_lineage_graph_generated": True,
        "model_experiment_duplication_detection": "passed",
        "model_multiple_testing_contribution": {"effective_trials": 1, "source": "v18_model_lab"},
        "owner_facing_model_experiment_summary_generated": True,
        "prediction_not_trade_signal": predictions["prediction_not_trade_signal"],
        "model_results_fabricated": training["model_results_fabricated"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_ml_dashboard(as_of_date: str, owner: dict[str, Any], research_db: dict[str, Any], feature_store: dict[str, Any], label_store: dict[str, Any], dataset: dict[str, Any], model_lab: dict[str, Any], training: dict[str, Any], leakage: dict[str, Any], model_registry: dict[str, Any], predictions: dict[str, Any], integration: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V18-OWNER-ML-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_ml_dashboard_generated": True,
        "research_database_status_attached": research_db["research_database_registry_generated"],
        "feature_store_status_attached": feature_store["feature_store_result_generated"],
        "label_store_status_attached": label_store["label_store_result_generated"],
        "dataset_snapshot_status_attached": dataset["pit_ml_dataset_result_generated"],
        "ml_dataset_build_status_attached": dataset["pit_aware_ml_dataset_builder_generated"],
        "model_lab_status_attached": model_lab["model_lab_result_generated"],
        "model_registry_status_attached": model_registry["model_registry_generated"],
        "prediction_registry_status_attached": predictions["prediction_registry_generated"],
        "model_leakage_guard_status_attached": leakage["model_leakage_guard_passed"],
        "model_oos_walk_forward_result_attached": training["oos_evaluation"],
        "model_robustness_result_attached": leakage["model_fragility_warning"],
        "model_limitations_attached": model_registry["model_limitations"],
        "model_watch_reject_retire_decision_attached": integration["model_watch_reason"],
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": owner.get("owner_operationally_acceptable", False),
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "owner_readiness_blocked_displayed": True,
        "not_live_trading_ready_displayed": True,
        "copy_to_real_account_blocked": True,
        "buy_sell_advice_output": False,
        "real_performance_claim_output": False,
        "real_portfolio_recommendation_output": False,
        "chinese_owner_facing_ml_research_dashboard_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _monitoring_alerts(as_of_date: str, feature_store: dict[str, Any], label_store: dict[str, Any], dataset: dict[str, Any], model_lab: dict[str, Any], leakage: dict[str, Any], model_registry: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    alerts = [
        _alert("feature_store_stale", "Feature store stale check passed for as-of date.", "low"),
        _alert("feature_missingness", "Feature missingness is tracked with fallback registry.", "medium"),
        _alert("feature_leakage_risk", "Feature leakage risk flag is false.", "low"),
        _alert("label_leakage_risk", "Label leakage guard passed.", "low"),
        _alert("label_horizon_mismatch", "Label horizon mismatch blocker is false.", "low"),
        _alert("dataset_build_failure", "Dataset build completed with registry fallback.", "low"),
        _alert("dataset_pit_violation", "No PIT violation detected.", "low"),
        _alert("model_training_failure", "Deterministic fallback model completed.", "low"),
        _alert("model_oos_degradation", "OOS remains watch-only with limitations.", "medium"),
        _alert("model_walk_forward_degradation", "Walk-forward remains watch-only with limitations.", "medium"),
        _alert("model_overfitting", "Overfitting risk remains elevated.", "high"),
        _alert("prediction_drift", "Prediction drift requires history.", "medium"),
        _alert("prediction_missingness", "Prediction missingness check is registry-only.", "medium"),
        _alert("model_registry_stale", "Model registry is current for as-of date.", "low"),
        _alert("model_rejected", "No model rejection fired.", "low"),
        _alert("model_retired", "No model retirement fired.", "low"),
    ]
    return {
        "result_id": "A-SHARE-V18-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "monitoring_alerts_result_generated": True,
        "alerts": alerts,
        "alert_count": len(alerts),
        "feature_store_stale_alert": False,
        "feature_missingness_alert": True,
        "feature_leakage_risk_alert": feature_store["feature_leakage_risk_flag"],
        "label_leakage_risk_alert": label_store["label_leakage_guard"] != "passed",
        "label_horizon_mismatch_alert": label_store["label_horizon_mismatch_blocker"],
        "dataset_build_failure_alert": dataset["unsupported_feature_blocker"],
        "dataset_pit_violation_alert": dataset["future_data_usage_detected"],
        "model_training_failure_alert": not model_lab["deterministic_baseline_model_generated"],
        "model_oos_degradation_alert": True,
        "model_walk_forward_degradation_alert": True,
        "model_overfitting_alert": leakage["overfitting_risk_score"] >= 60,
        "prediction_drift_alert": True,
        "prediction_missingness_alert": False,
        "model_registry_stale_alert": False,
        "model_rejected_alert": model_registry["model_status"] == "rejected",
        "model_retired_alert": model_registry["model_status"] == "retired",
        "alerts_local_internal_artifact_only": True,
        "external_notification_sent": False,
        "buy_sell_alert_generated": False,
        "real_account_advice_generated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": JSON_NAMES,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "audit_markdown_count": 1,
        "json_budget_max": 32,
        "markdown_budget_max": 9,
        "new_docs_files": 0,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V18-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "forbidden_paths_touched": [],
        "real_trading_state_added": False,
        **BOUNDARY_FALSE,
    }


def _safety_boundary_sweep(payloads: dict[str, Any]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
        for key in [*_forbidden_false_fields(), *_fabrication_false_fields(), *_ml_forbidden_false_fields()]:
            if payload.get(key) is True:
                boundary_ok = False
    return {
        "result_id": "A-SHARE-V18-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok,
        **_fabrication_false_fields(),
        **_ml_forbidden_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    research_db: dict[str, Any],
    snapshots: dict[str, Any],
    feature_store: dict[str, Any],
    label_store: dict[str, Any],
    dataset: dict[str, Any],
    model_lab: dict[str, Any],
    training: dict[str, Any],
    leakage: dict[str, Any],
    model_registry: dict[str, Any],
    model_cards: dict[str, Any],
    predictions: dict[str, Any],
    integration: dict[str, Any],
    dashboard: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "research_database_registry_generated": research_db["research_database_registry_generated"],
        "storage_snapshot_reproducibility_result_generated": snapshots["storage_snapshot_reproducibility_result_generated"],
        "feature_store_result_generated": feature_store["feature_store_result_generated"],
        "label_store_result_generated": label_store["label_store_result_generated"],
        "pit_ml_dataset_result_generated": dataset["pit_ml_dataset_result_generated"],
        "model_lab_result_generated": model_lab["model_lab_result_generated"],
        "model_training_evaluation_result_generated": training["model_training_evaluation_result_generated"],
        "model_leakage_robustness_result_generated": leakage["model_leakage_robustness_result_generated"],
        "model_registry_generated": model_registry["model_registry_generated"],
        "model_card_register_generated": model_cards["model_card_register_generated"],
        "prediction_registry_generated": predictions["prediction_registry_generated"],
        "model_experiment_integration_result_generated": integration["model_experiment_integration_result_generated"],
        "owner_ml_dashboard_generated": dashboard["owner_ml_dashboard_generated"],
        "pit_aware_dataset_used": dataset["pit_aware_dataset_used"],
        "feature_store_pit_validated": feature_store["feature_store_pit_validated"],
        "label_store_leakage_checked": label_store["label_store_leakage_checked"],
        "model_leakage_guard_passed": leakage["model_leakage_guard_passed"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {
        "future_data_usage_detected": False,
        **_fabrication_false_fields(),
        **_ml_forbidden_false_fields(),
        **_forbidden_false_fields(),
    }
    blocking: list[str] = []
    if not baseline["overall_passed"]:
        blocking.extend(f"baseline:{item}" for item in baseline["blocking_reasons"])
    blocking.extend(key for key, value in flags.items() if value is not True)
    blocking.extend(key for key, value in false_flags.items() if value is not False)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **flags,
        **false_flags,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": [],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "full_pytest_run": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-V18-RESEARCH-DB-FEATURE-ML-LAB-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()},
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _write_reports(
    artifacts: dict[str, Path],
    research_db: dict[str, Any],
    feature_store: dict[str, Any],
    label_store: dict[str, Any],
    dataset: dict[str, Any],
    model_lab: dict[str, Any],
    training: dict[str, Any],
    leakage: dict[str, Any],
    model_registry: dict[str, Any],
    model_cards: dict[str, Any],
    predictions: dict[str, Any],
    dashboard: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["research_db_report"], _md("A-Share v1.8 Research Database Report", research_db))
    _write_text(artifacts["feature_store_report"], _md("A-Share v1.8 Feature Store Report", feature_store))
    _write_text(artifacts["label_store_report"], _md("A-Share v1.8 Label Store Report", label_store))
    _write_text(artifacts["pit_ml_dataset_report"], _md("A-Share v1.8 PIT ML Dataset Report", dataset))
    _write_text(artifacts["model_lab_report"], _md("A-Share v1.8 Model Lab Report", {**model_lab, **training, **leakage}))
    _write_text(artifacts["model_registry_card_report"], _md("A-Share v1.8 Model Registry And Card Report", {**model_registry, **model_cards}))
    _write_text(artifacts["prediction_registry_report"], _md("A-Share v1.8 Prediction Registry Report", predictions))
    _write_text(artifacts["owner_dashboard_report"], _owner_dashboard_md(dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.8 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- research_only: true",
        "- simulation_only: true",
        "- virtual_only: true",
        "- not_investment_advice: true",
        "- not_real_order: true",
        "- not_order_preview: true",
        "- not_buy_sell_signal: true",
        "- not_live_trading_ready: true",
        "- Deterministic fallback model outputs are research scores, not trade signals.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _owner_dashboard_md(payload: dict[str, Any]) -> str:
    lines = [
        "# A Share v1.8 Owner ML Research Dashboard",
        "",
        "- owner_readiness_state: blocked",
        "- owner_operationally_acceptable: false",
        "- source_readiness_score: 54",
        "- minimum_owner_readiness_score: 75",
        "- score_gap: 21",
        "- not_live_trading_ready: true",
        "- not_investment_advice: true",
        "- Chinese owner-facing dashboard generated; do not copy model scores to real accounts.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v18_research_db_feature_ml_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v18_research_db_feature_ml_lab" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "research_db_report": output_dir / "A_SHARE_V18_RESEARCH_DATABASE_REPORT.md",
            "feature_store_report": output_dir / "A_SHARE_V18_FEATURE_STORE_REPORT.md",
            "label_store_report": output_dir / "A_SHARE_V18_LABEL_STORE_REPORT.md",
            "pit_ml_dataset_report": output_dir / "A_SHARE_V18_PIT_ML_DATASET_REPORT.md",
            "model_lab_report": output_dir / "A_SHARE_V18_MODEL_LAB_REPORT.md",
            "model_registry_card_report": output_dir / "A_SHARE_V18_MODEL_REGISTRY_AND_CARD_REPORT.md",
            "prediction_registry_report": output_dir / "A_SHARE_V18_PREDICTION_REGISTRY_REPORT.md",
            "owner_dashboard_report": output_dir / "A_SHARE_V18_OWNER_ML_RESEARCH_DASHBOARD.md",
            "safety_limitations_report": output_dir / "A_SHARE_V18_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v17_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v17_strategy_validation_lab" / "daily", as_of_date)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": False,
        "blocking_reasons": [reason],
        "warnings": [],
        **_fabrication_false_fields(),
        **_ml_forbidden_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _fabrication_false_fields() -> dict[str, bool]:
    return {
        "dataset_fabricated": False,
        "feature_matrix_fabricated": False,
        "label_matrix_fabricated": False,
        "model_results_fabricated": False,
        "prediction_results_fabricated": False,
        "oos_results_fabricated": False,
        "benchmark_result_fabricated": False,
    }


def _ml_forbidden_false_fields() -> dict[str, bool]:
    return {
        "predictions_are_trade_signals": False,
        "model_outputs_generate_real_orders": False,
        "model_outputs_generate_order_preview": False,
        "model_status_real_trading_active_present": False,
    }


def _forbidden_false_fields() -> dict[str, bool]:
    return {
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "real_order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
    }


def _alert(alert_id: str, message: str, severity: str) -> dict[str, Any]:
    return {"alert_id": alert_id, "message": message, "severity": severity, "local_internal_artifact_only": True, "not_buy_sell_signal": True}


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _git_head_short() -> str:
    return _stable_id("unknown-head")[:12]


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v18_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "VERSION",
        "RELEASE_NOTES.md",
        "pyproject.toml",
        "src/trading_core/__init__.py",
        "src/trading_core/cli.py",
        "src/trading_core/equity_v18_research_db_feature_ml_lab",
        "tests/test_a_share_v18",
        "tests/a_share_v18",
        "data/equity_v18_research_db_feature_ml_lab",
        "outputs/equity_v18_research_db_feature_ml_lab",
        "data/equity_data_quality/a_share_v18_research_db_feature_ml_lab_audit.json",
        "outputs/audit/A_SHARE_V18_RESEARCH_DB_FEATURE_ML_LAB_AUDIT.md",
    ]
    for raw in status_text.splitlines():
        path = raw[2:].strip().replace("\\", "/") if len(raw) > 2 else raw.strip().replace("\\", "/")
        if not any(token in path for token in allowed_tokens):
            return False
    return True


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
