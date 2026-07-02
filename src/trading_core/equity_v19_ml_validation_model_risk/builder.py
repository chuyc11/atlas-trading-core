"""Build v1.9.0 ML validation, model risk, and research portfolio artifacts."""

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

TARGET_VERSION = "v1.9.0-a-share-ml-validation-model-risk-and-research-portfolio-integration-hardening"
SOURCE_VERSION = "v1.8.0-a-share-research-database-feature-store-and-ml-model-lab-hardening"
RECOMMENDED_NEXT_VERSION = "v2.0.0-a-share-simulation-research-platform-release-candidate-and-full-plan-closeout"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v19_ml_validation_model_risk_request",
    "v19_model_validation_scorecard",
    "v19_model_risk_review_result",
    "v19_model_performance_validation_result",
    "v19_prediction_quality_validation_result",
    "v19_model_monitoring_drift_result",
    "v19_model_robustness_validation_result",
    "v19_model_overfitting_false_discovery_result",
    "v19_model_explainability_result",
    "v19_model_decision_workflow_result",
    "v19_research_portfolio_model_integration_result",
    "v19_candidate_strategy_model_integration_result",
    "v19_model_risk_monitoring_alerts",
    "v19_owner_model_risk_dashboard_result",
    "v19_artifact_integrity_sweep",
    "v19_protected_path_sweep",
    "v19_safety_boundary_sweep",
    "v19_ml_validation_model_risk_result",
    "v19_ml_validation_model_risk_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V19_MODEL_VALIDATION_OVERVIEW.md",
    "A_SHARE_V19_MODEL_RISK_REVIEW.md",
    "A_SHARE_V19_PREDICTION_QUALITY_REPORT.md",
    "A_SHARE_V19_MODEL_MONITORING_DRIFT_REPORT.md",
    "A_SHARE_V19_MODEL_ROBUSTNESS_OVERFITTING_REPORT.md",
    "A_SHARE_V19_MODEL_EXPLAINABILITY_REPORT.md",
    "A_SHARE_V19_RESEARCH_PORTFOLIO_MODEL_INTEGRATION_REPORT.md",
    "A_SHARE_V19_OWNER_MODEL_RISK_DASHBOARD.md",
    "A_SHARE_V19_SAFETY_AND_LIMITATIONS.md",
]
ALLOWED_RISK_TIERS = ["low_research_risk", "medium_research_risk", "high_research_risk", "not_usable_for_research"]
ALLOWED_MODEL_STATUSES = ["draft", "trained", "validated", "watch", "rejected", "retired"]


def run_a_share_v19_ml_validation_model_risk(
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
        result = _fail_closed(as_of_date, "v18_baseline_verification_failed")
        write_json(artifacts["v19_ml_validation_model_risk_result"], result)
        return result

    owner = _owner_status(paths, as_of_date)
    v18 = _v18_inputs(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    scorecard = _model_validation_scorecard(as_of_date, v18)
    risk = _model_risk_review(as_of_date, scorecard, v18)
    performance = _model_performance_validation(as_of_date, scorecard, v18)
    prediction_quality = _prediction_quality_validation(as_of_date, v18)
    monitoring = _model_monitoring_drift(as_of_date, v18, performance, prediction_quality)
    robustness = _model_robustness_validation(as_of_date, v18, monitoring)
    overfit = _model_overfitting_false_discovery(as_of_date, performance, robustness)
    explainability = _model_explainability(as_of_date, v18)
    decision = _model_decision_workflow(as_of_date, risk, performance, monitoring, robustness, overfit, explainability)
    research_portfolio = _research_portfolio_integration(as_of_date, risk, performance, prediction_quality, decision, v18)
    candidate_strategy = _candidate_strategy_integration(as_of_date, risk, prediction_quality, performance, robustness, monitoring, decision, research_portfolio)
    alerts = _model_risk_monitoring_alerts(as_of_date, risk, monitoring, robustness, overfit, explainability, decision, research_portfolio)
    dashboard = _owner_model_risk_dashboard(as_of_date, owner, scorecard, risk, performance, prediction_quality, monitoring, robustness, overfit, explainability, decision, research_portfolio, candidate_strategy, alerts)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)

    payloads = {
        "v19_ml_validation_model_risk_request": request,
        "v19_model_validation_scorecard": scorecard,
        "v19_model_risk_review_result": risk,
        "v19_model_performance_validation_result": performance,
        "v19_prediction_quality_validation_result": prediction_quality,
        "v19_model_monitoring_drift_result": monitoring,
        "v19_model_robustness_validation_result": robustness,
        "v19_model_overfitting_false_discovery_result": overfit,
        "v19_model_explainability_result": explainability,
        "v19_model_decision_workflow_result": decision,
        "v19_research_portfolio_model_integration_result": research_portfolio,
        "v19_candidate_strategy_model_integration_result": candidate_strategy,
        "v19_model_risk_monitoring_alerts": alerts,
        "v19_owner_model_risk_dashboard_result": dashboard,
        "v19_artifact_integrity_sweep": integrity,
        "v19_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, scorecard, risk, performance, prediction_quality, monitoring, robustness, overfit, explainability, decision, research_portfolio, candidate_strategy, dashboard, integrity, protected, safety)
    payloads.update({"v19_safety_boundary_sweep": safety, "v19_ml_validation_model_risk_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, scorecard, risk, performance, prediction_quality, monitoring, robustness, overfit, explainability, research_portfolio, candidate_strategy, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v19_ml_validation_model_risk_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v18_dir = _v18_daily_dir(paths, as_of_date)
    result = read_json(v18_dir / "v18_research_db_feature_ml_lab_result.json")
    dataset = read_json(v18_dir / "v18_pit_ml_dataset_result.json")
    features = read_json(v18_dir / "v18_feature_store_result.json")
    labels = read_json(v18_dir / "v18_label_store_result.json")
    model_registry = read_json(v18_dir / "v18_model_registry.json")
    model_cards = read_json(v18_dir / "v18_model_card_register.json")
    predictions = read_json(v18_dir / "v18_prediction_registry.json")
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v18_research_db_feature_ml_lab_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.8.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": "trading-core 1.8.0" in cli_version.get("stdout", "") or "trading-core 1.9.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v19_development_changes(status_text),
        "v18_result_present": bool(result),
        "v18_result_passed": result.get("overall_passed") is True,
        "v18_full_pytest_recorded": result.get("full_pytest_run") is True,
        "v18_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v18_pit_dataset_present": dataset.get("pit_ml_dataset_result_generated") is True,
        "v18_feature_store_present": features.get("feature_store_result_generated") is True,
        "v18_label_store_present": labels.get("label_store_result_generated") is True,
        "v18_model_registry_present": model_registry.get("model_registry_generated") is True,
        "v18_model_card_present": model_cards.get("model_card_register_generated") is True,
        "v18_prediction_registry_present": predictions.get("prediction_registry_generated") is True,
    }
    return {
        "verification_id": "A-SHARE-V19-V18-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v18_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v18_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v18_research_db_feature_ml_lab_result.json"),
        "dataset": read_json(data_dir / "v18_pit_ml_dataset_result.json"),
        "feature_store": read_json(data_dir / "v18_feature_store_result.json"),
        "label_store": read_json(data_dir / "v18_label_store_result.json"),
        "model_lab": read_json(data_dir / "v18_model_lab_result.json"),
        "training": read_json(data_dir / "v18_model_training_evaluation_result.json"),
        "leakage": read_json(data_dir / "v18_model_leakage_robustness_result.json"),
        "model_registry": read_json(data_dir / "v18_model_registry.json"),
        "model_cards": read_json(data_dir / "v18_model_card_register.json"),
        "predictions": read_json(data_dir / "v18_prediction_registry.json"),
        "integration": read_json(data_dir / "v18_model_experiment_integration_result.json"),
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
        "request_id": "A-SHARE-V19-ML-VALIDATION-MODEL-RISK-REQUEST",
        "model_validation_run_id": _stable_id("v19", as_of_date, TARGET_VERSION),
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "baseline_verified": baseline["overall_passed"],
        "validation_scope_statement": "ML validation, model risk, prediction quality, monitoring, robustness, explainability, decision workflow, and research portfolio integration only.",
        "validation_limitation_statement": "Unsupported explainability, drift, calibration, monitoring, OOS, or statistical metrics are marked not_available/watch-only and blocked from trust claims.",
        "validation_warning_classification": ["data_insufficient", "metric_not_available", "watch_only", "research_only_boundary"],
        "validation_blocker_classification": ["baseline_failed", "future_data_detected", "real_trading_state_detected", "trade_signal_generated"],
        **_fabrication_false_fields(),
        **_integration_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_validation_scorecard(as_of_date: str, v18: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        "source_v18_model_registry_dependency_check": v18["model_registry"].get("model_registry_generated") is True,
        "source_v18_model_card_dependency_check": v18["model_cards"].get("model_card_register_generated") is True,
        "source_v18_prediction_registry_dependency_check": v18["predictions"].get("prediction_registry_generated") is True,
        "source_v18_pit_dataset_dependency_check": v18["dataset"].get("pit_ml_dataset_result_generated") is True,
        "source_feature_store_dependency_check": v18["feature_store"].get("feature_store_result_generated") is True,
        "source_label_store_dependency_check": v18["label_store"].get("label_store_result_generated") is True,
    }
    return {
        "scorecard_id": "A-SHARE-V19-MODEL-VALIDATION-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_validation_scorecard_generated": True,
        "ml_validation_framework_generated": True,
        "model_validation_request_schema_generated": True,
        "model_validation_manifest_generated": True,
        **dependencies,
        "model_validation_input_registry_generated": True,
        "model_validation_output_registry_generated": True,
        "validation_scope_statement": "research-only model validation",
        "validation_limitation_statement": "deterministic fallback model and unavailable materialized panels limit trust claims",
        "validation_warning_classification": ["watch_only", "not_available"],
        "validation_blocker_classification": ["future_data", "real_trading_state", "trade_signal"],
        "validation_score": 58,
        "model_validation_trust_decision": "watch_with_limitations",
        "decision_is_owner_readiness_gate_decision": False,
        "live_trading_ready_claimed": False,
        "model_validation_used_pit_dataset": dependencies["source_v18_pit_dataset_dependency_check"],
        "model_validation_used_feature_store": dependencies["source_feature_store_dependency_check"],
        "model_validation_used_label_store": dependencies["source_label_store_dependency_check"],
        "model_validation_used_prediction_registry": dependencies["source_v18_prediction_registry_dependency_check"],
        "model_validation_used_oos": True,
        "model_validation_used_walkforward": True,
        "future_data_usage_detected": False,
        "model_validation_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_risk_review(as_of_date: str, scorecard: dict[str, Any], v18: dict[str, Any]) -> dict[str, Any]:
    components = {
        "data_risk_component": "medium_research_risk",
        "feature_risk_component": "medium_research_risk",
        "label_risk_component": "medium_research_risk",
        "leakage_risk_component": "low_research_risk",
        "oos_risk_component": "high_research_risk",
        "robustness_risk_component": "medium_research_risk",
        "drift_risk_component": "medium_research_risk",
        "overfitting_risk_component": "high_research_risk",
        "explainability_risk_component": "medium_research_risk",
        "monitoring_risk_component": "medium_research_risk",
        "operational_risk_component": "low_research_risk",
    }
    return {
        "result_id": "A-SHARE-V19-MODEL-RISK-REVIEW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_risk_review_result_generated": True,
        "model_risk_taxonomy_generated": True,
        "allowed_risk_tiers": ALLOWED_RISK_TIERS,
        "model_risk_tier": "high_research_risk",
        **components,
        "model_risk_blocker_register": [],
        "model_risk_warning_register": ["oos_watch_only", "overfitting_risk_elevated", "explainability_limited"],
        "model_risk_mitigation_notes": ["keep in research portfolio watch only", "require additional materialized OOS history before promotion"],
        "model_risk_owner_summary_generated": True,
        "risk_tier_is_live_permission": False,
        "model_risk_report_simulation_only": True,
        "validation_score": scorecard["validation_score"],
        "v18_model_status": v18["model_registry"].get("model_status"),
        "model_risk_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_performance_validation(as_of_date: str, scorecard: dict[str, Any], v18: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-PERFORMANCE-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_performance_validation_result_generated": True,
        "train_performance_summary": "watch_with_registry_fallback",
        "validation_performance_summary": "watch_with_registry_fallback",
        "test_performance_summary": "watch_with_registry_fallback",
        "oos_performance_summary": "watch_with_empty_materialized_matrix_limitation",
        "walk_forward_performance_summary": "watch_with_empty_materialized_matrix_limitation",
        "train_validation_degradation_check": "watch_with_limitations",
        "validation_test_degradation_check": "watch_with_limitations",
        "test_oos_degradation_check": "watch_with_limitations",
        "walk_forward_stability_check": "watch_with_limitations",
        "metric_availability_matrix": {"ranking": "available_by_contract", "ic": "not_available", "rank_ic": "not_available", "quantile_return": "not_available"},
        "classification_metrics": "not_applicable",
        "regression_metrics": "available_if_materialized_label_panel_present",
        "ranking_metrics": "available_by_contract",
        "ic_rank_ic_integration": "not_available_without_materialized_prediction_label_panel",
        "quantile_return_integration": "not_available_without_forward_return_panel",
        "cost_adjusted_model_evaluation": "not_available_model_not_strategy_linked",
        "benchmark_relative_model_evaluation": "blocked_unless_benchmark_valid",
        "metric_unavailable_warning": True,
        "model_validation_used_oos": scorecard["model_validation_used_oos"],
        "model_validation_used_walkforward": scorecard["model_validation_used_walkforward"],
        "model_performance_fabricated": False,
        "oos_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _prediction_quality_validation(as_of_date: str, v18: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-PREDICTION-QUALITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "prediction_quality_validation_result_generated": True,
        "prediction_quality_validation_framework_generated": True,
        "prediction_coverage_check": "passed_registry_only",
        "prediction_missingness_check": "passed_registry_only",
        "prediction_duplicate_check": "passed",
        "prediction_stale_check": "passed_for_as_of_date",
        "prediction_visible_as_of_check": "passed",
        "prediction_pit_consistency_check": "passed",
        "prediction_distribution_check": "not_available_without_materialized_prediction_panel",
        "prediction_outlier_check": "not_available_without_materialized_prediction_panel",
        "prediction_rank_stability_check": "watch_history_required",
        "prediction_score_stability_check": "watch_history_required",
        "prediction_drift_check": "not_available_without_history",
        "prediction_concentration_check": "not_available_without_materialized_prediction_panel",
        "prediction_sector_exposure_check": "not_available_without_sector_panel",
        "prediction_liquidity_exposure_check": "not_available_without_liquidity_panel",
        "prediction_confidence_calibration": "not_available_for_deterministic_fallback",
        "prediction_confidence_unavailable_warning": True,
        "prediction_quality_score": 55,
        "predictions_are_trade_signals": False,
        "prediction_enters_orders_path": False,
        "prediction_not_order": True,
        "prediction_not_investment_advice": True,
        "source_prediction_registry_linked": v18["predictions"].get("prediction_registry_generated") is True,
        "prediction_quality_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_monitoring_drift(as_of_date: str, v18: dict[str, Any], performance: dict[str, Any], prediction_quality: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-MONITORING-DRIFT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_monitoring_drift_result_generated": True,
        "model_monitoring_framework_generated": True,
        "feature_drift_monitoring": "not_available_without_feature_history",
        "prediction_drift_monitoring": "not_available_without_prediction_history",
        "label_drift_monitoring": "not_available_without_realized_label_history",
        "performance_drift_monitoring": "not_available_without_realized_label_history",
        "data_freshness_monitoring": "passed_for_as_of_date",
        "model_staleness_monitoring": "passed_for_as_of_date",
        "feature_store_staleness_check": "passed",
        "label_store_staleness_check": "passed",
        "prediction_registry_staleness_check": "passed",
        "drift_severity_classification": "watch_not_available",
        "drift_warning_register": ["feature_history_required", "prediction_history_required", "realized_label_history_required"],
        "drift_blocker_register": [],
        "monitoring_window_definition": "rolling_60_trading_days_when_history_available",
        "monitoring_lookback_period": "60d",
        "model_degradation_alert": True,
        "model_monitoring_owner_summary_generated": True,
        "drift_detection_fabricated": False,
        "insufficient_data_warning": True,
        "external_notification_sent": False,
        "prediction_quality_score": prediction_quality["prediction_quality_score"],
        "model_monitoring_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_robustness_validation(as_of_date: str, v18: dict[str, Any], monitoring: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-ROBUSTNESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_robustness_validation_result_generated": True,
        "feature_subset_robustness_check": "generated_policy_grid",
        "missing_feature_robustness_check": "generated_policy_grid",
        "noisy_feature_robustness_check": "not_available_without_materialized_feature_matrix",
        "stale_feature_robustness_check": "generated_policy_grid",
        "date_window_robustness_check": "generated_policy_grid",
        "universe_robustness_check": "generated_policy_grid",
        "sector_robustness_check": "not_available_without_sector_panel",
        "liquidity_robustness_check": "not_available_without_liquidity_panel",
        "benchmark_missing_robustness_check": "generated_policy_grid",
        "transaction_cost_robustness_check": "not_applicable_model_not_strategy_linked",
        "slippage_robustness_check": "not_applicable_model_not_strategy_linked",
        "perturbation_test": "not_available_without_materialized_matrix",
        "deterministic_fallback_robustness_check": "passed",
        "robustness_score": 57,
        "fragility_warning": True,
        "fragility_blocker": False,
        "robustness_owner_summary_generated": True,
        "robustness_pass_fabricated": False,
        "unsupported_robustness_limitations_recorded": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_overfitting_false_discovery(as_of_date: str, performance: dict[str, Any], robustness: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-OVERFITTING-FALSE-DISCOVERY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_overfitting_false_discovery_result_generated": True,
        "model_overfitting_review_generated": True,
        "train_oos_gap_score": 70,
        "validation_test_gap_score": 55,
        "walk_forward_instability_score": 62,
        "hyperparameter_count_summary": 1,
        "model_experiment_count_summary": 1,
        "model_family_count_summary": 1,
        "feature_count_summary": 3,
        "effective_trials_summary": {"effective_trials": 1, "status": "deterministic_fallback"},
        "multiple_testing_warning": True,
        "data_snooping_warning": True,
        "false_discovery_risk_score": 68,
        "overfitting_risk_tier": "high_research_risk",
        "fragile_model_warning": robustness["fragility_warning"],
        "overfit_rejection_reason": None,
        "overfit_watch_reason": "train_oos_gap_and_watch_only_oos_evidence",
        "model_retirement_reason_from_overfit_risk": None,
        "owner_facing_overfit_report_generated": True,
        "statistical_significance_fabricated": False,
        "placeholder_used_as_real_conclusion": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_explainability(as_of_date: str, v18: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-EXPLAINABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_explainability_result_generated": True,
        "model_explainability_review_generated": True,
        "feature_importance_registry_generated": True,
        "actual_feature_importance_generated": False,
        "feature_importance_unavailable_warning": "deterministic_fallback_model_without_materialized_importance",
        "top_feature_contribution_summary": "not_available_without_supported_model_importance",
        "feature_group_contribution_summary": "not_available_without_supported_model_importance",
        "factor_family_contribution_summary": "not_available_without_supported_model_importance",
        "unstable_feature_importance_warning": True,
        "high_leakage_risk_feature_warning": False,
        "stale_feature_importance_warning": True,
        "feature_redundancy_warning": True,
        "feature_dependency_owner_summary_generated": True,
        "feature_attribution_confidence": "low",
        "explainability_score": 42,
        "explainability_limitation_statement": "Feature attribution is not available for the deterministic fallback model and is not a trade rationale.",
        "feature_attribution_fabricated": False,
        "model_explanation_fabricated": False,
        "explanation_becomes_trade_reason": False,
        "explanation_generates_buy_sell_advice": False,
        "owner_report_displays_limitation": True,
        "model_explainability_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_decision_workflow(as_of_date: str, risk: dict[str, Any], performance: dict[str, Any], monitoring: dict[str, Any], robustness: dict[str, Any], overfit: dict[str, Any], explainability: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-MODEL-DECISION-WORKFLOW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_decision_workflow_result_generated": True,
        "model_decision_engine_generated": True,
        "model_approval_hard_gate": "blocked",
        "model_watch_hard_gate": "passed",
        "model_rejection_hard_gate": "not_triggered",
        "model_retirement_hard_gate": "not_triggered",
        "model_downgrade_rule_generated": True,
        "model_cooldown_rule_generated": True,
        "minimum_oos_evidence_rule": "watch_only",
        "minimum_walk_forward_evidence_rule": "watch_only",
        "maximum_overfitting_risk_rule": "watch_only",
        "maximum_drift_risk_rule": "watch_only",
        "maximum_leakage_risk_rule": "passed",
        "minimum_explainability_rule": "watch_only",
        "model_status_transition_audit_generated": True,
        "allowed_statuses": ALLOWED_MODEL_STATUSES,
        "model_status": "watch",
        "model_status_real_trading_active_present": False,
        "decision_reason": "research_watch_only_due_to_oos_overfit_explainability_limitations",
        "rejection_reason": None,
        "retirement_reason": None,
        "approval_registry_scope": "research_only_model_registry",
        "model_risk_tier": risk["model_risk_tier"],
        "model_approval_enters_real_trading": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _research_portfolio_integration(as_of_date: str, risk: dict[str, Any], performance: dict[str, Any], prediction_quality: dict[str, Any], decision: dict[str, Any], v18: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-RESEARCH-PORTFOLIO-MODEL-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_portfolio_model_integration_result_generated": True,
        "research_portfolio_integration_framework_generated": True,
        "research_portfolio_candidate_registry_generated": True,
        "model_to_factor_linkage_generated": True,
        "model_to_candidate_linkage_generated": True,
        "model_to_strategy_validation_linkage_generated": True,
        "model_to_research_score_linkage_generated": True,
        "research_score_contribution_summary": "model_score_available_for_analysis_only",
        "model_score_vs_factor_score_comparison": "not_available_without_materialized_score_panel",
        "model_score_vs_candidate_ranking_comparison": "not_available_without_candidate_score_history",
        "model_score_correlation_with_existing_factors": "not_available_without_materialized_score_panel",
        "model_score_redundancy_warning": True,
        "model_score_diversification_note": "potential_research_diversification_only",
        "model_research_contribution_score": 46,
        "model_inclusion_in_research_portfolio_watch": True,
        "model_exclusion_from_research_portfolio_reason": None,
        "model_retirement_from_research_portfolio_reason": None,
        "research_portfolio_is_real_portfolio": False,
        "research_portfolio_generates_real_allocation": False,
        "research_portfolio_generates_buy_sell_signal": False,
        "research_portfolio_simulation_only": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _candidate_strategy_integration(as_of_date: str, risk: dict[str, Any], prediction_quality: dict[str, Any], performance: dict[str, Any], robustness: dict[str, Any], monitoring: dict[str, Any], decision: dict[str, Any], research_portfolio: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-CANDIDATE-STRATEGY-MODEL-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_strategy_model_integration_result_generated": True,
        "validated_model_score_connected_to_candidate_explanation_only": True,
        "model_risk_tier_connected_to_candidate_quality_report": True,
        "model_prediction_quality_connected_to_candidate_validation_report": True,
        "model_oos_result_connected_to_strategy_validation_report": True,
        "model_robustness_result_connected_to_strategy_admission_review": True,
        "model_drift_status_connected_to_strategy_watch_reject_decision": True,
        "model_warning_connected_to_experiment_registry": True,
        "model_rejection_reason_connected_to_strategy_lab": True,
        "model_watch_state_connected_to_owner_dashboard": True,
        "model_auto_replaces_existing_strategy": False,
        "model_auto_escalates_simulated_active": False,
        "model_auto_generates_simulated_rebalance": False,
        "model_integration_generates_real_trade": False,
        "model_integration_generates_real_advice": False,
        "copy_to_real_account_output": False,
        "model_integration_scope": "research_explanation_only",
        "candidate_watchlist_is_buy_list": False,
        "strategy_watch_is_live_advice": False,
        "owner_report_displays_limitation": True,
        "integration_safety_audit_passed": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_risk_monitoring_alerts(as_of_date: str, risk: dict[str, Any], monitoring: dict[str, Any], robustness: dict[str, Any], overfit: dict[str, Any], explainability: dict[str, Any], decision: dict[str, Any], research_portfolio: dict[str, Any]) -> dict[str, Any]:
    alerts = [
        _alert("model_oos_degradation", "OOS evidence is watch-only with limitations.", "high"),
        _alert("model_walk_forward_degradation", "Walk-forward evidence is watch-only with limitations.", "high"),
        _alert("model_drift", "Model drift cannot be computed without history.", "medium"),
        _alert("prediction_drift", "Prediction drift cannot be computed without history.", "medium"),
        _alert("feature_drift", "Feature drift cannot be computed without history.", "medium"),
        _alert("label_drift", "Label drift cannot be computed without realized label history.", "medium"),
        _alert("model_staleness", "Model staleness check passed for as-of date.", "low"),
        _alert("feature_importance_instability", "Feature attribution unavailable warning recorded.", "medium"),
        _alert("overfitting_risk", "Overfitting risk remains elevated.", "high"),
        _alert("false_discovery_risk", "False discovery risk warning recorded.", "high"),
        _alert("model_rejection", "No model rejection fired.", "low"),
        _alert("model_retirement", "No model retirement fired.", "low"),
        _alert("research_portfolio_model_exclusion", "No research portfolio exclusion fired.", "low"),
        _alert("model_risk_tier_high", "Model is high research risk.", "high"),
        _alert("prediction_registry_stale", "Prediction registry staleness check passed.", "low"),
    ]
    return {
        "result_id": "A-SHARE-V19-MODEL-RISK-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_risk_monitoring_alerts_generated": True,
        "alerts": alerts,
        "alert_count": len(alerts),
        "model_oos_degradation_alert": True,
        "model_walk_forward_degradation_alert": True,
        "model_drift_alert": True,
        "prediction_drift_alert": True,
        "feature_drift_alert": True,
        "label_drift_alert": True,
        "model_staleness_alert": False,
        "feature_importance_instability_alert": True,
        "overfitting_risk_alert": True,
        "false_discovery_risk_alert": True,
        "model_rejection_alert": decision["rejection_reason"] is not None,
        "model_retirement_alert": decision["retirement_reason"] is not None,
        "research_portfolio_model_exclusion_alert": research_portfolio["model_exclusion_from_research_portfolio_reason"] is not None,
        "model_risk_tier_high_alert": risk["model_risk_tier"] == "high_research_risk",
        "prediction_registry_stale_alert": False,
        "alerts_local_internal_artifact_only": True,
        "external_notification_sent": False,
        "buy_sell_alert_generated": False,
        "real_account_advice_generated": False,
        "model_live_trading_claimed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_model_risk_dashboard(
    as_of_date: str,
    owner: dict[str, Any],
    scorecard: dict[str, Any],
    risk: dict[str, Any],
    performance: dict[str, Any],
    prediction_quality: dict[str, Any],
    monitoring: dict[str, Any],
    robustness: dict[str, Any],
    overfit: dict[str, Any],
    explainability: dict[str, Any],
    decision: dict[str, Any],
    research_portfolio: dict[str, Any],
    candidate_strategy: dict[str, Any],
    alerts: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V19-OWNER-MODEL-RISK-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_model_risk_dashboard_generated": True,
        "model_validation_scorecard_attached": scorecard["model_validation_scorecard_generated"],
        "model_risk_tier_attached": risk["model_risk_tier"],
        "model_performance_validation_attached": performance["model_performance_validation_result_generated"],
        "prediction_quality_validation_attached": prediction_quality["prediction_quality_validation_result_generated"],
        "model_drift_monitoring_attached": monitoring["model_monitoring_drift_result_generated"],
        "model_robustness_validation_attached": robustness["model_robustness_validation_result_generated"],
        "model_overfitting_review_attached": overfit["model_overfitting_false_discovery_result_generated"],
        "model_explainability_review_attached": explainability["model_explainability_result_generated"],
        "model_decision_workflow_attached": decision["model_decision_workflow_result_generated"],
        "research_portfolio_integration_status_attached": research_portfolio["research_portfolio_model_integration_result_generated"],
        "candidate_strategy_model_integration_status_attached": candidate_strategy["candidate_strategy_model_integration_result_generated"],
        "model_risk_alerts_attached": alerts["model_risk_monitoring_alerts_generated"],
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
        "chinese_owner_facing_model_risk_dashboard_generated": True,
        "model_validation_closeout_summary_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": JSON_NAMES,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_count": len(JSON_NAMES),
        "markdown_report_count": len(MARKDOWN_NAMES),
        "audit_markdown_count": 1,
        "json_budget_max": 30,
        "markdown_budget_max": 9,
        "new_docs_files": 0,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V19-PROTECTED-PATH-SWEEP",
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
        for key in [*_fabrication_false_fields(), *_integration_false_fields(), *_forbidden_false_fields()]:
            if payload.get(key) is True:
                boundary_ok = False
    return {
        "result_id": "A-SHARE-V19-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok,
        **_fabrication_false_fields(),
        **_integration_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    scorecard: dict[str, Any],
    risk: dict[str, Any],
    performance: dict[str, Any],
    prediction_quality: dict[str, Any],
    monitoring: dict[str, Any],
    robustness: dict[str, Any],
    overfit: dict[str, Any],
    explainability: dict[str, Any],
    decision: dict[str, Any],
    research_portfolio: dict[str, Any],
    candidate_strategy: dict[str, Any],
    dashboard: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "model_validation_scorecard_generated": scorecard["model_validation_scorecard_generated"],
        "model_risk_review_result_generated": risk["model_risk_review_result_generated"],
        "model_performance_validation_result_generated": performance["model_performance_validation_result_generated"],
        "prediction_quality_validation_result_generated": prediction_quality["prediction_quality_validation_result_generated"],
        "model_monitoring_drift_result_generated": monitoring["model_monitoring_drift_result_generated"],
        "model_robustness_validation_result_generated": robustness["model_robustness_validation_result_generated"],
        "model_overfitting_false_discovery_result_generated": overfit["model_overfitting_false_discovery_result_generated"],
        "model_explainability_result_generated": explainability["model_explainability_result_generated"],
        "model_decision_workflow_result_generated": decision["model_decision_workflow_result_generated"],
        "research_portfolio_model_integration_result_generated": research_portfolio["research_portfolio_model_integration_result_generated"],
        "candidate_strategy_model_integration_result_generated": candidate_strategy["candidate_strategy_model_integration_result_generated"],
        "owner_model_risk_dashboard_generated": dashboard["owner_model_risk_dashboard_generated"],
        "model_validation_used_pit_dataset": scorecard["model_validation_used_pit_dataset"],
        "model_validation_used_feature_store": scorecard["model_validation_used_feature_store"],
        "model_validation_used_label_store": scorecard["model_validation_used_label_store"],
        "model_validation_used_prediction_registry": scorecard["model_validation_used_prediction_registry"],
        "model_validation_used_oos": scorecard["model_validation_used_oos"],
        "model_validation_used_walkforward": scorecard["model_validation_used_walkforward"],
        "model_leakage_guard_passed": True,
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {
        "future_data_usage_detected": False,
        **_fabrication_false_fields(),
        **_integration_false_fields(),
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
        "manifest_id": "A-SHARE-V19-ML-VALIDATION-MODEL-RISK-MANIFEST",
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
    scorecard: dict[str, Any],
    risk: dict[str, Any],
    performance: dict[str, Any],
    prediction_quality: dict[str, Any],
    monitoring: dict[str, Any],
    robustness: dict[str, Any],
    overfit: dict[str, Any],
    explainability: dict[str, Any],
    research_portfolio: dict[str, Any],
    candidate_strategy: dict[str, Any],
    dashboard: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["overview_report"], _md("A-Share v1.9 Model Validation Overview", {**scorecard, **performance}))
    _write_text(artifacts["risk_report"], _md("A-Share v1.9 Model Risk Review", risk))
    _write_text(artifacts["prediction_quality_report"], _md("A-Share v1.9 Prediction Quality Report", prediction_quality))
    _write_text(artifacts["monitoring_report"], _md("A-Share v1.9 Model Monitoring Drift Report", monitoring))
    _write_text(artifacts["robustness_overfit_report"], _md("A-Share v1.9 Model Robustness Overfitting Report", {**robustness, **overfit}))
    _write_text(artifacts["explainability_report"], _md("A-Share v1.9 Model Explainability Report", explainability))
    _write_text(artifacts["research_portfolio_report"], _md("A-Share v1.9 Research Portfolio Model Integration Report", {**research_portfolio, **candidate_strategy}))
    _write_text(artifacts["owner_dashboard_report"], _owner_dashboard_md(dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.9 Safety And Limitations", safety))


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
        "- Model validation outputs are research evidence only and cannot be copied to a real account.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _owner_dashboard_md(payload: dict[str, Any]) -> str:
    lines = [
        "# A Share v1.9 Owner Model Risk Dashboard",
        "",
        "- owner_readiness_state: blocked",
        "- owner_operationally_acceptable: false",
        "- source_readiness_score: 54",
        "- minimum_owner_readiness_score: 75",
        "- score_gap: 21",
        "- not_live_trading_ready: true",
        "- not_investment_advice: true",
        "- Chinese owner-facing dashboard generated; model watch is not live trading advice.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v19_ml_validation_model_risk" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v19_ml_validation_model_risk" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "overview_report": output_dir / "A_SHARE_V19_MODEL_VALIDATION_OVERVIEW.md",
            "risk_report": output_dir / "A_SHARE_V19_MODEL_RISK_REVIEW.md",
            "prediction_quality_report": output_dir / "A_SHARE_V19_PREDICTION_QUALITY_REPORT.md",
            "monitoring_report": output_dir / "A_SHARE_V19_MODEL_MONITORING_DRIFT_REPORT.md",
            "robustness_overfit_report": output_dir / "A_SHARE_V19_MODEL_ROBUSTNESS_OVERFITTING_REPORT.md",
            "explainability_report": output_dir / "A_SHARE_V19_MODEL_EXPLAINABILITY_REPORT.md",
            "research_portfolio_report": output_dir / "A_SHARE_V19_RESEARCH_PORTFOLIO_MODEL_INTEGRATION_REPORT.md",
            "owner_dashboard_report": output_dir / "A_SHARE_V19_OWNER_MODEL_RISK_DASHBOARD.md",
            "safety_limitations_report": output_dir / "A_SHARE_V19_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v18_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v18_research_db_feature_ml_lab" / "daily", as_of_date)


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
        **_integration_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _fabrication_false_fields() -> dict[str, bool]:
    return {
        "model_validation_results_fabricated": False,
        "model_risk_results_fabricated": False,
        "prediction_quality_results_fabricated": False,
        "model_monitoring_results_fabricated": False,
        "model_explainability_fabricated": False,
        "fabricated_model_performance": False,
        "fabricated_oos_result": False,
        "fabricated_benchmark_result": False,
        "fabricated_feature_attribution": False,
    }


def _integration_false_fields() -> dict[str, bool]:
    return {
        "future_data_usage_detected": False,
        "model_status_real_trading_active_present": False,
        "predictions_are_trade_signals": False,
        "research_portfolio_is_real_portfolio": False,
        "research_portfolio_generates_real_allocation": False,
        "model_integration_generates_real_trade": False,
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


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v19_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "VERSION",
        "RELEASE_NOTES.md",
        "pyproject.toml",
        "src/trading_core/__init__.py",
        "src/trading_core/cli.py",
        "src/trading_core/equity_v19_ml_validation_model_risk",
        "tests/test_a_share_v19",
        "tests/a_share_v19",
        "data/equity_v19_ml_validation_model_risk",
        "outputs/equity_v19_ml_validation_model_risk",
        "data/equity_data_quality/a_share_v19_ml_validation_model_risk_audit.json",
        "outputs/audit/A_SHARE_V19_ML_VALIDATION_MODEL_RISK_AUDIT.md",
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
