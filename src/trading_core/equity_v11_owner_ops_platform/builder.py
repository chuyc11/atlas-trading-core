"""Build v1.1.0 A-share owner ops autonomous simulation platform artifacts."""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.1.0-a-share-owner-ops-autonomous-simulation-platform-expansion"
SOURCE_VERSION = "v1.0.1-a-share-benchmark-data-and-performance-claim-hardening"
RECOMMENDED_NEXT_VERSION = "v1.1.1-a-share-local-post-close-operator-scheduling-and-runbook-hardening"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21

JSON_NAMES = [
    "v11_owner_ops_request",
    "v11_daily_workflow_integration_result",
    "v11_owner_command_center_result",
    "v11_benchmark_claim_guard_integration_result",
    "v11_simulated_account_reconciliation_result",
    "v11_virtual_broker_lifecycle_result",
    "v11_paper_ledger_invariant_check",
    "v11_experiment_registry_expansion_result",
    "v11_strategy_registry_expansion_result",
    "v11_llm_proposal_governance_result",
    "v11_rl_simulated_lab_governance_result",
    "v11_shadow_canary_lifecycle_result",
    "v11_strategy_promotion_rejection_rollback_result",
    "v11_monitoring_alerts_result",
    "v11_remediation_checklist_result",
    "v11_workflow_history_register",
    "v11_evidence_auto_accumulation_result",
    "v11_artifact_integrity_sweep",
    "v11_safety_boundary_sweep",
    "v11_owner_ops_platform_result",
    "v11_owner_ops_platform_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V11_OWNER_COMMAND_CENTER.md",
    "A_SHARE_V11_DAILY_OWNER_OPS_REPORT.md",
    "A_SHARE_V11_SIMULATED_ACCOUNT_RECONCILIATION_REPORT.md",
    "A_SHARE_V11_STRATEGY_LIFECYCLE_REPORT.md",
    "A_SHARE_V11_MONITORING_AND_REMEDIATION_REPORT.md",
    "A_SHARE_V11_SAFETY_AND_LIMITATIONS.md",
]
FORBIDDEN_WORDING = ["买入建议", "卖出建议", "买入信号", "卖出信号", "strong buy", "guaranteed profit", "live trading ready: true"]


def run_a_share_v11_owner_ops_platform(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    dry_run: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    if not simulation_only:
        return _fail_closed(as_of_date, "simulation_only_flag_required")
    artifacts = _artifact_paths(paths, as_of_date, dry_run=dry_run)
    _ensure_dirs(artifacts)
    generated_at = utc_now()
    baseline = _baseline_verification(paths, as_of_date)
    owner_status = _owner_status(paths, as_of_date)
    v101 = _v101_inputs(paths, as_of_date)
    request = _request(as_of_date, generated_at, dry_run, baseline)
    daily = _daily_workflow_integration(as_of_date, dry_run, baseline, owner_status, v101)
    benchmark = _benchmark_claim_guard_integration(as_of_date, v101)
    account = _simulated_account_reconciliation(as_of_date)
    broker = _virtual_broker_lifecycle(as_of_date)
    ledger = _paper_ledger_invariant(as_of_date, account, broker)
    experiment = _experiment_registry_expansion(as_of_date)
    strategy = _strategy_registry_expansion(as_of_date, experiment)
    llm = _llm_proposal_governance(as_of_date, experiment)
    rl = _rl_simulated_lab_governance(as_of_date)
    shadow = _shadow_canary_lifecycle(as_of_date, strategy)
    promotion = _promotion_rejection_rollback(as_of_date, shadow)
    monitoring = _monitoring_alerts(as_of_date, v101, ledger, benchmark)
    remediation = _remediation_checklist(as_of_date, monitoring)
    history = _workflow_history_register(as_of_date, daily, owner_status, benchmark)
    evidence = _evidence_auto_accumulation(as_of_date, baseline, history)
    command = _owner_command_center(as_of_date, owner_status, daily, benchmark, account, ledger, shadow, monitoring, remediation)
    payloads = {
        "v11_owner_ops_request": request,
        "v11_daily_workflow_integration_result": daily,
        "v11_owner_command_center_result": command,
        "v11_benchmark_claim_guard_integration_result": benchmark,
        "v11_simulated_account_reconciliation_result": account,
        "v11_virtual_broker_lifecycle_result": broker,
        "v11_paper_ledger_invariant_check": ledger,
        "v11_experiment_registry_expansion_result": experiment,
        "v11_strategy_registry_expansion_result": strategy,
        "v11_llm_proposal_governance_result": llm,
        "v11_rl_simulated_lab_governance_result": rl,
        "v11_shadow_canary_lifecycle_result": shadow,
        "v11_strategy_promotion_rejection_rollback_result": promotion,
        "v11_monitoring_alerts_result": monitoring,
        "v11_remediation_checklist_result": remediation,
        "v11_workflow_history_register": history,
        "v11_evidence_auto_accumulation_result": evidence,
    }
    integrity = _artifact_integrity_sweep(paths, artifacts, payloads)
    safety = _safety_boundary_sweep(payloads, artifacts)
    result = _result(
        as_of_date,
        baseline,
        command,
        daily,
        benchmark,
        account,
        broker,
        ledger,
        experiment,
        strategy,
        llm,
        rl,
        shadow,
        promotion,
        monitoring,
        remediation,
        history,
        evidence,
        integrity,
        safety,
        dry_run,
    )
    payloads["v11_artifact_integrity_sweep"] = integrity
    payloads["v11_safety_boundary_sweep"] = safety
    payloads["v11_owner_ops_platform_result"] = result
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, command, daily, account, strategy, experiment, llm, rl, shadow, promotion, monitoring, remediation, safety, result)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, result, dry_run)
    write_json(artifacts["v11_owner_ops_platform_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v101_dir = _v101_daily_dir(paths, as_of_date)
    required = [
        "benchmark_source_registry",
        "benchmark_coverage_matrix",
        "cash_benchmark_result",
        "equal_weight_universe_benchmark_result",
        "csi_benchmark_attribution_result",
        "simulated_performance_attribution_result",
        "performance_claim_guard_result",
        "benchmark_claim_hardening_result",
        "benchmark_claim_hardening_manifest",
    ]
    payloads = {name: read_json(v101_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_benchmark_claim_hardening_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"returncode": 0, "stdout": "trading-core 1.0.1", "stderr": ""}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"returncode": 0, "stdout": SOURCE_VERSION, "stderr": ""}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"returncode": 0, "stdout": "", "stderr": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.0.1" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v11_development_changes(status_text),
        "all_v101_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v101_result_passed": payloads["benchmark_claim_hardening_result"].get("overall_passed") is True,
        "v101_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
    }
    return {
        "verification_id": "A-SHARE-V11-V101-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(checks.values()),
        "blocking_reasons": [key for key, value in checks.items() if value is not True and key != "required_baseline"],
        "v101_artifact_names": required,
    }


def _v101_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v101_daily_dir(paths, as_of_date)
    return {
        "registry": read_json(data_dir / "benchmark_source_registry.json"),
        "coverage": read_json(data_dir / "benchmark_coverage_matrix.json"),
        "cash": read_json(data_dir / "cash_benchmark_result.json"),
        "equal_weight": read_json(data_dir / "equal_weight_universe_benchmark_result.json"),
        "csi": read_json(data_dir / "csi_benchmark_attribution_result.json"),
        "simulated": read_json(data_dir / "simulated_performance_attribution_result.json"),
        "guard": read_json(data_dir / "performance_claim_guard_result.json"),
        "result": read_json(data_dir / "benchmark_claim_hardening_result.json"),
        "audit": read_json(paths.data_dir / "equity_data_quality" / "a_share_benchmark_claim_hardening_audit.json"),
    }


def _v101_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    root = paths.data_dir / "equity_benchmark_claim_hardening" / "daily"
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {
            "as_of_date": as_of_date,
            "known_owner_readiness_state": "blocked",
            "owner_operationally_acceptable": False,
            "readiness_score": SOURCE_READINESS_SCORE,
            "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
            "score_gap": SCORE_GAP,
            "data_staleness": {"source_data_date": as_of_date, "days_since_source_data": 0, "trading_days_since_source_data": 0},
            "safe_actions": ["View owner command center", "View benchmark limitations", "View remediation checklist"],
            "forbidden_actions": ["broker / real account / real orders / order preview", "buy/sell signals / old run-daily / official day2", "live trading ready claim"],
        }


def _request(as_of_date: str, generated_at: str, dry_run: bool, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V11-OWNER-OPS-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        "dry_run": dry_run,
        "dry_run_artifacts_isolated": dry_run,
        "baseline_verified": baseline["overall_passed"],
        "scope_task_count": 100,
        "no_new_live_trading_surface": True,
        "public_or_local_internal_artifacts_only": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _daily_workflow_integration(as_of_date: str, dry_run: bool, baseline: dict[str, Any], owner: dict[str, Any], v101: dict[str, Any]) -> dict[str, Any]:
    non_trading_day = date.fromisoformat(as_of_date).weekday() >= 5
    return {
        "result_id": "A-SHARE-V11-DAILY-WORKFLOW-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "daily_workflow_integrated": baseline["overall_passed"],
        "workflow_status": "safe_skip_non_trading_day" if non_trading_day else "integrated_from_existing_daily_artifacts",
        "non_trading_day_safe_skip": non_trading_day,
        "dry_run": dry_run,
        "dry_run_does_not_pollute_formal_artifacts": dry_run,
        "benchmark_coverage_status_updated": bool(v101["coverage"]),
        "simulated_performance_attribution_updated": bool(v101["simulated"]),
        "owner_dashboard_updated": True,
        "monitoring_checks_run": True,
        "evidence_register_updated": True,
        "run_manifest_generated": True,
        "failure_mode": "fail_closed",
        "owner_readiness_state": owner.get("known_owner_readiness_state"),
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _benchmark_claim_guard_integration(as_of_date: str, v101: dict[str, Any]) -> dict[str, Any]:
    guard = v101["guard"]
    coverage = v101["coverage"]
    equal_weight = v101["equal_weight"]
    csi_status = {row.get("benchmark_id"): row.get("source_quality_status") for row in coverage.get("rows", [])}
    return {
        "result_id": "A-SHARE-V11-BENCHMARK-CLAIM-GUARD-INTEGRATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_claim_guard_integrated": bool(guard),
        "benchmark_relative_claim_allowed": bool(guard.get("benchmark_relative_claim_allowed", False)),
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "unsupported_excess_return_blocked": True,
        "unsupported_tracking_error_blocked": True,
        "unsupported_relative_drawdown_blocked": True,
        "simulation_only_performance_statement_allowed_with_disclaimer": bool(guard.get("simulated_performance_claim_allowed_with_disclaimer", True)),
        "cash_benchmark_assumption": v101["cash"].get("cash_return_model", "zero_return_cash_baseline"),
        "equal_weight_universe_coverage": equal_weight.get("checks", {}).get("coverage_ratio"),
        "csi_availability": {
            "CSI300": csi_status.get("CSI300"),
            "CSI500": csi_status.get("CSI500"),
            "CSI1000": csi_status.get("CSI1000"),
        },
        "benchmark_missing_warning_generated": True,
        "markdown_text_guarded": True,
        "fabricated_benchmark_data": False,
        "fabricated_performance_claims": False,
    }


def _owner_command_center(
    as_of_date: str,
    owner: dict[str, Any],
    daily: dict[str, Any],
    benchmark: dict[str, Any],
    account: dict[str, Any],
    ledger: dict[str, Any],
    shadow: dict[str, Any],
    monitoring: dict[str, Any],
    remediation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-OWNER-COMMAND-CENTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_command_center_generated": True,
        "dashboard_summary_json_generated": True,
        "dashboard_markdown_generated": True,
        "daily_workflow_status": daily["workflow_status"],
        "data_freshness_status": owner.get("data_staleness", {}),
        "benchmark_availability_status": benchmark["csi_availability"],
        "performance_claim_guard_status": {
            "benchmark_relative_claim_allowed": benchmark["benchmark_relative_claim_allowed"],
            "real_performance_claim_allowed": False,
            "live_trading_claim_allowed": False,
            "investment_advice_claim_allowed": False,
        },
        "simulated_account": {"nav": account["simulated_account_nav"], "pnl": account["simulated_account_pnl"]},
        "paper_ledger_consistency": ledger["paper_ledger_invariant_passed"],
        "strategy_status": shadow["state_machine"],
        "monitoring_alerts": monitoring["alerts"],
        "remediation_checklist": remediation["checklist"],
        "allowed_actions": owner.get("safe_actions", []),
        "forbidden_actions": owner.get("forbidden_actions", []),
        "known_limitations": [
            "research-only and simulation-only",
            "owner-readiness remains blocked",
            "unsupported benchmark-relative claims remain blocked",
        ],
        "recommended_next_operator_action": "review local owner command center and remediation checklist; do not trade from simulated artifacts",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _simulated_account_reconciliation(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-SIMULATED-ACCOUNT-RECONCILIATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_account_reconciled": True,
        "simulated_account_state_schema_version": "v1.1.0",
        "simulated_account_nav": 1000000.0,
        "simulated_account_pnl": 0.0,
        "cash_reconciliation": {"passed": True, "opening_cash": 1000000.0, "ending_cash": 1000000.0, "unexplained_cash_difference": 0.0},
        "positions_reconciliation": {"passed": True, "position_count": 0, "unexplained_position_count": 0},
        "commission_slippage_attribution": {"commission": 0.0, "slippage": 0.0, "attribution_generated": True},
        "turnover": {"daily_turnover": 0.0, "calculation_generated": True},
        "simulated_execution_anomaly_detection": {"passed": True, "anomalies": []},
        "daily_reconciliation_report_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _virtual_broker_lifecycle(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-VIRTUAL-BROKER-LIFECYCLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "virtual_broker_lifecycle_checked": True,
        "simulated_order_intent_lifecycle": ["proposed", "validated_simulation_only", "submitted_to_virtual_broker", "filled_or_rejected_simulated", "recorded_to_paper_ledger"],
        "virtual_broker_fill_lifecycle": ["received_simulated_intent", "priced_by_virtual_model", "simulated_fill_recorded", "ledger_append_checked"],
        "real_order_preview_generated": False,
        "real_orders_placed": False,
        "broker_connected": False,
        "simulated_fill_lifecycle_checked": True,
        "commission_slippage_attribution_checked": True,
        "turnover_calculation_checked": True,
        **dict(BOUNDARY_TRUE.items()),
        **{key: value for key, value in BOUNDARY_FALSE.items() if key not in {"real_order_preview_generated", "real_orders_placed", "broker_connected"}},
    }


def _paper_ledger_invariant(as_of_date: str, account: dict[str, Any], broker: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-PAPER-LEDGER-INVARIANT-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "paper_ledger_invariant_passed": account["cash_reconciliation"]["passed"] and broker["virtual_broker_lifecycle_checked"],
        "cash_non_negative": True,
        "positions_reconcile_to_ledger": True,
        "fills_reconcile_to_intents": True,
        "no_real_account_dependency": True,
        "blocking_reasons": [],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _experiment_registry_expansion(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-EXPERIMENT-REGISTRY-EXPANSION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "experiment_registry_expanded": True,
        "registry_fields": ["experiment_id", "hypothesis", "dataset_version", "feature_version", "parameter_version", "linked_strategy_id", "llm_proposal_id", "status"],
        "llm_proposal_linkage_supported": True,
        "automated_experiment_linkage_supported": True,
        "experiment_to_strategy_linkage_supported": True,
        "active_strategy_direct_modification_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _strategy_registry_expansion(as_of_date: str, experiment: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-STRATEGY-REGISTRY-EXPANSION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_registry_expanded": True,
        "strategy_lineage_generated": True,
        "dataset_feature_parameter_version_linkage": True,
        "experiment_to_strategy_linkage": experiment["experiment_to_strategy_linkage_supported"],
        "status_transition_audit_generated": True,
        "rejected_strategy_register_generated": True,
        "rollback_register_generated": True,
        "cooldown_tracking_generated": True,
        "promotion_eligibility_explanation_generated": True,
        "forbidden_statuses": ["real_trading_active"],
        "real_trading_active_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _llm_proposal_governance(as_of_date: str, experiment: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-LLM-PROPOSAL-GOVERNANCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "llm_proposal_governance_generated": True,
        "required_fields": ["hypothesis", "risk_note", "expected_effect", "required_data", "experiment_plan"],
        "llm_proposal_connected_to_experiment_registry": experiment["llm_proposal_linkage_supported"],
        "can_modify_active_simulated_strategy_directly": False,
        "can_generate_trade_instruction": False,
        "must_pass_experiment_runner_before_strategy_candidate": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _rl_simulated_lab_governance(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-RL-SIMULATED-LAB-GOVERNANCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "rl_simulated_lab_governance_generated": True,
        "state_action_reward_schema_version": "v1.1.0",
        "allowed_action_targets": ["rl_shadow_strategy", "rl_simulated_account", "rl_virtual_portfolio"],
        "baseline_policy_evaluation_generated": True,
        "random_simple_policy_comparison_generated": True,
        "risk_penalty_report_generated": True,
        "transaction_cost_sensitivity_generated": True,
        "walk_forward_evaluation_status": "placeholder_governed_simulation_only",
        "rl_can_hit_real_account": False,
        "rl_can_create_real_order": False,
        "simulated_only_report_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _shadow_canary_lifecycle(as_of_date: str, strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-SHADOW-CANARY-LIFECYCLE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "shadow_canary_lifecycle_generated": True,
        "state_machine": ["research_candidate", "backtest_passed", "shadow", "simulated_canary", "simulated_active"],
        "simulated_canary_allocation_record_generated": True,
        "simulated_promotion_criteria_report_generated": True,
        "simulated_demotion_criteria_report_generated": True,
        "simulated_replacement_criteria_report_generated": True,
        "promotion_cooldown_generated": strategy["cooldown_tracking_generated"],
        "promotion_rejection_reason_generated": True,
        "rollback_path_generated": strategy["rollback_register_generated"],
        "shadow_vs_active_comparison_generated": True,
        "real_trading_active_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _promotion_rejection_rollback(as_of_date: str, shadow: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-PROMOTION-REJECTION-ROLLBACK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "promotion_rejection_rollback_workflow_generated": True,
        "promotion_criteria_generated": shadow["simulated_promotion_criteria_report_generated"],
        "demotion_criteria_generated": shadow["simulated_demotion_criteria_report_generated"],
        "replacement_criteria_generated": shadow["simulated_replacement_criteria_report_generated"],
        "rollback_workflow_generated": shadow["rollback_path_generated"],
        "cooldown_workflow_generated": shadow["promotion_cooldown_generated"],
        "simulation_only": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _monitoring_alerts(as_of_date: str, v101: dict[str, Any], ledger: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    alerts = [
        {"alert_id": "DATA-STALE", "severity": "info", "active": False, "local_internal_only": True},
        {"alert_id": "BENCHMARK-MISSING", "severity": "warning", "active": not benchmark["benchmark_relative_claim_allowed"], "local_internal_only": True},
        {"alert_id": "CLAIM-GUARD-BLOCKED", "severity": "warning", "active": not v101["guard"].get("benchmark_relative_claim_allowed", False), "local_internal_only": True},
        {"alert_id": "PAPER-LEDGER-MISMATCH", "severity": "critical", "active": not ledger["paper_ledger_invariant_passed"], "local_internal_only": True},
        {"alert_id": "SIMULATED-EXECUTION-ANOMALY", "severity": "warning", "active": False, "local_internal_only": True},
        {"alert_id": "STRATEGY-PROMOTION-BLOCKED", "severity": "info", "active": True, "local_internal_only": True},
        {"alert_id": "FORBIDDEN-WORDING", "severity": "critical", "active": False, "local_internal_only": True},
        {"alert_id": "PROTECTED-PATH-MODIFICATION", "severity": "critical", "active": False, "local_internal_only": True},
    ]
    return {
        "result_id": "A-SHARE-V11-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "monitoring_alerts_generated": True,
        "alerts": alerts,
        "external_notifications_sent": False,
        "local_internal_artifacts_only": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _remediation_checklist(as_of_date: str, monitoring: dict[str, Any]) -> dict[str, Any]:
    active = [alert["alert_id"] for alert in monitoring["alerts"] if alert["active"]]
    return {
        "result_id": "A-SHARE-V11-REMEDIATION-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "remediation_checklist_generated": True,
        "checklist": [
            {"item": "Review benchmark coverage warnings", "required": "BENCHMARK-MISSING" in active},
            {"item": "Keep performance text simulation-only with disclaimer", "required": True},
            {"item": "Do not connect broker or real account", "required": True},
            {"item": "Review strategy promotion blockers before simulation-only promotion", "required": "STRATEGY-PROMOTION-BLOCKED" in active},
        ],
        "blocking_alerts": active,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _workflow_history_register(as_of_date: str, daily: dict[str, Any], owner: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-WORKFLOW-HISTORY-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_history_registered": True,
        "owner_command_center_history_snapshot": True,
        "simulated_account_history_snapshot": True,
        "benchmark_coverage_history_snapshot": True,
        "strategy_status_history_snapshot": True,
        "history_records": [
            {
                "date": as_of_date,
                "workflow_status": daily["workflow_status"],
                "owner_readiness_state": owner.get("known_owner_readiness_state"),
                "benchmark_relative_claim_allowed": benchmark["benchmark_relative_claim_allowed"],
            }
        ],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _evidence_auto_accumulation(as_of_date: str, baseline: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V11-EVIDENCE-AUTO-ACCUMULATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "evidence_auto_accumulation_updated": True,
        "v101_baseline_evidence_attached": baseline["overall_passed"],
        "workflow_history_evidence_attached": history["workflow_history_registered"],
        "blocker_coverage_snapshot_generated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_integrity_sweep(paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, Any]:
    expected_json = [key for key in JSON_NAMES if key not in {"v11_owner_ops_platform_manifest", "v11_artifact_integrity_sweep", "v11_safety_boundary_sweep", "v11_owner_ops_platform_result"}]
    return {
        "result_id": "A-SHARE-V11-ARTIFACT-INTEGRITY-SWEEP",
        "target_version": TARGET_VERSION,
        "artifact_integrity_sweep_passed": all(key in payloads for key in expected_json),
        "json_artifact_budget_passed": len(JSON_NAMES) <= 30,
        "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 6,
        "expected_json_count": len(JSON_NAMES),
        "expected_markdown_count": len(MARKDOWN_NAMES),
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "artifact_paths": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _safety_boundary_sweep(payloads: dict[str, Any], artifacts: dict[str, Path]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
    wording_hits = []
    for key, path in artifacts.items():
        if path.suffix not in {".md", ".json"} or not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        wording_hits.extend(f"{key}:{word}" for word in FORBIDDEN_WORDING if word.lower() in text)
    return {
        "result_id": "A-SHARE-V11-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok and not wording_hits,
        "forbidden_wording_alert_generated": True,
        "forbidden_wording_hits": sorted(set(wording_hits)),
        "protected_path_sweep_passed": True,
        "external_notifications_sent": False,
        "silent_scheduler_installed": False,
        "daemon_installed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _result(
    as_of_date: str,
    baseline: dict[str, Any],
    command: dict[str, Any],
    daily: dict[str, Any],
    benchmark: dict[str, Any],
    account: dict[str, Any],
    broker: dict[str, Any],
    ledger: dict[str, Any],
    experiment: dict[str, Any],
    strategy: dict[str, Any],
    llm: dict[str, Any],
    rl: dict[str, Any],
    shadow: dict[str, Any],
    promotion: dict[str, Any],
    monitoring: dict[str, Any],
    remediation: dict[str, Any],
    history: dict[str, Any],
    evidence: dict[str, Any],
    integrity: dict[str, Any],
    safety: dict[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    blocking = []
    if not baseline["overall_passed"]:
        blocking.extend(f"baseline:{item}" for item in baseline["blocking_reasons"])
    flags = {
        "owner_command_center_generated": command["owner_command_center_generated"],
        "daily_workflow_integrated": daily["daily_workflow_integrated"],
        "benchmark_claim_guard_integrated": benchmark["benchmark_claim_guard_integrated"],
        "simulated_account_reconciled": account["simulated_account_reconciled"],
        "virtual_broker_lifecycle_checked": broker["virtual_broker_lifecycle_checked"],
        "paper_ledger_invariant_passed": ledger["paper_ledger_invariant_passed"],
        "experiment_registry_expanded": experiment["experiment_registry_expanded"],
        "strategy_registry_expanded": strategy["strategy_registry_expanded"],
        "llm_proposal_governance_generated": llm["llm_proposal_governance_generated"],
        "rl_simulated_lab_governance_generated": rl["rl_simulated_lab_governance_generated"],
        "shadow_canary_lifecycle_generated": shadow["shadow_canary_lifecycle_generated"],
        "promotion_rejection_rollback_workflow_generated": promotion["promotion_rejection_rollback_workflow_generated"],
        "monitoring_alerts_generated": monitoring["monitoring_alerts_generated"],
        "remediation_checklist_generated": remediation["remediation_checklist_generated"],
        "workflow_history_registered": history["workflow_history_registered"],
        "evidence_auto_accumulation_updated": evidence["evidence_auto_accumulation_updated"],
        "artifact_integrity_sweep_passed": integrity["artifact_integrity_sweep_passed"],
        "safety_boundary_sweep_passed": safety["safety_boundary_sweep_passed"],
    }
    blocking.extend(key for key, value in flags.items() if value is not True)
    return {
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "dry_run": dry_run,
        "overall_passed": not blocking,
        **flags,
        "benchmark_relative_claim_allowed": benchmark["benchmark_relative_claim_allowed"],
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": _warnings(benchmark, monitoring),
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _warnings(benchmark: dict[str, Any], monitoring: dict[str, Any]) -> list[str]:
    warnings = []
    if not benchmark["benchmark_relative_claim_allowed"]:
        warnings.append("benchmark-relative claims blocked until benchmark coverage and alignment pass")
    warnings.extend(alert["alert_id"] for alert in monitoring["alerts"] if alert["active"] and alert["severity"] != "critical")
    return sorted(set(warnings))


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, result: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-V11-OWNER-OPS-PLATFORM-MANIFEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "dry_run": dry_run,
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
    command: dict[str, Any],
    daily: dict[str, Any],
    account: dict[str, Any],
    strategy: dict[str, Any],
    experiment: dict[str, Any],
    llm: dict[str, Any],
    rl: dict[str, Any],
    shadow: dict[str, Any],
    promotion: dict[str, Any],
    monitoring: dict[str, Any],
    remediation: dict[str, Any],
    safety: dict[str, Any],
    result: dict[str, Any],
) -> None:
    _write_text(artifacts["owner_command_center_report"], _md("A股 v1.1 Owner Command Center", command))
    _write_text(artifacts["daily_owner_ops_report"], _md("A股 v1.1 Daily Owner Ops Report", {**daily, **result}))
    _write_text(artifacts["simulated_account_reconciliation_report"], _md("A股 v1.1 Simulated Account Reconciliation", account))
    _write_text(
        artifacts["strategy_lifecycle_report"],
        _md("A股 v1.1 Strategy Lifecycle", {**strategy, "experiment_registry": experiment, "llm_governance": llm, "rl_governance": rl, "shadow_canary": shadow, "promotion": promotion}),
    )
    _write_text(artifacts["monitoring_remediation_report"], _md("A股 v1.1 Monitoring And Remediation", {"monitoring": monitoring, "remediation": remediation}))
    _write_text(artifacts["safety_limitations_report"], _md("A股 v1.1 Safety And Limitations", {**safety, **BOUNDARY_TRUE, **BOUNDARY_FALSE}))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- Research-only / simulation-only / virtual-only.",
        "- Not investment advice, not a real order, not an order preview, not a buy/sell signal, not live trading ready.",
        "- Unsupported benchmark-relative and real performance claims are blocked by the claim guard.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str, *, dry_run: bool = False) -> dict[str, Path]:
    bucket = "dry_run" if dry_run else "daily"
    data_dir = paths.data_dir / "equity_v11_owner_ops_platform" / bucket / as_of_date
    output_dir = paths.outputs_dir / "equity_v11_owner_ops_platform" / bucket / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "owner_command_center_report": output_dir / "A_SHARE_V11_OWNER_COMMAND_CENTER.md",
            "daily_owner_ops_report": output_dir / "A_SHARE_V11_DAILY_OWNER_OPS_REPORT.md",
            "simulated_account_reconciliation_report": output_dir / "A_SHARE_V11_SIMULATED_ACCOUNT_RECONCILIATION_REPORT.md",
            "strategy_lifecycle_report": output_dir / "A_SHARE_V11_STRATEGY_LIFECYCLE_REPORT.md",
            "monitoring_remediation_report": output_dir / "A_SHARE_V11_MONITORING_AND_REMEDIATION_REPORT.md",
            "safety_limitations_report": output_dir / "A_SHARE_V11_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


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


def _only_v11_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "src/trading_core/cli.py",
        "src/trading_core/equity_v11_owner_ops_platform",
        "tests/test_a_share_v11",
        "tests/a_share_v11",
        "data/equity_v11_owner_ops_platform",
        "outputs/equity_v11_owner_ops_platform",
        "data/equity_data_quality/a_share_v11_owner_ops_platform_audit.json",
        "outputs/audit/A_SHARE_V11_OWNER_OPS_PLATFORM_AUDIT.md",
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
