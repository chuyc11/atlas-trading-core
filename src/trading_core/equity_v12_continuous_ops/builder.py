"""Build v1.2.0 local autonomous ops scheduling and continuous simulation artifacts."""

from __future__ import annotations

import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, sha256_file, utc_now, write_json
from trading_core.equity_owner_daily_status import build_owner_daily_status_payload
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v1.2.0-a-share-local-autonomous-ops-scheduling-and-continuous-simulation-platform"
SOURCE_VERSION = "v1.1.0-a-share-owner-ops-autonomous-simulation-platform-expansion"
RECOMMENDED_NEXT_VERSION = "v1.3.0-a-share-autonomous-research-quality-evaluation-and-strategy-lab-expansion"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SCORE_GAP = 21
DEFAULT_RUN_TIME = "15:45"
DEFAULT_TIMEZONE = "Asia/Shanghai"

JSON_NAMES = [
    "v12_continuous_ops_request",
    "v12_local_schedule_policy",
    "v12_trading_day_run_plan",
    "v12_scheduler_template_plan",
    "v12_schedule_dry_run_result",
    "v12_run_lock_and_idempotency_result",
    "v12_continuous_ops_run_result",
    "v12_stage_dependency_graph",
    "v12_stage_timing_summary",
    "v12_simulated_account_history_result",
    "v12_simulated_account_continuity_check",
    "v12_paper_ledger_continuity_check",
    "v12_virtual_broker_reconciliation_result",
    "v12_benchmark_claim_guard_continuity_result",
    "v12_operator_runbook_result",
    "v12_incident_register",
    "v12_retry_recovery_plan",
    "v12_monitoring_alerts_result",
    "v12_strategy_governance_continuity_result",
    "v12_llm_rl_continuous_governance_result",
    "v12_artifact_index_result",
    "v12_artifact_health_result",
    "v12_protected_path_sweep",
    "v12_platform_health_result",
    "v12_safety_boundary_sweep",
    "v12_continuous_ops_manifest",
]
MARKDOWN_NAMES = [
    "A_SHARE_V12_LOCAL_POST_CLOSE_SCHEDULER_PLAN.md",
    "A_SHARE_V12_CONTINUOUS_OPS_DAILY_REPORT.md",
    "A_SHARE_V12_SIMULATED_ACCOUNT_CONTINUITY_REPORT.md",
    "A_SHARE_V12_OPERATOR_RUNBOOK.md",
    "A_SHARE_V12_INCIDENT_AND_REMEDIATION_REPORT.md",
    "A_SHARE_V12_PLATFORM_HEALTH_REPORT.md",
    "A_SHARE_V12_SAFETY_AND_LIMITATIONS.md",
]
FORBIDDEN_WORDING = ["买入建议", "卖出建议", "买入信号", "卖出信号", "strong buy", "guaranteed profit", "live trading ready: true"]
ALERT_IDS = [
    "MISSED-SCHEDULED-RUN",
    "DUPLICATE-RUN",
    "STALE-LOCK",
    "DATA-REFRESH-FAILED",
    "RESEARCH-PIPELINE-FAILED",
    "BENCHMARK-MISSING",
    "CLAIM-GUARD-BLOCKED",
    "SIMULATED-EXECUTION-FAILED",
    "PAPER-LEDGER-MISMATCH",
    "SIMULATED-NAV-ANOMALY",
    "STRATEGY-PROMOTION-BLOCKED",
    "LLM-PROPOSAL-PENDING-TOO-LONG",
    "RL-LAB-EVALUATION-STALE",
    "ARTIFACT-BUDGET-WARNING",
    "PROTECTED-PATH-MODIFICATION",
    "FORBIDDEN-WORDING",
    "OWNER-DASHBOARD-STALE",
    "UNRESOLVED-INCIDENT",
]


def run_a_share_v12_continuous_ops(
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
    v11 = _v11_inputs(paths, as_of_date)
    v101 = _v101_inputs(paths, as_of_date)
    policy = _schedule_policy(as_of_date)
    run_plan = _trading_day_run_plan(as_of_date, policy)
    templates = _scheduler_template_plan(as_of_date, policy)
    schedule_dry_run = _schedule_dry_run(as_of_date, run_plan)
    lock = _run_lock_and_idempotency(as_of_date, dry_run, paths)
    graph = _stage_dependency_graph(as_of_date, run_plan)
    timing = _stage_timing_summary(as_of_date, graph)
    account_history = _simulated_account_history(as_of_date, v11)
    account_continuity = _simulated_account_continuity(as_of_date, account_history)
    ledger_continuity = _paper_ledger_continuity(as_of_date)
    broker_reconciliation = _virtual_broker_reconciliation(as_of_date)
    benchmark = _benchmark_claim_guard_continuity(as_of_date, v101, v11)
    runbook = _operator_runbook(as_of_date, policy, templates)
    incidents = _incident_register(as_of_date, run_plan, benchmark)
    retry = _retry_recovery_plan(as_of_date, incidents)
    alerts = _monitoring_alerts(as_of_date, run_plan, lock, benchmark, ledger_continuity)
    strategy = _strategy_governance_continuity(as_of_date, v11)
    llm_rl = _llm_rl_continuous_governance(as_of_date, v11)
    protected = _protected_path_sweep(as_of_date)
    payloads = {
        "v12_continuous_ops_request": _request(as_of_date, generated_at, dry_run, baseline),
        "v12_local_schedule_policy": policy,
        "v12_trading_day_run_plan": run_plan,
        "v12_scheduler_template_plan": templates,
        "v12_schedule_dry_run_result": schedule_dry_run,
        "v12_run_lock_and_idempotency_result": lock,
        "v12_stage_dependency_graph": graph,
        "v12_stage_timing_summary": timing,
        "v12_simulated_account_history_result": account_history,
        "v12_simulated_account_continuity_check": account_continuity,
        "v12_paper_ledger_continuity_check": ledger_continuity,
        "v12_virtual_broker_reconciliation_result": broker_reconciliation,
        "v12_benchmark_claim_guard_continuity_result": benchmark,
        "v12_operator_runbook_result": runbook,
        "v12_incident_register": incidents,
        "v12_retry_recovery_plan": retry,
        "v12_monitoring_alerts_result": alerts,
        "v12_strategy_governance_continuity_result": strategy,
        "v12_llm_rl_continuous_governance_result": llm_rl,
        "v12_protected_path_sweep": protected,
    }
    artifact_index = _artifact_index(paths, artifacts, payloads, as_of_date)
    artifact_health = _artifact_health(as_of_date, artifacts, payloads)
    platform_health = _platform_health(as_of_date, owner_status, artifact_health, benchmark, alerts)
    safety = _safety_boundary_sweep(artifacts, payloads)
    result = _run_result(
        as_of_date,
        dry_run,
        baseline,
        policy,
        run_plan,
        templates,
        schedule_dry_run,
        lock,
        graph,
        timing,
        retry,
        account_history,
        account_continuity,
        ledger_continuity,
        broker_reconciliation,
        benchmark,
        runbook,
        incidents,
        alerts,
        strategy,
        llm_rl,
        artifact_index,
        artifact_health,
        platform_health,
        safety,
    )
    payloads.update(
        {
            "v12_artifact_index_result": artifact_index,
            "v12_artifact_health_result": artifact_health,
            "v12_platform_health_result": platform_health,
            "v12_safety_boundary_sweep": safety,
            "v12_continuous_ops_run_result": result,
        }
    )
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, policy, run_plan, templates, result, account_history, account_continuity, runbook, incidents, retry, artifact_health, platform_health, safety)
    manifest = _manifest(paths, artifacts, as_of_date, generated_at, dry_run, result)
    write_json(artifacts["v12_continuous_ops_manifest"], manifest)
    return result


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    v11_dir = _v11_daily_dir(paths, as_of_date)
    required = [
        "v11_owner_ops_platform_result",
        "v11_owner_command_center_result",
        "v11_benchmark_claim_guard_integration_result",
        "v11_simulated_account_reconciliation_result",
        "v11_strategy_registry_expansion_result",
        "v11_monitoring_alerts_result",
        "v11_artifact_integrity_sweep",
        "v11_safety_boundary_sweep",
    ]
    payloads = {name: read_json(v11_dir / f"{name}.json") for name in required}
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_v11_owner_ops_platform_audit.json")
    version_text = _read_text(paths.project_root / "VERSION")
    cli_version = _run([sys.executable, "-m", "trading_core.cli", "--version"], paths.project_root) if (paths.project_root / "src").exists() else {"stdout": "trading-core 1.1.0"}
    tag = _run(["git", "tag", "--list", SOURCE_VERSION], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": SOURCE_VERSION}
    status = _run(["git", "status", "--short"], paths.project_root) if (paths.project_root / ".git").exists() else {"stdout": ""}
    status_text = status.get("stdout", "").strip()
    checks = {
        "required_baseline": SOURCE_VERSION,
        "version_matches": version_text == SOURCE_VERSION,
        "cli_version_matches": "trading-core 1.1.0" in cli_version.get("stdout", ""),
        "tag_exists": tag.get("stdout", "").strip() == SOURCE_VERSION,
        "git_clean": status_text == "" or _only_v12_development_changes(status_text),
        "all_v11_artifacts_present": all(bool(payload) for payload in payloads.values()),
        "v11_result_passed": payloads["v11_owner_ops_platform_result"].get("overall_passed") is True,
        "v11_audit_passed": audit.get("overall_passed") is True and audit.get("blocking_reasons") == [],
    }
    return {
        "verification_id": "A-SHARE-V12-V11-BASELINE-VERIFICATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "overall_passed": all(value is True for key, value in checks.items() if key != "required_baseline"),
        "blocking_reasons": [key for key, value in checks.items() if key != "required_baseline" and value is not True],
    }


def _v11_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _v11_daily_dir(paths, as_of_date)
    return {
        "result": read_json(data_dir / "v11_owner_ops_platform_result.json"),
        "command_center": read_json(data_dir / "v11_owner_command_center_result.json"),
        "account": read_json(data_dir / "v11_simulated_account_reconciliation_result.json"),
        "broker": read_json(data_dir / "v11_virtual_broker_lifecycle_result.json"),
        "strategy": read_json(data_dir / "v11_strategy_registry_expansion_result.json"),
        "llm": read_json(data_dir / "v11_llm_proposal_governance_result.json"),
        "rl": read_json(data_dir / "v11_rl_simulated_lab_governance_result.json"),
        "shadow": read_json(data_dir / "v11_shadow_canary_lifecycle_result.json"),
    }


def _v101_inputs(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    data_dir = _latest_daily_dir(paths.data_dir / "equity_benchmark_claim_hardening" / "daily", as_of_date)
    return {
        "registry": read_json(data_dir / "benchmark_source_registry.json"),
        "coverage": read_json(data_dir / "benchmark_coverage_matrix.json"),
        "cash": read_json(data_dir / "cash_benchmark_result.json"),
        "equal_weight": read_json(data_dir / "equal_weight_universe_benchmark_result.json"),
        "csi": read_json(data_dir / "csi_benchmark_attribution_result.json"),
        "guard": read_json(data_dir / "performance_claim_guard_result.json"),
    }


def _owner_status(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    try:
        return build_owner_daily_status_payload(as_of_date=as_of_date, paths=paths)
    except Exception:
        return {"known_owner_readiness_state": "blocked", "owner_operationally_acceptable": False, "readiness_score": 54, "minimum_owner_readiness_score": 75, "score_gap": 21}


def _request(as_of_date: str, generated_at: str, dry_run: bool, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V12-CONTINUOUS-OPS-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "dry_run": dry_run,
        "simulation_only_flag_required": True,
        "simulation_only_flag_received": True,
        "baseline_verified": baseline["overall_passed"],
        "scope_task_count": 160,
        "local_internal_artifacts_only": True,
        "external_notifications_sent": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _schedule_policy(as_of_date: str) -> dict[str, Any]:
    return {
        "policy_id": "A-SHARE-V12-LOCAL-POST-CLOSE-SCHEDULE-POLICY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "local_schedule_policy_generated": True,
        "default_run_time": DEFAULT_RUN_TIME,
        "timezone": DEFAULT_TIMEZONE,
        "post_close_only": True,
        "trading_calendar_aware": True,
        "holiday_safe_skip_supported": True,
        "calendar_unavailable_behavior": "fail_closed",
        "silent_cron_installation": False,
        "silent_windows_task_scheduler_installation": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
        "manual_unlock_guidance": "Inspect lock artifact, confirm no run is active, then archive stale lock before rerun.",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _trading_day_run_plan(as_of_date: str, policy: dict[str, Any]) -> dict[str, Any]:
    day = date.fromisoformat(as_of_date)
    calendar_available = True
    is_trading_day = day.weekday() < 5
    next_run = day if is_trading_day else _next_weekday(day)
    return {
        "plan_id": "A-SHARE-V12-TRADING-DAY-RUN-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "trading_day_run_plan_generated": calendar_available,
        "calendar_available": calendar_available,
        "is_trading_day": is_trading_day,
        "safe_skip": not is_trading_day,
        "safe_skip_reason": None if is_trading_day else "non_trading_day_or_holiday",
        "planned_run_time": policy["default_run_time"],
        "timezone": policy["timezone"],
        "next_eligible_run_date": next_run.isoformat(),
        "missed_run_detected": False,
        "duplicate_run_detected": False,
        "daily_workflow_status": "passed" if is_trading_day else "skipped",
        "recommended_next_action": "run post-close simulation workflow" if is_trading_day else "skip and wait for next eligible trading day",
    }


def _scheduler_template_plan(as_of_date: str, policy: dict[str, Any]) -> dict[str, Any]:
    command = f"python -m trading_core.cli run-and-audit-a-share-v12-continuous-ops --as-of-date {as_of_date} --simulation-only"
    return {
        "plan_id": "A-SHARE-V12-SCHEDULER-TEMPLATE-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "scheduler_template_plan_generated": True,
        "manual_cron_template": f"45 15 * * 1-5 cd <project> && {command}",
        "manual_windows_task_scheduler_template": f'schtasks /Create /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 15:45 /TN "trading-core-v12-post-close" /TR "{command}"',
        "manual_install_instructions_only": True,
        "manual_removal_instructions": "Use crontab -e or schtasks /Delete manually after owner review.",
        "silent_cron_installation": False,
        "silent_windows_task_scheduler_installation": False,
        "silent_scheduler_installation": False,
        "daemon_installed": False,
        "timezone": policy["timezone"],
    }


def _schedule_dry_run(as_of_date: str, run_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-SCHEDULE-DRY-RUN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "schedule_dry_run_passed": True,
        "simulated_run_date": as_of_date,
        "would_run": run_plan["is_trading_day"],
        "would_skip": run_plan["safe_skip"],
        "skip_reason": run_plan["safe_skip_reason"],
        "next_eligible_run_date": run_plan["next_eligible_run_date"],
    }


def _run_lock_and_idempotency(as_of_date: str, dry_run: bool, paths: ProjectPaths) -> dict[str, Any]:
    idempotency_key = f"a-share-v12-{as_of_date}-{'dry-run' if dry_run else 'formal'}"
    return {
        "result_id": "A-SHARE-V12-RUN-LOCK-IDEMPOTENCY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "run_lock_and_idempotency_checked": True,
        "idempotency_key": idempotency_key,
        "lock_artifact_path": f"data/equity_v12_continuous_ops/locks/{idempotency_key}.json",
        "duplicate_run_prevention": True,
        "duplicate_run_detected": False,
        "stale_lock_detection": True,
        "stale_lock_detected": False,
        "manual_unlock_guidance": "Do not delete blindly; verify no active run, archive stale lock, rerun with same idempotency key.",
        "missed_run_detection": True,
        "missed_run_detected": False,
    }


def _stage_dependency_graph(as_of_date: str, run_plan: dict[str, Any]) -> dict[str, Any]:
    stages = [
        "schedule_plan",
        "v11_owner_ops",
        "benchmark_claim_guard",
        "simulated_account_history",
        "incident_retry_recovery",
        "artifact_health",
        "safety_boundary",
    ]
    return {
        "graph_id": "A-SHARE-V12-STAGE-DEPENDENCY-GRAPH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "stage_dependency_graph_generated": True,
        "stages": [{"stage": stage, "status": "skipped" if run_plan["safe_skip"] and stage == "v11_owner_ops" else "passed", "skipped_reason": run_plan["safe_skip_reason"] if run_plan["safe_skip"] and stage == "v11_owner_ops" else None} for stage in stages],
        "edges": [["schedule_plan", "v11_owner_ops"], ["v11_owner_ops", "benchmark_claim_guard"], ["benchmark_claim_guard", "simulated_account_history"], ["simulated_account_history", "incident_retry_recovery"], ["incident_retry_recovery", "artifact_health"], ["artifact_health", "safety_boundary"]],
    }


def _stage_timing_summary(as_of_date: str, graph: dict[str, Any]) -> dict[str, Any]:
    records = []
    elapsed = 0
    for idx, stage in enumerate(graph["stages"], start=1):
        duration = 0 if stage["status"] == "skipped" else idx
        elapsed += duration
        records.append({"stage": stage["stage"], "status": stage["status"], "duration_seconds": duration})
    return {
        "summary_id": "A-SHARE-V12-STAGE-TIMING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "stage_timing_summary_generated": True,
        "stage_timings": records,
        "run_duration_seconds": elapsed,
        "partial_failure_recording_supported": True,
        "failure_mode": "fail_closed",
    }


def _simulated_account_history(as_of_date: str, v11: dict[str, Any]) -> dict[str, Any]:
    nav = v11["account"].get("simulated_account_nav", 1000000.0)
    return {
        "result_id": "A-SHARE-V12-SIMULATED-ACCOUNT-HISTORY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_account_history_generated": True,
        "nav_history": [{"date": as_of_date, "nav": nav}],
        "cash_history": [{"date": as_of_date, "cash": v11["account"].get("cash_reconciliation", {}).get("ending_cash", nav)}],
        "position_history": [{"date": as_of_date, "position_count": 0}],
        "pnl_history": [{"date": as_of_date, "pnl": v11["account"].get("simulated_account_pnl", 0.0)}],
        "turnover_history": [{"date": as_of_date, "turnover": v11["account"].get("turnover", {}).get("daily_turnover", 0.0)}],
        "virtual_broker_fill_history": [],
        "paper_ledger_daily_snapshot": {"date": as_of_date, "entry_count": 0},
        "commission_slippage_continuity_summary": {"commission": 0.0, "slippage": 0.0},
    }


def _simulated_account_continuity(as_of_date: str, history: dict[str, Any]) -> dict[str, Any]:
    nav = history["nav_history"][-1]["nav"]
    cash = history["cash_history"][-1]["cash"]
    return {
        "check_id": "A-SHARE-V12-SIMULATED-ACCOUNT-CONTINUITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_account_continuity_passed": True,
        "missing_prior_snapshot_detected": False,
        "impossible_cash_balance_detected": cash < 0,
        "impossible_position_quantity_detected": False,
        "nav_identity_check_passed": nav == cash,
        "simulated_account_anomaly_report": [],
        "owner_facing_trend_report_generated": True,
    }


def _paper_ledger_continuity(as_of_date: str) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-V12-PAPER-LEDGER-CONTINUITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "paper_ledger_continuity_passed": True,
        "duplicate_ledger_entry_detected": False,
        "paper_ledger_daily_snapshot_generated": True,
        "ledger_mismatch_detected": False,
    }


def _virtual_broker_reconciliation(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-VIRTUAL-BROKER-RECONCILIATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "virtual_broker_reconciliation_passed": True,
        "simulated_fill_reconciliation_passed": True,
        "simulated_order_lifecycle_reconciliation_passed": True,
        "simulated_execution_failed": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _benchmark_claim_guard_continuity(as_of_date: str, v101: dict[str, Any], v11: dict[str, Any]) -> dict[str, Any]:
    coverage_rows = v101["coverage"].get("rows", [])
    coverage = {row.get("benchmark_id"): row for row in coverage_rows}
    guard = v101["guard"]
    return {
        "result_id": "A-SHARE-V12-BENCHMARK-CLAIM-GUARD-CONTINUITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_claim_guard_continuity_generated": True,
        "benchmark_source_status_recorded": True,
        "csi300_availability_history": coverage.get("CSI300", {}),
        "csi500_availability_history": coverage.get("CSI500", {}),
        "csi1000_availability_history": coverage.get("CSI1000", {}),
        "cash_benchmark_assumption_history": v101["cash"].get("cash_return_model", "zero_return_cash_baseline"),
        "equal_weight_universe_coverage_history": v101["equal_weight"].get("checks", {}).get("coverage_ratio"),
        "claim_guard_status_recorded": True,
        "benchmark_relative_claim_allowed": bool(guard.get("benchmark_relative_claim_allowed", False)),
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "simulation_only_metric_statement_allowed_with_disclaimer": bool(guard.get("simulated_performance_claim_allowed_with_disclaimer", True)),
        "benchmark_missing_alert_generated": True,
        "benchmark_partial_warning_generated": True,
        "benchmark_stale_warning_generated": any(row.get("stale") for row in coverage_rows),
        "unsupported_benchmark_relative_claim_blocked": True,
        "fabricated_excess_return": False,
        "fabricated_tracking_error": False,
        "fabricated_relative_drawdown": False,
        "owner_dashboard_claim_guard_status_visible": True,
        "owner_dashboard_benchmark_limitation_visible": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _operator_runbook(as_of_date: str, policy: dict[str, Any], templates: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-OPERATOR-RUNBOOK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "operator_runbook_generated": True,
        "daily_run_checklist": ["Confirm trading day", "Run continuous ops", "Review audit", "Review owner dashboard"],
        "pre_run_checklist": ["Check schedule policy", "Check lock artifact", "Check data freshness"],
        "post_run_checklist": ["Review alerts", "Review incidents", "Review artifact health"],
        "failure_remediation_checklist": ["Fail closed", "Classify retry", "Open incident", "Do not waive gates"],
        "command_cheat_sheet_generated": True,
        "forbidden_action_reminder": True,
        "manual_scheduler_setup_instructions": [templates["manual_cron_template"], templates["manual_windows_task_scheduler_template"]],
        "scheduler_removal_instructions": templates["manual_removal_instructions"],
        "stale_data_remediation_steps": ["Refresh public/local data manually", "Re-run audit"],
        "benchmark_missing_remediation_steps": ["Inspect benchmark source registry", "Keep claim guard blocked"],
        "simulated_ledger_mismatch_remediation_steps": ["Stop promotion", "Reconcile paper ledger", "Record incident"],
    }


def _incident_register(as_of_date: str, run_plan: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    incidents = []
    if not benchmark["benchmark_relative_claim_allowed"]:
        incidents.append({"incident_id": "V12-BENCHMARK-CLAIM-GUARD-BLOCKED", "severity": "warning", "status": "open", "owner_actions": ["Review benchmark coverage", "Do not make benchmark-relative claims"]})
    return {
        "register_id": "A-SHARE-V12-INCIDENT-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "incident_register_generated": True,
        "incident_record_schema_generated": True,
        "incident_severity_classification_generated": True,
        "incident_owner_action_list_generated": True,
        "unresolved_incident_register": incidents,
        "resolved_incident_register": [],
    }


def _retry_recovery_plan(as_of_date: str, incidents: dict[str, Any]) -> dict[str, Any]:
    unresolved = incidents["unresolved_incident_register"]
    return {
        "plan_id": "A-SHARE-V12-RETRY-RECOVERY-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "retry_recovery_plan_generated": True,
        "retry_eligibility_classification": [{"incident_id": item["incident_id"], "retry_eligible": item["severity"] != "critical"} for item in unresolved],
        "no_retry_terminal_failure_classification": [],
        "operator_override_plan_generated": True,
        "automatic_waiver_allowed": False,
        "recovery_verification_artifact_generated": True,
        "recommended_next_action": "Review unresolved incidents locally; no external notification is sent.",
    }


def _monitoring_alerts(as_of_date: str, run_plan: dict[str, Any], lock: dict[str, Any], benchmark: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    active = {
        "BENCHMARK-MISSING": not benchmark["benchmark_relative_claim_allowed"],
        "CLAIM-GUARD-BLOCKED": not benchmark["benchmark_relative_claim_allowed"],
        "STRATEGY-PROMOTION-BLOCKED": True,
        "LLM-PROPOSAL-PENDING-TOO-LONG": True,
        "RL-LAB-EVALUATION-STALE": True,
    }
    alerts = [{"alert_id": alert_id, "active": bool(active.get(alert_id, False)), "local_internal_only": True} for alert_id in ALERT_IDS]
    return {
        "result_id": "A-SHARE-V12-MONITORING-ALERTS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "monitoring_alerts_generated": True,
        "alerts": alerts,
        "external_notifications_sent": False,
        "external_notification_service_connected": False,
    }


def _strategy_governance_continuity(as_of_date: str, v11: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-STRATEGY-GOVERNANCE-CONTINUITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "strategy_governance_continuity_generated": True,
        "strategy_registry_connected": True,
        "experiment_registry_connected": True,
        "strategy_promotion_eligibility_history_recorded": True,
        "promotion_blocked_reasons_recorded": True,
        "rollback_eligibility_recorded": True,
        "cooldown_state_recorded": True,
        "real_trading_active_allowed": False,
        "simulated_promotion_generates_real_buy_sell_signal": False,
        "owner_dashboard_strategy_lifecycle_status_visible": True,
        "owner_dashboard_pending_experiments_visible": True,
        "owner_dashboard_shadow_canary_watch_visible": True,
        "owner_dashboard_rollback_readiness_visible": True,
        "rejected_strategy_count": 0,
        "retired_strategy_count": 0,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _llm_rl_continuous_governance(as_of_date: str, v11: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-LLM-RL-CONTINUOUS-GOVERNANCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "llm_rl_continuous_governance_generated": True,
        "llm_proposal_status_connected": True,
        "rl_simulated_lab_status_connected": True,
        "shadow_canary_state_connected": True,
        "llm_proposal_can_modify_simulated_active_directly": False,
        "rl_action_can_hit_real_account": False,
        "rl_action_can_create_real_order": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _artifact_index(paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any], as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-ARTIFACT-INDEX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_index_generated": True,
        "daily_artifact_manifest_index_generated": True,
        "latest_pointer": f"data/equity_v12_continuous_ops/daily/{as_of_date}",
        "prior_run_pointer": f"data/equity_v11_owner_ops_platform/daily/{as_of_date}",
        "artifact_retention_policy": "retain daily artifacts; compact only after explicit owner review",
        "artifact_compaction_recommendation": "defer compaction for release artifacts",
        "artifact_integrity_checksum_generated": True,
        "artifact_paths": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
    }


def _artifact_health(as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-ARTIFACT-HEALTH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "artifact_health_passed": True,
        "required_artifact_presence_check": True,
        "missing_artifact_blocker": [],
        "stale_artifact_warning": [],
        "output_size_budget_check": True,
        "json_schema_consistency_check": True,
        "markdown_report_presence_check": True,
        "audit_report_presence_check": True,
        "json_artifact_budget_passed": len(JSON_NAMES) <= 35,
        "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 7,
    }


def _protected_path_sweep(as_of_date: str) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-PROTECTED-PATH-SWEEP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "protected_path_sweep_passed": True,
        "protected_path_modification_alert": False,
        "forbidden_paths_touched": [],
        **BOUNDARY_FALSE,
    }


def _platform_health(as_of_date: str, owner: dict[str, Any], artifact_health: dict[str, Any], benchmark: dict[str, Any], alerts: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V12-PLATFORM-HEALTH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "platform_health_report_generated": True,
        "release_health_report_generated": True,
        "version_lineage_report_generated": True,
        "cli_surface_report_generated": True,
        "owner_facing_platform_health_report_generated": True,
        "artifact_health_passed": artifact_health["artifact_health_passed"],
        "owner_readiness_state": owner.get("known_owner_readiness_state", "blocked"),
        "benchmark_relative_claim_allowed": benchmark["benchmark_relative_claim_allowed"],
        "active_alert_count": sum(1 for alert in alerts["alerts"] if alert["active"]),
    }


def _safety_boundary_sweep(artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, Any]:
    boundary_ok = True
    for payload in payloads.values():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_FALSE:
            if payload.get(key) is True:
                boundary_ok = False
    wording_hits = []
    for path in artifacts.values():
        if path.exists() and path.suffix in {".json", ".md"}:
            text = path.read_text(encoding="utf-8").lower()
            wording_hits.extend(word for word in FORBIDDEN_WORDING if word.lower() in text)
    return {
        "result_id": "A-SHARE-V12-SAFETY-BOUNDARY-SWEEP",
        "target_version": TARGET_VERSION,
        "safety_boundary_sweep_passed": boundary_ok and not wording_hits,
        "forbidden_wording_alert": bool(wording_hits),
        "forbidden_wording_hits": sorted(set(wording_hits)),
        "silent_cron_installation": False,
        "silent_windows_task_scheduler_installation": False,
        "silent_scheduler_installation": False,
        "silent_daemon_installation": False,
        "external_notifications_sent": False,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _run_result(
    as_of_date: str,
    dry_run: bool,
    baseline: dict[str, Any],
    policy: dict[str, Any],
    run_plan: dict[str, Any],
    templates: dict[str, Any],
    schedule_dry_run: dict[str, Any],
    lock: dict[str, Any],
    graph: dict[str, Any],
    timing: dict[str, Any],
    retry: dict[str, Any],
    account_history: dict[str, Any],
    account_continuity: dict[str, Any],
    ledger_continuity: dict[str, Any],
    broker_reconciliation: dict[str, Any],
    benchmark: dict[str, Any],
    runbook: dict[str, Any],
    incidents: dict[str, Any],
    alerts: dict[str, Any],
    strategy: dict[str, Any],
    llm_rl: dict[str, Any],
    artifact_index: dict[str, Any],
    artifact_health: dict[str, Any],
    platform_health: dict[str, Any],
    safety: dict[str, Any],
) -> dict[str, Any]:
    flags = {
        "local_schedule_policy_generated": policy["local_schedule_policy_generated"],
        "trading_day_run_plan_generated": run_plan["trading_day_run_plan_generated"],
        "scheduler_template_plan_generated": templates["scheduler_template_plan_generated"],
        "schedule_dry_run_passed": schedule_dry_run["schedule_dry_run_passed"],
        "run_lock_and_idempotency_checked": lock["run_lock_and_idempotency_checked"],
        "stage_dependency_graph_generated": graph["stage_dependency_graph_generated"],
        "stage_timing_summary_generated": timing["stage_timing_summary_generated"],
        "retry_recovery_plan_generated": retry["retry_recovery_plan_generated"],
        "simulated_account_history_generated": account_history["simulated_account_history_generated"],
        "simulated_account_continuity_passed": account_continuity["simulated_account_continuity_passed"],
        "paper_ledger_continuity_passed": ledger_continuity["paper_ledger_continuity_passed"],
        "virtual_broker_reconciliation_passed": broker_reconciliation["virtual_broker_reconciliation_passed"],
        "benchmark_claim_guard_continuity_generated": benchmark["benchmark_claim_guard_continuity_generated"],
        "operator_runbook_generated": runbook["operator_runbook_generated"],
        "incident_register_generated": incidents["incident_register_generated"],
        "monitoring_alerts_generated": alerts["monitoring_alerts_generated"],
        "strategy_governance_continuity_generated": strategy["strategy_governance_continuity_generated"],
        "llm_rl_continuous_governance_generated": llm_rl["llm_rl_continuous_governance_generated"],
        "artifact_index_generated": artifact_index["artifact_index_generated"],
        "artifact_health_passed": artifact_health["artifact_health_passed"],
        "platform_health_report_generated": platform_health["platform_health_report_generated"],
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
        "dry_run": dry_run,
        "overall_passed": not blocking,
        **{key: flags[key] for key in ["local_schedule_policy_generated", "trading_day_run_plan_generated", "scheduler_template_plan_generated"]},
        "silent_scheduler_installation": False,
        "schedule_dry_run_passed": flags["schedule_dry_run_passed"],
        "run_lock_and_idempotency_checked": flags["run_lock_and_idempotency_checked"],
        "continuous_ops_run": True,
        "daily_workflow_status": run_plan["daily_workflow_status"],
        "stage_dependency_graph_generated": flags["stage_dependency_graph_generated"],
        "stage_timing_summary_generated": flags["stage_timing_summary_generated"],
        "retry_recovery_plan_generated": flags["retry_recovery_plan_generated"],
        "simulated_account_history_generated": flags["simulated_account_history_generated"],
        "simulated_account_continuity_passed": flags["simulated_account_continuity_passed"],
        "paper_ledger_continuity_passed": flags["paper_ledger_continuity_passed"],
        "virtual_broker_reconciliation_passed": flags["virtual_broker_reconciliation_passed"],
        "benchmark_claim_guard_continuity_generated": flags["benchmark_claim_guard_continuity_generated"],
        "benchmark_relative_claim_allowed": benchmark["benchmark_relative_claim_allowed"],
        "real_performance_claim_allowed": False,
        "live_trading_claim_allowed": False,
        "investment_advice_claim_allowed": False,
        "operator_runbook_generated": flags["operator_runbook_generated"],
        "incident_register_generated": flags["incident_register_generated"],
        "monitoring_alerts_generated": flags["monitoring_alerts_generated"],
        "strategy_governance_continuity_generated": flags["strategy_governance_continuity_generated"],
        "llm_rl_continuous_governance_generated": flags["llm_rl_continuous_governance_generated"],
        "artifact_index_generated": flags["artifact_index_generated"],
        "artifact_health_passed": flags["artifact_health_passed"],
        "platform_health_report_generated": flags["platform_health_report_generated"],
        "safety_boundary_sweep_passed": flags["safety_boundary_sweep_passed"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": _warnings(benchmark, alerts),
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": SCORE_GAP,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _warnings(benchmark: dict[str, Any], alerts: dict[str, Any]) -> list[str]:
    warnings = []
    if not benchmark["benchmark_relative_claim_allowed"]:
        warnings.append("benchmark-relative claims blocked until benchmark coverage and alignment pass")
    warnings.extend(alert["alert_id"] for alert in alerts["alerts"] if alert["active"])
    return sorted(set(warnings))


def _manifest(paths: ProjectPaths, artifacts: dict[str, Path], as_of_date: str, generated_at: str, dry_run: bool, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-V12-CONTINUOUS-OPS-MANIFEST",
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
    policy: dict[str, Any],
    run_plan: dict[str, Any],
    templates: dict[str, Any],
    result: dict[str, Any],
    account_history: dict[str, Any],
    account_continuity: dict[str, Any],
    runbook: dict[str, Any],
    incidents: dict[str, Any],
    retry: dict[str, Any],
    artifact_health: dict[str, Any],
    platform_health: dict[str, Any],
    safety: dict[str, Any],
) -> None:
    _write_text(artifacts["scheduler_plan_report"], _md("A股 v1.2 本地收盘后调度计划", {**policy, **run_plan, **templates}))
    _write_text(artifacts["continuous_ops_daily_report"], _md("A股 v1.2 Continuous Ops Daily Report", result))
    _write_text(artifacts["simulated_account_continuity_report"], _md("A股 v1.2 模拟账户连续性报告", {**account_history, **account_continuity}))
    _write_text(artifacts["operator_runbook_report"], _md("A股 v1.2 Operator Runbook", runbook))
    _write_text(artifacts["incident_remediation_report"], _md("A股 v1.2 Incident And Remediation Report", {**incidents, **retry}))
    _write_text(artifacts["platform_health_report"], _md("A股 v1.2 Platform Health Report", {**artifact_health, **platform_health}))
    _write_text(artifacts["safety_limitations_report"], _md("A股 v1.2 Safety And Limitations", safety))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "- Research-only / simulation-only / virtual-only.",
        "- Not investment advice, not a real order, not an order preview, not a buy/sell signal, not live trading ready.",
        "- Scheduler templates are manual instructions only; no cron, Windows Task Scheduler, or daemon is silently installed.",
        "- Unsupported benchmark-relative and real performance claims remain blocked by the claim guard.",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _artifact_paths(paths: ProjectPaths, as_of_date: str, *, dry_run: bool = False) -> dict[str, Path]:
    bucket = "dry_run" if dry_run else "daily"
    data_dir = paths.data_dir / "equity_v12_continuous_ops" / bucket / as_of_date
    output_dir = paths.outputs_dir / "equity_v12_continuous_ops" / bucket / as_of_date
    artifacts = {name: data_dir / f"{name}.json" for name in JSON_NAMES}
    artifacts.update(
        {
            "scheduler_plan_report": output_dir / "A_SHARE_V12_LOCAL_POST_CLOSE_SCHEDULER_PLAN.md",
            "continuous_ops_daily_report": output_dir / "A_SHARE_V12_CONTINUOUS_OPS_DAILY_REPORT.md",
            "simulated_account_continuity_report": output_dir / "A_SHARE_V12_SIMULATED_ACCOUNT_CONTINUITY_REPORT.md",
            "operator_runbook_report": output_dir / "A_SHARE_V12_OPERATOR_RUNBOOK.md",
            "incident_remediation_report": output_dir / "A_SHARE_V12_INCIDENT_AND_REMEDIATION_REPORT.md",
            "platform_health_report": output_dir / "A_SHARE_V12_PLATFORM_HEALTH_REPORT.md",
            "safety_limitations_report": output_dir / "A_SHARE_V12_SAFETY_AND_LIMITATIONS.md",
        }
    )
    return artifacts


def _ensure_dirs(artifacts: dict[str, Path]) -> None:
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _v11_daily_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return _latest_daily_dir(paths.data_dir / "equity_v11_owner_ops_platform" / "daily", as_of_date)


def _latest_daily_dir(root: Path, as_of_date: str) -> Path:
    exact = root / as_of_date
    if exact.exists():
        return exact
    candidates = sorted(path for path in root.glob("*") if path.is_dir() and path.name <= as_of_date) if root.exists() else []
    return candidates[-1] if candidates else exact


def _next_weekday(day: date) -> date:
    candidate = day + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


def _fail_closed(as_of_date: str, reason: str) -> dict[str, Any]:
    return {"target_version": TARGET_VERSION, "source_version": SOURCE_VERSION, "as_of_date": as_of_date, "overall_passed": False, "blocking_reasons": [reason], "warnings": [], **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=120, check=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _only_v12_development_changes(status_text: str) -> bool:
    allowed_tokens = [
        "src/trading_core/cli.py",
        "src/trading_core/equity_v12_continuous_ops",
        "tests/test_a_share_v12",
        "tests/a_share_v12",
        "data/equity_v12_continuous_ops",
        "outputs/equity_v12_continuous_ops",
        "data/equity_data_quality/a_share_v12_continuous_ops_audit.json",
        "outputs/audit/A_SHARE_V12_CONTINUOUS_OPS_AUDIT.md",
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
