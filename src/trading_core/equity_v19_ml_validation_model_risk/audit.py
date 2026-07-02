"""Audit v1.9.0 ML validation, model risk, and research portfolio artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v19_ml_validation_model_risk.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v19_ml_validation_model_risk(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v19_ml_validation_model_risk" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v19_ml_validation_model_risk" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v19_ml_validation_model_risk_result"]
    blocking: list[str] = []

    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
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

    audit = {
        "audit_id": "A-SHARE-V19-ML-VALIDATION-MODEL-RISK-AUDIT",
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
            "json_budget_passed": len(JSON_NAMES) <= 30,
            "markdown_budget_passed": len(MARKDOWN_NAMES) <= 9,
        },
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "platform_health_report": "passed" if not blocking else "blocked",
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "full_regression_closeout": {"full_pytest_run": result.get("full_pytest_run") is True},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v19_ml_validation_model_risk_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V19_ML_VALIDATION_MODEL_RISK_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "model_validation_scorecard_generated",
        "model_risk_review_result_generated",
        "model_performance_validation_result_generated",
        "prediction_quality_validation_result_generated",
        "model_monitoring_drift_result_generated",
        "model_robustness_validation_result_generated",
        "model_overfitting_false_discovery_result_generated",
        "model_explainability_result_generated",
        "model_decision_workflow_result_generated",
        "research_portfolio_model_integration_result_generated",
        "candidate_strategy_model_integration_result_generated",
        "owner_model_risk_dashboard_generated",
        "model_validation_used_pit_dataset",
        "model_validation_used_feature_store",
        "model_validation_used_label_store",
        "model_validation_used_prediction_registry",
        "model_validation_used_oos",
        "model_validation_used_walkforward",
        "model_leakage_guard_passed",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
        "full_pytest_run",
    ]


def _required_false_fields() -> list[str]:
    return [
        "model_validation_results_fabricated",
        "model_risk_results_fabricated",
        "prediction_quality_results_fabricated",
        "model_monitoring_results_fabricated",
        "model_explainability_fabricated",
        "future_data_usage_detected",
        "model_status_real_trading_active_present",
        "predictions_are_trade_signals",
        "research_portfolio_is_real_portfolio",
        "research_portfolio_generates_real_allocation",
        "model_integration_generates_real_trade",
        "owner_readiness_gate_rerun",
        "controlled_gate_reevaluation_run",
        "new_gate_score_generated",
        "new_gate_decision_generated",
        "broker_connected",
        "real_account_data_read",
        "real_orders_placed",
        "real_order_preview_generated",
        "buy_sell_signals_generated",
        "old_run_daily_called",
        "day2_executed",
        "live_trading_ready",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.9 ML Validation Model Risk Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- release_readiness_decision: {audit['release_readiness_decision']}",
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
