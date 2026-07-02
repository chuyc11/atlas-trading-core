"""Audit v1.6.0 point-in-time backtest and market-rule hardening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v16_pit_backtest_market_rules.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v16_pit_backtest_market_rules(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v16_pit_backtest_market_rules" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v16_pit_backtest_market_rules" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v16_pit_backtest_market_rules_result"]
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
        "audit_id": "A-SHARE-V16-PIT-BACKTEST-MARKET-RULES-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {"json_count": len(JSON_NAMES), "markdown_count": len(MARKDOWN_NAMES), "audit_markdown_count": 1, "all_json_present": all(bool(payload) for payload in payloads.values()), "all_markdown_present": all(path.exists() for path in markdowns)},
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v16_pit_backtest_market_rules_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V16_PIT_BACKTEST_MARKET_RULES_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "point_in_time_data_registry_generated",
        "dataset_feature_label_version_registry_generated",
        "leakage_lookahead_survivorship_guard_generated",
        "event_driven_replay_result_generated",
        "a_share_market_rule_registry_generated",
        "virtual_broker_rule_hardening_result_generated",
        "transaction_cost_slippage_result_generated",
        "benchmark_index_source_result_generated",
        "paper_ledger_replay_consistency_result_generated",
        "backtest_trust_scorecard_generated",
        "owner_trust_dashboard_generated",
        "lookahead_bias_guard_passed",
        "a_share_market_rules_covered",
        "t_plus_one_rule_checked",
        "price_limit_rule_checked",
        "suspension_rule_checked",
        "lot_size_rule_checked",
        "virtual_broker_rule_audit_passed",
        "paper_ledger_replay_passed",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "point_in_time_visibility_fabricated",
        "backtest_results_fabricated",
        "simulated_fills_fabricated",
        "benchmark_index_data_fabricated",
        "transaction_cost_fabricated",
        "future_data_usage_detected",
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
    lines = ["# A-Share v1.6 PIT Backtest Market Rules Audit", "", f"- overall_passed: {audit['overall_passed']}", f"- blocking_reasons: {audit['blocking_reasons']}", f"- warnings_count: {len(audit['warnings'])}", "", "## Artifact Checks", *[f"- {key}: {value}" for key, value in audit["artifact_checks"].items()], "", "## Quality Checks", *[f"- {key}: {value}" for key, value in audit["quality_checks"].items()], "", "## Forbidden Checks", *[f"- {key}: {value}" for key, value in audit["forbidden_checks"].items()], ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
