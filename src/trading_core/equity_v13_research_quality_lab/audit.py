"""Audit v1.3.0 research quality evaluation and strategy lab artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v13_research_quality_lab.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v13_research_quality_lab(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v13_research_quality_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v13_research_quality_lab" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v13_research_quality_lab_result"]
    safety = payloads["v13_safety_boundary_sweep"]
    protected = payloads["v13_protected_path_sweep"]
    integrity = payloads["v13_artifact_integrity_sweep"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 30:
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
        "audit_id": "A-SHARE-V13-RESEARCH-QUALITY-LAB-AUDIT",
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
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v13_research_quality_lab_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V13_RESEARCH_QUALITY_LAB_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "research_quality_scorecard_generated",
        "factor_quality_diagnostics_generated",
        "candidate_quality_diagnostics_generated",
        "strategy_lab_registry_expanded",
        "strategy_card_register_generated",
        "backtest_walkforward_oos_result_generated",
        "robustness_sensitivity_stress_result_generated",
        "overfitting_false_discovery_result_generated",
        "llm_proposal_quality_result_generated",
        "rl_policy_quality_result_generated",
        "shadow_canary_quality_gate_result_generated",
        "strategy_lifecycle_decision_result_generated",
        "research_quality_monitoring_alerts_generated",
        "owner_research_quality_dashboard_generated",
        "data_leakage_guard_passed",
        "lookahead_bias_check_passed",
        "survivorship_bias_warning_recorded",
        "overfitting_risk_classified",
        "robustness_score_generated",
        "strategy_promotion_hard_gate_generated",
        "strategy_rejection_hard_gate_generated",
        "strategy_rollback_gate_generated",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "llm_proposals_are_trade_instructions",
        "rl_actions_are_real_account_actions",
        "rl_actions_are_real_orders",
        "strategy_real_trading_active_state_present",
        "real_performance_claim_allowed",
        "live_trading_claim_allowed",
        "investment_advice_claim_allowed",
        "external_notifications_sent",
        "silent_scheduler_installation",
        "daemon_installed",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.3 Research Quality Lab Audit",
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
