"""Audit v1.5.0 market regime and adaptive research simulation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v15_market_regime_lab.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v15_market_regime_lab(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v15_market_regime_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v15_market_regime_lab" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v15_market_regime_lab_result"]
    safety = payloads["v15_safety_boundary_sweep"]
    protected = payloads["v15_protected_path_sweep"]
    integrity = payloads["v15_artifact_integrity_sweep"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 32:
        blocking.append("json_artifact_budget_exceeded")
    if len(MARKDOWN_NAMES) > 9:
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
        "audit_id": "A-SHARE-V15-MARKET-REGIME-LAB-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {"json_count": len(JSON_NAMES), "markdown_count": len(MARKDOWN_NAMES), "audit_markdown_count": 1, "all_json_present": all(bool(payload) for payload in payloads.values()), "all_markdown_present": all(path.exists() for path in markdowns), "json_artifact_budget_passed": len(JSON_NAMES) <= 32, "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 9},
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "owner_readiness": {"owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "source_readiness_score": result.get("source_readiness_score"), "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"), "score_gap": result.get("score_gap")},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v15_market_regime_lab_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V15_MARKET_REGIME_LAB_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "market_regime_classification_generated",
        "trend_diagnostics_generated",
        "volatility_diagnostics_generated",
        "liquidity_regime_result_generated",
        "market_breadth_diagnostics_generated",
        "risk_appetite_diagnostics_generated",
        "regime_factor_quality_overlay_generated",
        "regime_candidate_quality_overlay_generated",
        "regime_strategy_quality_result_generated",
        "adaptive_research_queue_generated",
        "llm_regime_governance_generated",
        "rl_regime_governance_generated",
        "regime_portfolio_overlay_generated",
        "regime_monitoring_alerts_generated",
        "owner_regime_dashboard_generated",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "market_regime_fabricated",
        "volatility_fabricated",
        "breadth_fabricated",
        "liquidity_fabricated",
        "adaptive_queue_generates_trade_instruction",
        "regime_overlay_generates_real_allocation",
        "regime_overlay_generates_real_rebalance",
        "regime_overlay_generates_buy_sell_signal",
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
        "# A-Share v1.5 Market Regime Lab Audit",
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
