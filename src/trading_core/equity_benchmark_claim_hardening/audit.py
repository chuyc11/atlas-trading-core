"""Audit v1.0.1 A-share benchmark and performance claim hardening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_benchmark_claim_hardening.builder import (
    DEFAULT_AS_OF_DATE,
    INDEX_BENCHMARK_IDS,
    JSON_NAMES,
    MARKDOWN_NAMES,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_benchmark_claim_hardening(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_benchmark_claim_hardening" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_benchmark_claim_hardening" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    result = payloads["benchmark_claim_hardening_result"]
    registry = payloads["benchmark_source_registry"]
    csi = payloads["csi_benchmark_attribution_result"]
    guard = payloads["performance_claim_guard_result"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 12:
        blocking.append("json_artifact_budget_exceeded")
    if len(MARKDOWN_NAMES) > 2:
        blocking.append("markdown_artifact_budget_exceeded")
    if result.get("target_version") != TARGET_VERSION:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
    if not result.get("benchmark_source_registry_generated"):
        blocking.append("benchmark_source_registry_missing")
    if not result.get("benchmark_coverage_matrix_generated"):
        blocking.append("benchmark_coverage_matrix_missing")
    if not result.get("cash_benchmark_generated"):
        blocking.append("cash_benchmark_missing")
    if not guard or not result.get("performance_claim_guard_generated"):
        blocking.append("performance_claim_guard_missing")
    if not _all_registry_ids_present(registry):
        blocking.append("benchmark_registry_ids_missing")
    if _fabrication_flag_true(result, csi):
        blocking.append("fabrication_flag_true")
    if guard.get("real_performance_claim_allowed") is not False:
        blocking.append("real_performance_claim_not_blocked")
    if guard.get("live_trading_claim_allowed") is not False:
        blocking.append("live_trading_claim_not_blocked")
    if guard.get("investment_advice_claim_allowed") is not False:
        blocking.append("investment_advice_claim_not_blocked")
    if _unverified_csi_allowed(registry, guard):
        blocking.append("unverified_benchmark_relative_claim_allowed")
    if result.get("simulated_performance_claim_allowed_with_disclaimer") is not True:
        blocking.append("simulation_claim_disclaimer_policy_missing")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    audit = {
        "audit_id": "A-SHARE-BENCHMARK-CLAIM-HARDENING-AUDIT",
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
            "json_artifact_budget_passed": len(JSON_NAMES) <= 12,
            "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 2,
        },
        "claim_guard": {
            "benchmark_relative_claim_allowed": guard.get("benchmark_relative_claim_allowed"),
            "real_performance_claim_allowed": guard.get("real_performance_claim_allowed"),
            "live_trading_claim_allowed": guard.get("live_trading_claim_allowed"),
            "investment_advice_claim_allowed": guard.get("investment_advice_claim_allowed"),
            "simulated_performance_claim_allowed_with_disclaimer": guard.get("simulated_performance_claim_allowed_with_disclaimer"),
        },
        "benchmark_status": {
            "csi300_benchmark_status": result.get("csi300_benchmark_status"),
            "csi500_benchmark_status": result.get("csi500_benchmark_status"),
            "csi1000_benchmark_status": result.get("csi1000_benchmark_status"),
            "equal_weight_universe_benchmark_status": result.get("equal_weight_universe_benchmark_status"),
        },
        "owner_readiness": {
            "owner_readiness_state": result.get("owner_readiness_state"),
            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
            "source_readiness_score": result.get("source_readiness_score"),
            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),
            "score_gap": result.get("score_gap"),
        },
        "boundary": {key: result.get(key) for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_benchmark_claim_hardening_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_BENCHMARK_CLAIM_HARDENING_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _all_registry_ids_present(registry: dict[str, Any]) -> bool:
    ids = {row.get("benchmark_id") for row in registry.get("records", [])}
    return {"CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_TRADABLE_UNIVERSE"}.issubset(ids)


def _fabrication_flag_true(result: dict[str, Any], csi: dict[str, Any]) -> bool:
    keys = ["fabricated_benchmark_data", "fabricated_excess_return", "fabricated_tracking_error", "fabricated_relative_drawdown"]
    if any(result.get(key) is not False for key in keys):
        return True
    if any(csi.get(key) is not False for key in keys):
        return True
    for row in csi.get("benchmarks", []):
        if any(row.get(key) is not False for key in keys[1:]):
            return True
        if row.get("benchmark_relative_metrics_generated") is False:
            metric_values = [row.get("excess_return"), row.get("tracking_error"), row.get("relative_drawdown")]
            if any(value is not None for value in metric_values):
                return True
    return False


def _unverified_csi_allowed(registry: dict[str, Any], guard: dict[str, Any]) -> bool:
    csi_rows = [row for row in registry.get("records", []) if row.get("benchmark_id") in INDEX_BENCHMARK_IDS]
    all_verified = bool(csi_rows) and all(row.get("usable_for_simulated_relative_metrics") for row in csi_rows)
    return not all_verified and guard.get("benchmark_relative_claim_allowed") is True


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share Benchmark Claim Hardening Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        "",
        "## Claim Guard",
        *[f"- {key}: {value}" for key, value in audit["claim_guard"].items()],
        "",
        "## Benchmark Status",
        *[f"- {key}: {value}" for key, value in audit["benchmark_status"].items()],
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
