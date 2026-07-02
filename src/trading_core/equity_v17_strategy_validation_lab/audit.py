"""Audit v1.7.0 strategy validation lab artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v17_strategy_validation_lab.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v17_strategy_validation_lab(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v17_strategy_validation_lab" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v17_strategy_validation_lab" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v17_strategy_validation_lab_result"]
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
        "audit_id": "A-SHARE-V17-STRATEGY-VALIDATION-LAB-AUDIT",
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
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "platform_health_report": "passed" if not blocking else "blocked",
        "full_regression_closeout": {"full_pytest_run": result.get("full_pytest_run") is True},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v17_strategy_validation_lab_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V17_STRATEGY_VALIDATION_LAB_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "pit_sample_split_result_generated",
        "factor_validation_result_generated",
        "candidate_ranking_validation_result_generated",
        "strategy_backtest_validation_result_generated",
        "walkforward_oos_evaluation_result_generated",
        "robustness_sensitivity_validation_result_generated",
        "statistical_false_discovery_result_generated",
        "strategy_admission_decision_result_generated",
        "experiment_validation_registry_generated",
        "llm_rl_validation_result_generated",
        "owner_strategy_validation_dashboard_generated",
        "pit_aware_validation_used",
        "event_driven_replay_used",
        "a_share_market_rules_used",
        "virtual_broker_rules_used",
        "transaction_cost_adjustment_used",
        "slippage_adjustment_used",
        "lookahead_bias_guard_passed",
        "survivorship_bias_warning_recorded",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
        "full_pytest_run",
    ]


def _required_false_fields() -> list[str]:
    return [
        "factor_results_fabricated",
        "ic_results_fabricated",
        "backtest_results_fabricated",
        "oos_results_fabricated",
        "statistical_significance_fabricated",
        "future_data_usage_detected",
        "strategy_real_trading_active_state_present",
        "strategy_admission_generates_real_trade",
        "candidate_validation_generates_buy_sell_signal",
        "llm_rl_validation_generates_trade_instruction",
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
        "# A-Share v1.7 Strategy Validation Lab Audit",
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
