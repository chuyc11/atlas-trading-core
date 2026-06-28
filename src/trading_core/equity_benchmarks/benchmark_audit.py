"""Audit v0.7.10 A-share benchmark comparison artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_benchmarks.benchmark_config import (
    BENCHMARK_BOUNDARY,
    BENCHMARK_IDS,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_POSITIVE_WORDING,
    INDEX_BENCHMARK_IDS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    benchmark_artifact_paths,
)
from trading_core.equity_benchmarks.benchmark_report import render_benchmark_audit
from trading_core.equity_benchmarks.benchmark_source_trace import forbidden_source_path_hits, update_trace_with_audit_artifacts
from trading_core.equity_data_quality.common import json_safe, write_json, write_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_benchmark_comparison(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_placeholder_benchmarks: bool | None = None,
    fail_on_placeholder_benchmarks: bool = True,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = benchmark_artifact_paths(paths, as_of_date)
    config = _load_dict(artifacts["benchmark_config"])
    availability_payload = _load_dict(artifacts["benchmark_data_availability"])
    comparison = _load_dict(artifacts["portfolio_benchmark_comparison"])
    relative = _load_dict(artifacts["relative_performance_snapshot"])
    source_trace = _load_dict(artifacts["benchmark_source_trace"])
    boundary = _load_dict(artifacts["benchmark_boundary_check"])
    manifest = _load_dict(artifacts["benchmark_manifest"])
    placeholder_allowed = bool(config.get("allow_placeholder_benchmarks")) if allow_placeholder_benchmarks is None else allow_placeholder_benchmarks
    checks = _checks(
        artifacts=artifacts,
        config=config,
        availability=availability_payload,
        comparison=comparison,
        relative=relative,
        source_trace=source_trace,
        boundary=boundary,
        manifest=manifest,
        placeholder_allowed=placeholder_allowed,
        fail_on_placeholder_benchmarks=fail_on_placeholder_benchmarks,
        as_of_date=as_of_date,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    availability_checks = {
        row.get("benchmark_id"): row.get("status")
        for row in availability_payload.get("benchmarks", [])
    }
    payload = {
        "audit_id": "A-SHARE-BENCHMARK-COMPARISON-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(availability_payload, relative),
        "benchmark_availability_checks": {benchmark_id: availability_checks.get(benchmark_id) for benchmark_id in BENCHMARK_IDS},
        "comparison_checks": {
            "long_comparisons_present": _portfolio_present(comparison, "long_virtual_portfolio"),
            "mid_comparisons_present": _portfolio_present(comparison, "mid_virtual_portfolio"),
            "short_comparisons_present": _portfolio_present(comparison, "short_virtual_portfolio"),
            "limited_history_correctly_flagged": bool(comparison.get("limited_history_correctly_flagged")),
            "performance_not_fabricated": bool(comparison.get("performance_not_fabricated")),
        },
        "checks": checks,
        "boundary": {key: boundary.get(key) for key in BENCHMARK_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    result = write_report(
        artifacts["benchmark_audit_json"],
        json_safe(payload),
        artifacts["benchmark_audit_report"],
        render_benchmark_audit(payload),
    )
    if source_trace:
        updated = update_trace_with_audit_artifacts(
            paths=paths,
            trace=source_trace,
            audit_json=artifacts["benchmark_audit_json"],
            audit_report=artifacts["benchmark_audit_report"],
        )
        write_json(artifacts["benchmark_source_trace"], updated)
    return result


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    config = kwargs["config"]
    availability = kwargs["availability"]
    comparison = kwargs["comparison"]
    relative = kwargs["relative"]
    source_trace = kwargs["source_trace"]
    boundary = kwargs["boundary"]
    manifest = kwargs["manifest"]
    statuses = {row.get("benchmark_id"): row for row in availability.get("benchmarks", [])}
    required_artifacts = [
        "benchmark_config",
        "benchmark_data_availability",
        "benchmark_universe_snapshot",
        "benchmark_price_snapshot",
        "benchmark_return_snapshot",
        "benchmark_nav_snapshot",
        "portfolio_benchmark_comparison",
        "relative_performance_snapshot",
        "benchmark_exclusion_report",
        "benchmark_source_trace",
        "benchmark_manifest",
        "benchmark_boundary_check",
        "benchmark_summary",
    ]
    checks = {
        "benchmark_config_exists": artifacts["benchmark_config"].exists(),
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in required_artifacts),
        "target_version_matches": config.get("target_version") == TARGET_VERSION and manifest.get("target_version") == TARGET_VERSION,
        "all_required_benchmark_ids_present": set(statuses) == set(BENCHMARK_IDS),
        "cash_available": statuses.get("CASH", {}).get("status") == "available",
        "strict_equal_weight_available": statuses.get("EQUAL_WEIGHT_STRICT_TRADABLE", {}).get("status") == "available",
        "candidate_equal_weight_available": statuses.get("EQUAL_WEIGHT_CANDIDATE_POOL", {}).get("status") == "available",
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", [])),
        "portfolio_history_limitation_correctly_flagged": bool(relative.get("limited_history_flagged")) and bool(comparison.get("limited_history_correctly_flagged")),
        "benchmark_metrics_do_not_fabricate_portfolio_history": bool(comparison.get("performance_not_fabricated")) and bool(relative.get("performance_not_yet_observed")),
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in BENCHMARK_BOUNDARY.items()),
        "boundary_overall_passed": boundary.get("overall_passed") is True,
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not _forbidden_wording_hits(artifacts),
        "no_future_leakage": _no_future_dates(artifacts, kwargs["as_of_date"]),
    }
    for benchmark_id in INDEX_BENCHMARK_IDS:
        row = statuses.get(benchmark_id, {})
        if kwargs["placeholder_allowed"]:
            checks[f"{benchmark_id}_available_or_placeholder_allowed"] = row.get("status") in {"available", "placeholder_allowed"}
        else:
            checks[f"{benchmark_id}_available"] = row.get("status") == "available" and row.get("is_placeholder") is False
        if kwargs["fail_on_placeholder_benchmarks"]:
            checks[f"{benchmark_id}_not_placeholder"] = row.get("is_placeholder") is False
    return checks


def _portfolio_present(comparison: dict[str, Any], portfolio_id: str) -> bool:
    rows = [row for row in comparison.get("comparisons", []) if row.get("portfolio_id") == portfolio_id]
    return len(rows) == len(BENCHMARK_IDS)


def _no_future_dates(artifacts: dict[str, Path], as_of_date: str) -> bool:
    for key in ["benchmark_price_snapshot", "benchmark_return_snapshot", "benchmark_nav_snapshot"]:
        payload = _load_dict(artifacts[key])
        for row in payload.get("records", []):
            if str(row.get("date", "")) > as_of_date:
                return False
    return True


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for key, path in artifacts.items():
        if key.endswith("_report") or path.suffix in {".md", ".json"}:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_POSITIVE_WORDING:
                if phrase.lower() in text:
                    hits.append(f"{path.name}:{phrase}")
    return sorted(set(hits))


def _warnings(availability: dict[str, Any], relative: dict[str, Any]) -> list[str]:
    warnings = []
    for row in availability.get("benchmarks", []):
        if row.get("status") != "available":
            warnings.append(f"{row.get('benchmark_id')} status={row.get('status')}")
        if row.get("trading_days_available", 0) < 20:
            warnings.append(f"{row.get('benchmark_id')} limited benchmark history")
    if relative.get("limited_history_flagged"):
        warnings.append("portfolio relative metrics limited by first-day initialization")
    return sorted(set(warnings))


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}
