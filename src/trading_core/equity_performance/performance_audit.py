"""Audit v0.7.11 A-share multi-day performance artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, sha256_file, write_json, write_report
from trading_core.equity_performance.performance_config import (
    BENCHMARK_IDS,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_POSITIVE_WORDING,
    PERFORMANCE_BOUNDARY,
    PORTFOLIO_IDS,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    performance_artifact_paths,
)
from trading_core.equity_performance.performance_report import render_performance_audit
from trading_core.equity_performance.performance_source_trace import forbidden_source_path_hits, update_trace_with_audit_artifacts
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_multi_day_performance(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = performance_artifact_paths(paths, as_of_date)
    config = _load_dict(artifacts["performance_config"])
    availability = _load_dict(artifacts["performance_data_availability"])
    nav = _load_dict(artifacts["portfolio_nav_series"])
    returns = _load_dict(artifacts["portfolio_return_series"])
    drawdown = _load_dict(artifacts["portfolio_drawdown_series"])
    relative = _load_dict(artifacts["portfolio_relative_performance_series"])
    benchmark_relative = _load_dict(artifacts["portfolio_benchmark_relative_series"])
    holdings = _load_dict(artifacts["holding_mark_to_market_series"])
    metrics = _load_dict(artifacts["performance_metric_snapshot"])
    limitations = _load_dict(artifacts["performance_limitations"])
    append_log = _load_dict(artifacts["performance_append_log"])
    source_trace = _load_dict(artifacts["performance_source_trace"])
    manifest = _load_dict(artifacts["performance_manifest"])
    boundary = _load_dict(artifacts["performance_boundary_check"])
    summary = _load_dict(artifacts["performance_summary"])

    checks = _checks(
        artifacts=artifacts,
        config=config,
        availability=availability,
        nav=nav,
        returns=returns,
        drawdown=drawdown,
        relative=relative,
        benchmark_relative=benchmark_relative,
        holdings=holdings,
        metrics=metrics,
        limitations=limitations,
        append_log=append_log,
        source_trace=source_trace,
        manifest=manifest,
        boundary=boundary,
        summary=summary,
        as_of_date=as_of_date,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    observation_counts = availability.get("portfolio_observation_counts", {})
    observation_checks = {
        "minimum_required_observations": availability.get("minimum_required_observations"),
        "sufficient_history": bool(availability.get("sufficient_history")),
        "insufficient_history_correctly_flagged": bool(availability.get("insufficient_history")) and not bool(availability.get("sufficient_history")),
    }
    for key in PORTFOLIO_KEYS:
        observation_checks[PORTFOLIO_IDS[key]] = observation_counts.get(PORTFOLIO_IDS[key], 0)
    payload = {
        "audit_id": "A-SHARE-MULTI-DAY-PERFORMANCE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(availability, limitations),
        "observation_checks": observation_checks,
        "series_checks": {
            "nav_series_present": bool(nav.get("records")),
            "return_series_present": bool(returns.get("records")),
            "drawdown_series_present": bool(drawdown.get("records")),
            "relative_performance_series_present": bool(relative.get("records")),
            "benchmark_relative_series_present": bool(benchmark_relative.get("records")),
            "holding_mark_to_market_series_present": bool(holdings.get("records")),
            "math_checks_passed": checks.get("daily_return_math_correct") and checks.get("cumulative_return_math_correct") and checks.get("drawdown_math_correct"),
            "performance_not_fabricated": checks.get("performance_not_fabricated"),
        },
        "checks": checks,
        "boundary": {key: boundary.get(key) for key in PERFORMANCE_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    result = write_report(
        artifacts["performance_audit_json"],
        json_safe(payload),
        artifacts["performance_audit_report"],
        render_performance_audit(payload),
    )
    if source_trace:
        updated = update_trace_with_audit_artifacts(
            paths=paths,
            trace=source_trace,
            audit_json=artifacts["performance_audit_json"],
            audit_report=artifacts["performance_audit_report"],
        )
        write_json(artifacts["performance_source_trace"], updated)
    return result


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    config = kwargs["config"]
    availability = kwargs["availability"]
    nav = kwargs["nav"]
    returns = kwargs["returns"]
    drawdown = kwargs["drawdown"]
    relative = kwargs["relative"]
    benchmark_relative = kwargs["benchmark_relative"]
    holdings = kwargs["holdings"]
    metrics = kwargs["metrics"]
    limitations = kwargs["limitations"]
    append_log = kwargs["append_log"]
    source_trace = kwargs["source_trace"]
    manifest = kwargs["manifest"]
    boundary = kwargs["boundary"]
    summary = kwargs["summary"]
    required_artifacts = [
        "performance_config",
        "performance_data_availability",
        "portfolio_nav_series",
        "portfolio_return_series",
        "portfolio_drawdown_series",
        "portfolio_relative_performance_series",
        "portfolio_benchmark_relative_series",
        "holding_mark_to_market_series",
        "performance_metric_snapshot",
        "performance_limitations",
        "performance_append_log",
        "performance_source_trace",
        "performance_manifest",
        "performance_boundary_check",
        "performance_summary",
    ]
    checks = {
        "performance_config_exists": artifacts["performance_config"].exists(),
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in required_artifacts),
        "target_version_matches": all(
            payload.get("target_version") == TARGET_VERSION
            for payload in [config, availability, nav, returns, drawdown, relative, benchmark_relative, holdings, metrics, limitations, append_log, source_trace, manifest, boundary, summary]
        ),
        "all_required_portfolio_ids_present": set(nav.get("observation_counts", {})) == {PORTFOLIO_IDS[key] for key in PORTFOLIO_KEYS},
        "all_required_benchmark_ids_present": set(benchmark_relative.get("benchmark_ids", [])) == set(BENCHMARK_IDS),
        "observation_counts_correct": _observation_counts_correct(nav, availability),
        "first_day_initialization_correctly_flagged": _first_day_flags_correct(nav, returns, limitations, availability),
        "insufficient_history_correctly_flagged": _insufficient_history_correct(availability, metrics, limitations),
        "performance_not_yet_observed_correctly_flagged": bool(summary.get("performance_not_yet_observed")) and bool(limitations.get("performance_not_yet_observed")),
        "daily_return_math_correct": _daily_return_math_correct(nav, returns),
        "cumulative_return_math_correct": _cumulative_return_math_correct(nav, returns),
        "drawdown_math_correct": _drawdown_math_correct(nav, drawdown),
        "benchmark_relative_metrics_do_not_fabricate_history": bool(relative.get("benchmark_metrics_do_not_fabricate_portfolio_history")) and bool(benchmark_relative.get("performance_not_fabricated")),
        "holding_mark_to_market_math_correct": _holding_math_correct(holdings),
        "holding_mark_to_market_has_no_forbidden_fields": not holdings.get("forbidden_fields_present"),
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(kwargs["artifacts"], source_trace),
        "no_future_data_used": _no_future_dates([nav, returns, drawdown, relative, benchmark_relative, holdings], kwargs["as_of_date"]),
        "performance_not_fabricated": boundary.get("historical_performance_fabricated") is False and bool(benchmark_relative.get("performance_not_fabricated")),
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in PERFORMANCE_BOUNDARY.items()),
        "boundary_overall_passed": boundary.get("overall_passed") is True,
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not _forbidden_wording_hits(artifacts),
        "append_log_append_only": append_log.get("append_only") is True and append_log.get("prior_dates_rewritten") is False,
        "historical_reconstruction_labeled_if_used": not append_log.get("historical_reconstruction_used") or append_log.get("historical_reconstruction_labeled_separately") is True,
    }
    return checks


def _observation_counts_correct(nav: dict[str, Any], availability: dict[str, Any]) -> bool:
    counts: dict[str, int] = {}
    for row in nav.get("records", []):
        counts[str(row.get("portfolio_id"))] = counts.get(str(row.get("portfolio_id")), 0) + 1
    return counts == availability.get("portfolio_observation_counts")


def _first_day_flags_correct(nav: dict[str, Any], returns: dict[str, Any], limitations: dict[str, Any], availability: dict[str, Any]) -> bool:
    one_day = int(availability.get("portfolio_observation_count") or 0) == 1
    if not one_day:
        return True
    return bool(nav.get("first_day_initialization")) and bool(limitations.get("first_day_initialization")) and all(row.get("first_day_initialization") for row in returns.get("records", []))


def _insufficient_history_correct(availability: dict[str, Any], metrics: dict[str, Any], limitations: dict[str, Any]) -> bool:
    if availability.get("portfolio_observation_count", 0) >= availability.get("minimum_required_observations", 0):
        return bool(availability.get("sufficient_history"))
    metric_statuses = [
        portfolio.get("metric_status")
        for portfolio in metrics.get("portfolios", {}).values()
    ]
    return bool(availability.get("insufficient_history")) and bool(limitations.get("insufficient_history")) and all(status == "insufficient_history" for status in metric_statuses)


def _daily_return_math_correct(nav: dict[str, Any], returns: dict[str, Any]) -> bool:
    nav_by_portfolio = _by(nav.get("records", []), "portfolio_id")
    returns_by_key = {(row.get("portfolio_id"), row.get("as_of_date")): row for row in returns.get("records", [])}
    for portfolio_id, rows in nav_by_portfolio.items():
        previous_nav: float | None = None
        for idx, row in enumerate(sorted(rows, key=lambda item: item["as_of_date"])):
            expected = 0.0 if idx == 0 or previous_nav in (None, 0.0) else float(row["nav"]) / previous_nav - 1.0
            actual = returns_by_key.get((portfolio_id, row["as_of_date"]), {}).get("daily_return")
            if actual is None or abs(float(actual) - expected) > 1e-9:
                return False
            previous_nav = float(row["nav"])
    return bool(returns.get("records"))


def _cumulative_return_math_correct(nav: dict[str, Any], returns: dict[str, Any]) -> bool:
    nav_by_portfolio = _by(nav.get("records", []), "portfolio_id")
    returns_by_key = {(row.get("portfolio_id"), row.get("as_of_date")): row for row in returns.get("records", [])}
    for portfolio_id, rows in nav_by_portfolio.items():
        sorted_rows = sorted(rows, key=lambda item: item["as_of_date"])
        start_nav = float(sorted_rows[0]["nav"]) if sorted_rows else 0.0
        for row in sorted_rows:
            expected = 0.0 if not start_nav else float(row["nav"]) / start_nav - 1.0
            actual = returns_by_key.get((portfolio_id, row["as_of_date"]), {}).get("cumulative_return")
            if actual is None or abs(float(actual) - expected) > 1e-9:
                return False
    return bool(returns.get("records"))


def _drawdown_math_correct(nav: dict[str, Any], drawdown: dict[str, Any]) -> bool:
    nav_by_portfolio = _by(nav.get("records", []), "portfolio_id")
    drawdown_by_key = {(row.get("portfolio_id"), row.get("as_of_date")): row for row in drawdown.get("records", [])}
    for portfolio_id, rows in nav_by_portfolio.items():
        peak = 0.0
        max_drawdown = 0.0
        for row in sorted(rows, key=lambda item: item["as_of_date"]):
            nav_value = float(row["nav"])
            peak = max(peak, nav_value)
            expected_drawdown = 0.0 if peak == 0.0 else nav_value / peak - 1.0
            max_drawdown = min(max_drawdown, expected_drawdown)
            actual = drawdown_by_key.get((portfolio_id, row["as_of_date"]), {})
            if abs(float(actual.get("drawdown") or 0.0) - expected_drawdown) > 1e-9:
                return False
            if abs(float(actual.get("max_drawdown") or 0.0) - max_drawdown) > 1e-9:
                return False
    return bool(drawdown.get("records"))


def _holding_math_correct(holdings: dict[str, Any]) -> bool:
    for row in holdings.get("records", []):
        expected = float(row.get("virtual_shares") or 0.0) * float(row.get("mark_price") or 0.0)
        actual = float(row.get("position_value") or 0.0)
        if abs(expected - actual) > max(1e-4, abs(actual) * 1e-8):
            return False
    return bool(holdings.get("records"))


def _source_hashes_match(artifacts: dict[str, Path], source_trace: dict[str, Any]) -> bool:
    project_root = artifacts["performance_config"].parents[4]
    for row in source_trace.get("source_artifacts", []):
        path = Path(row.get("path") or "")
        full_path = path if path.is_absolute() else project_root / path
        if row.get("exists") and row.get("sha256") and full_path.exists() and sha256_file(full_path) != row.get("sha256"):
            return False
    return True


def _no_future_dates(payloads: list[dict[str, Any]], as_of_date: str) -> bool:
    for payload in payloads:
        for row in payload.get("records", []):
            day = row.get("as_of_date") or row.get("date")
            if day and str(day) > as_of_date:
                return False
    return True


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for _key, path in artifacts.items():
        if not path.exists() or path.suffix not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return sorted(set(hits))


def _warnings(availability: dict[str, Any], limitations: dict[str, Any]) -> list[str]:
    warnings = []
    if availability.get("insufficient_history") or limitations.get("insufficient_history"):
        warnings.append("portfolio observation history is below the minimum required window")
    return sorted(set(warnings))


def _by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        grouped.setdefault(str(row.get(key)), []).append(row)
    return grouped


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}
