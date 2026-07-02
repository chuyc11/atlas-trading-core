"""Audit v1.2.0 local autonomous ops scheduling and continuous simulation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v12_continuous_ops.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v12_continuous_ops(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v12_continuous_ops" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v12_continuous_ops" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v12_continuous_ops_run_result"]
    policy = payloads["v12_local_schedule_policy"]
    benchmark = payloads["v12_benchmark_claim_guard_continuity_result"]
    safety = payloads["v12_safety_boundary_sweep"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 35:
        blocking.append("json_artifact_budget_exceeded")
    if len(MARKDOWN_NAMES) > 7:
        blocking.append("markdown_artifact_budget_exceeded")
    if result.get("target_version") != TARGET_VERSION:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
    for key in _required_true_fields():
        if result.get(key) is not True:
            blocking.append(f"required_true_missing:{key}")
    if result.get("silent_scheduler_installation") is not False:
        blocking.append("silent_scheduler_installation_not_false")
    if policy.get("silent_cron_installation") is not False or policy.get("silent_windows_task_scheduler_installation") is not False:
        blocking.append("silent_os_scheduler_installation_not_false")
    for key in ["real_performance_claim_allowed", "live_trading_claim_allowed", "investment_advice_claim_allowed"]:
        if result.get(key) is not False or benchmark.get(key) is not False:
            blocking.append(f"claim_not_blocked:{key}")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    if safety.get("safety_boundary_sweep_passed") is not True:
        blocking.append("safety_boundary_sweep_failed")
    audit = {
        "audit_id": "A-SHARE-V12-CONTINUOUS-OPS-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {
            "json_count": len(JSON_NAMES),
            "markdown_count": len(MARKDOWN_NAMES),
            "audit_markdown_count": 1,
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
            "json_artifact_budget_passed": len(JSON_NAMES) <= 35,
            "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 7,
        },
        "schedule": {
            "local_schedule_policy_generated": result.get("local_schedule_policy_generated"),
            "trading_day_run_plan_generated": result.get("trading_day_run_plan_generated"),
            "scheduler_template_plan_generated": result.get("scheduler_template_plan_generated"),
            "silent_scheduler_installation": result.get("silent_scheduler_installation"),
            "schedule_dry_run_passed": result.get("schedule_dry_run_passed"),
            "run_lock_and_idempotency_checked": result.get("run_lock_and_idempotency_checked"),
        },
        "claim_guard": {
            "benchmark_relative_claim_allowed": result.get("benchmark_relative_claim_allowed"),
            "real_performance_claim_allowed": result.get("real_performance_claim_allowed"),
            "live_trading_claim_allowed": result.get("live_trading_claim_allowed"),
            "investment_advice_claim_allowed": result.get("investment_advice_claim_allowed"),
        },
        "owner_readiness": {
            "owner_readiness_state": result.get("owner_readiness_state"),
            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
            "source_readiness_score": result.get("source_readiness_score"),
            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),
            "score_gap": result.get("score_gap"),
        },
        "major_area_checks": {key: result.get(key) for key in _required_true_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v12_continuous_ops_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V12_CONTINUOUS_OPS_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "local_schedule_policy_generated",
        "trading_day_run_plan_generated",
        "scheduler_template_plan_generated",
        "schedule_dry_run_passed",
        "run_lock_and_idempotency_checked",
        "continuous_ops_run",
        "stage_dependency_graph_generated",
        "stage_timing_summary_generated",
        "retry_recovery_plan_generated",
        "simulated_account_history_generated",
        "simulated_account_continuity_passed",
        "paper_ledger_continuity_passed",
        "virtual_broker_reconciliation_passed",
        "benchmark_claim_guard_continuity_generated",
        "operator_runbook_generated",
        "incident_register_generated",
        "monitoring_alerts_generated",
        "strategy_governance_continuity_generated",
        "llm_rl_continuous_governance_generated",
        "artifact_index_generated",
        "artifact_health_passed",
        "platform_health_report_generated",
        "safety_boundary_sweep_passed",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.2 Continuous Ops Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        "",
        "## Schedule",
        *[f"- {key}: {value}" for key, value in audit["schedule"].items()],
        "",
        "## Claim Guard",
        *[f"- {key}: {value}" for key, value in audit["claim_guard"].items()],
        "",
        "## Owner Readiness",
        *[f"- {key}: {value}" for key, value in audit["owner_readiness"].items()],
        "",
        "## Major Areas",
        *[f"- {key}: {value}" for key, value in audit["major_area_checks"].items()],
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
