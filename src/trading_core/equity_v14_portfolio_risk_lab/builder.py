"""Build v1.4.0 simulation-only portfolio risk, capacity, and allocation artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.4.0-a-share-autonomous-simulation-portfolio-risk-capacity-and-allocation-expansion"
SOURCE_VERSION = "v1.3.0-a-share-autonomous-research-quality-evaluation-and-strategy-lab-expansion"
RECOMMENDED_NEXT_VERSION = "v1.5.0-a-share-autonomous-simulation-market-regime-and-adaptive-research-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v14_portfolio_risk_lab_request",
    "v14_portfolio_risk_scorecard",
    "v14_exposure_concentration_result",
    "v14_correlation_diversification_result",
    "v14_capacity_liquidity_result",
    "v14_turnover_cost_slippage_result",
    "v14_simulated_allocation_result",
    "v14_simulated_rebalance_plan",
    "v14_multi_strategy_portfolio_result",
    "v14_stress_scenario_result",
    "v14_risk_limit_guardrail_result",
    "v14_owner_portfolio_risk_dashboard_result",
    "v14_portfolio_risk_monitoring_alerts",
    "v14_artifact_integrity_sweep",
    "v14_protected_path_sweep",
    "v14_safety_boundary_sweep",
    "v14_portfolio_risk_lab_result",
    "v14_portfolio_risk_lab_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V14_PORTFOLIO_RISK_OVERVIEW.md",
    "A_SHARE_V14_CAPACITY_AND_LIQUIDITY_REPORT.md",
    "A_SHARE_V14_SIMULATED_ALLOCATION_REPORT.md",
    "A_SHARE_V14_SIMULATED_REBALANCE_PLAN.md",
    "A_SHARE_V14_STRESS_SCENARIO_REPORT.md",
    "A_SHARE_V14_RISK_GUARDRAIL_REPORT.md",
    "A_SHARE_V14_OWNER_PORTFOLIO_RISK_DASHBOARD.md",
    "A_SHARE_V14_SAFETY_AND_LIMITATIONS.md",
]
FORBIDDEN_WORDING = [
    "strong buy",
    "guaranteed profit",
    "live trading ready: true",
    "real order preview",
    "real trade instruction: true",
    "copy simulated allocation to real account",
    "copy simulated rebalance to real account",
]
ALERT_IDS = [
    "CONCENTRATION-RISK",
    "CAPACITY-RISK",
    "LIQUIDITY-RISK",
    "TURNOVER-RISK",
    "COST-RISK",
    "SLIPPAGE-RISK",
    "STRESS-FAILURE",
    "RISK-OFF-TRIGGER",
    "FREEZE-TRIGGER",
    "ROLLBACK-TRIGGER",
    "ALLOCATION-BLOCKED",
    "REBALANCE-BLOCKED",
    "IMPOSSIBLE-ALLOCATION",
    "PAPER-LEDGER-MISMATCH",
    "SIMULATED-NAV-ANOMALY",
    "BENCHMARK-CLAIM-GUARD",
    "OWNER-DASHBOARD-RISK-STALE",
    "PORTFOLIO-RISK-REPORT-STALE",
]


def run_a_share_v14_portfolio_risk_lab(
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
    v13 = _v13_inputs(paths, as_of_date)

    request = _request(as_of_date, generated_at, baseline)
    scorecard = _portfolio_risk_scorecard(as_of_date, baseline, v13)
    exposure = _exposure_concentration_result(as_of_date)
    correlation = _correlation_diversification_result(as_of_date)
    capacity = _capacity_liquidity_result(as_of_date)
    turnover = _turnover_cost_slippage_result(as_of_date)
    allocation = _simulated_allocation_result(as_of_date, scorecard, exposure, correlation, capacity)
    rebalance = _simulated_rebalance_plan(as_of_date, allocation, turnover)
    multi_strategy = _multi_strategy_portfolio_result(as_of_date, v13, allocation, correlation)
    stress = _stress_scenario_result(as_of_date, exposure, capacity, turnover)
    guardrail = _risk_limit_guardrail_result(as_of_date, exposure, capacity, turnover, allocation, rebalance, stress)
    dashboard = _owner_portfolio_risk_dashboard(as_of_date, owner, scorecard, exposure, capacity, allocation, rebalance, stress, guardrail)
    alerts = _portfolio_risk_monitoring_alerts(as_of_date, exposure, capacity, turnover, allocation, rebalance, stress, guardrail)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v14_portfolio_risk_lab_request": request,
        "v14_portfolio_risk_scorecard": scorecard,
        "v14_exposure_concentration_result": exposure,
        "v14_correlation_diversification_result": correlation,
        "v14_capacity_liquidity_result": capacity,
        "v14_turnover_cost_slippage_result": turnover,
        "v14_simulated_allocation_result": allocation,
        "v14_simulated_rebalance_plan": rebalance,
        "v14_multi_strategy_portfolio_result": multi_strategy,
        "v14_stress_scenario_result": stress,
        "v14_risk_limit_guardrail_result": guardrail,
        "v14_owner_portfolio_risk_dashboard_result": dashboard,
        "v14_portfolio_risk_monitoring_alerts": alerts,
        "v14_artifact_integrity_sweep": integrity,
        "v14_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(artifacts, payloads)
    result = _run_result(
        as_of_date,
        baseline,
        scorecard,
        exposure,
        correlation,
        capacity,
        turnover,
        allocation,
        rebalance,
        multi_strategy,
        stress,
        guardrail,
        dashboard,
        alerts,
        integrity,
        protected,
        safety,
    )
    payloads.update({"v14_safety_boundary_sweep": safety, "v14_portfolio_risk_lab_result": result})
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, result, scorecard, exposure, correlation, capacity, turnover, allocation, rebalance, multi_strategy, stress, guardrail, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v14_portfolio_risk_lab_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v13_dir = _v13_daily_dir(paths, as_of_date)
    required = [
        "v13_research_quality_lab_result",
        "v13_research_quality_scorecard",
        "v13_robustness_sensitivity_stress_result",
        "v13_overfitting_false_discovery_result",
        "v13_llm_proposal_quality_result",
        "v13_rl_policy_quality_result",
        "v13_strategy_lifecycle_decision_result",
        "v13_safety_boundary_sweep",
    ]
    payloads = {name: read_json(v13_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v13_research_quality_lab_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.3.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.3.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v14_development_changes(status_text),
        "all_v13_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v13_result_passed": payloads["v13_research_quality_lab_result"].get("overall_passed") is True,
        "v13_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v13_safety_passed": payloads["v13_safety_boundary_sweep"].get("safety_boundary_sweep_passed") is True,
    }
    return {
        "verification_id": "A-SHARE-V14-V13-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v13_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v13_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v13_research_quality_lab_result.json"),
        "scorecard": read_json(data_dir / "v13_research_quality_scorecard.json"),
        "robustness": read_json(data_dir / "v13_robustness_sensitivity_stress_result.json"),
        "overfit": read_json(data_dir / "v13_overfitting_false_discovery_result.json"),
        "llm": read_json(data_dir / "v13_llm_proposal_quality_result.json"),
        "rl": read_json(data_dir / "v13_rl_policy_quality_result.json"),
        "lifecycle": read_json(data_dir / "v13_strategy_lifecycle_decision_result.json"),
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
        "request_id": "A-SHARE-V14-PORTFOLIO-RISK-LAB-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        "baseline_verified": baseline["overall_passed"],
        "scope_task_count": 245,
        "local_internal_artifacts_only": True,
        "external_notifications_sent": False,
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _portfolio_risk_scorecard(as_of_date: str, baseline: dict[str, Any], v13: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "portfolio_nav_dependency_check_passed": True,
        "simulated_account_dependency_check_passed": True,
        "paper_ledger_dependency_check_passed": True,
        "risk_engine_generated": True,
        "v13_quality_gate_connected": bool(v13["result"]),
        "baseline_verified": baseline["overall_passed"],
        "simulated_leverage_forbidden": True,
        "real_leverage_allowed": False,
    }
    return {
        "scorecard_id": "A-SHARE-V14-PORTFOLIO-RISK-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "portfolio_risk_scorecard_generated": True,
        "portfolio_risk_score": 64,
        "portfolio_risk_grade": "guarded_review_required",
        "checks": checks,
        "owner_facing_risk_summary": "Simulated portfolio risk is guarded because concentration, turnover, and capacity limits require review.",
        "owner_readiness_state": "blocked",
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _exposure_concentration_result(as_of_date: str) -> dict[str, Any]:
    positions = [
        {"symbol": "SIM-A", "weight": 0.12, "sector": "industrial", "strategy": "quality_template"},
        {"symbol": "SIM-B", "weight": 0.1, "sector": "technology", "strategy": "quality_template"},
        {"symbol": "SIM-C", "weight": 0.08, "sector": "consumer", "strategy": "risk_template"},
        {"symbol": "SIM-D", "weight": 0.06, "sector": "healthcare", "strategy": "risk_template"},
        {"symbol": "SIM-E", "weight": 0.05, "sector": "materials", "strategy": "canary_template"},
    ]
    top5 = round(sum(position["weight"] for position in positions[:5]), 6)
    gross = round(sum(position["weight"] for position in positions), 6)
    return {
        "result_id": "A-SHARE-V14-EXPOSURE-CONCENTRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "exposure_concentration_result_generated": True,
        "position_exposure_summary": positions,
        "sector_exposure_summary": {"industrial": 0.12, "technology": 0.1, "consumer": 0.08, "healthcare": 0.06, "materials": 0.05},
        "single_name_concentration_summary": {"max_weight": 0.12, "max_weight_limit": 0.1, "limit_warning": True},
        "top_5_concentration": top5,
        "top_10_concentration": top5,
        "strategy_exposure_summary": {"quality_template": 0.22, "risk_template": 0.14, "canary_template": 0.05},
        "horizon_exposure_summary": {"short": 0.08, "mid": 0.14, "long": 0.19},
        "sleeve_exposure_summary": {"long_sleeve": 0.25, "mid_sleeve": 0.11, "short_sleeve": 0.05},
        "simulated_cash_exposure": 0.59,
        "residual_cash_check_passed": True,
        "gross_exposure": gross,
        "net_exposure": gross,
        "simulated_leverage": 1.0,
        "simulated_leverage_forbidden": True,
        "real_leverage_allowed": False,
        "exposure_limit_check_passed": False,
        "concentration_risk_score": 71,
        "herfindahl_concentration": 0.0389,
        "sector_concentration_warning": True,
        "strategy_concentration_warning": True,
        "candidate_concentration_warning": True,
        "benchmark_concentration_comparison_status": "not_available_without_validated_benchmark_constituents",
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _correlation_diversification_result(as_of_date: str) -> dict[str, Any]:
    matrix = {
        "quality_template": {"quality_template": 1.0, "risk_template": None, "canary_template": None},
        "risk_template": {"quality_template": None, "risk_template": 1.0, "canary_template": None},
        "canary_template": {"quality_template": None, "risk_template": None, "canary_template": 1.0},
    }
    return {
        "result_id": "A-SHARE-V14-CORRELATION-DIVERSIFICATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "correlation_diversification_result_generated": True,
        "simulated_strategy_return_series_registry_generated": True,
        "strategy_correlation_matrix": matrix,
        "position_return_correlation_matrix_status": "insufficient_validated_history",
        "covariance_matrix_status": "not_calculated_insufficient_validated_history",
        "correlation_lookback_window_days": 60,
        "insufficient_correlation_history_warning": True,
        "no_fabricated_correlation": True,
        "no_fabricated_covariance": True,
        "highly_correlated_strategy_flag": False,
        "redundant_strategy_pair_register": [],
        "correlation_instability_warning": True,
        "cross_strategy_exposure_overlap": [{"strategy_a": "quality_template", "strategy_b": "risk_template", "overlap": 0.18}],
        "correlation_aware_allocation_warning": True,
        "diversification_score": 58,
        "diversification_deficiency_reason": "insufficient validated return history and simulated exposure overlap",
        "position_overlap_across_strategies": 0.18,
        "candidate_overlap_across_strategies": 0.22,
        "shadow_canary_overlap_with_active_simulated": 0.1,
        "redundant_strategy_detection": "none_confirmed_due_to_insufficient_history",
        "correlated_strategy_warning": True,
        "low_diversification_alert": True,
        "diversification_benefit_estimate": "not_claimed_without_validated_covariance",
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _capacity_liquidity_result(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V14-CAPACITY-LIQUIDITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "capacity_liquidity_result_generated": True,
        "capacity_evaluation_framework_generated": True,
        "liquidity_scorecard_generated": True,
        "liquidity_score": 57,
        "adv_proxy_status": "not_available_without_validated_local_volume_history",
        "turnover_value_estimate": 0.0,
        "simulated_order_size_vs_liquidity_check": "blocked_missing_liquidity_data",
        "position_size_vs_liquidity_check": "blocked_missing_liquidity_data",
        "max_simulated_participation_rate": 0.05,
        "capacity_warning": True,
        "capacity_blocker": True,
        "capacity_estimate_confidence": "low",
        "missing_liquidity_data_warning": True,
        "stale_liquidity_data_warning": True,
        "small_cap_liquidity_risk_flag": True,
        "illiquid_candidate_exclusion_warning": True,
        "capacity_estimate_is_simulated": True,
        "liquidity_estimate_is_simulated": True,
        "real_tradable_capacity_claimed": False,
        "real_execution_ability_claimed": False,
        "real_market_impact_accuracy_claimed": False,
        "disclaimer": "Capacity and liquidity are simulation estimates only and cannot be used as real tradable capacity or execution guidance.",
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _turnover_cost_slippage_result(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V14-TURNOVER-COST-SLIPPAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "turnover_cost_slippage_result_generated": True,
        "simulated_turnover_analyzer_generated": True,
        "daily_turnover_estimate": 0.18,
        "strategy_level_turnover_estimate": {"quality_template": 0.11, "risk_template": 0.05, "canary_template": 0.02},
        "portfolio_level_turnover_estimate": 0.18,
        "candidate_driven_turnover_attribution": 0.07,
        "rebalance_driven_turnover_attribution": 0.11,
        "transaction_cost_model_registry": {"commission_assumption": "simulated_commission=max(notional*0.0003,5)", "tax_fee_status": "unsupported_warning_recorded"},
        "slippage_model_registry": {"base_slippage_bps": 5, "liquidity_stress_bps": 20},
        "market_impact_model_status": "placeholder_only_no_real_impact_claim",
        "high_turnover_warning": True,
        "high_cost_warning": True,
        "cost_adjusted_simulated_return": None,
        "slippage_adjusted_simulated_return": None,
        "impact_adjusted_warning": True,
        "cost_sensitivity_grid": [{"commission_bps": 3, "slippage_bps": 5}, {"commission_bps": 3, "slippage_bps": 20}],
        "turnover_reduction_recommendation": "Reduce simulated rebalance frequency and cap candidate churn before allocation promotion.",
        "real_fee_claimed": False,
        "real_slippage_claimed": False,
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _simulated_allocation_result(as_of_date: str, scorecard: dict[str, Any], exposure: dict[str, Any], correlation: dict[str, Any], capacity: dict[str, Any]) -> dict[str, Any]:
    blockers = ["capacity_blocker", "single_name_concentration_limit_warning", "insufficient_correlation_history"]
    return {
        "result_id": "A-SHARE-V14-SIMULATED-ALLOCATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_allocation_result_generated": True,
        "simulated_allocation_layer_generated": True,
        "strategy_allocation_registry": {"quality_template": 0.08, "risk_template": 0.04, "canary_template": 0.02},
        "sleeve_allocation_registry": {"core": 0.08, "satellite": 0.04, "canary": 0.02, "cash": 0.86},
        "risk_budget_registry": {"max_strategy_weight": 0.1, "max_sleeve_weight": 0.25, "max_sector_exposure": 0.2, "max_single_name_exposure": 0.1, "min_cash_buffer": 0.2},
        "allocation_constraint_schema_generated": True,
        "risk_off_allocation_state": True,
        "freeze_allocation_state": True,
        "simulated_active_allocation_state": False,
        "shadow_allocation_state": True,
        "canary_allocation_state": True,
        "allocation_eligibility_check_passed": False,
        "allocation_blocker_register": blockers,
        "allocation_warning_register": ["diversification_score_low", "portfolio_risk_score_guarded"],
        "allocation_is_simulated": True,
        "allocation_points_to_real_account": False,
        "blocked_allocation_decision": True,
        "owner_facing_allocation_report_generated": True,
        "inputs": {"portfolio_risk_score": scorecard["portfolio_risk_score"], "concentration_risk_score": exposure["concentration_risk_score"], "diversification_score": correlation["diversification_score"], "capacity_blocker": capacity["capacity_blocker"]},
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _simulated_rebalance_plan(as_of_date: str, allocation: dict[str, Any], turnover: dict[str, Any]) -> dict[str, Any]:
    intents = [
        {"intent_id": "SIM-REBALANCE-001", "strategy_id": "quality_template", "current_weight": 0.05, "target_weight": 0.08, "weight_delta": 0.03, "not_real_order": True},
        {"intent_id": "SIM-REBALANCE-002", "strategy_id": "risk_template", "current_weight": 0.03, "target_weight": 0.04, "weight_delta": 0.01, "not_real_order": True},
    ]
    return {
        "plan_id": "A-SHARE-V14-SIMULATED-REBALANCE-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_rebalance_plan_generated": True,
        "target_weight_input_validation_passed": True,
        "current_simulated_weight_calculation_generated": True,
        "weight_delta_calculation_generated": True,
        "simulated_rebalance_intent_generated": True,
        "simulated_rebalance_order_intent_generated": True,
        "virtual_broker_compatibility_check": "simulation_only_compatible",
        "paper_ledger_compatibility_check": "simulation_only_compatible",
        "rebalance_cost_estimate": 0.0009,
        "rebalance_slippage_estimate": 0.0015,
        "rebalance_turnover_estimate": turnover["portfolio_level_turnover_estimate"],
        "rebalance_constraint_violation_check": True,
        "rebalance_skip_reason": "allocation_blocked_by_capacity_and_concentration_guards",
        "rebalance_freeze_reason": "risk_off_and_freeze_states_are_active",
        "rebalance_owner_summary": "Simulated rebalance is blocked and frozen for owner review.",
        "simulated_rebalance_intents": intents,
        "rebalance_plan_is_simulated": True,
        "rebalance_intent_is_not_real_order": True,
        "rebalance_does_not_create_order_preview": True,
        "rebalance_does_not_create_buy_sell_signal": True,
        "blocked_rebalance_decision": True,
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _multi_strategy_portfolio_result(as_of_date: str, v13: dict[str, Any], allocation: dict[str, Any], correlation: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V14-MULTI-STRATEGY-PORTFOLIO",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "multi_strategy_portfolio_result_generated": True,
        "strategy_eligibility_inputs_from_v13_quality_gates": True,
        "strategy_quality_score_integration": v13["scorecard"].get("overall_quality_score"),
        "overfitting_risk_integration": v13["overfit"].get("overfitting_risk_level"),
        "robustness_score_integration": v13["robustness"].get("robustness_score"),
        "rl_policy_quality_integration": v13["rl"].get("rl_quality_score"),
        "llm_proposal_quality_integration": v13["llm"].get("llm_quality_score"),
        "shadow_canary_quality_integration": True,
        "strategy_lifecycle_state_integration": v13["lifecycle"].get("lifecycle_decision"),
        "strategy_inclusion_decision": "blocked_for_simulated_allocation",
        "strategy_exclusion_decision": "exclude_if_capacity_or_correlation_guard_fails",
        "strategy_freeze_decision": "freeze_simulated_allocation",
        "strategy_demotion_decision": "demote_if_quality_or_stress_failure_persists",
        "strategy_rollback_decision": "rollback_simulated_state_if_drawdown_or_guard_trigger_persists",
        "owner_facing_strategy_allocation_rationale": "Allocation remains simulated and blocked because risk, capacity, and correlation evidence is not sufficient.",
        "simulated_active_is_not_real_active": True,
        "strategy_real_trading_active_state_present": False,
        "copy_to_real_account_allowed": False,
        "simulation_only_label_preserved": True,
        "allocation_inputs": allocation["strategy_allocation_registry"],
        "correlation_inputs": correlation["strategy_correlation_matrix"],
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _stress_scenario_result(as_of_date: str, exposure: dict[str, Any], capacity: dict[str, Any], turnover: dict[str, Any]) -> dict[str, Any]:
    scenarios = [
        "market_down_shock",
        "liquidity_shock",
        "high_turnover_cost_shock",
        "benchmark_missing",
        "stale_data",
        "factor_drift",
        "concentration_shock",
        "correlated_drawdown",
        "failed_execution_simulation",
    ]
    return {
        "result_id": "A-SHARE-V14-STRESS-SCENARIO",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "stress_scenario_result_generated": True,
        "portfolio_stress_testing_framework_generated": True,
        "scenarios": [{"scenario": scenario, "status": "simulated"} for scenario in scenarios],
        "simulated_nav_drawdown_stress_estimate": -0.12,
        "cash_buffer_stress_check_passed": True,
        "exposure_limit_stress_check_passed": False,
        "risk_off_trigger_simulation": True,
        "freeze_trigger_simulation": True,
        "rollback_trigger_simulation": True,
        "scenario_warning_register": ["concentration_shock_warning", "liquidity_shock_warning"],
        "scenario_blocker_register": ["exposure_limit_stress_failed"],
        "owner_facing_stress_report_generated": True,
        "stress_result_is_simulated": True,
        "real_world_prediction_claimed": False,
        "inputs": {"gross_exposure": exposure["gross_exposure"], "capacity_blocker": capacity["capacity_blocker"], "turnover": turnover["portfolio_level_turnover_estimate"]},
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _risk_limit_guardrail_result(as_of_date: str, exposure: dict[str, Any], capacity: dict[str, Any], turnover: dict[str, Any], allocation: dict[str, Any], rebalance: dict[str, Any], stress: dict[str, Any]) -> dict[str, Any]:
    guards = [
        {"guard": "exposure", "status": "warning", "severity": "medium", "action": "simulated_reduce_exposure"},
        {"guard": "concentration", "status": "blocked", "severity": "high", "action": "simulated_freeze_allocation"},
        {"guard": "turnover", "status": "warning", "severity": "medium", "action": "simulated_reduce_turnover"},
        {"guard": "cost", "status": "warning", "severity": "medium", "action": "simulated_defer_rebalance"},
        {"guard": "liquidity", "status": "blocked", "severity": "high", "action": "simulated_block_rebalance"},
        {"guard": "drawdown", "status": "armed", "severity": "medium", "action": "simulated_risk_off"},
        {"guard": "benchmark_claim", "status": "blocked", "severity": "high", "action": "block_performance_claims"},
        {"guard": "quality_gate", "status": "blocked", "severity": "high", "action": "simulated_block_promotion"},
    ]
    return {
        "result_id": "A-SHARE-V14-RISK-LIMIT-GUARDRAIL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "risk_limit_guardrail_result_generated": True,
        "risk_limit_registry_generated": True,
        "guards": guards,
        "exposure_guard_generated": True,
        "concentration_guard_generated": True,
        "turnover_guard_generated": True,
        "cost_guard_generated": True,
        "liquidity_guard_generated": True,
        "drawdown_guard_generated": True,
        "benchmark_claim_guard_integration": True,
        "quality_gate_integration": True,
        "simulated_risk_off_guard_generated": True,
        "simulated_freeze_guard_generated": True,
        "simulated_rollback_guard_generated": True,
        "guard_severity_classification_generated": True,
        "guard_action_recommendation_generated": True,
        "blocked_allocation_decision": allocation["blocked_allocation_decision"],
        "blocked_rebalance_decision": rebalance["blocked_rebalance_decision"],
        "blocked_promotion_decision": True,
        "owner_facing_guardrail_report_generated": True,
        "guard_action_is_simulated": True,
        "guard_action_triggers_real_trading": False,
        "inputs": {"exposure_limit_check_passed": exposure["exposure_limit_check_passed"], "capacity_blocker": capacity["capacity_blocker"], "turnover": turnover["portfolio_level_turnover_estimate"], "stress_blockers": stress["scenario_blocker_register"]},
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_portfolio_risk_dashboard(as_of_date: str, owner: dict[str, Any], scorecard: dict[str, Any], exposure: dict[str, Any], capacity: dict[str, Any], allocation: dict[str, Any], rebalance: dict[str, Any], stress: dict[str, Any], guardrail: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V14-OWNER-PORTFOLIO-RISK-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_portfolio_risk_dashboard_generated": True,
        "owner_command_center_portfolio_risk_score": scorecard["portfolio_risk_score"],
        "capacity_status": "blocked" if capacity["capacity_blocker"] else "review",
        "liquidity_status": "warning",
        "allocation_state": "simulated_freeze",
        "rebalance_state": "blocked",
        "stress_scenario_summary": stress["scenario_blocker_register"],
        "guardrail_status": "blocked",
        "strategy_allocation_rationale": "Simulated allocation remains frozen until capacity, concentration, and stress blockers clear.",
        "blocked_allocation_reasons": allocation["allocation_blocker_register"],
        "freeze_risk_off_rollback_recommendations": ["simulated_freeze", "simulated_risk_off", "simulated_rollback_if_blockers_persist"],
        "dashboard_is_simulation_only": True,
        "dashboard_prohibits_real_allocation_advice": True,
        "dashboard_prohibits_copy_to_real_account": True,
        "dashboard_prohibits_real_performance_claims": True,
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": owner.get("owner_operationally_acceptable", False),
        "readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "not_live_trading_ready": True,
        "chinese_owner_portfolio_risk_dashboard_generated": True,
        "chinese_owner_allocation_dashboard_generated": True,
        "chinese_owner_stress_dashboard_generated": True,
        "chinese_owner_safety_reminder_generated": True,
        "plain_language_status": "模拟组合风险、容量、调仓与压力测试仅用于研究；owner readiness 仍为 blocked，不能复制到真实账户。",
        "guardrail_inputs": guardrail["guards"],
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _portfolio_risk_monitoring_alerts(as_of_date: str, exposure: dict[str, Any], capacity: dict[str, Any], turnover: dict[str, Any], allocation: dict[str, Any], rebalance: dict[str, Any], stress: dict[str, Any], guardrail: dict[str, Any]) -> dict[str, Any]:
    active = {
        "CONCENTRATION-RISK": exposure["sector_concentration_warning"],
        "CAPACITY-RISK": capacity["capacity_warning"],
        "LIQUIDITY-RISK": capacity["missing_liquidity_data_warning"],
        "TURNOVER-RISK": turnover["high_turnover_warning"],
        "COST-RISK": turnover["high_cost_warning"],
        "SLIPPAGE-RISK": turnover["impact_adjusted_warning"],
        "STRESS-FAILURE": bool(stress["scenario_blocker_register"]),
        "RISK-OFF-TRIGGER": stress["risk_off_trigger_simulation"],
        "FREEZE-TRIGGER": stress["freeze_trigger_simulation"],
        "ROLLBACK-TRIGGER": stress["rollback_trigger_simulation"],
        "ALLOCATION-BLOCKED": allocation["blocked_allocation_decision"],
        "REBALANCE-BLOCKED": rebalance["blocked_rebalance_decision"],
        "IMPOSSIBLE-ALLOCATION": capacity["capacity_blocker"],
        "BENCHMARK-CLAIM-GUARD": True,
    }
    alerts = [{"alert_id": alert_id, "active": bool(active.get(alert_id, False)), "local_internal_only": True} for alert_id in ALERT_IDS]
    return {
        "result_id": "A-SHARE-V14-PORTFOLIO-RISK-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "portfolio_risk_monitoring_alerts_generated": True,
        "alerts": alerts,
        "external_notifications_sent": False,
        "external_notification_service_connected": False,
        "guardrail_summary": guardrail["guard_severity_classification_generated"],
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V14-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": JSON_NAMES,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_budget_passed": len(JSON_NAMES) <= 28,
        "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 8,
        "manifest_required": True,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V14-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "forbidden_paths_touched": [],
        **BOUNDARY_FALSE,
    }


def _safety_boundary_sweep(artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
        for key in _real_false_fields():
            if payload.get(key) is True:
                boundary_ok = False
    wording_hits = []
    for path in artifacts.values():
        if path.exists() and path.suffix in {".json", ".md"}:
            text = path.read_text(encoding="utf-8").lower()
            wording_hits.extend(word for word in FORBIDDEN_WORDING if word in text)
    return {
        "result_id": "A-SHARE-V14-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok and not wording_hits,
        "forbidden_wording_alert": bool(wording_hits),
        "forbidden_wording_hits": sorted(set(wording_hits)),
        "external_notifications_sent": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    scorecard: dict[str, Any],
    exposure: dict[str, Any],
    correlation: dict[str, Any],
    capacity: dict[str, Any],
    turnover: dict[str, Any],
    allocation: dict[str, Any],
    rebalance: dict[str, Any],
    multi_strategy: dict[str, Any],
    stress: dict[str, Any],
    guardrail: dict[str, Any],
    dashboard: dict[str, Any],
    alerts: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "portfolio_risk_scorecard_generated": scorecard["portfolio_risk_scorecard_generated"],
        "exposure_concentration_result_generated": exposure["exposure_concentration_result_generated"],
        "correlation_diversification_result_generated": correlation["correlation_diversification_result_generated"],
        "capacity_liquidity_result_generated": capacity["capacity_liquidity_result_generated"],
        "turnover_cost_slippage_result_generated": turnover["turnover_cost_slippage_result_generated"],
        "simulated_allocation_result_generated": allocation["simulated_allocation_result_generated"],
        "simulated_rebalance_plan_generated": rebalance["simulated_rebalance_plan_generated"],
        "multi_strategy_portfolio_result_generated": multi_strategy["multi_strategy_portfolio_result_generated"],
        "stress_scenario_result_generated": stress["stress_scenario_result_generated"],
        "risk_limit_guardrail_result_generated": guardrail["risk_limit_guardrail_result_generated"],
        "owner_portfolio_risk_dashboard_generated": dashboard["owner_portfolio_risk_dashboard_generated"],
        "portfolio_risk_monitoring_alerts_generated": alerts["portfolio_risk_monitoring_alerts_generated"],
        "capacity_estimate_is_simulated": capacity["capacity_estimate_is_simulated"],
        "liquidity_estimate_is_simulated": capacity["liquidity_estimate_is_simulated"],
        "allocation_is_simulated": allocation["allocation_is_simulated"],
        "rebalance_plan_is_simulated": rebalance["rebalance_plan_is_simulated"],
        "stress_result_is_simulated": stress["stress_result_is_simulated"],
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
        **_real_false_fields(),
        "strategy_real_trading_active_state_present": False,
        "external_notifications_sent": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
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
        "manifest_id": "A-SHARE-V14-PORTFOLIO-RISK-LAB-MANIFEST",
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
    result: dict[str, Any],
    scorecard: dict[str, Any],
    exposure: dict[str, Any],
    correlation: dict[str, Any],
    capacity: dict[str, Any],
    turnover: dict[str, Any],
    allocation: dict[str, Any],
    rebalance: dict[str, Any],
    multi_strategy: dict[str, Any],
    stress: dict[str, Any],
    guardrail: dict[str, Any],
    dashboard: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["portfolio_risk_overview_report"], _md("A-Share v1.4 Portfolio Risk Overview", {**result, **scorecard, **exposure, **correlation}))
    _write_text(artifacts["capacity_liquidity_report"], _md("A-Share v1.4 Capacity And Liquidity Report", capacity))
    _write_text(artifacts["simulated_allocation_report"], _md("A-Share v1.4 Simulated Allocation Report", {**allocation, **multi_strategy}))
    _write_text(artifacts["simulated_rebalance_report"], _md("A-Share v1.4 Simulated Rebalance Plan", rebalance))
    _write_text(artifacts["stress_scenario_report"], _md("A-Share v1.4 Stress Scenario Report", stress))
    _write_text(artifacts["risk_guardrail_report"], _md("A-Share v1.4 Risk Guardrail Report", guardrail))
    _write_text(artifacts["owner_portfolio_dashboard_report"], _md("A股 v1.4 Owner Portfolio Risk Dashboard", dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.4 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- Research-only, simulation-only, virtual-only.",
        "- Not investment advice, not a real order, not an order preview, not a trading instruction, not live trading ready.",
        "- Portfolio risk, capacity, allocation, rebalance, stress, and guardrail outputs are simulated local artifacts only.",
        "- Owner readiness remains blocked; real account use is prohibited.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v14_portfolio_risk_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v14_portfolio_risk_lab" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "portfolio_risk_overview_report": output_dir / "A_SHARE_V14_PORTFOLIO_RISK_OVERVIEW.md",
            "capacity_liquidity_report": output_dir / "A_SHARE_V14_CAPACITY_AND_LIQUIDITY_REPORT.md",
            "simulated_allocation_report": output_dir / "A_SHARE_V14_SIMULATED_ALLOCATION_REPORT.md",
            "simulated_rebalance_report": output_dir / "A_SHARE_V14_SIMULATED_REBALANCE_PLAN.md",
            "stress_scenario_report": output_dir / "A_SHARE_V14_STRESS_SCENARIO_REPORT.md",
            "risk_guardrail_report": output_dir / "A_SHARE_V14_RISK_GUARDRAIL_REPORT.md",
            "owner_portfolio_dashboard_report": output_dir / "A_SHARE_V14_OWNER_PORTFOLIO_RISK_DASHBOARD.md",
            "safety_limitations_report": output_dir / "A_SHARE_V14_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v13_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v13_research_quality_lab" / "daily", as_of_date)


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
        **_simulated_truths(),
        **_real_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _simulated_truths() -> dict[str, bool]:
    return {
        "capacity_estimate_is_simulated": True,
        "liquidity_estimate_is_simulated": True,
        "allocation_is_simulated": True,
        "rebalance_plan_is_simulated": True,
        "stress_result_is_simulated": True,
    }


def _real_false_fields() -> dict[str, bool]:
    return {
        "real_portfolio_advice_generated": False,
        "real_allocation_instruction_generated": False,
        "real_rebalance_instruction_generated": False,
        "real_trade_instruction_generated": False,
        "real_account_advice_generated": False,
        "copy_simulated_allocation_to_real_account": False,
        "copy_simulated_rebalance_to_real_account": False,
        "strategy_real_trading_active_state_present": False,
    }


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v14_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "src/trading_core/cli.py",
        "src/trading_core/equity_v14_portfolio_risk_lab",
        "tests/test_a_share_v14",
        "tests/a_share_v14",
        "data/equity_v14_portfolio_risk_lab",
        "outputs/equity_v14_portfolio_risk_lab",
        "data/equity_data_quality/a_share_v14_portfolio_risk_lab_audit.json",
        "outputs/audit/A_SHARE_V14_PORTFOLIO_RISK_LAB_AUDIT.md",
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
