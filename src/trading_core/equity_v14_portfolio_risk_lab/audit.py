"""Audit v1.4.0 portfolio risk, capacity, allocation, and rebalance simulation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v14_portfolio_risk_lab.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v14_portfolio_risk_lab(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v14_portfolio_risk_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v14_portfolio_risk_lab" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v14_portfolio_risk_lab_result"]
    safety = payloads["v14_safety_boundary_sweep"]
    protected = payloads["v14_protected_path_sweep"]
    integrity = payloads["v14_artifact_integrity_sweep"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 28:
        blocking.append("json_artifact_budget_exceeded")
    if len(MARKDOWN_NAMES) > 8:
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
    for key in _required_false_fields():
        if result.get(key) is not False:
            blocking.append(f"required_false_not_false:{key}")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    if safety.get("safety_boundary_sweep_passed") is not True:
        blocking.append("safety_boundary_sweep_failed")
    if protected.get("protected_path_sweep_passed") is not True:
        blocking.append("protected_path_sweep_failed")
    if integrity.get("artifact_integrity_sweep_passed") is not True:
        blocking.append("artifact_integrity_sweep_failed")
    audit = {
        "audit_id": "A-SHARE-V14-PORTFOLIO-RISK-LAB-AUDIT",
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
            "json_artifact_budget_passed": len(JSON_NAMES) <= 28,
            "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 8,
        },
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "owner_readiness": {
            "owner_readiness_state": result.get("owner_readiness_state"),
            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
            "source_readiness_score": result.get("source_readiness_score"),
            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),
            "score_gap": result.get("score_gap"),
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v14_portfolio_risk_lab_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V14_PORTFOLIO_RISK_LAB_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "portfolio_risk_scorecard_generated",
        "exposure_concentration_result_generated",
        "correlation_diversification_result_generated",
        "capacity_liquidity_result_generated",
        "turnover_cost_slippage_result_generated",
        "simulated_allocation_result_generated",
        "simulated_rebalance_plan_generated",
        "multi_strategy_portfolio_result_generated",
        "stress_scenario_result_generated",
        "risk_limit_guardrail_result_generated",
        "owner_portfolio_risk_dashboard_generated",
        "portfolio_risk_monitoring_alerts_generated",
        "capacity_estimate_is_simulated",
        "liquidity_estimate_is_simulated",
        "allocation_is_simulated",
        "rebalance_plan_is_simulated",
        "stress_result_is_simulated",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "real_portfolio_advice_generated",
        "real_allocation_instruction_generated",
        "real_rebalance_instruction_generated",
        "real_trade_instruction_generated",
        "strategy_real_trading_active_state_present",
        "broker_connected",
        "real_account_data_read",
        "real_orders_placed",
        "real_order_preview_generated",
        "buy_sell_signals_generated",
        "owner_readiness_gate_rerun",
        "controlled_gate_reevaluation_run",
        "new_gate_score_generated",
        "new_gate_decision_generated",
        "old_run_daily_called",
        "day2_executed",
        "live_trading_ready",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.4 Portfolio Risk Lab Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        "",
        "## Artifact Checks",
        *[f"- {key}: {value}" for key, value in audit["artifact_checks"].items()],
        "",
        "## Quality Checks",
        *[f"- {key}: {value}" for key, value in audit["quality_checks"].items()],
        "",
        "## Forbidden Checks",
        *[f"- {key}: {value}" for key, value in audit["forbidden_checks"].items()],
        "",
        "## Owner Readiness",
        *[f"- {key}: {value}" for key, value in audit["owner_readiness"].items()],
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
