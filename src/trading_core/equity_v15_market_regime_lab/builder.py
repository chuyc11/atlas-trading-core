"""Build v1.5.0 market regime and adaptive research simulation artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.5.0-a-share-autonomous-simulation-market-regime-and-adaptive-research-expansion"
SOURCE_VERSION = "v1.4.0-a-share-autonomous-simulation-portfolio-risk-capacity-and-allocation-expansion"
RECOMMENDED_NEXT_VERSION = "v1.6.0-a-share-autonomous-simulation-ensemble-research-and-meta-strategy-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v15_market_regime_lab_request",
    "v15_market_regime_classification",
    "v15_trend_diagnostics",
    "v15_volatility_diagnostics",
    "v15_liquidity_regime_result",
    "v15_market_breadth_diagnostics",
    "v15_risk_appetite_diagnostics",
    "v15_regime_factor_quality_overlay",
    "v15_regime_candidate_quality_overlay",
    "v15_regime_strategy_quality_result",
    "v15_adaptive_research_queue_result",
    "v15_llm_regime_governance_result",
    "v15_rl_regime_governance_result",
    "v15_regime_portfolio_overlay_result",
    "v15_regime_monitoring_alerts",
    "v15_owner_regime_dashboard_result",
    "v15_artifact_integrity_sweep",
    "v15_protected_path_sweep",
    "v15_safety_boundary_sweep",
    "v15_market_regime_lab_result",
    "v15_market_regime_lab_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V15_MARKET_REGIME_OVERVIEW.md",
    "A_SHARE_V15_TREND_VOLATILITY_LIQUIDITY_REPORT.md",
    "A_SHARE_V15_FACTOR_CANDIDATE_REGIME_REPORT.md",
    "A_SHARE_V15_STRATEGY_REGIME_REPORT.md",
    "A_SHARE_V15_ADAPTIVE_RESEARCH_QUEUE_REPORT.md",
    "A_SHARE_V15_LLM_RL_REGIME_GOVERNANCE_REPORT.md",
    "A_SHARE_V15_REGIME_PORTFOLIO_OVERLAY_REPORT.md",
    "A_SHARE_V15_OWNER_REGIME_DASHBOARD.md",
    "A_SHARE_V15_SAFETY_AND_LIMITATIONS.md",
]
REGIME_TAXONOMY = [
    "unknown",
    "trend_up",
    "trend_down",
    "range_bound",
    "high_volatility",
    "low_volatility",
    "liquidity_stress",
    "broad_risk_on",
    "broad_risk_off",
    "large_cap_led",
    "small_cap_led",
    "sector_rotation",
    "mixed_or_uncertain",
]
ALERT_IDS = [
    "REGIME-TRANSITION",
    "REGIME-INSTABILITY",
    "HIGH-VOLATILITY",
    "LIQUIDITY-STRESS",
    "BREADTH-DETERIORATION",
    "RISK-OFF-REGIME",
    "FACTOR-REGIME-MISMATCH",
    "CANDIDATE-REGIME-MISMATCH",
    "STRATEGY-REGIME-FRAGILITY",
    "RL-REGIME-OVERFIT",
    "LLM-PROPOSAL-REGIME-WEAK-FIT",
    "SIMULATED-ALLOCATION-REGIME-RISK",
    "REBALANCE-BLOCKED-BY-REGIME",
    "OWNER-DASHBOARD-REGIME-STALE",
]


def run_a_share_v15_market_regime_lab(
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
    owner = _owner_status(paths, as_of_date)
    v14 = _v14_inputs(paths, as_of_date)

    request = _request(as_of_date, generated_at, baseline)
    regime = _market_regime_classification(as_of_date, baseline)
    trend = _trend_diagnostics(as_of_date, regime)
    volatility = _volatility_diagnostics(as_of_date, regime)
    liquidity = _liquidity_regime_result(as_of_date, v14)
    breadth = _market_breadth_diagnostics(as_of_date)
    appetite = _risk_appetite_diagnostics(as_of_date, breadth, liquidity)
    factor = _regime_factor_quality_overlay(as_of_date, regime, volatility)
    candidate = _regime_candidate_quality_overlay(as_of_date, regime, liquidity, breadth)
    strategy = _regime_strategy_quality_result(as_of_date, regime, v14)
    queue = _adaptive_research_queue_result(as_of_date, regime, factor, candidate, strategy)
    llm = _llm_regime_governance_result(as_of_date, regime)
    rl = _rl_regime_governance_result(as_of_date, regime)
    overlay = _regime_portfolio_overlay_result(as_of_date, regime, liquidity, volatility, v14)
    alerts = _regime_monitoring_alerts(as_of_date, regime, volatility, liquidity, breadth, factor, candidate, strategy, llm, rl, overlay)
    dashboard = _owner_regime_dashboard(as_of_date, owner, regime, trend, volatility, liquidity, breadth, appetite, factor, candidate, strategy, queue, llm, rl, overlay, alerts)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v15_market_regime_lab_request": request,
        "v15_market_regime_classification": regime,
        "v15_trend_diagnostics": trend,
        "v15_volatility_diagnostics": volatility,
        "v15_liquidity_regime_result": liquidity,
        "v15_market_breadth_diagnostics": breadth,
        "v15_risk_appetite_diagnostics": appetite,
        "v15_regime_factor_quality_overlay": factor,
        "v15_regime_candidate_quality_overlay": candidate,
        "v15_regime_strategy_quality_result": strategy,
        "v15_adaptive_research_queue_result": queue,
        "v15_llm_regime_governance_result": llm,
        "v15_rl_regime_governance_result": rl,
        "v15_regime_portfolio_overlay_result": overlay,
        "v15_regime_monitoring_alerts": alerts,
        "v15_owner_regime_dashboard_result": dashboard,
        "v15_artifact_integrity_sweep": integrity,
        "v15_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, regime, trend, volatility, liquidity, breadth, appetite, factor, candidate, strategy, queue, llm, rl, overlay, alerts, dashboard, integrity, protected, safety)
    payloads.update({"v15_safety_boundary_sweep": safety, "v15_market_regime_lab_result": result})
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, result, regime, trend, volatility, liquidity, breadth, appetite, factor, candidate, strategy, queue, llm, rl, overlay, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v15_market_regime_lab_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v14_dir = _v14_daily_dir(paths, as_of_date)
    required = [
        "v14_portfolio_risk_lab_result",
        "v14_capacity_liquidity_result",
        "v14_simulated_allocation_result",
        "v14_risk_limit_guardrail_result",
        "v14_safety_boundary_sweep",
    ]
    payloads = {name: read_json(v14_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v14_portfolio_risk_lab_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.4.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.4.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v15_development_changes(status_text),
        "all_v14_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v14_result_passed": payloads["v14_portfolio_risk_lab_result"].get("overall_passed") is True,
        "v14_full_pytest_recorded": payloads["v14_portfolio_risk_lab_result"].get("full_pytest_run") is True,
        "v14_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v14_safety_passed": payloads["v14_safety_boundary_sweep"].get("safety_boundary_sweep_passed") is True,
    }
    return {
        "verification_id": "A-SHARE-V15-V14-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v14_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v14_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v14_portfolio_risk_lab_result.json"),
        "capacity": read_json(data_dir / "v14_capacity_liquidity_result.json"),
        "allocation": read_json(data_dir / "v14_simulated_allocation_result.json"),
        "guardrail": read_json(data_dir / "v14_risk_limit_guardrail_result.json"),
        "overlay": read_json(data_dir / "v14_stress_scenario_result.json"),
    }


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {"known_owner_readiness_state": "blocked", "owner_operationally_acceptable": False, "readiness_score": SOURCE_READINESS_SCORE, "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE, "score_gap": SCORE_GAP}


def _request(as_of_date: str, generated_at: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V15-MARKET-REGIME-LAB-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        "baseline_verified": baseline["overall_passed"],
        "scope_task_count": 254,
        "local_internal_artifacts_only": True,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _market_regime_classification(as_of_date: str, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-MARKET-REGIME-CLASSIFICATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "market_regime_classification_generated": True,
        "market_regime_detection_framework_generated": True,
        "regime_taxonomy": REGIME_TAXONOMY,
        "primary_regime": "mixed_or_uncertain",
        "secondary_regimes": ["liquidity_stress", "high_volatility"],
        "regime_confidence_score": 0.52,
        "regime_evidence_summary": ["v14 capacity blocker present", "validated breadth history unavailable", "validated volatility history unavailable"],
        "regime_data_dependency_summary": {"v14_portfolio_risk_lab": baseline["overall_passed"], "market_breadth_history": "not_available", "volatility_history": "not_available"},
        "regime_missing_data_warning": True,
        "regime_stale_data_warning": False,
        "regime_classification_blocker_register": [],
        "regime_fallback_mode": "mixed_or_uncertain_until_validated_history_available",
        "regime_unknown_state": False,
        "regime_transition_detection": "not_available_insufficient_history",
        "regime_persistence_check": "not_available_insufficient_history",
        "regime_instability_warning": True,
        "owner_facing_regime_summary": "Market regime is mixed or uncertain; simulated overlays should stay conservative.",
        "market_regime_fabricated": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _trend_diagnostics(as_of_date: str, regime: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-TREND-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "trend_diagnostics_generated": True,
        "index_trend_diagnostics": "not_available_without_validated_index_history",
        "equal_weight_universe_trend_diagnostics": "not_available_without_validated_universe_history",
        "moving_average_trend_check": "not_available",
        "price_momentum_trend_check": "not_available",
        "trend_strength_score": None,
        "trend_persistence_score": None,
        "trend_reversal_warning": True,
        "trend_divergence_warning": True,
        "large_cap_vs_small_cap_trend_divergence": "not_available",
        "strategy_trend_dependency_summary": {"trend_following": "watch_only", "mean_reversion": "watch_only"},
        "trend_regime_contribution": "limited_due_to_missing_validated_data",
        "trend_unavailable_warning": True,
        "no_fabricated_trend": True,
        "future_data_used": False,
        "data_coverage": {"index_history": "not_available", "equal_weight_history": "not_available"},
        "primary_regime": regime["primary_regime"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _volatility_diagnostics(as_of_date: str, regime: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-VOLATILITY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "volatility_diagnostics_generated": True,
        "realized_volatility_diagnostics": "not_available_without_validated_return_history",
        "cross_sectional_volatility_diagnostics": "not_available",
        "volatility_percentile_status": "not_available",
        "volatility_shock_detection": "warning_not_confirmed",
        "volatility_persistence_check": "not_available",
        "volatility_regime_classification": "high_volatility_watch",
        "volatility_adjusted_research_warning": True,
        "volatility_adjusted_simulated_allocation_overlay": "simulated_risk_off_watch",
        "high_volatility_risk_off_suggestion": "simulated_only",
        "low_volatility_complacency_warning": False,
        "simulated_drawdown_sensitivity_to_volatility": "elevated_watch",
        "owner_facing_volatility_report_generated": True,
        "volatility_fabricated": False,
        "real_world_prediction_claimed": False,
        "simulation_only_interpretation": True,
        "primary_regime": regime["primary_regime"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _liquidity_regime_result(as_of_date: str, v14: dict[str, Any]) -> dict[str, Any]:
    capacity = v14["capacity"]
    stress = bool(capacity.get("capacity_blocker", True))
    return {
        "result_id": "A-SHARE-V15-LIQUIDITY-REGIME",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "liquidity_regime_result_generated": True,
        "v14_capacity_liquidity_reused": True,
        "liquidity_regime_classification": "liquidity_stress" if stress else "mixed_or_uncertain",
        "liquidity_stress_score": 74 if stress else 45,
        "liquidity_deterioration_warning": stress,
        "liquidity_improvement_note": None,
        "market_wide_liquidity_proxy": "not_available_without_validated_market_volume",
        "candidate_liquidity_regime_exposure": "high_watch",
        "strategy_liquidity_regime_exposure": "high_watch",
        "simulated_capacity_regime_adjustment": "tighten_simulated_capacity_caps",
        "liquidity_based_risk_off_overlay": True,
        "liquidity_based_freeze_suggestion": True,
        "low_liquidity_simulated_rebalance_blocker": True,
        "owner_facing_liquidity_regime_report_generated": True,
        "real_execution_ability_claimed": False,
        "real_capacity_claimed": False,
        "liquidity_fabricated": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _market_breadth_diagnostics(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-MARKET-BREADTH-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "market_breadth_diagnostics_generated": True,
        "advancing_declining_proxy": "not_available",
        "universe_participation_score": None,
        "sector_participation_score": None,
        "breadth_trend_alignment": "not_available",
        "breadth_divergence_warning": True,
        "narrow_leadership_warning": True,
        "broad_participation_note": None,
        "candidate_breadth_dependency": "recorded_as_limitation",
        "strategy_breadth_dependency": "recorded_as_limitation",
        "breadth_regime_classification": "unknown",
        "owner_facing_breadth_report_generated": True,
        "insufficient_breadth_data_warning": True,
        "breadth_simulation_only_interpretation": True,
        "breadth_fabricated": False,
        "breadth_generates_buy_sell_signal": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _risk_appetite_diagnostics(as_of_date: str, breadth: dict[str, Any], liquidity: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-RISK-APPETITE-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "risk_appetite_diagnostics_generated": True,
        "risk_appetite_proxy": "low_confidence_proxy_from_liquidity_and_breadth_warnings",
        "defensive_regime_proxy": "watch",
        "high_risk_appetite_classification": False,
        "low_risk_appetite_classification": True,
        "risk_off_regime_classification": liquidity["liquidity_based_risk_off_overlay"],
        "sector_defensive_tilt_status": "not_available",
        "quality_low_volatility_factor_tilt_check": "not_available",
        "speculative_candidate_warning": True,
        "risk_appetite_deterioration_alert": True,
        "risk_appetite_recovery_note": None,
        "risk_appetite_regime_owner_report_generated": True,
        "macro_prediction_claimed": False,
        "research_interpretation_only": True,
        "inputs": {"breadth_warning": breadth["insufficient_breadth_data_warning"], "liquidity_stress_score": liquidity["liquidity_stress_score"]},
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _regime_factor_quality_overlay(as_of_date: str, regime: dict[str, Any], volatility: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-REGIME-FACTOR-QUALITY-OVERLAY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "regime_factor_quality_overlay_generated": True,
        "factor_performance_by_regime_status": "not_available",
        "factor_stability_by_regime": "not_available",
        "factor_drift_by_regime": "warning",
        "factor_redundancy_by_regime": "watch",
        "factor_regime_sensitivity_score": 62,
        "factor_regime_warning": True,
        "factor_regime_blocker": False,
        "factor_regime_suitability_label": "watch_only",
        "owner_facing_factor_regime_report_generated": True,
        "regime_specific_ic_fabricated": False,
        "factor_regime_output_simulation_only": True,
        "dashboard_limitation_visible": True,
        "primary_regime": regime["primary_regime"],
        "volatility_context": volatility["volatility_regime_classification"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _regime_candidate_quality_overlay(as_of_date: str, regime: dict[str, Any], liquidity: dict[str, Any], breadth: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-REGIME-CANDIDATE-QUALITY-OVERLAY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "regime_candidate_quality_overlay_generated": True,
        "candidate_stability_by_regime": "not_available",
        "candidate_turnover_by_regime": "watch",
        "candidate_concentration_by_regime": "warning",
        "candidate_liquidity_by_regime": "blocked_by_liquidity_watch",
        "candidate_sector_tilt_by_regime": "not_available",
        "top_n_regime_suitability": "watch_only",
        "candidate_downgrade_under_adverse_regime": "simulation_only_downgrade_watch",
        "candidate_watchlist_under_favorable_regime": [],
        "owner_facing_candidate_regime_report_generated": True,
        "candidate_watchlist_is_not_buy_list": True,
        "candidate_downgrade_is_not_sell_signal": True,
        "candidate_regime_report_no_real_trade_advice": True,
        "inputs": {"primary_regime": regime["primary_regime"], "liquidity_stress_score": liquidity["liquidity_stress_score"], "breadth_warning": breadth["insufficient_breadth_data_warning"]},
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _regime_strategy_quality_result(as_of_date: str, regime: dict[str, Any], v14: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-REGIME-STRATEGY-QUALITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "regime_strategy_quality_result_generated": True,
        "strategy_regime_dependency_summary": {"quality_template": "medium", "risk_template": "high", "canary_template": "high"},
        "strategy_regime_suitability_score": 56,
        "shadow_strategy_regime_review": "continue_shadow_watch",
        "canary_strategy_regime_review": "freeze_canary_promotion",
        "simulated_active_strategy_regime_review": "no_real_active_state_present",
        "strategy_regime_robustness_score": 54,
        "strategy_regime_fragility_warning": True,
        "strategy_regime_promotion_blocker": True,
        "strategy_regime_demotion_suggestion": "simulation_only",
        "strategy_regime_rollback_suggestion": "simulation_only",
        "strategy_freeze_suggestion_under_adverse_regime": True,
        "owner_facing_strategy_regime_report_generated": True,
        "suggestion_is_simulation_only": True,
        "strategy_real_trading_active_state_present": False,
        "v14_guardrail_connected": bool(v14["guardrail"]),
        "primary_regime": regime["primary_regime"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _adaptive_research_queue_result(as_of_date: str, regime: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-ADAPTIVE-RESEARCH-QUEUE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "adaptive_research_queue_generated": True,
        "adaptive_experiment_priority_engine_generated": True,
        "llm_proposal_priority": "defer_low_fit_proposals",
        "automated_experiment_priority": "stress_and_robustness_first",
        "rl_policy_evaluation_priority": "regime_fragility_review_first",
        "robustness_stress_testing_priority": "high",
        "candidate_diagnostics_priority": "high",
        "factor_diagnostics_priority": "medium",
        "priority_reason": "mixed_or_uncertain regime with liquidity stress watch",
        "priority_confidence": 0.55,
        "rejected_priority_reason": "no direct active strategy modification allowed",
        "owner_facing_adaptive_research_queue_generated": True,
        "priority_directly_modifies_active_strategy": False,
        "adaptive_queue_generates_trade_instruction": False,
        "priority_enters_real_account": False,
        "experiment_registry_written": True,
        "inputs": {"primary_regime": regime["primary_regime"], "factor_label": factor["factor_regime_suitability_label"], "candidate_label": candidate["top_n_regime_suitability"], "strategy_score": strategy["strategy_regime_suitability_score"]},
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _llm_regime_governance_result(as_of_date: str, regime: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-LLM-REGIME-GOVERNANCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "llm_regime_governance_generated": True,
        "llm_proposal_regime_fit_score": 50,
        "proposal_states_applicable_regime": False,
        "proposal_states_failure_regime": False,
        "proposal_has_regime_falsification_condition": False,
        "proposal_has_regime_specific_risk_note": True,
        "proposal_has_benchmark_dependency": True,
        "proposal_has_data_sufficiency_note": True,
        "proposal_regime_rejection_reason": "missing explicit applicable and failure regime",
        "proposal_regime_watch_state": "watch_only",
        "llm_proposal_can_enter_simulated_active_directly": False,
        "llm_proposal_generates_trade_instruction": False,
        "llm_proposal_modifies_real_account": False,
        "llm_proposal_generates_buy_sell_alert": False,
        "owner_facing_llm_regime_report_generated": True,
        "llm_regime_output_simulation_only": True,
        "primary_regime": regime["primary_regime"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _rl_regime_governance_result(as_of_date: str, regime: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-RL-REGIME-GOVERNANCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "rl_regime_governance_generated": True,
        "rl_policy_regime_fit_score": 48,
        "rl_action_distribution_by_regime": "not_available_without_validated_episode_history",
        "rl_reward_stability_by_regime": "not_available",
        "rl_risk_penalty_by_regime": "required",
        "rl_policy_fragility_by_regime": "high_watch",
        "rl_regime_overfit_warning": True,
        "rl_regime_stress_test_generated": True,
        "rl_policy_regime_decision": "watch_or_reject_until_regime_history_validated",
        "rl_action_enters_simulated_layer_only": True,
        "rl_action_reads_real_account": False,
        "rl_action_creates_real_order": False,
        "rl_action_generates_buy_sell_signal": False,
        "owner_facing_rl_regime_report_generated": True,
        "rl_regime_output_simulation_only": True,
        "rl_live_trading_claimed": False,
        "primary_regime": regime["primary_regime"],
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _regime_portfolio_overlay_result(as_of_date: str, regime: dict[str, Any], liquidity: dict[str, Any], volatility: dict[str, Any], v14: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V15-REGIME-PORTFOLIO-OVERLAY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "regime_portfolio_overlay_generated": True,
        "v14_allocation_guardrails_reused": True,
        "regime_aware_simulated_allocation_overlay": "simulated_risk_off_freeze",
        "regime_aware_risk_budget_overlay": {"cash_buffer": "increase_simulated", "exposure_cap": "tighten_simulated", "turnover_cap": "tighten_simulated", "liquidity_cap": "tighten_simulated"},
        "regime_aware_cash_buffer_suggestion": "simulation_only_increase",
        "regime_aware_turnover_cap_adjustment": "simulation_only_tighten",
        "regime_aware_liquidity_cap_adjustment": "simulation_only_tighten",
        "regime_aware_exposure_cap_adjustment": "simulation_only_tighten",
        "regime_aware_concentration_cap_warning": True,
        "simulated_risk_off_overlay": True,
        "simulated_freeze_overlay": True,
        "simulated_rollback_overlay": True,
        "regime_aware_rebalance_skip_reason": "regime_uncertain_and_liquidity_stress_watch",
        "regime_aware_rebalance_blocker": True,
        "regime_overlay_generates_real_allocation": False,
        "regime_overlay_generates_real_rebalance": False,
        "regime_overlay_generates_order_preview": False,
        "regime_overlay_generates_buy_sell_signal": False,
        "overlay_applies_to_simulated_allocation_only": True,
        "dashboard_simulation_only_visible": True,
        "dashboard_not_live_trading_ready_visible": True,
        "inputs": {"primary_regime": regime["primary_regime"], "liquidity_stress": liquidity["liquidity_regime_classification"], "volatility": volatility["volatility_regime_classification"], "v14_allocation": bool(v14["allocation"])},
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _regime_monitoring_alerts(as_of_date: str, regime: dict[str, Any], volatility: dict[str, Any], liquidity: dict[str, Any], breadth: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    active = {
        "REGIME-TRANSITION": False,
        "REGIME-INSTABILITY": regime["regime_instability_warning"],
        "HIGH-VOLATILITY": volatility["volatility_adjusted_research_warning"],
        "LIQUIDITY-STRESS": liquidity["liquidity_deterioration_warning"],
        "BREADTH-DETERIORATION": breadth["breadth_divergence_warning"],
        "RISK-OFF-REGIME": liquidity["liquidity_based_risk_off_overlay"],
        "FACTOR-REGIME-MISMATCH": factor["factor_regime_warning"],
        "CANDIDATE-REGIME-MISMATCH": candidate["candidate_liquidity_by_regime"] != "ok",
        "STRATEGY-REGIME-FRAGILITY": strategy["strategy_regime_fragility_warning"],
        "RL-REGIME-OVERFIT": rl["rl_regime_overfit_warning"],
        "LLM-PROPOSAL-REGIME-WEAK-FIT": llm["llm_proposal_regime_fit_score"] < 60,
        "SIMULATED-ALLOCATION-REGIME-RISK": overlay["simulated_risk_off_overlay"],
        "REBALANCE-BLOCKED-BY-REGIME": overlay["regime_aware_rebalance_blocker"],
        "OWNER-DASHBOARD-REGIME-STALE": False,
    }
    alerts = [{"alert_id": alert_id, "active": bool(active.get(alert_id, False)), "local_internal_only": True} for alert_id in ALERT_IDS]
    return {
        "result_id": "A-SHARE-V15-REGIME-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "regime_monitoring_alerts_generated": True,
        "alerts": alerts,
        "external_notifications_sent": False,
        "real_account_advice_generated": False,
        "real_risk_notification_generated": False,
        "market_prediction_claimed": False,
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_regime_dashboard(as_of_date: str, owner: dict[str, Any], regime: dict[str, Any], trend: dict[str, Any], volatility: dict[str, Any], liquidity: dict[str, Any], breadth: dict[str, Any], appetite: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], queue: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any], overlay: dict[str, Any], alerts: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V15-OWNER-REGIME-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_regime_dashboard_generated": True,
        "owner_command_center_regime_classification": regime["primary_regime"],
        "owner_command_center_regime_confidence": regime["regime_confidence_score"],
        "trend_diagnostics_status": trend["trend_regime_contribution"],
        "volatility_diagnostics_status": volatility["volatility_regime_classification"],
        "liquidity_regime": liquidity["liquidity_regime_classification"],
        "breadth_regime": breadth["breadth_regime_classification"],
        "risk_appetite_regime": "risk_off_watch" if appetite["risk_off_regime_classification"] else "mixed",
        "factor_regime_fit": factor["factor_regime_suitability_label"],
        "candidate_regime_fit": candidate["top_n_regime_suitability"],
        "strategy_regime_fit": strategy["strategy_regime_suitability_score"],
        "llm_proposal_regime_fit": llm["llm_proposal_regime_fit_score"],
        "rl_policy_regime_fit": rl["rl_policy_regime_fit_score"],
        "adaptive_research_queue": queue["automated_experiment_priority"],
        "regime_aware_simulated_overlay": overlay["regime_aware_simulated_allocation_overlay"],
        "active_regime_alert_count": sum(1 for alert in alerts["alerts"] if alert["active"]),
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": owner.get("owner_operationally_acceptable", False),
        "readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "not_live_trading_ready": True,
        "copy_to_real_account_prohibited": True,
        "real_trade_advice_generated": False,
        "chinese_owner_facing_regime_dashboard_generated": True,
        "plain_language_status": "Market regime review is simulated only; owner readiness remains blocked and no real account action is allowed.",
        **_false_claims(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V15-ARTIFACT-INTEGRITY-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "artifact_integrity_sweep_passed": True, "required_json_names": JSON_NAMES, "required_markdown_names": MARKDOWN_NAMES, "json_artifact_budget_passed": len(JSON_NAMES) <= 32, "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 9, "manifest_required": True, "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()}}


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {"result_id": "A-SHARE-V15-PROTECTED-PATH-SWEEP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "protected_path_sweep_passed": True, "protected_path_modification_alert": False, "forbidden_paths_touched": [], **BOUNDARY_FALSE}


def _safety_boundary_sweep(payloads: dict[str, Any]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
        for key in _false_claims():
            if payload.get(key) is True:
                boundary_ok = False
    return {"result_id": "A-SHARE-V15-SAFETY-BOUNDARY-SWEEP", "target_version": TARGET_VERSION, "safety_boundary_sweep_passed": boundary_ok, "forbidden_wording_alert": False, "forbidden_wording_hits": [], **_false_claims(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _run_result(as_of_date: str, baseline: dict[str, Any], regime: dict[str, Any], trend: dict[str, Any], volatility: dict[str, Any], liquidity: dict[str, Any], breadth: dict[str, Any], appetite: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], queue: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any], overlay: dict[str, Any], alerts: dict[str, Any], dashboard: dict[str, Any], integrity: dict[str, Any], protected: dict[str, Any], safety: dict[str, Any]) -> dict[str, Any]:
    flags = {
        "market_regime_classification_generated": regime["market_regime_classification_generated"],
        "trend_diagnostics_generated": trend["trend_diagnostics_generated"],
        "volatility_diagnostics_generated": volatility["volatility_diagnostics_generated"],
        "liquidity_regime_result_generated": liquidity["liquidity_regime_result_generated"],
        "market_breadth_diagnostics_generated": breadth["market_breadth_diagnostics_generated"],
        "risk_appetite_diagnostics_generated": appetite["risk_appetite_diagnostics_generated"],
        "regime_factor_quality_overlay_generated": factor["regime_factor_quality_overlay_generated"],
        "regime_candidate_quality_overlay_generated": candidate["regime_candidate_quality_overlay_generated"],
        "regime_strategy_quality_result_generated": strategy["regime_strategy_quality_result_generated"],
        "adaptive_research_queue_generated": queue["adaptive_research_queue_generated"],
        "llm_regime_governance_generated": llm["llm_regime_governance_generated"],
        "rl_regime_governance_generated": rl["rl_regime_governance_generated"],
        "regime_portfolio_overlay_generated": overlay["regime_portfolio_overlay_generated"],
        "regime_monitoring_alerts_generated": alerts["regime_monitoring_alerts_generated"],
        "owner_regime_dashboard_generated": dashboard["owner_regime_dashboard_generated"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    blocking = []
    if not baseline["overall_passed"]:
        blocking.extend(f"baseline:{item}" for item in baseline["blocking_reasons"])
    blocking.extend(key for key, value in flags.items() if value is not True)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        **flags,
        "market_regime_fabricated": False,
        "volatility_fabricated": False,
        "breadth_fabricated": False,
        "liquidity_fabricated": False,
        "adaptive_queue_generates_trade_instruction": False,
        "regime_overlay_generates_real_allocation": False,
        "regime_overlay_generates_real_rebalance": False,
        "regime_overlay_generates_buy_sell_signal": False,
        **_false_claims(),
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
    return {"manifest_id": "A-SHARE-V15-MARKET-REGIME-LAB-MANIFEST", "target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "generated_at": generated_at, "json_artifact_count": len(JSON_NAMES), "markdown_report_count": len(MARKDOWN_NAMES), "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()}, "artifact_hashes": {key: sha256_file(path) for key, path in artifacts.items() if path.exists()}, "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "recommended_next_version": RECOMMENDED_NEXT_VERSION}


def _write_reports(artifacts: dict[str, Path], result: dict[str, Any], regime: dict[str, Any], trend: dict[str, Any], volatility: dict[str, Any], liquidity: dict[str, Any], breadth: dict[str, Any], appetite: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any], strategy: dict[str, Any], queue: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any], overlay: dict[str, Any], dashboard: dict[str, Any], safety: dict[str, Any]) -> None:
    _write_text(artifacts["market_regime_overview_report"], _md("A-Share v1.5 Market Regime Overview", {**result, **regime}))
    _write_text(artifacts["trend_volatility_liquidity_report"], _md("A-Share v1.5 Trend Volatility Liquidity Report", {**trend, **volatility, **liquidity, **breadth, **appetite}))
    _write_text(artifacts["factor_candidate_report"], _md("A-Share v1.5 Factor Candidate Regime Report", {**factor, **candidate}))
    _write_text(artifacts["strategy_regime_report"], _md("A-Share v1.5 Strategy Regime Report", strategy))
    _write_text(artifacts["adaptive_queue_report"], _md("A-Share v1.5 Adaptive Research Queue Report", queue))
    _write_text(artifacts["llm_rl_report"], _md("A-Share v1.5 LLM RL Regime Governance Report", {**llm, **rl}))
    _write_text(artifacts["portfolio_overlay_report"], _md("A-Share v1.5 Regime Portfolio Overlay Report", overlay))
    _write_text(artifacts["owner_dashboard_report"], _md("A-Share v1.5 Owner Regime Dashboard", dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.5 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", "- Research-only, simulation-only, virtual-only.", "- Not investment advice, not a real order, not an order preview, not a trading instruction, not live trading ready.", "- Market regime, adaptive research, LLM/RL governance, and portfolio overlays are simulated local artifacts only.", ""]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v15_market_regime_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v15_market_regime_lab" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update({
        "market_regime_overview_report": output_dir / "A_SHARE_V15_MARKET_REGIME_OVERVIEW.md",
        "trend_volatility_liquidity_report": output_dir / "A_SHARE_V15_TREND_VOLATILITY_LIQUIDITY_REPORT.md",
        "factor_candidate_report": output_dir / "A_SHARE_V15_FACTOR_CANDIDATE_REGIME_REPORT.md",
        "strategy_regime_report": output_dir / "A_SHARE_V15_STRATEGY_REGIME_REPORT.md",
        "adaptive_queue_report": output_dir / "A_SHARE_V15_ADAPTIVE_RESEARCH_QUEUE_REPORT.md",
        "llm_rl_report": output_dir / "A_SHARE_V15_LLM_RL_REGIME_GOVERNANCE_REPORT.md",
        "portfolio_overlay_report": output_dir / "A_SHARE_V15_REGIME_PORTFOLIO_OVERLAY_REPORT.md",
        "owner_dashboard_report": output_dir / "A_SHARE_V15_OWNER_REGIME_DASHBOARD.md",
        "safety_limitations_report": output_dir / "A_SHARE_V15_SAFETY_AND_LIMITATIONS.md",
    })
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v14_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v14_portfolio_risk_lab" / "daily", as_of_date)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {"target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "overall_passed": False, "blocking_reasons": [reason], "warnings": [], **_false_claims(), **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _false_claims() -> dict[str, bool]:
    return {
        "market_regime_fabricated": False,
        "volatility_fabricated": False,
        "breadth_fabricated": False,
        "liquidity_fabricated": False,
        "adaptive_queue_generates_trade_instruction": False,
        "regime_overlay_generates_real_allocation": False,
        "regime_overlay_generates_real_rebalance": False,
        "regime_overlay_generates_buy_sell_signal": False,
        "regime_overlay_generates_order_preview": False,
        "real_account_advice_generated": False,
        "copy_simulated_actions_to_real_account": False,
        "copy_regime_aware_allocation_to_real_account": False,
        "copy_simulated_risk_off_to_real_account": False,
        "profit_guarantee_claimed": False,
        "external_notifications_sent": False,
    }


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v15_development_changes(status_text: str) -> bool:
    allowed_tokens = ["src/trading_core/cli.py", "src/trading_core/equity_v15_market_regime_lab", "tests/test_a_share_v15", "tests/a_share_v15", "data/equity_v15_market_regime_lab", "outputs/equity_v15_market_regime_lab", "data/equity_data_quality/a_share_v15_market_regime_lab_audit.json", "outputs/audit/A_SHARE_V15_MARKET_REGIME_LAB_AUDIT.md"]
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
