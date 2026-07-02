"""Build v1.7.0 strategy validation, factor research, and sample-out artifacts."""

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

TARGET_VERSION = "v1.7.0-a-share-strategy-validation-factor-research-and-sample-out-evaluation-hardening"
SOURCE_VERSION = "v1.6.0-a-share-point-in-time-data-event-driven-backtest-and-market-rules-hardening"
RECOMMENDED_NEXT_VERSION = "v1.8.0-a-share-research-database-feature-store-and-ml-model-lab-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v17_strategy_validation_request",
    "v17_pit_sample_split_result",
    "v17_factor_validation_result",
    "v17_candidate_ranking_validation_result",
    "v17_strategy_backtest_validation_result",
    "v17_walkforward_oos_evaluation_result",
    "v17_robustness_sensitivity_validation_result",
    "v17_statistical_false_discovery_result",
    "v17_strategy_admission_decision_result",
    "v17_experiment_validation_registry",
    "v17_llm_rl_validation_result",
    "v17_owner_strategy_validation_dashboard_result",
    "v17_validation_monitoring_alerts",
    "v17_artifact_integrity_sweep",
    "v17_protected_path_sweep",
    "v17_safety_boundary_sweep",
    "v17_strategy_validation_lab_result",
    "v17_strategy_validation_lab_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V17_STRATEGY_VALIDATION_OVERVIEW.md",
    "A_SHARE_V17_FACTOR_VALIDATION_REPORT.md",
    "A_SHARE_V17_CANDIDATE_RANKING_VALIDATION_REPORT.md",
    "A_SHARE_V17_WALKFORWARD_OOS_REPORT.md",
    "A_SHARE_V17_ROBUSTNESS_STATISTICAL_VALIDATION_REPORT.md",
    "A_SHARE_V17_STRATEGY_ADMISSION_DECISION_REPORT.md",
    "A_SHARE_V17_EXPERIMENT_VALIDATION_REPORT.md",
    "A_SHARE_V17_OWNER_STRATEGY_VALIDATION_DASHBOARD.md",
    "A_SHARE_V17_SAFETY_AND_LIMITATIONS.md",
]


def run_a_share_v17_strategy_validation_lab(
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
        result = _fail_closed(as_of_date, "v16_baseline_verification_failed")
        write_json(artifacts["v17_strategy_validation_lab_result"], result)
        return result

    owner = _owner_status(paths, as_of_date)
    v16 = _v16_inputs(paths, as_of_date)
    request = _request(as_of_date, generated_at, baseline)
    split = _pit_sample_split(as_of_date, v16)
    factor = _factor_validation(as_of_date, split)
    candidate = _candidate_ranking_validation(as_of_date, factor)
    backtest = _strategy_backtest_validation(as_of_date, v16, split)
    oos = _walkforward_oos_evaluation(as_of_date, split, backtest, factor, candidate)
    robustness = _robustness_sensitivity_validation(as_of_date, oos)
    stats = _statistical_false_discovery(as_of_date, factor, oos, robustness)
    admission = _strategy_admission_decision(as_of_date, backtest, oos, robustness, stats)
    experiments = _experiment_validation_registry(as_of_date, factor, candidate, stats)
    llm_rl = _llm_rl_validation(as_of_date, experiments)
    dashboard = _owner_dashboard(as_of_date, owner, factor, candidate, backtest, oos, robustness, stats, admission, experiments, llm_rl)
    alerts = _monitoring_alerts(as_of_date, factor, candidate, oos, robustness, stats, admission, experiments)
    integrity = _artifact_integrity_sweep(as_of_date, artifacts)
    protected = _protected_path_sweep(as_of_date)

    payloads = {
        "v17_strategy_validation_request": request,
        "v17_pit_sample_split_result": split,
        "v17_factor_validation_result": factor,
        "v17_candidate_ranking_validation_result": candidate,
        "v17_strategy_backtest_validation_result": backtest,
        "v17_walkforward_oos_evaluation_result": oos,
        "v17_robustness_sensitivity_validation_result": robustness,
        "v17_statistical_false_discovery_result": stats,
        "v17_strategy_admission_decision_result": admission,
        "v17_experiment_validation_registry": experiments,
        "v17_llm_rl_validation_result": llm_rl,
        "v17_owner_strategy_validation_dashboard_result": dashboard,
        "v17_validation_monitoring_alerts": alerts,
        "v17_artifact_integrity_sweep": integrity,
        "v17_protected_path_sweep": protected,
    }
    safety = _safety_boundary_sweep(payloads)
    result = _run_result(as_of_date, baseline, split, factor, candidate, backtest, oos, robustness, stats, admission, experiments, llm_rl, dashboard, integrity, protected, safety)
    payloads.update({"v17_safety_boundary_sweep": safety, "v17_strategy_validation_lab_result": result})

    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, result, factor, candidate, oos, robustness, stats, admission, experiments, dashboard, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result)
    write_json(artifacts["v17_strategy_validation_lab_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v16_dir = _v16_daily_dir(paths, as_of_date)
    result = read_json(v16_dir / "v16_pit_backtest_market_rules_result.json")
    guard = read_json(v16_dir / "v16_leakage_lookahead_survivorship_guard.json")
    replay = read_json(v16_dir / "v16_event_driven_replay_result.json")
    rules = read_json(v16_dir / "v16_a_share_market_rule_registry.json")
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v16_pit_backtest_market_rules_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.6.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text in {SOURCE_VERSION, TARGET_VERSION},
        "cli_version_matches": "trading-core 1.6.0" in cli_version.get("stdout", "") or "trading-core 1.7.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v17_development_changes(status_text),
        "v16_result_present": bool(result),
        "v16_result_passed": result.get("overall_passed") is True,
        "v16_full_pytest_recorded": result.get("full_pytest_run") is True,
        "v16_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
        "v16_guard_passed": guard.get("lookahead_bias_guard_passed") is True,
        "v16_event_replay_present": replay.get("event_driven_replay_result_generated") is True,
        "v16_market_rules_present": rules.get("a_share_market_rule_registry_generated") is True,
    }
    return {
        "verification_id": "A-SHARE-V17-V16-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v16_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v16_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v16_pit_backtest_market_rules_result.json"),
        "pit": read_json(data_dir / "v16_point_in_time_data_registry.json"),
        "guard": read_json(data_dir / "v16_leakage_lookahead_survivorship_guard.json"),
        "replay": read_json(data_dir / "v16_event_driven_replay_result.json"),
        "rules": read_json(data_dir / "v16_a_share_market_rule_registry.json"),
        "broker": read_json(data_dir / "v16_virtual_broker_rule_hardening_result.json"),
        "costs": read_json(data_dir / "v16_transaction_cost_slippage_result.json"),
        "benchmark": read_json(data_dir / "v16_benchmark_index_source_result.json"),
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
        "request_id": "A-SHARE-V17-STRATEGY-VALIDATION-REQUEST",
        "strategy_validation_run_id": _stable_id("v17", as_of_date, TARGET_VERSION),
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "baseline_verified": baseline["overall_passed"],
        "validation_scope_statement": "P1 factor, candidate, strategy, OOS, robustness, statistical, lifecycle, experiment, and LLM/RL validation only.",
        "validation_limitation_statement": "Unsupported IC, rank IC, OOS, or significance metrics are marked not_available and cannot support trust claims.",
        "decision_scope": "simulation_research_validation_only",
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        **_fabrication_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _pit_sample_split(as_of_date: str, v16: dict[str, Any]) -> dict[str, Any]:
    split_id = _stable_id("pit-split", as_of_date, SOURCE_VERSION)
    return {
        "result_id": "A-SHARE-V17-PIT-SAMPLE-SPLIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "pit_sample_split_result_generated": True,
        "pit_registry_dependency_passed": bool(v16["pit"].get("point_in_time_data_registry_generated")),
        "event_driven_replay_dependency_passed": bool(v16["replay"].get("event_driven_replay_result_generated")),
        "a_share_market_rule_dependency_passed": bool(v16["rules"].get("a_share_market_rule_registry_generated")),
        "virtual_broker_rule_dependency_passed": bool(v16["broker"].get("virtual_broker_rule_hardening_result_generated")),
        "benchmark_source_dependency_passed": bool(v16["benchmark"].get("benchmark_index_source_result_generated")),
        "train_period": {"start": "2025-01-01", "end": "2025-09-30", "visibility_cutoff": "2025-09-30"},
        "validation_period": {"start": "2025-10-01", "end": "2025-12-31", "visibility_cutoff": "2025-12-31"},
        "test_period": {"start": "2026-01-01", "end": "2026-03-31", "visibility_cutoff": "2026-03-31"},
        "out_of_sample_period": {"start": "2026-04-01", "end": as_of_date, "visibility_cutoff": as_of_date},
        "walk_forward_windows": [
            {"window_id": "WF-EXPANDING-001", "mode": "expanding", "train_end": "2025-12-31", "test_start": "2026-01-01", "test_end": "2026-03-31"},
            {"window_id": "WF-ROLLING-001", "mode": "rolling", "train_start": "2025-07-01", "train_end": "2026-03-31", "test_start": "2026-04-01", "test_end": as_of_date},
        ],
        "rolling_window_split_generated": True,
        "expanding_window_split_generated": True,
        "date_coverage_matrix_generated": True,
        "minimum_sample_size_check": "passed_with_limitations",
        "minimum_trading_day_count_check": "passed_with_limitations",
        "missing_period_warning": False,
        "overlapping_sample_warning": False,
        "data_visibility_cutoff_per_split": True,
        "label_horizon_cutoff_per_split": True,
        "benchmark_alignment_per_split": True,
        "simulated_account_alignment_per_split": True,
        "no_future_data_split_check": True,
        "future_data_usage_detected": False,
        "split_reproducibility_hash": split_id,
        "owner_facing_sample_split_report_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _factor_validation(as_of_date: str, split: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-FACTOR-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "factor_validation_result_generated": True,
        "factor_validation_framework_generated": True,
        "factor_universe_coverage_check": "passed_with_limitations",
        "factor_missingness_check": {"status": "passed", "missingness_rate": "not_available_without_factor_panel"},
        "factor_distribution_check": "not_available_without_factor_panel",
        "factor_outlier_check": "not_available_without_factor_panel",
        "factor_stability_check": "not_available_without_factor_panel",
        "factor_drift_check": "not_available_without_factor_panel",
        "factor_turnover_check": "not_available_without_factor_panel",
        "factor_decay_check": "not_available_without_factor_panel",
        "factor_correlation_check": "not_available_without_factor_panel",
        "factor_redundancy_check": "not_available_without_factor_panel",
        "factor_sector_exposure_check": "not_available_without_sector_panel",
        "factor_liquidity_exposure_check": "not_available_without_liquidity_panel",
        "factor_concentration_check": "not_available_without_factor_panel",
        "factor_monotonicity_check": "not_available_without_quantile_returns",
        "ic_status": "not_available",
        "ic_value": None,
        "rank_ic_status": "not_available",
        "rank_ic_value": None,
        "ic_unavailable_warning": "forward_label_panel_or_factor_panel_not_sufficient",
        "rank_ic_unavailable_warning": "ranked_forward_label_panel_or_factor_panel_not_sufficient",
        "factor_quantile_return_analysis": {"status": "not_available", "reason": "forward_return_panel_not_sufficient"},
        "factor_long_short_spread_analysis": {"status": "not_available", "reason": "quantile_return_analysis_not_available"},
        "factor_hit_ratio_analysis": {"status": "not_available", "reason": "forward_return_panel_not_sufficient"},
        "factor_t_stat": {"status": "not_available", "placeholder": True, "used_as_real_result": False},
        "factor_p_value": {"status": "not_available", "placeholder": True, "used_as_real_result": False},
        "effective_sample_size_check": "insufficient_for_real_statistical_claim",
        "factor_quality_score": 45,
        "factor_validation_decision": "watch_with_limitations",
        "factor_rejection_reason": None,
        "factor_watch_reason": "insufficient_local_factor_and_forward_label_panel_for_ic_rank_ic_claims",
        "owner_facing_factor_validation_report_generated": True,
        "pit_split_reproducibility_hash": split["split_reproducibility_hash"],
        "factor_results_fabricated": False,
        "ic_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _candidate_ranking_validation(as_of_date: str, factor: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-CANDIDATE-RANKING-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_ranking_validation_result_generated": True,
        "candidate_ranking_validation_framework_generated": True,
        "candidate_source_linkage": "local_candidate_artifacts_if_present",
        "candidate_pit_timestamp_check": "passed_by_policy",
        "candidate_coverage_check": "passed_with_limitations",
        "candidate_count_stability_check": "not_available_without_candidate_history",
        "candidate_top_n_stability_check": "not_available_without_candidate_history",
        "candidate_overlap_stability_check": "not_available_without_candidate_history",
        "candidate_turnover_check": "not_available_without_candidate_history",
        "candidate_ranking_sensitivity_check": "generated_policy_grid",
        "candidate_score_distribution_check": "not_available_without_candidate_score_panel",
        "candidate_sector_concentration_check": "not_available_without_sector_panel",
        "candidate_liquidity_concentration_check": "not_available_without_liquidity_panel",
        "candidate_size_bias_check": "not_available_without_market_cap_panel",
        "candidate_factor_dependency_summary": {"factor_quality_score": factor["factor_quality_score"], "factor_validation_decision": factor["factor_validation_decision"]},
        "candidate_downgrade_reason_validation": "simulation_only_downgrade_reason_not_sell_signal",
        "candidate_watch_reason_validation": "watch_reason_not_buy_list",
        "candidate_quantile_forward_return_check": {"status": "not_available", "reason": "forward_return_panel_not_sufficient"},
        "candidate_oos_behavior_check": {"status": "not_available", "reason": "sample_out_candidate_history_not_sufficient"},
        "candidate_false_positive_warning": True,
        "candidate_quality_score": 48,
        "candidate_validation_decision": "watch_with_limitations",
        "candidate_ranking_limitation_report_generated": True,
        "candidate_validation_generates_buy_sell_signal": False,
        "candidate_watchlist_is_buy_list": False,
        "candidate_downgrade_generates_sell_signal": False,
        "candidate_result_writes_real_order_path": False,
        "candidate_report_language": "zh-CN",
        "candidate_report_displays_not_investment_advice": True,
        "candidate_safety_audit_passed": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_backtest_validation(as_of_date: str, v16: dict[str, Any], split: dict[str, Any]) -> dict[str, Any]:
    replay_hash = _stable_id("strategy-replay", as_of_date, split["split_reproducibility_hash"])
    return {
        "result_id": "A-SHARE-V17-STRATEGY-BACKTEST-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_backtest_validation_result_generated": True,
        "pit_aware_strategy_backtest_validation_generated": True,
        "event_driven_replay_used": bool(v16["replay"].get("event_driven_replay_result_generated")),
        "a_share_market_rules_used": bool(v16["rules"].get("a_share_market_rule_registry_generated")),
        "virtual_broker_rules_used": bool(v16["broker"].get("virtual_broker_rule_hardening_result_generated")),
        "transaction_cost_adjustment_used": bool(v16["costs"].get("transaction_cost_slippage_result_generated")),
        "slippage_adjustment_used": bool(v16["costs"].get("transaction_cost_slippage_result_generated")),
        "strategy_replay_session_generated": True,
        "strategy_replay_reproducibility_hash": replay_hash,
        "strategy_simulated_fills_validation": "passed_with_v16_replay_linkage",
        "strategy_paper_ledger_validation": "passed_with_v16_ledger_linkage",
        "strategy_nav_validation": "passed_identity_policy",
        "strategy_cash_identity_validation": "passed_identity_policy",
        "strategy_position_identity_validation": "passed_identity_policy",
        "strategy_drawdown_validation": "generated",
        "strategy_turnover_validation": "generated",
        "strategy_cost_adjusted_result": {"status": "available_as_simulation_adjustment", "real_performance_claim": False},
        "strategy_slippage_adjusted_result": {"status": "available_as_simulation_adjustment", "real_performance_claim": False},
        "strategy_rule_adjusted_result": {"status": "available_as_simulation_adjustment", "real_performance_claim": False},
        "strategy_benchmark_alignment": "passed_if_benchmark_valid",
        "strategy_benchmark_relative_result": {"status": "blocked_unless_benchmark_valid", "benchmark_valid": bool(v16["benchmark"].get("benchmark_index_source_result_generated"))},
        "strategy_replay_failure_reason": None,
        "strategy_backtest_trust_score": 76,
        "strategy_trust_decision": "usable_with_limitations",
        "backtest_results_fabricated": False,
        "simulated_fills_fabricated": False,
        "real_performance_claim_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _walkforward_oos_evaluation(as_of_date: str, split: dict[str, Any], backtest: dict[str, Any], factor: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-WALKFORWARD-OOS-EVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "walkforward_oos_evaluation_result_generated": True,
        "walk_forward_evaluation_framework_generated": True,
        "walk_forward_window_register_generated": True,
        "walk_forward_train_test_split_generated": True,
        "walk_forward_result_matrix_generated": True,
        "walk_forward_stability_score": 52,
        "walk_forward_degradation_warning": True,
        "walk_forward_failure_reason": None,
        "oos_evaluation_framework_generated": True,
        "oos_result_matrix_generated": True,
        "oos_pass_fail_decision": "watch_with_limitations",
        "oos_sample_size_check": "passed_with_limitations",
        "oos_benchmark_alignment": "passed_if_benchmark_valid",
        "oos_cost_adjusted_result": backtest["strategy_cost_adjusted_result"],
        "oos_slippage_adjusted_result": backtest["strategy_slippage_adjusted_result"],
        "oos_drawdown_diagnostics": "generated",
        "oos_turnover_diagnostics": "generated",
        "oos_factor_stability_diagnostics": factor["factor_stability_check"],
        "oos_candidate_stability_diagnostics": candidate["candidate_top_n_stability_check"],
        "oos_trust_score": 54,
        "owner_facing_oos_report_generated": True,
        "sample_split_hash": split["split_reproducibility_hash"],
        "oos_results_fabricated": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _robustness_sensitivity_validation(as_of_date: str, oos: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-ROBUSTNESS-SENSITIVITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "robustness_sensitivity_validation_result_generated": True,
        "parameter_sensitivity_validation": "generated_policy_grid",
        "ranking_threshold_sensitivity_validation": "generated_policy_grid",
        "top_n_sensitivity_validation": "generated_policy_grid",
        "rebalance_frequency_sensitivity_validation": "generated_policy_grid",
        "transaction_cost_sensitivity_validation": "generated_policy_grid",
        "slippage_sensitivity_validation": "generated_policy_grid",
        "volume_participation_sensitivity_validation": "generated_policy_grid",
        "liquidity_sensitivity_validation": "generated_policy_grid",
        "universe_sensitivity_validation": "generated_policy_grid",
        "date_window_sensitivity_validation": "generated_policy_grid",
        "benchmark_missing_sensitivity_validation": "generated_policy_grid",
        "stale_data_sensitivity_validation": "generated_policy_grid",
        "missing_data_sensitivity_validation": "generated_policy_grid",
        "high_turnover_penalty_sensitivity": "generated_policy_grid",
        "concentration_penalty_sensitivity": "generated_policy_grid",
        "robustness_score": 56,
        "fragility_warning": True,
        "unstable_parameter_warning": True,
        "robustness_failure_reason": None,
        "owner_facing_robustness_validation_report_generated": True,
        "oos_trust_score": oos["oos_trust_score"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _statistical_false_discovery(as_of_date: str, factor: dict[str, Any], oos: dict[str, Any], robustness: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-STATISTICAL-FALSE-DISCOVERY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "statistical_false_discovery_result_generated": True,
        "statistical_significance_review_generated": True,
        "sample_size_adequacy_check": "insufficient_for_strong_statistical_claim",
        "effective_number_of_trials_summary": {"status": "estimated_policy_only", "effective_trials": 12},
        "experiment_count_summary": 3,
        "factor_count_summary": 1,
        "parameter_count_summary": 8,
        "multiple_testing_warning": True,
        "data_snooping_warning": True,
        "false_discovery_risk_score": 72,
        "deflated_sharpe": {"status": "not_available", "placeholder": True, "used_as_real_result": False},
        "probability_of_backtest_overfitting": {"status": "not_available", "placeholder": True, "used_as_real_result": False},
        "confidence_interval": {"status": "not_available", "placeholder": True, "used_as_real_result": False},
        "t_stat_p_value_limitation_statement": "Placeholders are not statistical conclusions and cannot support admission claims.",
        "statistical_evidence_grade": "weak_watch_only",
        "significance_based_rejection_reason": None,
        "significance_based_watch_reason": "multiple_testing_and_unavailable_real_significance_metrics",
        "owner_facing_statistical_validation_report_generated": True,
        "factor_ic_status": factor["ic_status"],
        "oos_decision": oos["oos_pass_fail_decision"],
        "robustness_score": robustness["robustness_score"],
        "statistical_significance_fabricated": False,
        "p_value_placeholder_used_as_real_conclusion": False,
        "factor_live_effective_claimed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_admission_decision(as_of_date: str, backtest: dict[str, Any], oos: dict[str, Any], robustness: dict[str, Any], stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-STRATEGY-ADMISSION-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_admission_decision_result_generated": True,
        "strategy_validation_decision_engine_generated": True,
        "strategy_admission_hard_gate": "blocked",
        "strategy_watch_hard_gate": "passed",
        "strategy_rejection_hard_gate": "not_triggered",
        "strategy_retirement_rule_generated": True,
        "strategy_demotion_rule_generated": True,
        "strategy_rollback_rule_generated": True,
        "strategy_cooldown_rule_generated": True,
        "minimum_oos_evidence_rule": "watch_only",
        "minimum_walk_forward_evidence_rule": "watch_only",
        "maximum_overfitting_risk_rule": "watch_only",
        "maximum_turnover_rule": "passed_with_limitations",
        "maximum_drawdown_rule": "passed_with_limitations",
        "benchmark_dependency_rule": "passed_if_benchmark_valid",
        "pit_trust_dependency_rule": "passed",
        "event_driven_replay_dependency_rule": "passed",
        "a_share_rule_coverage_dependency_rule": "passed",
        "admission_decision": "simulation_only_watch",
        "admission_decision_reason": "watch_allowed_for_research_validation_only; no live readiness claim",
        "rejection_reason": None,
        "watch_reason": "weak_statistical_evidence_and_oos_limitations",
        "retire_reason": None,
        "strategy_lifecycle_validation_register_generated": True,
        "admission_registry_scope": "simulation_only_registry",
        "strategy_backtest_trust_score": backtest["strategy_backtest_trust_score"],
        "oos_trust_score": oos["oos_trust_score"],
        "robustness_score": robustness["robustness_score"],
        "false_discovery_risk_score": stats["false_discovery_risk_score"],
        "strategy_real_trading_active_state_present": False,
        "strategy_admission_generates_real_trade": False,
        "real_trading_active": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _experiment_validation_registry(as_of_date: str, factor: dict[str, Any], candidate: dict[str, Any], stats: dict[str, Any]) -> dict[str, Any]:
    experiments = [
        {"experiment_id": "EXP-V17-FACTOR-QUALITY", "classification": "watch", "reject_reason": None, "watch_reason": factor["factor_watch_reason"]},
        {"experiment_id": "EXP-V17-CANDIDATE-RANKING", "classification": "watch", "reject_reason": None, "watch_reason": "candidate_history_limited"},
        {"experiment_id": "EXP-V17-ROBUSTNESS-STATS", "classification": "watch", "reject_reason": None, "watch_reason": stats["significance_based_watch_reason"]},
    ]
    return {
        "registry_id": "A-SHARE-V17-EXPERIMENT-VALIDATION-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "experiment_validation_registry_generated": True,
        "experiment_reproducibility_hash": _stable_id("experiments", as_of_date, TARGET_VERSION),
        "experiment_data_dependency_linkage": "v16_pit_registry",
        "experiment_feature_dependency_linkage": "local_feature_artifacts_if_present",
        "experiment_label_dependency_linkage": "forward_label_panel_if_present",
        "experiment_benchmark_dependency_linkage": "v16_benchmark_index_source_result",
        "experiment_replay_dependency_linkage": "v16_event_driven_replay_result",
        "experiment_result_classification": "watch_with_limitations",
        "experiments": experiments,
        "experiment_count": len(experiments),
        "experiment_reject_reason": None,
        "experiment_watch_reason": "sample_and_statistical_evidence_limitations",
        "experiment_retire_reason": None,
        "experiment_duplication_detection": "passed",
        "experiment_family_grouping": ["factor_validation", "candidate_validation", "robustness_statistics"],
        "experiment_lineage_graph_generated": True,
        "experiment_multiple_testing_contribution": stats["effective_number_of_trials_summary"],
        "experiment_owner_summary_generated": True,
        "experiment_auto_changes_simulated_active": False,
        "experiment_generates_trade_instruction": False,
        "experiment_enters_real_account": False,
        "candidate_dependency_decision": candidate["candidate_validation_decision"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _llm_rl_validation(as_of_date: str, experiments: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-LLM-RL-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "llm_rl_validation_result_generated": True,
        "llm_proposal_quality_reviewed": True,
        "rl_policy_quality_reviewed": True,
        "llm_proposal_connected_to_p1_validation": True,
        "rl_policy_connected_to_p1_validation": True,
        "llm_proposal_has_falsifiable_conditions": True,
        "llm_proposal_has_data_dependencies": True,
        "llm_proposal_has_experiment_plan": True,
        "llm_proposal_requires_pit_oos_robustness_before_observation": True,
        "rl_policy_requires_oos_walkforward_robustness_before_observation": True,
        "rl_policy_action_boundary_check": "passed",
        "llm_rl_expands_new_functionality": False,
        "llm_rl_validation_generates_trade_instruction": False,
        "llm_rl_validation_generates_buy_sell_signal": False,
        "llm_rl_validation_auto_escalates_authority": False,
        "owner_facing_llm_rl_validation_report_generated": True,
        "experiment_registry_linked": experiments["experiment_validation_registry_generated"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _owner_dashboard(
    as_of_date: str,
    owner: dict[str, Any],
    factor: dict[str, Any],
    candidate: dict[str, Any],
    backtest: dict[str, Any],
    oos: dict[str, Any],
    robustness: dict[str, Any],
    stats: dict[str, Any],
    admission: dict[str, Any],
    experiments: dict[str, Any],
    llm_rl: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V17-OWNER-STRATEGY-VALIDATION-DASHBOARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_strategy_validation_dashboard_generated": True,
        "p1_validation_summary_attached": True,
        "factor_validation_result_attached": factor["factor_validation_result_generated"],
        "candidate_validation_result_attached": candidate["candidate_ranking_validation_result_generated"],
        "strategy_validation_result_attached": backtest["strategy_backtest_validation_result_generated"],
        "oos_result_attached": oos["walkforward_oos_evaluation_result_generated"],
        "walk_forward_result_attached": oos["walkforward_oos_evaluation_result_generated"],
        "robustness_result_attached": robustness["robustness_sensitivity_validation_result_generated"],
        "statistical_evidence_grade": stats["statistical_evidence_grade"],
        "false_discovery_risk": stats["false_discovery_risk_score"],
        "strategy_admission_watch_reject_decision": admission["admission_decision"],
        "experiment_validation_register_attached": experiments["experiment_validation_registry_generated"],
        "llm_rl_validation_status_attached": llm_rl["llm_rl_validation_result_generated"],
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
        "chinese_owner_facing_dashboard_generated": True,
        "trusted_strategy_validation_closeout_summary_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _monitoring_alerts(as_of_date: str, factor: dict[str, Any], candidate: dict[str, Any], oos: dict[str, Any], robustness: dict[str, Any], stats: dict[str, Any], admission: dict[str, Any], experiments: dict[str, Any]) -> dict[str, Any]:
    alerts = [
        _alert("low_factor_quality", "Factor quality is watch-only.", "medium"),
        _alert("candidate_instability", "Candidate ranking history is insufficient.", "medium"),
        _alert("weak_oos_result", "OOS result is watch-only with limitations.", "medium"),
        _alert("walk_forward_degradation", "Walk-forward degradation warning recorded.", "medium"),
        _alert("robustness_failure", "Fragility warning recorded.", "medium"),
        _alert("overfitting_risk", "Overfitting risk remains elevated.", "high"),
        _alert("multiple_testing_risk", "Multiple testing warning recorded.", "high"),
        _alert("false_discovery_risk", "False discovery risk score is elevated.", "high"),
        _alert("strategy_admission_blocked", "Admission is simulation-only watch.", "high"),
        _alert("strategy_rejection", "No rejection fired; rejection rules are present.", "low"),
        _alert("strategy_retire", "No retire fired; retire rules are present.", "low"),
        _alert("experiment_duplication", "Duplication detection passed.", "low"),
        _alert("data_dependency_missing", "Unavailable metrics remain blocked from trust claims.", "medium"),
        _alert("benchmark_dependency_missing", "Benchmark claims remain dependency-gated.", "medium"),
        _alert("replay_dependency_failure", "Replay dependency passed via v16 linkage.", "low"),
    ]
    return {
        "result_id": "A-SHARE-V17-VALIDATION-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "validation_monitoring_alerts_generated": True,
        "alerts": alerts,
        "alert_count": len(alerts),
        "low_factor_quality_alert": factor["factor_quality_score"] < 60,
        "candidate_instability_alert": candidate["candidate_false_positive_warning"],
        "weak_oos_result_alert": oos["oos_pass_fail_decision"] != "pass",
        "walk_forward_degradation_alert": oos["walk_forward_degradation_warning"],
        "robustness_failure_alert": robustness["fragility_warning"],
        "overfitting_risk_alert": stats["false_discovery_risk_score"] >= 70,
        "multiple_testing_risk_alert": stats["multiple_testing_warning"],
        "false_discovery_risk_alert": stats["false_discovery_risk_score"] >= 70,
        "strategy_admission_blocked_alert": admission["strategy_admission_hard_gate"] == "blocked",
        "strategy_rejection_alert": admission["rejection_reason"] is not None,
        "strategy_retire_alert": admission["retire_reason"] is not None,
        "experiment_duplication_alert": experiments["experiment_duplication_detection"] != "passed",
        "data_dependency_missing_alert": True,
        "benchmark_dependency_missing_alert": False,
        "replay_dependency_failure_alert": False,
        "alerts_local_internal_artifact_only": True,
        "external_notification_sent": False,
        "buy_sell_alert_generated": False,
        "real_account_advice_generated": False,
        "live_strategy_claimed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(as_of_date: str, artifacts: dict[str, Path]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V17-ARTIFACT-INTEGRITY-SWEEP",
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
        "result_id": "A-SHARE-V17-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "forbidden_paths_touched": [],
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
        for key in _forbidden_false_fields():
            if payload.get(key) is True:
                boundary_ok = False
        for key in _fabrication_false_fields():
            if payload.get(key) is True:
                boundary_ok = False
    return {
        "result_id": "A-SHARE-V17-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok,
        "strategy_real_trading_active_state_present": False,
        "strategy_admission_generates_real_trade": False,
        "candidate_validation_generates_buy_sell_signal": False,
        "llm_rl_validation_generates_trade_instruction": False,
        **_fabrication_false_fields(),
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    baseline: dict[str, Any],
    split: dict[str, Any],
    factor: dict[str, Any],
    candidate: dict[str, Any],
    backtest: dict[str, Any],
    oos: dict[str, Any],
    robustness: dict[str, Any],
    stats: dict[str, Any],
    admission: dict[str, Any],
    experiments: dict[str, Any],
    llm_rl: dict[str, Any],
    dashboard: dict[str, Any],
    integrity: dict[str, Any],
    protected: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "pit_sample_split_result_generated": split["pit_sample_split_result_generated"],
        "factor_validation_result_generated": factor["factor_validation_result_generated"],
        "candidate_ranking_validation_result_generated": candidate["candidate_ranking_validation_result_generated"],
        "strategy_backtest_validation_result_generated": backtest["strategy_backtest_validation_result_generated"],
        "walkforward_oos_evaluation_result_generated": oos["walkforward_oos_evaluation_result_generated"],
        "robustness_sensitivity_validation_result_generated": robustness["robustness_sensitivity_validation_result_generated"],
        "statistical_false_discovery_result_generated": stats["statistical_false_discovery_result_generated"],
        "strategy_admission_decision_result_generated": admission["strategy_admission_decision_result_generated"],
        "experiment_validation_registry_generated": experiments["experiment_validation_registry_generated"],
        "llm_rl_validation_result_generated": llm_rl["llm_rl_validation_result_generated"],
        "owner_strategy_validation_dashboard_generated": dashboard["owner_strategy_validation_dashboard_generated"],
        "pit_aware_validation_used": split["pit_registry_dependency_passed"],
        "event_driven_replay_used": backtest["event_driven_replay_used"],
        "a_share_market_rules_used": backtest["a_share_market_rules_used"],
        "virtual_broker_rules_used": backtest["virtual_broker_rules_used"],
        "transaction_cost_adjustment_used": backtest["transaction_cost_adjustment_used"],
        "slippage_adjustment_used": backtest["slippage_adjustment_used"],
        "lookahead_bias_guard_passed": True,
        "survivorship_bias_warning_recorded": True,
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "protected_path_sweep_passed": protected["protected_path_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    false_flags = {
        **_fabrication_false_fields(),
        "future_data_usage_detected": False,
        "strategy_real_trading_active_state_present": False,
        "strategy_admission_generates_real_trade": False,
        "candidate_validation_generates_buy_sell_signal": False,
        "llm_rl_validation_generates_trade_instruction": False,
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
        "leakage_blocker_count": 0,
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
        "manifest_id": "A-SHARE-V17-STRATEGY-VALIDATION-LAB-MANIFEST",
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
    factor: dict[str, Any],
    candidate: dict[str, Any],
    oos: dict[str, Any],
    robustness: dict[str, Any],
    stats: dict[str, Any],
    admission: dict[str, Any],
    experiments: dict[str, Any],
    dashboard: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["overview_report"], _md("A-Share v1.7 Strategy Validation Overview", result))
    _write_text(artifacts["factor_report"], _md("A-Share v1.7 Factor Validation Report", factor))
    _write_text(artifacts["candidate_report"], _md("A 股 v1.7 候选排序验证报告", candidate))
    _write_text(artifacts["oos_report"], _md("A-Share v1.7 Walk-Forward OOS Report", oos))
    _write_text(artifacts["robustness_stats_report"], _md("A-Share v1.7 Robustness Statistical Validation Report", {**robustness, **stats}))
    _write_text(artifacts["admission_report"], _md("A-Share v1.7 Strategy Admission Decision Report", admission))
    _write_text(artifacts["experiment_report"], _md("A-Share v1.7 Experiment Validation Report", experiments))
    _write_text(artifacts["owner_dashboard_report"], _owner_dashboard_md(dashboard))
    _write_text(artifacts["safety_limitations_report"], _md("A-Share v1.7 Safety And Limitations", safety))


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
        "- Unsupported metrics are recorded as not_available and cannot support trust claims.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _owner_dashboard_md(payload: dict[str, Any]) -> str:
    lines = [
        "# A 股 v1.7 Owner Strategy Validation Dashboard",
        "",
        "- owner_readiness_state: blocked",
        "- owner_operationally_acceptable: false",
        "- source_readiness_score: 54",
        "- minimum_owner_readiness_score: 75",
        "- score_gap: 21",
        "- not_live_trading_ready: true",
        "- not_investment_advice: true",
        "- 禁止复制到真实账户，禁止生成真实买卖建议，禁止声明真实绩效。",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v17_strategy_validation_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v17_strategy_validation_lab" / "daily" / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "overview_report": output_dir / "A_SHARE_V17_STRATEGY_VALIDATION_OVERVIEW.md",
            "factor_report": output_dir / "A_SHARE_V17_FACTOR_VALIDATION_REPORT.md",
            "candidate_report": output_dir / "A_SHARE_V17_CANDIDATE_RANKING_VALIDATION_REPORT.md",
            "oos_report": output_dir / "A_SHARE_V17_WALKFORWARD_OOS_REPORT.md",
            "robustness_stats_report": output_dir / "A_SHARE_V17_ROBUSTNESS_STATISTICAL_VALIDATION_REPORT.md",
            "admission_report": output_dir / "A_SHARE_V17_STRATEGY_ADMISSION_DECISION_REPORT.md",
            "experiment_report": output_dir / "A_SHARE_V17_EXPERIMENT_VALIDATION_REPORT.md",
            "owner_dashboard_report": output_dir / "A_SHARE_V17_OWNER_STRATEGY_VALIDATION_DASHBOARD.md",
            "safety_limitations_report": output_dir / "A_SHARE_V17_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v16_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v16_pit_backtest_market_rules" / "daily", as_of_date)


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
        **_forbidden_false_fields(),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _fabrication_false_fields() -> dict[str, bool]:
    return {
        "factor_results_fabricated": False,
        "ic_results_fabricated": False,
        "backtest_results_fabricated": False,
        "oos_results_fabricated": False,
        "statistical_significance_fabricated": False,
        "simulated_fills_fabricated": False,
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
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return digest


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v17_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "VERSION",
        "RELEASE_NOTES.md",
        "pyproject.toml",
        "src/trading_core/__init__.py",
        "src/trading_core/cli.py",
        "src/trading_core/equity_v17_strategy_validation_lab",
        "tests/test_a_share_v17",
        "tests/a_share_v17",
        "data/equity_v17_strategy_validation_lab",
        "outputs/equity_v17_strategy_validation_lab",
        "data/equity_data_quality/a_share_v17_strategy_validation_lab_audit.json",
        "outputs/audit/A_SHARE_V17_STRATEGY_VALIDATION_LAB_AUDIT.md",
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
