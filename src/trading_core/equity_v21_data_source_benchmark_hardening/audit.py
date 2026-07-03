"""Audit v2.1.0 A-share data source and benchmark hardening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v21_data_source_benchmark_hardening.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v21_data_source_benchmark_hardening(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["v21_data_source_benchmark_hardening_result"]
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
    if result.get("owner_readiness_state") != "blocked":
        blocking.append("owner_readiness_state_not_blocked")
    if result.get("source_readiness_score") != 54 or result.get("minimum_owner_readiness_score") != 75 or result.get("score_gap") != 21:
        blocking.append("owner_readiness_score_mismatch")

    audit = {
        "audit_id": "A-SHARE-V21-DATA-SOURCE-BENCHMARK-HARDENING-AUDIT",
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
            "json_budget_passed": len(JSON_NAMES) <= 26,
            "markdown_budget_passed": len(MARKDOWN_NAMES) <= 8,
            "audit_markdown_budget_passed": True,
        },
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "owner_readiness_state": result.get("owner_readiness_state"),
        "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
        "live_trading_ready": result.get("live_trading_ready"),
        "platform_health_report": "passed" if not blocking else "blocked",
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v21_data_source_benchmark_hardening_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V21_DATA_SOURCE_BENCHMARK_HARDENING_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "v20_baseline_verified",
        "public_data_source_adapter_registry_generated",
        "benchmark_source_depth_result_generated",
        "index_constituent_source_result_generated",
        "industry_sector_source_result_generated",
        "corporate_action_adjusted_price_result_generated",
        "suspension_delisting_st_status_result_generated",
        "financial_statement_pit_result_generated",
        "data_quality_sla_result_generated",
        "benchmark_claim_guard_rehardening_result_generated",
        "owner_data_reliability_dashboard_generated",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "broker_adapter_added",
        "private_account_adapter_added",
        "fabricated_data_source",
        "fabricated_benchmark_data",
        "fabricated_index_constituents",
        "fabricated_industry_classification",
        "fabricated_corporate_action",
        "fabricated_suspension_delisting_st_status",
        "fabricated_financial_pit_visibility",
        "fabricated_benchmark_relative_metrics",
        "benchmark_relative_claim_allowed",
        "real_performance_claim_allowed",
        "live_trading_claim_allowed",
        "investment_advice_claim_allowed",
        "data_quality_score_is_owner_readiness_score",
        "data_quality_pass_means_live_trading_ready",
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
        "# A-Share v2.1 Data Source Benchmark Hardening Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- owner_readiness_state: {audit['owner_readiness_state']}",
        f"- owner_operationally_acceptable: {audit['owner_operationally_acceptable']}",
        f"- live_trading_ready: {audit['live_trading_ready']}",
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
