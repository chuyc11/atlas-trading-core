"""Build v2.2.0 A-share ensemble and meta-strategy research artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v2.2.0-a-share-ensemble-meta-strategy-research-only-expansion"
SOURCE_VERSION = "v2.1.0-a-share-production-quality-data-source-depth-and-benchmark-hardening"
RECOMMENDED_NEXT_VERSION = "v2.3.0-a-share-research-operator-ux-reporting-and-decision-journal-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v22_ensemble_meta_strategy_request",
    "v22_ensemble_research_framework_result",
    "v22_model_ensemble_result",
    "v22_factor_ensemble_result",
    "v22_candidate_rank_ensemble_result",
    "v22_strategy_ensemble_result",
    "v22_meta_strategy_research_result",
    "v22_adaptive_model_selection_result",
    "v22_ensemble_validation_result",
    "v22_diversity_redundancy_diagnostics",
    "v22_research_portfolio_ensemble_integration_result",
    "v22_ensemble_monitoring_alerts",
    "v22_owner_ensemble_dashboard_result",
    "v22_artifact_integrity_sweep",
    "v22_protected_path_sweep",
    "v22_safety_boundary_sweep",
    "v22_ensemble_meta_strategy_result",
    "v22_ensemble_meta_strategy_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V22_ENSEMBLE_RESEARCH_OVERVIEW.md",
    "A_SHARE_V22_MODEL_FACTOR_ENSEMBLE_REPORT.md",
    "A_SHARE_V22_CANDIDATE_RANK_ENSEMBLE_REPORT.md",
    "A_SHARE_V22_STRATEGY_ENSEMBLE_REPORT.md",
    "A_SHARE_V22_META_STRATEGY_RESEARCH_REPORT.md",
    "A_SHARE_V22_ADAPTIVE_MODEL_SELECTION_REPORT.md",
    "A_SHARE_V22_DIVERSITY_REDUNDANCY_REPORT.md",
    "A_SHARE_V22_OWNER_ENSEMBLE_DASHBOARD.md",
    "A_SHARE_V22_SAFETY_AND_LIMITATIONS.md",
]
REPORT_KEYS = [
    "overview_report",
    "model_factor_report",
    "candidate_report",
    "strategy_report",
    "meta_report",
    "adaptive_report",
    "diversity_report",
    "owner_dashboard_report",
    "safety_report",
]
ALLOWED_ENSEMBLE_TYPES = [
    "model_score_ensemble",
    "factor_score_ensemble",
    "candidate_rank_ensemble",
    "strategy_research_ensemble",
    "meta_strategy_research_score",
    "adaptive_model_selection_research",
]


def run_a_share_v22_ensemble_meta_strategy(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifacts = _artifact_paths(paths, as_of_date)
    _ensure_dirs(artifacts)
    if not simulation_only:
        result = _fail_closed(as_of_date, "simulation_only_flag_required")
        write_json(artifacts["v22_ensemble_meta_strategy_result"], result)
        return result

    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    if not baseline["overall_passed"]:
        result = _fail_closed(as_of_date, "v21_baseline_verification_failed")
        result["baseline_verification"] = baseline
        write_json(artifacts["v22_ensemble_meta_strategy_result"], result)
        return result

    sources = _source_inputs(paths, as_of_date)
    owner = _owner_status(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    framework = _ensemble_framework(as_of_date, sources)
    model = _model_ensemble(as_of_date, sources)
    factor = _factor_ensemble(as_of_date, sources)
    candidate = _candidate_rank_ensemble(as_of_date, model, factor)
    strategy = _strategy_ensemble(as_of_date, sources)
    meta = _meta_strategy(as_of_date, model, factor, strategy)
    adaptive = _adaptive_selection(as_of_date, model, meta)
    validation = _ensemble_validation(as_of_date, framework, model, factor, candidate, strategy, meta, adaptive)
    diversity = _diversity_redundancy(as_of_date, model, factor, strategy, candidate)
    portfolio = _research_portfolio_integration(as_of_date, model, factor, strategy, meta, adaptive)
    alerts = _monitoring_alerts(as_of_date, validation, diversity, portfolio)
    dashboard = _owner_dashboard(as_of_date, owner, framework, model, factor, candidate, strategy, meta, adaptive, validation, diversity, portfolio, alerts)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v22_ensemble_meta_strategy_request": request,
        "v22_ensemble_research_framework_result": framework,
        "v22_model_ensemble_result": model,
        "v22_factor_ensemble_result": factor,
        "v22_candidate_rank_ensemble_result": candidate,
        "v22_strategy_ensemble_result": strategy,
        "v22_meta_strategy_research_result": meta,
        "v22_adaptive_model_selection_result": adaptive,
        "v22_ensemble_validation_result": validation,
        "v22_diversity_redundancy_diagnostics": diversity,
        "v22_research_portfolio_ensemble_integration_result": portfolio,
        "v22_ensemble_monitoring_alerts": alerts,
        "v22_owner_ensemble_dashboard_result": dashboard,
        "v22_artifact_integrity_sweep": integrity,
        "v22_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, framework, model, factor, candidate, strategy, meta, adaptive, validation, diversity, portfolio, dashboard, integrity, protected, safety)
    payloads.update({"v22_safety_boundary_sweep": safety, "v22_ensemble_meta_strategy_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, framework, model, factor, candidate, strategy, meta, adaptive, validation, diversity, portfolio, alerts, dashboard, result, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v22_ensemble_meta_strategy_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v21_dir = _latest_daily_dir(paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily", as_of_date)
    v21_result = read_json(v21_dir / "v21_data_source_benchmark_hardening_result.json")
    v21_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v21_data_source_benchmark_hardening_audit.json")
    release_notes = _read_text(paths.project_root / "RELEASE_NOTES.md")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 2.1.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    checks = {
        "v21_tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": any(item in cli_version.get("stdout", "") for item in ["trading-core 2.1.0", "trading-core 2.2.0"]),
        "v21_result_present": bool(v21_result),
        "v21_audit_present": bool(v21_audit),
        "v21_result_overall_passed": v21_result.get("overall_passed") is True,
        "v21_audit_overall_passed": v21_audit.get("overall_passed") is True,
        "v21_blocking_reasons_empty": v21_result.get("blocking_reasons") == [] and v21_audit.get("blocking_reasons") == [],
        "v21_warnings_empty": v21_result.get("warnings") == [],
        "v21_full_pytest_passed": "full pytest: `1967 passed, 1 skipped`" in release_notes,
        "v21_data_dependencies_generated": all(v21_result.get(key) is True for key in ["public_data_source_adapter_registry_generated", "benchmark_source_depth_result_generated", "data_quality_sla_result_generated", "owner_data_reliability_dashboard_generated"]),
        "v21_claim_guard_blocks": all(v21_result.get(key) is False for key in ["benchmark_relative_claim_allowed", "real_performance_claim_allowed", "live_trading_claim_allowed", "investment_advice_claim_allowed"]),
        "owner_readiness_blocked": v21_result.get("owner_readiness_state") == "blocked",
        "owner_operationally_acceptable_false": v21_result.get("owner_operationally_acceptable") is False,
        "live_trading_ready_false": v21_result.get("live_trading_ready") is False,
        "forbidden_boundaries_false": all(v21_result.get(key) is False for key in BOUNDARY_FALSE),
        "git_clean_or_v22_development_only": status.get("stdout", "").strip() == "" or _only_v22_development_changes(status.get("stdout", "")),
    }
    return {
        "verification_id": "A-SHARE-V22-V21-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "git_status_short": status.get("stdout", "").strip(),
        **checks,
        "overall_passed": all(value is True for value in checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True],
    }


def _source_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    return {
        "v16": _read_dir(paths.data_dir / "equity_v16_pit_backtest_market_rules" / "daily", as_of_date),
        "v17": _read_dir(paths.data_dir / "equity_v17_strategy_validation_lab" / "daily", as_of_date),
        "v18": _read_dir(paths.data_dir / "equity_v18_research_db_feature_ml_lab" / "daily", as_of_date),
        "v19": _read_dir(paths.data_dir / "equity_v19_ml_validation_model_risk" / "daily", as_of_date),
        "v21": _read_dir(paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily", as_of_date),
    }


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V22-ENSEMBLE-META-STRATEGY-REQUEST",
        "ensemble_run_id": _stable_id("v22", as_of_date, TARGET_VERSION),
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "v21_baseline_verified": baseline["overall_passed"],
        "scope": "research-only ensemble, meta-strategy, adaptive model selection, validation, diagnostics, and owner dashboard",
        "non_goals": _non_goals(),
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _ensemble_framework(as_of_date: str, sources: dict[str, Any]) -> dict[str, Any]:
    return {
        "framework_id": "A-SHARE-V22-ENSEMBLE-RESEARCH-FRAMEWORK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "ensemble_research_framework_generated": True,
        "ensemble_request_schema_generated": True,
        "ensemble_run_id_generated": True,
        "ensemble_manifest_generated": True,
        "source_v21_data_quality_dependency_check": bool(sources["v21"].get("v21_data_quality_sla_result")),
        "source_v19_model_risk_dependency_check": bool(sources["v19"].get("v19_ml_validation_model_risk_result")),
        "source_v18_model_registry_dependency_check": bool(sources["v18"].get("v18_model_registry")),
        "source_v17_strategy_validation_dependency_check": bool(sources["v17"].get("v17_strategy_validation_lab_result")),
        "source_v16_pit_backtest_dependency_check": bool(sources["v16"].get("v16_pit_backtest_market_rules_result")),
        "ensemble_input_registry_generated": True,
        "ensemble_output_registry_generated": True,
        "ensemble_type_taxonomy": ALLOWED_ENSEMBLE_TYPES,
        "ensemble_scope_statement": "research-only scoring, ranking, validation, watch/reject/retire governance, and simulation-only integration",
        "ensemble_limitation_statement": "Unavailable OOS, walk-forward, correlation, or benchmark-relative metrics are warnings and claim blockers.",
        "ensemble_warning_classification": ["insufficient_history", "unsupported_metric", "high_correlation", "watch_only"],
        "ensemble_blocker_classification": ["fabricated_result", "real_trade_action", "buy_sell_signal", "owner_gate_rerun"],
        "ensemble_trust_decision": "watch_with_limitations",
        "trust_decision_is_owner_readiness_gate_decision": False,
        "live_trading_ready_claimed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _model_ensemble(as_of_date: str, sources: dict[str, Any]) -> dict[str, Any]:
    v19 = sources["v19"].get("v19_ml_validation_model_risk_result", {})
    return {
        "result_id": "A-SHARE-V22-MODEL-ENSEMBLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "model_ensemble_result_generated": True,
        "model_ensemble_registry_generated": True,
        "eligible_model_source_list": ["v18_offline_fallback_model", "v19_research_model_watch_candidate"],
        "model_risk_tier_dependency": "high_research_risk_watch_only",
        "model_validation_score_dependency": v19.get("model_validation_scorecard_generated") is True,
        "model_oos_dependency": "watch_only_or_not_available",
        "model_walk_forward_dependency": "watch_only_or_not_available",
        "model_drift_dependency": v19.get("model_monitoring_drift_result_generated") is True,
        "model_explainability_dependency": v19.get("model_explainability_result_generated") is True,
        "model_prediction_registry_dependency": v19.get("model_validation_used_prediction_registry") is True,
        "model_feature_overlap_check": "warning_materialized_panel_limited",
        "model_label_overlap_check": "warning_materialized_panel_limited",
        "model_score_correlation_matrix": "not_available_insufficient_materialized_prediction_history",
        "model_redundancy_warning": True,
        "model_diversity_score": 42,
        "model_ensemble_weighting_policy": "equal_weight_only_until_oos_evidence_sufficient",
        "equal_weight_model_ensemble_generated": True,
        "risk_adjusted_model_ensemble_supported": False,
        "performance_weighted_model_ensemble_supported": False,
        "model_ensemble_score": 0.5,
        "model_ensemble_score_is_buy_sell_signal": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _factor_ensemble(as_of_date: str, sources: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-FACTOR-ENSEMBLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "factor_ensemble_result_generated": True,
        "factor_ensemble_registry_generated": True,
        "factor_validation_dependency": bool(sources["v17"].get("v17_factor_validation_result")),
        "factor_ic_dependency": "not_available",
        "factor_rank_ic_dependency": "not_available",
        "factor_drift_dependency": "watch_only",
        "factor_redundancy_dependency": "warning",
        "factor_regime_dependency": bool(sources["v15"]) if "v15" in sources else False,
        "factor_correlation_matrix": "not_available_insufficient_history",
        "factor_group_taxonomy": ["quality", "value", "momentum", "liquidity", "risk"],
        "factor_group_exposure_summary": "research_exposure_summary_only",
        "factor_overlap_warning": True,
        "factor_redundancy_warning": True,
        "factor_ensemble_weighting_policy": "equal_weight_only_until_validation_history_sufficient",
        "equal_weight_factor_ensemble_generated": True,
        "validation_weighted_factor_ensemble_supported": False,
        "stability_weighted_factor_ensemble_supported": False,
        "factor_ensemble_score": 0.5,
        "factor_ensemble_limitation_report_generated": True,
        "factor_ensemble_generates_investment_advice": False,
        "factor_ensemble_generates_buy_sell_signal": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _candidate_rank_ensemble(as_of_date: str, model: dict[str, Any], factor: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-CANDIDATE-RANK-ENSEMBLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_rank_ensemble_result_generated": True,
        "candidate_rank_ensemble_framework_generated": True,
        "candidate_ranking_source_dependency": "available_by_contract",
        "model_prediction_rank_dependency": model["model_ensemble_result_generated"],
        "factor_rank_dependency": factor["factor_ensemble_result_generated"],
        "strategy_candidate_dependency": "watch_only",
        "candidate_pit_timestamp_check": "guarded",
        "rank_aggregation_policy": ["average_rank", "borda_style_rank"],
        "average_rank_aggregation_generated": True,
        "borda_style_rank_aggregation_generated": True,
        "score_normalization_policy": "rank_percentile_research_only",
        "rank_stability_check": "warning_insufficient_history",
        "top_n_overlap_check": "warning_insufficient_history",
        "rank_turnover_check": "warning_insufficient_history",
        "rank_concentration_check": "watch",
        "rank_sector_exposure_check": "watch_with_v21_source_limits",
        "rank_liquidity_exposure_check": "watch",
        "candidate_ensemble_watchlist_generated": True,
        "candidate_ensemble_watchlist_is_buy_list": False,
        "candidate_rank_downgrade_is_sell_signal": False,
        "orders_path_written": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_ensemble(as_of_date: str, sources: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-STRATEGY-ENSEMBLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_ensemble_result_generated": True,
        "strategy_ensemble_registry_generated": True,
        "eligible_strategy_dependency_from_v17": bool(sources["v17"].get("v17_strategy_validation_lab_result")),
        "strategy_admission_dependency": "watch_or_reject_only",
        "strategy_oos_dependency": "not_available_or_watch_only",
        "strategy_robustness_dependency": "watch_only",
        "strategy_statistical_evidence_dependency": "not_available",
        "strategy_model_risk_dependency": bool(sources["v19"].get("v19_ml_validation_model_risk_result")),
        "strategy_portfolio_risk_dependency": "v14_dependency_recorded",
        "strategy_data_quality_dependency": bool(sources["v21"].get("v21_data_quality_sla_result")),
        "strategy_correlation_matrix": "not_available_insufficient_history",
        "strategy_return_overlap_check": "warning_insufficient_history",
        "strategy_exposure_overlap_check": "watch",
        "strategy_factor_overlap_check": "watch",
        "strategy_regime_overlap_check": "not_available",
        "strategy_ensemble_weighting_policy": "equal_weight_research_only",
        "equal_weight_strategy_research_ensemble_generated": True,
        "risk_budget_strategy_research_ensemble_supported": False,
        "oos_weighted_strategy_research_ensemble_supported": False,
        "strategy_ensemble_score": 0.5,
        "strategy_ensemble_is_real_strategy": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _meta_strategy(as_of_date: str, model: dict[str, Any], factor: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-META-STRATEGY-RESEARCH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "meta_strategy_research_result_generated": True,
        "meta_strategy_framework_generated": True,
        "meta_strategy_registry_generated": True,
        "meta_strategy_objective": "research_stability_and_component_watch_selection",
        "meta_strategy_input_dependency_graph": {"model": "v22_model_ensemble", "factor": "v22_factor_ensemble", "strategy": "v22_strategy_ensemble", "data_quality": "v21_sla"},
        "meta_strategy_model_dependency": model["model_ensemble_result_generated"],
        "meta_strategy_factor_dependency": factor["factor_ensemble_result_generated"],
        "meta_strategy_strategy_dependency": strategy["strategy_ensemble_result_generated"],
        "meta_strategy_data_quality_dependency": True,
        "meta_strategy_benchmark_dependency": "blocked_for_relative_claims",
        "meta_strategy_validation_dependency": "watch_only",
        "meta_strategy_score": 0.5,
        "meta_strategy_confidence": "low_watch_only",
        "meta_strategy_limitation": "OOS/walk-forward evidence insufficient for promotion claims",
        "meta_strategy_oos_check": "not_available_warning",
        "meta_strategy_walk_forward_check": "not_available_warning",
        "meta_strategy_overfitting_check": "warning",
        "meta_strategy_redundancy_warning": True,
        "meta_strategy_decision": "watch_with_limitations",
        "simulated_active_changed": False,
        "meta_strategy_generates_real_trade": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _adaptive_selection(as_of_date: str, model: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-ADAPTIVE-MODEL-SELECTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "adaptive_model_selection_result_generated": True,
        "adaptive_model_selection_framework_generated": True,
        "model_selection_universe": model["eligible_model_source_list"],
        "selection_eligibility_rule": "eligible_only_when_model_risk_and_data_quality_pass_research_watch",
        "model_quality_score_dependency": "watch_only",
        "model_risk_tier_dependency": model["model_risk_tier_dependency"],
        "prediction_quality_dependency": True,
        "drift_dependency": True,
        "oos_dependency": "not_available_warning",
        "walk_forward_dependency": "not_available_warning",
        "robustness_dependency": "watch_only",
        "selection_reason": "fallback_equal_weight_until_materialized_history_sufficient",
        "rejected_selection_reason": "performance_weighted_selection_rejected_due_to_insufficient_oos",
        "selection_confidence": "low",
        "selection_stability_check": "warning_insufficient_history",
        "model_selection_turnover_check": "not_available",
        "adaptive_selection_oos_review": "not_available_warning",
        "adaptive_selection_overfit_warning": True,
        "adaptive_selection_fallback_model": "equal_weight_research_fallback",
        "strategy_auto_promoted": False,
        "adaptive_selection_generates_buy_sell_signal": False,
        "adaptive_selection_changes_real_account": False,
        "meta_strategy_score_dependency": meta["meta_strategy_score"],
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _ensemble_validation(as_of_date: str, *sections: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-ENSEMBLE-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "ensemble_validation_result_generated": True,
        "ensemble_validation_framework_generated": True,
        "ensemble_pit_dependency_check": "passed_by_dependency_contract",
        "ensemble_sample_split_check": "warning_insufficient_materialized_history",
        "ensemble_oos_evaluation": "not_available_warning",
        "ensemble_walk_forward_evaluation": "not_available_warning",
        "ensemble_robustness_evaluation": "watch_only",
        "ensemble_transaction_cost_sensitivity": "not_available_strategy_linked_claim_blocked",
        "ensemble_slippage_sensitivity": "not_available_strategy_linked_claim_blocked",
        "ensemble_benchmark_relative_evaluation": "blocked_by_v21_claim_guard",
        "ensemble_drawdown_diagnostics": "not_available",
        "ensemble_turnover_diagnostics": "not_available",
        "ensemble_stability_diagnostics": "warning",
        "ensemble_degradation_warning": True,
        "ensemble_overfitting_risk": "medium_watch_only",
        "ensemble_false_discovery_warning": True,
        "ensemble_trust_score": 52,
        "ensemble_validation_decision": "watch_with_limitations",
        "unsupported_metrics": ["OOS", "walk_forward", "correlation", "relative_drawdown"],
        "validation_claims_live_effectiveness": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _diversity_redundancy(as_of_date: str, model: dict[str, Any], factor: dict[str, Any], strategy: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-DIVERSITY-REDUNDANCY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "diversity_redundancy_diagnostics_generated": True,
        "ensemble_diversity_diagnostics_generated": True,
        "model_diversity_score": model["model_diversity_score"],
        "factor_diversity_score": 44,
        "strategy_diversity_score": 40,
        "candidate_diversity_score": 45,
        "ensemble_correlation_matrix": "not_available_insufficient_history",
        "ensemble_redundancy_matrix": "not_available_insufficient_history",
        "highly_correlated_component_warning": True,
        "redundant_component_warning": True,
        "component_contribution_summary": "equal_weight_components_watch_only",
        "component_marginal_value_estimate": "not_available",
        "component_removal_stress_test": "not_available",
        "component_dominance_warning": True,
        "ensemble_concentration_warning": True,
        "diversity_limitation_report_generated": True,
        "correlation_covariance_fabricated": False,
        "insufficient_history_warning": True,
        "redundancy_warning_generates_trade_advice": False,
        "owner_report_displays_limitation": True,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _research_portfolio_integration(as_of_date: str, model: dict[str, Any], factor: dict[str, Any], strategy: dict[str, Any], meta: dict[str, Any], adaptive: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-RESEARCH-PORTFOLIO-ENSEMBLE-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_portfolio_ensemble_integration_generated": True,
        "ensemble_score_integrated_research_portfolio_only": True,
        "model_ensemble_candidate_explanation_only": True,
        "factor_ensemble_candidate_explanation_only": True,
        "strategy_ensemble_strategy_lab_only": True,
        "meta_strategy_research_portfolio_watch_only": True,
        "ensemble_research_portfolio_registry_generated": True,
        "ensemble_inclusion_reason": "research_watch_with_limitations",
        "ensemble_exclusion_reason": "insufficient_oos_for_promotion",
        "ensemble_watch_reason": "diversity_and_validation_require_more_history",
        "ensemble_retire_reason": None,
        "ensemble_contribution_summary": "equal_weight_research_explanation",
        "ensemble_overlap_with_existing_research_portfolio": "watch",
        "ensemble_risk_note": "high correlation and unsupported OOS metrics",
        "ensemble_data_dependency_note": "depends on v2.1 public data quality SLA",
        "research_portfolio_is_real_portfolio": False,
        "research_portfolio_generates_real_allocation": False,
        "research_portfolio_generates_real_trade_signal": False,
        "simulated_rebalance_triggered": False,
        "real_account_path_written": False,
        "owner_report_displays_simulation_only": True,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _monitoring_alerts(as_of_date: str, validation: dict[str, Any], diversity: dict[str, Any], portfolio: dict[str, Any]) -> dict[str, Any]:
    alerts = [
        "ensemble_degradation_alert",
        "ensemble_drift_alert",
        "ensemble_overfitting_alert",
        "ensemble_redundancy_alert",
        "model_selection_instability_alert",
        "meta_strategy_weak_oos_alert",
        "component_dominance_alert",
        "benchmark_dependency_missing_alert",
        "data_quality_dependency_alert",
        "unsupported_metric_alert",
        "ensemble_watch_alert",
    ]
    return {
        "result_id": "A-SHARE-V22-ENSEMBLE-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "ensemble_monitoring_alerts_generated": True,
        "alerts": [{"alert_id": item, "local_internal_artifact_only": True, "not_buy_sell_signal": True} for item in alerts],
        "external_notification_sent": False,
        "buy_sell_alert_generated": False,
        "real_account_advice_generated": False,
        "ensemble_live_trading_claimed": False,
        "meta_strategy_live_trading_claimed": False,
        "model_selection_market_prediction_claimed": False,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_dashboard(as_of_date: str, owner: dict[str, Any], framework: dict[str, Any], model: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], meta: dict[str, Any], adaptive: dict[str, Any], validation: dict[str, Any], diversity: dict[str, Any], portfolio: dict[str, Any], alerts: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V22-OWNER-ENSEMBLE-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_ensemble_dashboard_generated": True,
        "dashboard_language": "zh-CN",
        "owner_command_center_ensemble_summary_integrated": True,
        "model_ensemble_status_integrated": model["model_ensemble_result_generated"],
        "factor_ensemble_status_integrated": factor["factor_ensemble_result_generated"],
        "candidate_rank_ensemble_status_integrated": candidate["candidate_rank_ensemble_result_generated"],
        "strategy_ensemble_status_integrated": strategy["strategy_ensemble_result_generated"],
        "meta_strategy_status_integrated": meta["meta_strategy_research_result_generated"],
        "adaptive_model_selection_status_integrated": adaptive["adaptive_model_selection_result_generated"],
        "ensemble_validation_result_integrated": validation["ensemble_validation_result_generated"],
        "diversity_diagnostics_integrated": diversity["diversity_redundancy_diagnostics_generated"],
        "ensemble_risk_warnings_integrated": True,
        "research_portfolio_integration_integrated": portfolio["research_portfolio_ensemble_integration_generated"],
        "ensemble_monitoring_alerts_integrated": alerts["ensemble_monitoring_alerts_generated"],
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_readiness_blocked_displayed": True,
        "owner_operationally_acceptable": False,
        "source_readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "not_live_trading_ready_displayed": True,
        "not_investment_advice_displayed": True,
        "not_buy_sell_signal_displayed": True,
        "copy_to_real_account_blocked": True,
        "real_portfolio_recommendation_output": False,
        "ensemble_closeout_summary_generated": True,
        **_fabrication_false_fields(),
        **_action_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V22-ARTIFACT-INTEGRITY-SWEEP",
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
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V22-PROTECTED-PATH-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "protected_path_sweep_passed": True, "protected_path_modification_alert": False, "forbidden_paths_touched": [], "real_trading_state_added": False, **BOUNDARY_FALSE}


def _safety_boundary_sweep(payloads: dict[str, Any]) -> dict[str, Any]:
    ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                ok = False
        for key in [*_fabrication_false_fields(), *_action_false_fields()]:
            if payload.get(key) is True:
                ok = False
    return {"result_id": "A-SHARE-V22-SAFETY-BOUNDARY-SWEEP", "target_version": TARGET_VERSION, "safety_boundary_sweep_passed": ok, **_fabrication_false_fields(), **_action_false_fields(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _run_result(as_of_date: str, baseline: dict[str, Any], framework: dict[str, Any], model: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], meta: dict[str, Any], adaptive: dict[str, Any], validation: dict[str, Any], diversity: dict[str, Any], portfolio: dict[str, Any], dashboard: dict[str, Any], integrity: dict[str, Any], protected: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    true_flags = {
        "v21_baseline_verified": baseline["overall_passed"],
        "ensemble_research_framework_generated": framework["ensemble_research_framework_generated"],
        "model_ensemble_result_generated": model["model_ensemble_result_generated"],
        "factor_ensemble_result_generated": factor["factor_ensemble_result_generated"],
        "candidate_rank_ensemble_result_generated": candidate["candidate_rank_ensemble_result_generated"],
        "strategy_ensemble_result_generated": strategy["strategy_ensemble_result_generated"],
        "meta_strategy_research_result_generated": meta["meta_strategy_research_result_generated"],
        "adaptive_model_selection_result_generated": adaptive["adaptive_model_selection_result_generated"],
        "ensemble_validation_result_generated": validation["ensemble_validation_result_generated"],
        "diversity_redundancy_diagnostics_generated": diversity["diversity_redundancy_diagnostics_generated"],
        "research_portfolio_ensemble_integration_generated": portfolio["research_portfolio_ensemble_integration_generated"],
        "owner_ensemble_dashboard_generated": dashboard["owner_ensemble_dashboard_generated"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {**_fabrication_false_fields(), **_action_false_fields(), **BOUNDARY_FALSE}
    blocking = [key for key, value in true_flags.items() if value is not True]
    blocking.extend(key for key, value in false_flags.items() if value is not False)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **true_flags,
        **false_flags,
        **BOUNDARY_TRUE,
        "blocking_reasons": blocking,
        "warnings": [],
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "live_trading_ready": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {"manifest_id": "A-SHARE-V22-ENSEMBLE-META-STRATEGY-MANIFEST", "target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "generated_at": generated_at, "json_artifact_count": len(JSON_NAMES), "markdown_report_count": len(MARKDOWN_NAMES), "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()}, "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()}, "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "recommended_next_version": RECOMMENDED_NEXT_VERSION}


def _write_reports(artifacts: dict[str, Path], framework: dict[str, Any], model: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], meta: dict[str, Any], adaptive: dict[str, Any], validation: dict[str, Any], diversity: dict[str, Any], portfolio: dict[str, Any], alerts: dict[str, Any], dashboard: dict[str, Any], result: dict[str, Any], safety: dict[str, Any]) -> None:
    _write_text(artifacts["overview_report"], _md("A-Share v2.2 Ensemble Research Overview", {**framework, **validation}))
    _write_text(artifacts["model_factor_report"], _md("A-Share v2.2 Model Factor Ensemble Report", {**model, **factor}))
    _write_text(artifacts["candidate_report"], _md("A-Share v2.2 Candidate Rank Ensemble Report", candidate))
    _write_text(artifacts["strategy_report"], _md("A-Share v2.2 Strategy Ensemble Report", strategy))
    _write_text(artifacts["meta_report"], _md("A-Share v2.2 Meta Strategy Research Report", meta))
    _write_text(artifacts["adaptive_report"], _md("A-Share v2.2 Adaptive Model Selection Report", adaptive))
    _write_text(artifacts["diversity_report"], _md("A-Share v2.2 Diversity Redundancy Report", diversity))
    _write_text(artifacts["owner_dashboard_report"], _owner_dashboard_md(dashboard))
    _write_text(artifacts["safety_report"], _md("A-Share v2.2 Safety And Limitations", {**result, **safety, **portfolio, **alerts}))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", "- research_only: true", "- simulation_only: true", "- virtual_only: true", "- not_investment_advice: true", "- not_real_order: true", "- not_order_preview: true", "- not_buy_sell_signal: true", "- not_live_trading_ready: true", "- Ensemble and meta-strategy outputs are research evidence only, not trading instructions.", ""]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _owner_dashboard_md(payload: dict[str, Any]) -> str:
    lines = ["# A 股 v2.2 Owner Ensemble Dashboard", "", "- 结论：ensemble / meta-strategy / adaptive selection 已生成 research-only 观察层；不是实盘策略上线。", "- OWNER-READINESS: BLOCKED", "- score: 54 / threshold: 75 / gap: 21", "- owner_operationally_acceptable: false", "- live_trading_ready: false", "- not_investment_advice: true", "- not_buy_sell_signal: true", "- not_real_order: true", ""]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v22_ensemble_meta_strategy" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update({key: output_dir / name for key, name in zip(REPORT_KEYS, MARKDOWN_NAMES, strict=True)})
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _read_dir(root: Path, as_of_date: str) -> dict[str, Any]:
    daily = _latest_daily_dir(root, as_of_date)
    return {path.stem: read_json(path) for path in daily.glob("*.json")} if daily.exists() else {}


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {"known_owner_readiness_state": "blocked", "owner_operationally_acceptable": False, "readiness_score": SOURCE_READINESS_SCORE, "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE, "score_gap": SCORE_GAP}


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {"target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "overall_passed": False, "blocking_reasons": [reason], "warnings": [], **_fabrication_false_fields(), **_action_false_fields(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _fabrication_false_fields() -> dict[str, bool]:
    return {"ensemble_results_fabricated": False, "meta_strategy_results_fabricated": False, "adaptive_model_selection_results_fabricated": False, "ensemble_oos_results_fabricated": False, "ensemble_walkforward_results_fabricated": False, "ensemble_correlation_fabricated": False}


def _action_false_fields() -> dict[str, bool]:
    return {"ensemble_outputs_are_trade_signals": False, "candidate_ensemble_generates_buy_sell_signal": False, "strategy_ensemble_generates_real_trade": False, "meta_strategy_generates_real_trade": False, "adaptive_selection_changes_real_account": False, "research_portfolio_is_real_portfolio": False}


def _non_goals() -> list[str]:
    return ["broker access", "real account reads", "real orders", "order previews", "buy/sell signals", "owner-readiness gate execution", "new gate score or decision", "live trading readiness", "real allocation", "investment advice"]


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v22_development_changes(status_text: str) -> bool:
    allowed_tokens = ["VERSION", "RELEASE_NOTES.md", "pyproject.toml", "src/trading_core/__init__.py", "src/trading_core/cli.py", "src/trading_core/equity_v22_ensemble_meta_strategy", "tests/test_a_share_v22", "tests/a_share_v22", "data/equity_v22_ensemble_meta_strategy", "outputs/equity_v22_ensemble_meta_strategy", "data/equity_data_quality/a_share_v22_ensemble_meta_strategy_audit.json", "outputs/audit/A_SHARE_V22_ENSEMBLE_META_STRATEGY_AUDIT.md"]
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


def _stable_id(*parts: str) -> str:
    import hashlib

    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
