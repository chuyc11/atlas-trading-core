"""Audit v0.7.12 A-share attribution diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_attribution.attribution_config import (
    ATTRIBUTION_BOUNDARY,
    BENCHMARK_IDS,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_POSITIVE_WORDING,
    PORTFOLIO_IDS,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    attribution_artifact_paths,
)
from trading_core.equity_attribution.attribution_report import render_attribution_audit
from trading_core.equity_attribution.attribution_source_trace import forbidden_source_path_hits, update_trace_with_audit_artifacts
from trading_core.equity_data_quality.common import sha256_file, write_json, write_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = [
    "attribution_config",
    "attribution_data_availability",
    "holding_contribution_snapshot",
    "industry_contribution_snapshot",
    "candidate_source_contribution_snapshot",
    "score_bucket_contribution_snapshot",
    "risk_bucket_contribution_snapshot",
    "liquidity_bucket_contribution_snapshot",
    "benchmark_relative_attribution_snapshot",
    "portfolio_concentration_diagnostics",
    "risk_diagnostics_snapshot",
    "liquidity_diagnostics_snapshot",
    "industry_diagnostics_snapshot",
    "factor_exposure_snapshot",
    "attribution_limitations",
    "attribution_source_trace",
    "attribution_manifest",
    "attribution_boundary_check",
    "attribution_summary",
]


def audit_a_share_performance_attribution(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = attribution_artifact_paths(paths, as_of_date)
    payloads = {key: _load_dict(artifacts[key]) for key in REQUIRED_ARTIFACTS}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads, as_of_date=as_of_date)
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    availability = payloads["attribution_data_availability"]
    risk_bucket = payloads["risk_bucket_contribution_snapshot"]
    concentration = payloads["portfolio_concentration_diagnostics"]
    boundary = payloads["attribution_boundary_check"]
    audit = {
        "audit_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(availability),
        "availability_checks": {
            "structural_diagnostics_available": availability.get("structural_diagnostics_available") is True,
            "realized_performance_attribution_available": availability.get("realized_performance_attribution_available") is False,
            "limited_history": availability.get("limited_history") is True,
            "limited_history_correctly_flagged": availability.get("insufficient_history") is True and availability.get("sufficient_history") is False,
        },
        "reconciliation_checks": {
            "holding_weights_reconcile": checks["holding_weights_reconcile"],
            "industry_weights_reconcile": checks["industry_weights_reconcile"],
            "score_bucket_weights_reconcile": checks["score_bucket_weights_reconcile"],
            "risk_bucket_weights_reconcile": checks["risk_bucket_weights_reconcile"],
            "liquidity_bucket_weights_reconcile": checks["liquidity_bucket_weights_reconcile"],
        },
        "risk_checks": {
            "risk_downgraded_symbols_in_portfolio": risk_bucket.get("risk_downgraded_symbols_in_portfolio", []),
            "excluded_universe_exposure": _total_field(concentration, "excluded_universe_exposure"),
            "concentration_diagnostics_present": bool(concentration.get("portfolios")),
            "liquidity_diagnostics_present": bool(payloads["liquidity_diagnostics_snapshot"].get("portfolios")),
            "industry_diagnostics_present": bool(payloads["industry_diagnostics_snapshot"].get("portfolios")),
        },
        "checks": checks,
        "boundary": {key: boundary.get(key) for key in ATTRIBUTION_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    result = write_report(artifacts["attribution_audit_json"], audit, artifacts["attribution_audit_report"], render_attribution_audit(audit))
    trace = payloads.get("attribution_source_trace", {})
    if trace:
        updated = update_trace_with_audit_artifacts(
            paths=paths,
            trace=trace,
            audit_json=artifacts["attribution_audit_json"],
            audit_report=artifacts["attribution_audit_report"],
        )
        write_json(artifacts["attribution_source_trace"], updated)
    return result


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any], as_of_date: str) -> dict[str, bool]:
    config = payloads["attribution_config"]
    availability = payloads["attribution_data_availability"]
    holding = payloads["holding_contribution_snapshot"]
    industry = payloads["industry_contribution_snapshot"]
    score = payloads["score_bucket_contribution_snapshot"]
    risk = payloads["risk_bucket_contribution_snapshot"]
    liquidity = payloads["liquidity_bucket_contribution_snapshot"]
    benchmark = payloads["benchmark_relative_attribution_snapshot"]
    concentration = payloads["portfolio_concentration_diagnostics"]
    source_trace = payloads["attribution_source_trace"]
    manifest = payloads["attribution_manifest"]
    boundary = payloads["attribution_boundary_check"]
    summary = payloads["attribution_summary"]
    checks = {
        "attribution_config_exists": artifacts["attribution_config"].exists(),
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values()),
        "all_required_portfolio_ids_present": _portfolio_ids_present(holding, industry, score, risk, liquidity, concentration),
        "all_required_benchmark_ids_present": set(benchmark.get("benchmark_ids", [])) == set(BENCHMARK_IDS),
        "limited_history_correctly_flagged": availability.get("limited_history") is True and availability.get("sufficient_history") is False,
        "realized_performance_attribution_not_fabricated": availability.get("realized_performance_attribution_available") is False and summary.get("realized_performance_attribution_available") is False,
        "structural_diagnostics_available": availability.get("structural_diagnostics_available") is True,
        "risk_downgraded_symbols_in_portfolio_empty": risk.get("risk_downgraded_symbols_in_portfolio") == [],
        "excluded_universe_exposure_zero": abs(_total_field(concentration, "excluded_universe_exposure")) < 1e-9,
        "holding_weights_reconcile": _holding_weights_reconcile(holding),
        "industry_weights_reconcile": _group_weights_reconcile(holding, industry.get("portfolios", {})),
        "score_bucket_weights_reconcile": _group_weights_reconcile(holding, score.get("portfolios", {})),
        "risk_bucket_weights_reconcile": _group_weights_reconcile(holding, risk.get("portfolios", {})),
        "liquidity_bucket_weights_reconcile": _group_weights_reconcile(holding, liquidity.get("portfolios", {})),
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "no_future_data_used": _no_future_dates(payloads, as_of_date),
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in ATTRIBUTION_BOUNDARY.items()),
        "boundary_overall_passed": boundary.get("overall_passed") is True,
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not _forbidden_wording_hits(artifacts),
        "attribution_used_as_trade_signal_false": boundary.get("attribution_used_as_trade_signal") is False,
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-PERFORMANCE-ATTRIBUTION-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-PERFORMANCE-ATTRIBUTION-SUMMARY",
        "mode_valid": config.get("mode") in config.get("allowed_modes", []),
    }
    return checks


def _portfolio_ids_present(*payloads: dict[str, Any]) -> bool:
    expected = {PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS}
    for payload in payloads:
        if "records" in payload:
            present = {row.get("portfolio_id") for row in payload.get("records", [])}
        else:
            present = set(payload.get("portfolios", {}))
        if present != expected:
            return False
    return True


def _holding_weights_reconcile(holding: dict[str, Any]) -> bool:
    for portfolio_id, expected in holding.get("portfolio_weight_sums", {}).items():
        actual = sum(float(row.get("actual_weight") or 0.0) for row in holding.get("records", []) if row.get("portfolio_id") == portfolio_id)
        if abs(actual - float(expected)) > 1e-9 or abs(actual - 1.0) > 1e-6:
            return False
    return True


def _group_weights_reconcile(holding: dict[str, Any], grouped: dict[str, list[dict[str, Any]]]) -> bool:
    expected = holding.get("portfolio_weight_sums", {})
    for portfolio_id, rows in grouped.items():
        if abs(sum(float(row.get("weight") or 0.0) for row in rows) - float(expected.get(portfolio_id, 0.0))) > 1e-6:
            return False
    return set(grouped) == set(expected)


def _total_field(payload: dict[str, Any], field: str) -> float:
    return float(sum(float(row.get(field) or 0.0) for row in payload.get("portfolios", {}).values()))


def _source_hashes_match(paths: ProjectPaths, source_trace: dict[str, Any]) -> bool:
    for group in ["source_artifacts", "output_artifacts"]:
        records = source_trace.get(group, {})
        iterable = records.values() if isinstance(records, dict) else records
        for row in iterable:
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _no_future_dates(payloads: dict[str, Any], as_of_date: str) -> bool:
    text = json.dumps(payloads, ensure_ascii=False)
    for token in ["day_002", "day_003"]:
        if token in text:
            return False
    return as_of_date in text


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for path in artifacts.values():
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for phrase in FORBIDDEN_POSITIVE_WORDING:
                if phrase.lower() in text:
                    hits.append(f"{path}:{phrase}")
    return hits


def _warnings(availability: dict[str, Any]) -> list[str]:
    warnings = []
    if availability.get("limited_history"):
        warnings.append("portfolio observation history is below the minimum required window")
    return warnings


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
