"""Audit v0.9.8 A-share platform completion artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE, DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v09_platform(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v09_platform" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v09_platform" / "daily" / as_of_date
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v09_platform_completion_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V09_PLATFORM_COMPLETION_AUDIT.md"
    names = [
        "v09_platform_request",
        "v09_daily_workflow_result",
        "v09_simulated_account_state",
        "v09_virtual_broker_execution_report",
        "v09_paper_ledger_snapshot",
        "v09_benchmark_attribution_result",
        "v09_owner_dashboard_result",
        "v09_monitoring_alerts_result",
        "v09_evidence_auto_accumulation_result",
        "v09_experiment_registry",
        "v09_strategy_registry",
        "v09_llm_research_proposal_register",
        "v09_automated_experiment_result",
        "v09_rl_simulated_strategy_lab_result",
        "v09_shadow_canary_promotion_result",
        "v09_platform_boundary_check",
        "v09_platform_manifest",
    ]
    payloads = {name: read_json(data_dir / f"{name}.json") for name in names}
    markdowns = [
        output_dir / "A_SHARE_V09_DAILY_RESEARCH_PLATFORM_REPORT.md",
        output_dir / "A_SHARE_V09_SIMULATED_ACCOUNT_AND_VIRTUAL_BROKER_REPORT.md",
        output_dir / "A_SHARE_V09_BENCHMARK_ATTRIBUTION_REPORT.md",
        output_dir / "A_SHARE_V09_AUTONOMOUS_RESEARCH_AND_SIMULATION_REPORT.md",
        output_dir / "A_SHARE_V09_OWNER_COMMAND_CENTER.md",
    ]
    workflow = payloads["v09_daily_workflow_result"]
    boundary = payloads["v09_platform_boundary_check"]
    blocking = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    for name, payload in payloads.items():
        if not isinstance(payload, dict):
            continue
        for key in BOUNDARY_TRUE:
            if payload.get(key) is not True and name not in {"v09_platform_manifest"}:
                blocking.append(f"{name}:{key}_not_true")
        for key in BOUNDARY_FALSE:
            if payload.get(key, False) is True:
                blocking.append(f"{name}:{key}_true")
    if workflow.get("owner_readiness_gate_rerun") or workflow.get("controlled_gate_reevaluation_run"):
        blocking.append("owner_gate_or_controlled_reevaluation_executed")
    if not boundary.get("protected_paths_untouched"):
        blocking.append("protected_paths_touched")
    if payloads["v09_strategy_registry"].get("forbidden_statuses") and any(strategy.get("status") == "real_trading_active" for strategy in payloads["v09_strategy_registry"].get("strategies", [])):
        blocking.append("real_trading_active_strategy_status_found")
    if payloads["v09_llm_research_proposal_register"].get("external_llm_api_called"):
        blocking.append("external_llm_api_called")
    if payloads["v09_shadow_canary_promotion_result"].get("real_trading_promotion"):
        blocking.append("real_trading_promotion_found")
    blocking.extend(workflow.get("blocking_reasons", []))
    blocking.extend(boundary.get("blocking_reasons", []))
    warnings = list(dict.fromkeys([*workflow.get("warnings", []), *payloads["v09_benchmark_attribution_result"].get("warnings", []), *boundary.get("warnings", [])]))
    audit = {
        "audit_id": "A-SHARE-V09-PLATFORM-COMPLETION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "artifact_checks": {"json_count": len(names), "markdown_count": len(markdowns), "all_json_present": all(bool(payload) for payload in payloads.values()), "all_markdown_present": all(path.exists() for path in markdowns)},
        "boundary": {key: boundary.get(key) for key in [*BOUNDARY_TRUE.keys(), *BOUNDARY_FALSE.keys(), "protected_paths_untouched"]},
        "workflow": {
            "run_status": workflow.get("run_status"),
            "public_data_refresh_status": workflow.get("public_data_refresh_status"),
            "research_pipeline_status": workflow.get("research_pipeline_status"),
            "simulated_account_updated": workflow.get("simulated_account_updated"),
            "virtual_broker_execution_run": workflow.get("virtual_broker_execution_run"),
            "paper_ledger_updated": workflow.get("paper_ledger_updated"),
        },
        "test_policy": {"targeted_pytest_required": True, "full_pytest_run": False},
    }
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v0.9 Platform Completion Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
        "## Test Policy",
        "- full_pytest_run: false",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
