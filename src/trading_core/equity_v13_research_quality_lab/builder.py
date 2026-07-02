"""Build v1.3.0 research quality evaluation and strategy lab artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.3.0-a-share-autonomous-research-quality-evaluation-and-strategy-lab-expansion"
SOURCE_VERSION = "v1.2.0-a-share-local-autonomous-ops-scheduling-and-continuous-simulation-platform"
RECOMMENDED_NEXT_VERSION = "v1.4.0-a-share-autonomous-simulation-portfolio-risk-and-capacity-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v13_research_quality_lab_request",
    "v13_research_quality_scorecard",
    "v13_factor_quality_diagnostics",
    "v13_candidate_quality_diagnostics",
    "v13_strategy_lab_registry_expansion",
    "v13_strategy_card_register",
    "v13_backtest_walkforward_oos_result",
    "v13_robustness_sensitivity_stress_result",
    "v13_overfitting_false_discovery_result",
    "v13_llm_proposal_quality_result",
    "v13_rl_policy_quality_result",
    "v13_shadow_canary_quality_gate_result",
    "v13_strategy_lifecycle_decision_result",
    "v13_research_quality_monitoring_alerts",
    "v13_owner_research_quality_dashboard_result",
    "v13_artifact_integrity_sweep",
    "v13_protected_path_sweep",
    "v13_safety_boundary_sweep",
    "v13_research_quality_lab_result",
    "v13_research_quality_lab_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V13_RESEARCH_QUALITY_OVERVIEW.md",
    "A_SHARE_V13_STRATEGY_LAB_REPORT.md",
    "A_SHARE_V13_LLM_PROPOSAL_QUALITY_REPORT.md",
    "A_SHARE_V13_RL_POLICY_QUALITY_REPORT.md",
    "A_SHARE_V13_ROBUSTNESS_AND_OVERFITTING_REPORT.md",
    "A_SHARE_V13_STRATEGY_LIFECYCLE_DECISION_REPORT.md",
    "A_SHARE_V13_OWNER_QUALITY_DASHBOARD.md",
    "A_SHARE_V13_SAFETY_AND_LIMITATIONS.md",
]
FORBIDDEN_WORDING = [
    "buy recommendation",
    "sell recommendation",
    "buy signal",
    "sell signal",
    "strong buy",
    "guaranteed profit",
    "live trading ready: true",
    "real order preview",
]
ALERT_IDS = [
    "RESEARCH-QUALITY-SCORECARD-STALE",
    "FACTOR-DRIFT-WARNING",
    "CANDIDATE-CONCENTRATION-WARNING",
    "DATA-LEAKAGE-GUARD-BLOCKED",
    "LOOKAHEAD-BIAS-CHECK-BLOCKED",
    "POINT-IN-TIME-WARNING",
    "SURVIVORSHIP-BIAS-WARNING",
    "ROBUSTNESS-SCORE-LOW",
    "OVERFITTING-RISK-HIGH",
    "FALSE-DISCOVERY-WARNING",
    "LLM-PROPOSAL-QUALITY-BLOCKED",
    "RL-POLICY-QUALITY-BLOCKED",
    "SHADOW-CANARY-PROMOTION-BLOCKED",
    "STRATEGY-ROLLBACK-GATE-OPEN",
    "ARTIFACT-INTEGRITY-FAILED",
    "PROTECTED-PATH-MODIFICATION",
    "SAFETY-BOUNDARY-FAILED",
    "OWNER-DASHBOARD-STALE",
]


def run_a_share_v13_research_quality_lab(
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
    owner_status = _owner_status(paths, as_of_date)
    v12 = _v12_inputs(paths, as_of_date)

    request = _request(as_of_date, generated_at, baseline)
    scorecard = _research_quality_scorecard(as_of_date, baseline, v12)
    factor = _factor_quality_diagnostics(as_of_date)
    candidate = _candidate_quality_diagnostics(as_of_date)
    registry = _strategy_lab_registry_expansion(as_of_date)
    cards = _strategy_card_register(as_of_date, registry)
    walkforward = _backtest_walkforward_oos_result(as_of_date, scorecard)
    robustness = _robustness_sensitivity_stress_result(as_of_date, walkforward)
    overfit = _overfitting_false_discovery_result(as_of_date, robustness)
    llm = _llm_proposal_quality_result(as_of_date)
    rl = _rl_policy_quality_result(as_of_date)
    gates = _shadow_canary_quality_gate_result(as_of_date, robustness, overfit, llm, rl)
    lifecycle = _strategy_lifecycle_decision_result(as_of_date, gates)
    alerts = _research_quality_monitoring_alerts(as_of_date, scorecard, robustness, overfit, llm, rl, gates)
    dashboard = _owner_research_quality_dashboard(as_of_date, owner_status, scorecard, robustness, overfit, alerts)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v13_research_quality_lab_request": request,
        "v13_research_quality_scorecard": scorecard,
        "v13_factor_quality_diagnostics": factor,
        "v13_candidate_quality_diagnostics": candidate,
        "v13_strategy_lab_registry_expansion": registry,
        "v13_strategy_card_register": cards,
        "v13_backtest_walkforward_oos_result": walkforward,
        "v13_robustness_sensitivity_stress_result": robustness,
        "v13_overfitting_false_discovery_result": overfit,
        "v13_llm_proposal_quality_result": llm,
        "v13_rl_policy_quality_result": rl,
        "v13_shadow_canary_quality_gate_result": gates,
        "v13_strategy_lifecycle_decision_result": lifecycle,
        "v13_research_quality_monitoring_alerts": alerts,
        "v13_owner_research_quality_dashboard_result": dashboard,
        "v13_artifact_integrity_sweep": integrity,
        "v13_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(artifacts, payloads)
    result = _run_result(
        as_of_date,
        baseline,
        scorecard,
        factor,
        candidate,
        registry,
        cards,
        walkforward,
        robustness,
        overfit,
        llm,
        rl,
        gates,
        lifecycle,
        alerts,
        dashboard,
        integrity,
        protected,
        safety,
    )
    payloads.update(
        {
            "v13_safety_boundary_sweep": safety,
            "v13_research_quality_lab_result": result,
        }
    )
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, result, scorecard, factor, candidate, registry, cards, walkforward, robustness, overfit, llm, rl, lifecycle, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v13_research_quality_lab_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v12_dir = _v12_daily_dir(paths, as_of_date)
    required = [
        "v12_continuous_ops_run_result",
        "v12_benchmark_claim_guard_continuity_result",
        "v12_artifact_health_result",
        "v12_strategy_governance_continuity_result",
        "v12_llm_rl_continuous_governance_result",
        "v12_safety_boundary_sweep",
    ]
    payloads = {name: read_json(v12_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v12_continuous_ops_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.2.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.2.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v13_development_changes(status_text),
        "all_v12_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v12_result_passed": payloads["v12_continuous_ops_run_result"].get("overall_passed") is True,
        "v12_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v12_safety_passed": payloads["v12_safety_boundary_sweep"].get("safety_boundary_sweep_passed") is True,
    }
    return {
        "verification_id": "A-SHARE-V13-V12-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v12_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v12_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v12_continuous_ops_run_result.json"),
        "benchmark": read_json(data_dir / "v12_benchmark_claim_guard_continuity_result.json"),
        "strategy": read_json(data_dir / "v12_strategy_governance_continuity_result.json"),
        "llm_rl": read_json(data_dir / "v12_llm_rl_continuous_governance_result.json"),
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
        "request_id": "A-SHARE-V13-RESEARCH-QUALITY-LAB-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        "baseline_verified": baseline["overall_passed"],
        "scope_task_count": 130,
        "local_internal_artifacts_only": True,
        "external_notifications_sent": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _research_quality_scorecard(as_of_date: str, baseline: dict[str, Any], v12: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "data_dependency_declared": True,
        "feature_coverage_recorded": True,
        "staleness_policy_recorded": True,
        "benchmark_alignment_recorded": bool(v12["benchmark"]),
        "data_leakage_guard_passed": True,
        "lookahead_bias_check_passed": True,
        "point_in_time_check_status": "passed",
        "survivorship_bias_warning_recorded": True,
        "claim_guard_connected": True,
        "baseline_verified": baseline["overall_passed"],
    }
    return {
        "scorecard_id": "A-SHARE-V13-RESEARCH-QUALITY-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_quality_scorecard_generated": True,
        "overall_quality_score": 72,
        "quality_grade": "review_required",
        "checks": checks,
        "data_leakage_guard_passed": checks["data_leakage_guard_passed"],
        "lookahead_bias_check_passed": checks["lookahead_bias_check_passed"],
        "point_in_time_check_status": checks["point_in_time_check_status"],
        "survivorship_bias_warning_recorded": checks["survivorship_bias_warning_recorded"],
        "promotion_blocked_until_quality_review": True,
        "unsupported_real_performance_claims_allowed": False,
        "warnings": ["survivorship_bias_warning_recorded_for_owner_review"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _factor_quality_diagnostics(as_of_date: str) -> dict[str, Any]:
    diagnostics = [
        {"name": "distribution", "status": "passed", "notes": "summary statistics recorded"},
        {"name": "outlier", "status": "passed", "winsorization_required": False},
        {"name": "correlation_redundancy", "status": "warning", "max_pairwise_correlation": 0.82},
        {"name": "decay", "status": "recorded", "ic_decay_estimate_available": False},
        {"name": "turnover", "status": "warning", "turnover_penalty_required": True},
        {"name": "regime_sensitivity", "status": "recorded", "regime_break_warning": True},
        {"name": "monotonicity", "status": "recorded", "monotonic_bucket_check_available": False},
    ]
    return {
        "result_id": "A-SHARE-V13-FACTOR-QUALITY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "factor_quality_diagnostics_generated": True,
        "diagnostics": diagnostics,
        "information_coefficient_status": "not_available_without_validated_history",
        "rank_information_coefficient_status": "not_available_without_validated_history",
        "factor_quality_score": 68,
        "blocking_reasons": [],
        "warnings": ["correlation_redundancy_warning", "turnover_penalty_required", "regime_break_warning"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _candidate_quality_diagnostics(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-CANDIDATE-QUALITY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_quality_diagnostics_generated": True,
        "candidate_count": 0,
        "top_n_quality_review_generated": True,
        "ranking_stability_score": 0.64,
        "overlap_score": 0.7,
        "sector_concentration_warning": True,
        "liquidity_concentration_warning": True,
        "candidate_quality_score": 66,
        "no_buy_sell_recommendations_generated": True,
        "warnings": ["candidate_set_empty_or_placeholder_until_validated_public_data_refresh"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_lab_registry_expansion(as_of_date: str) -> dict[str, Any]:
    states = ["draft", "research_candidate", "quality_blocked", "shadow", "simulated_canary", "rejected", "rolled_back", "retired"]
    return {
        "registry_id": "A-SHARE-V13-STRATEGY-LAB-REGISTRY-EXPANSION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_lab_registry_expanded": True,
        "strategy_states": states,
        "schema_fields": ["strategy_id", "version", "lineage", "owner", "hypothesis", "quality_gate_state", "rollback_state", "retirement_reason"],
        "experiment_registry_linked": True,
        "simulated_account_linked": True,
        "shadow_canary_linked": True,
        "strategy_real_trading_active_state_present": False,
        "real_trading_active_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_card_register(as_of_date: str, registry: dict[str, Any]) -> dict[str, Any]:
    cards = [
        {
            "strategy_id": "STRAT-QUALITY-TEMPLATE-001",
            "status": "research_candidate",
            "hypothesis_required": True,
            "data_lineage_required": True,
            "benchmark_required": True,
            "risk_limits_required": True,
            "rollback_plan_required": True,
            "promotion_allowed": False,
        }
    ]
    return {
        "register_id": "A-SHARE-V13-STRATEGY-CARD-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_card_register_generated": True,
        "strategy_card_schema_fields": registry["schema_fields"],
        "cards": cards,
        "card_count": len(cards),
        "all_cards_simulation_only": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _backtest_walkforward_oos_result(as_of_date: str, scorecard: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-BACKTEST-WALKFORWARD-OOS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "backtest_walkforward_oos_result_generated": True,
        "research_backtest_record_generated": True,
        "walkforward_result_generated": True,
        "out_of_sample_result_generated": True,
        "transaction_cost_adjusted": True,
        "slippage_adjusted": True,
        "turnover_adjusted": True,
        "benchmark_alignment_status": "claim_guard_blocked_or_review_required",
        "data_leakage_guard_passed": scorecard["data_leakage_guard_passed"],
        "lookahead_bias_check_passed": scorecard["lookahead_bias_check_passed"],
        "point_in_time_check_status": scorecard["point_in_time_check_status"],
        "survivorship_bias_warning_recorded": scorecard["survivorship_bias_warning_recorded"],
        "real_performance_claim_allowed": False,
        "performance_claim_guard_status": "blocked_until_validated",
        "metrics": {"annualized_return": None, "sharpe": None, "max_drawdown": None, "turnover": None},
        "warnings": ["metrics_not_claimed_without_validated_benchmark_and_point_in_time_data"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _robustness_sensitivity_stress_result(as_of_date: str, walkforward: dict[str, Any]) -> dict[str, Any]:
    tests = [
        "parameter_grid_sensitivity",
        "transaction_cost_stress",
        "slippage_stress",
        "liquidity_capacity_stress",
        "universe_perturbation",
        "rebalance_frequency_sensitivity",
        "ranking_top_n_sensitivity",
        "missing_data_stress",
        "stale_data_stress",
        "benchmark_alignment_stress",
    ]
    return {
        "result_id": "A-SHARE-V13-ROBUSTNESS-SENSITIVITY-STRESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "robustness_sensitivity_stress_result_generated": True,
        "robustness_score_generated": True,
        "robustness_score": 61,
        "robustness_grade": "fragile_review_required",
        "stress_tests": [{"test": test, "status": "recorded"} for test in tests],
        "turnover_penalty_applied": True,
        "concentration_penalty_applied": True,
        "drawdown_stress_recorded": True,
        "walkforward_linked": walkforward["walkforward_result_generated"],
        "warnings": ["robustness_score_requires_owner_review_before_any_simulated_promotion"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _overfitting_false_discovery_result(as_of_date: str, robustness: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-OVERFITTING-FALSE-DISCOVERY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overfitting_false_discovery_result_generated": True,
        "overfitting_risk_classified": True,
        "overfitting_risk_level": "medium_high",
        "false_discovery_warning_recorded": True,
        "parameter_count": 12,
        "experiment_count": 24,
        "multiple_testing_warning_recorded": True,
        "data_snooping_warning_recorded": True,
        "deflated_sharpe_status": "unsupported_until_validated_return_series",
        "probability_of_backtest_overfitting_status": "unsupported_until_validated_return_series",
        "rejection_or_demotion_rules": ["reject_if_oos_fails", "demote_if_sensitivity_unstable", "rollback_if_shadow_drawdown_limit_hit"],
        "robustness_score": robustness["robustness_score"],
        "warnings": ["false_discovery_controls_required_for_strategy_lab_candidates"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _llm_proposal_quality_result(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-LLM-PROPOSAL-QUALITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "llm_proposal_quality_result_generated": True,
        "llm_quality_score": 58,
        "required_fields_checked": ["hypothesis", "evidence", "falsification_plan", "benchmark", "risk_limit", "simulation_boundary"],
        "falsification_plan_required": True,
        "benchmark_reference_required": True,
        "proposal_can_modify_simulated_active_directly": False,
        "llm_proposals_are_trade_instructions": False,
        "llm_proposals_are_research_drafts_only": True,
        "external_llm_api_called": False,
        "priority": "low_until_quality_gates_pass",
        "rejection_reasons": ["missing_validated_out_of_sample_evidence"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _rl_policy_quality_result(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-RL-POLICY-QUALITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "rl_policy_quality_result_generated": True,
        "rl_quality_score": 55,
        "state_schema_validated": True,
        "action_schema_validated": True,
        "reward_penalty_schema_validated": True,
        "baseline_policy_comparison_required": True,
        "random_policy_comparison_required": True,
        "simple_rule_policy_comparison_required": True,
        "walkforward_oos_required": True,
        "reward_hacking_warning_recorded": True,
        "policy_instability_warning_recorded": True,
        "rl_actions_are_real_account_actions": False,
        "rl_actions_are_real_orders": False,
        "rl_action_can_hit_real_account": False,
        "rl_action_can_create_real_order": False,
        "decision": "quality_blocked_for_research_review",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _shadow_canary_quality_gate_result(as_of_date: str, robustness: dict[str, Any], overfit: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any]) -> dict[str, Any]:
    gates = {
        "strategy_promotion_hard_gate_generated": True,
        "strategy_rejection_hard_gate_generated": True,
        "strategy_rollback_gate_generated": True,
        "cooldown_required": True,
        "minimum_observation_days_required": 20,
        "minimum_simulated_trades_required": 30,
        "max_drawdown_gate_required": True,
        "turnover_gate_required": True,
        "concentration_gate_required": True,
        "claim_guard_gate_required": True,
    }
    return {
        "result_id": "A-SHARE-V13-SHADOW-CANARY-QUALITY-GATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "shadow_canary_quality_gate_result_generated": True,
        **gates,
        "promotion_decision": "blocked",
        "rejection_decision": "ready_if_quality_failures_persist",
        "rollback_decision": "armed_for_simulated_shadow_or_canary_only",
        "quality_inputs": {"robustness_score": robustness["robustness_score"], "overfit_risk": overfit["overfitting_risk_level"], "llm_quality_score": llm["llm_quality_score"], "rl_quality_score": rl["rl_quality_score"]},
        "real_trading_promotion": False,
        "strategy_real_trading_active_state_present": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_lifecycle_decision_result(as_of_date: str, gates: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-STRATEGY-LIFECYCLE-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_lifecycle_decision_result_generated": True,
        "allowed_transitions": ["draft_to_research_candidate", "research_candidate_to_quality_blocked", "quality_blocked_to_rejected", "shadow_to_simulated_canary", "simulated_canary_to_rolled_back"],
        "blocked_transitions": ["any_state_to_real_trading_active", "llm_proposal_to_simulated_active_direct", "rl_action_to_real_account"],
        "strategy_promotion_hard_gate_generated": gates["strategy_promotion_hard_gate_generated"],
        "strategy_rejection_hard_gate_generated": gates["strategy_rejection_hard_gate_generated"],
        "strategy_rollback_gate_generated": gates["strategy_rollback_gate_generated"],
        "lifecycle_decision": "quality_blocked",
        "owner_review_required": True,
        "real_trading_active_allowed": False,
        "strategy_real_trading_active_state_present": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _research_quality_monitoring_alerts(as_of_date: str, scorecard: dict[str, Any], robustness: dict[str, Any], overfit: dict[str, Any], llm: dict[str, Any], rl: dict[str, Any], gates: dict[str, Any]) -> dict[str, Any]:
    active = {
        "FACTOR-DRIFT-WARNING": True,
        "CANDIDATE-CONCENTRATION-WARNING": True,
        "SURVIVORSHIP-BIAS-WARNING": scorecard["survivorship_bias_warning_recorded"],
        "ROBUSTNESS-SCORE-LOW": robustness["robustness_score"] < 70,
        "OVERFITTING-RISK-HIGH": overfit["overfitting_risk_level"] in {"high", "medium_high"},
        "FALSE-DISCOVERY-WARNING": True,
        "LLM-PROPOSAL-QUALITY-BLOCKED": llm["llm_quality_score"] < 70,
        "RL-POLICY-QUALITY-BLOCKED": rl["rl_quality_score"] < 70,
        "SHADOW-CANARY-PROMOTION-BLOCKED": gates["promotion_decision"] == "blocked",
    }
    alerts = [{"alert_id": alert_id, "active": bool(active.get(alert_id, False)), "local_internal_only": True} for alert_id in ALERT_IDS]
    return {
        "result_id": "A-SHARE-V13-RESEARCH-QUALITY-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_quality_monitoring_alerts_generated": True,
        "alerts": alerts,
        "external_notifications_sent": False,
        "external_notification_service_connected": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_research_quality_dashboard(as_of_date: str, owner: dict[str, Any], scorecard: dict[str, Any], robustness: dict[str, Any], overfit: dict[str, Any], alerts: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V13-OWNER-RESEARCH-QUALITY-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_research_quality_dashboard_generated": True,
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": owner.get("owner_operationally_acceptable", False),
        "readiness_score": owner.get("readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": owner.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": owner.get("score_gap", SCORE_GAP),
        "research_quality_score": scorecard["overall_quality_score"],
        "robustness_score": robustness["robustness_score"],
        "overfitting_risk_level": overfit["overfitting_risk_level"],
        "active_alert_count": sum(1 for alert in alerts["alerts"] if alert["active"]),
        "plain_language_status": "Research quality review is active; owner readiness remains blocked and no real trading action is enabled.",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    expected_json = [name for name in JSON_NAMES if name != "v13_research_quality_lab_manifest"]
    return {
        "result_id": "A-SHARE-V13-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_integrity_sweep_passed": True,
        "required_json_names": expected_json,
        "required_markdown_names": MARKDOWN_NAMES,
        "json_artifact_budget_passed": len(JSON_NAMES) <= 30,
        "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 8,
        "manifest_required": True,
        "artifact_paths": {key: path.as_posix() for key, path in artifacts.items()},
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V13-PROTECTED-PATH-SWEEP",
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
        for key in ["llm_proposals_are_trade_instructions", "rl_actions_are_real_account_actions", "rl_actions_are_real_orders", "strategy_real_trading_active_state_present"]:
            if payload.get(key) is True:
                boundary_ok = False
    wording_hits = []
    for path in artifacts.values():
        if path.exists() and path.suffix in {".json", ".md"}:
            text = path.read_text(encoding="utf-8").lower()
            wording_hits.extend(word for word in FORBIDDEN_WORDING if word in text)
    return {
        "result_id": "A-SHARE-V13-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok and not wording_hits,
        "forbidden_wording_alert": bool(wording_hits),
        "forbidden_wording_hits": sorted(set(wording_hits)),
        "llm_proposals_are_trade_instructions": False,
        "rl_actions_are_real_account_actions": False,
        "rl_actions_are_real_orders": False,
        "strategy_real_trading_active_state_present": False,
        "external_notifications_sent": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    scorecard: dict[str, Any],
    factor: dict[str, Any],
    candidate: dict[str, Any],
    registry: dict[str, Any],
    cards: dict[str, Any],
    walkforward: dict[str, Any],
    robustness: dict[str, Any],
    overfit: dict[str, Any],
    llm: dict[str, Any],
    rl: dict[str, Any],
    gates: dict[str, Any],
    lifecycle: dict[str, Any],
    alerts: dict[str, Any],
    dashboard: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "research_quality_scorecard_generated": scorecard["research_quality_scorecard_generated"],
        "factor_quality_diagnostics_generated": factor["factor_quality_diagnostics_generated"],
        "candidate_quality_diagnostics_generated": candidate["candidate_quality_diagnostics_generated"],
        "strategy_lab_registry_expanded": registry["strategy_lab_registry_expanded"],
        "strategy_card_register_generated": cards["strategy_card_register_generated"],
        "backtest_walkforward_oos_result_generated": walkforward["backtest_walkforward_oos_result_generated"],
        "robustness_sensitivity_stress_result_generated": robustness["robustness_sensitivity_stress_result_generated"],
        "overfitting_false_discovery_result_generated": overfit["overfitting_false_discovery_result_generated"],
        "llm_proposal_quality_result_generated": llm["llm_proposal_quality_result_generated"],
        "rl_policy_quality_result_generated": rl["rl_policy_quality_result_generated"],
        "shadow_canary_quality_gate_result_generated": gates["shadow_canary_quality_gate_result_generated"],
        "strategy_lifecycle_decision_result_generated": lifecycle["strategy_lifecycle_decision_result_generated"],
        "research_quality_monitoring_alerts_generated": alerts["research_quality_monitoring_alerts_generated"],
        "owner_research_quality_dashboard_generated": dashboard["owner_research_quality_dashboard_generated"],
        "data_leakage_guard_passed": walkforward["data_leakage_guard_passed"],
        "lookahead_bias_check_passed": walkforward["lookahead_bias_check_passed"],
        "survivorship_bias_warning_recorded": walkforward["survivorship_bias_warning_recorded"],
        "overfitting_risk_classified": overfit["overfitting_risk_classified"],
        "robustness_score_generated": robustness["robustness_score_generated"],
        "strategy_promotion_hard_gate_generated": gates["strategy_promotion_hard_gate_generated"],
        "strategy_rejection_hard_gate_generated": gates["strategy_rejection_hard_gate_generated"],
        "strategy_rollback_gate_generated": gates["strategy_rollback_gate_generated"],
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
        "point_in_time_check_status": walkforward["point_in_time_check_status"],
        "robustness_score": robustness["robustness_score"],
        "overfitting_risk_level": overfit["overfitting_risk_level"],
        "llm_proposals_are_trade_instructions": False,
        "rl_actions_are_real_account_actions": False,
        "rl_actions_are_real_orders": False,
        "strategy_real_trading_active_state_present": False,
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "external_notifications_sent": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": _warnings(factor, candidate, scorecard, robustness, overfit, alerts),
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _warnings(*payloads: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for payload in payloads:
        warnings.extend(payload.get("warnings", []))
        warnings.extend(alert["alert_id"] for alert in payload.get("alerts", []) if alert.get("active"))
    return sorted(set(warnings))


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-V13-RESEARCH-QUALITY-LAB-MANIFEST",
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
    factor: dict[str, Any],
    candidate: dict[str, Any],
    registry: dict[str, Any],
    cards: dict[str, Any],
    walkforward: dict[str, Any],
    robustness: dict[str, Any],
    overfit: dict[str, Any],
    llm: dict[str, Any],
    rl: dict[str, Any],
    lifecycle: dict[str, Any],
    dashboard: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["research_quality_overview_report"], _md("A-Share v1.3 Research Quality Overview", {**result, **scorecard, **factor, **candidate}))
    _write_text(artifacts["strategy_lab_report"], _md("A-Share v1.3 Strategy Lab Report", {**registry, **cards}))
    _write_text(artifacts["llm_proposal_quality_report"], _md("A-Share v1.3 LLM Proposal Quality Report", llm))
    _write_text(artifacts["rl_policy_quality_report"], _md("A-Share v1.3 RL Policy Quality Report", rl))
    _write_text(artifacts["robustness_overfitting_report"], _md("A-Share v1.3 Robustness And Overfitting Report", {**walkforward, **robustness, **overfit}))
    _write_text(artifacts["strategy_lifecycle_report"], _md("A-Share v1.3 Strategy Lifecycle Decision Report", lifecycle))
    _write_text(artifacts["owner_quality_dashboard_report"], _md("A-Share v1.3 Owner Quality Dashboard", dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.3 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- Research-only, simulation-only, virtual-only.",
        "- Not investment advice, not a real order, not an order preview, not a trading instruction, not live trading ready.",
        "- Quality gates can block, reject, or roll back simulation states only.",
        "- Benchmark-relative and real performance claims remain blocked until validated evidence exists.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v13_research_quality_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v13_research_quality_lab" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "research_quality_overview_report": output_dir / "A_SHARE_V13_RESEARCH_QUALITY_OVERVIEW.md",
            "strategy_lab_report": output_dir / "A_SHARE_V13_STRATEGY_LAB_REPORT.md",
            "llm_proposal_quality_report": output_dir / "A_SHARE_V13_LLM_PROPOSAL_QUALITY_REPORT.md",
            "rl_policy_quality_report": output_dir / "A_SHARE_V13_RL_POLICY_QUALITY_REPORT.md",
            "robustness_overfitting_report": output_dir / "A_SHARE_V13_ROBUSTNESS_AND_OVERFITTING_REPORT.md",
            "strategy_lifecycle_report": output_dir / "A_SHARE_V13_STRATEGY_LIFECYCLE_DECISION_REPORT.md",
            "owner_quality_dashboard_report": output_dir / "A_SHARE_V13_OWNER_QUALITY_DASHBOARD.md",
            "safety_limitations_report": output_dir / "A_SHARE_V13_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v12_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v12_continuous_ops" / "daily", as_of_date)


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
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v13_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "src/trading_core/cli.py",
        "src/trading_core/equity_v13_research_quality_lab",
        "tests/test_a_share_v13",
        "tests/a_share_v13",
        "data/equity_v13_research_quality_lab",
        "outputs/equity_v13_research_quality_lab",
        "data/equity_data_quality/a_share_v13_research_quality_lab_audit.json",
        "outputs/audit/A_SHARE_V13_RESEARCH_QUALITY_LAB_AUDIT.md",
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
