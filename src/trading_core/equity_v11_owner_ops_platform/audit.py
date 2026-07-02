"""Audit v1.1.0 A-share owner ops autonomous simulation platform artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v11_owner_ops_platform.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v11_owner_ops_platform(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v11_owner_ops_platform" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v11_owner_ops_platform" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v11_owner_ops_platform_result"]
    safety = payloads["v11_safety_boundary_sweep"]
    integrity = payloads["v11_artifact_integrity_sweep"]
    command = payloads["v11_owner_command_center_result"]
    benchmark = payloads["v11_benchmark_claim_guard_integration_result"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 30:
        blocking.append("json_artifact_budget_exceeded")
    if len(MARKDOWN_NAMES) > 6:
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
    if result.get("real_performance_claim_allowed") is not False:
        blocking.append("real_performance_claim_not_blocked")
    if result.get("live_trading_claim_allowed") is not False:
        blocking.append("live_trading_claim_not_blocked")
    if result.get("investment_advice_claim_allowed") is not False:
        blocking.append("investment_advice_claim_not_blocked")
    if benchmark.get("unsupported_excess_return_blocked") is not True:
        blocking.append("unsupported_excess_return_not_blocked")
    if benchmark.get("unsupported_tracking_error_blocked") is not True:
        blocking.append("unsupported_tracking_error_not_blocked")
    if benchmark.get("unsupported_relative_drawdown_blocked") is not True:
        blocking.append("unsupported_relative_drawdown_not_blocked")
    if command.get("performance_claim_guard_status", {}).get("real_performance_claim_allowed") is not False:
        blocking.append("owner_command_center_claim_guard_missing")
    if integrity.get("artifact_integrity_sweep_passed") is not True:
        blocking.append("artifact_integrity_sweep_failed")
    if safety.get("safety_boundary_sweep_passed") is not True:
        blocking.append("safety_boundary_sweep_failed")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    audit = {
        "audit_id": "A-SHARE-V11-OWNER-OPS-PLATFORM-AUDIT",
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
            "json_artifact_budget_passed": len(JSON_NAMES) <= 30,
            "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 6,
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
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v11_owner_ops_platform_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V11_OWNER_OPS_PLATFORM_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "owner_command_center_generated",
        "daily_workflow_integrated",
        "benchmark_claim_guard_integrated",
        "simulated_account_reconciled",
        "virtual_broker_lifecycle_checked",
        "paper_ledger_invariant_passed",
        "experiment_registry_expanded",
        "strategy_registry_expanded",
        "llm_proposal_governance_generated",
        "rl_simulated_lab_governance_generated",
        "shadow_canary_lifecycle_generated",
        "promotion_rejection_rollback_workflow_generated",
        "monitoring_alerts_generated",
        "remediation_checklist_generated",
        "workflow_history_registered",
        "evidence_auto_accumulation_updated",
        "artifact_integrity_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.1 Owner Ops Platform Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
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
