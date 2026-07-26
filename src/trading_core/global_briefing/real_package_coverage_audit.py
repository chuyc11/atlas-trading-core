"""Coverage and point-in-time audit for normalized real packages."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from typing import Any

from trading_core.global_briefing.replay_bundle_builder import _load_price_dates
from trading_core.global_briefing.signal_schema import (
    DEFAULT_DECISION_TIME,
    calendar_dates,
    normalize_datetime,
    parse_datetime,
    read_signal_package,
    resolve_project_path,
    validate_signal_row,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


def audit_global_briefing_package_coverage(
    signals_path: str,
    *,
    start_date: str,
    end_date: str,
    prices_path: str | None = None,
    calendar_path: str | None = None,
    min_coverage: float = 0.80,
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    audit_id, created_at = timestamp_id("GB-PACKAGE-COVERAGE")
    package = read_signal_package(signals_path, paths)
    blocking = list(package.blocking_reasons)
    warnings = list(package.warnings)
    valid_rows: list[dict[str, Any]] = []
    future_rows = 0
    timezone_ambiguous = 0
    generated_after_as_of = 0

    for index, row in enumerate(package.rows, 1):
        clean, row_blocking, row_warnings = validate_signal_row(
            row,
            index,
            start_date=start_date,
            end_date=end_date,
            decision_time=DEFAULT_DECISION_TIME,
            check_point_in_time=True,
        )
        warnings.extend(row_warnings)
        timezone_ambiguous += len([item for item in row_warnings if "timezone ambiguity" in item])
        if any("future signal leakage" in item for item in row_blocking):
            future_rows += 1
        if row_blocking:
            blocking.extend(row_blocking)
        elif clean is not None:
            valid_rows.append(clean)
        generated_dt, _ = parse_datetime(row.get("generated_at"))
        as_of = row.get("as_of_date")
        if generated_dt is not None and isinstance(as_of, str):
            if normalize_datetime(generated_dt).date() > date.fromisoformat(as_of):
                generated_after_as_of += 1

    expected_days = _expected_days(prices_path, calendar_path, start_date, end_date, paths)
    observed_counter = Counter(row["as_of_date"] for row in valid_rows)
    observed_days = sorted(observed_counter)
    missing_days = [day for day in expected_days if day not in observed_counter]
    duplicate_days = sorted(day for day, count in observed_counter.items() if count > 1)
    if duplicate_days:
        warnings.append(f"duplicate signal days: {duplicate_days}")
    coverage_ratio = (len(observed_days) / len(expected_days)) if expected_days else 0.0
    coverage_passed = coverage_ratio >= min_coverage
    if not coverage_passed:
        warnings.append(f"coverage ratio {coverage_ratio:.4f} below min_coverage {min_coverage:.4f}")
        if strict:
            blocking.append("coverage below min_coverage in strict mode")
    regions = sorted({str(row.get("region")) for row in valid_rows if row.get("region")})
    sources = sorted({str(row.get("source")) for row in valid_rows if row.get("source")})
    versions = sorted({str(row.get("version")) for row in valid_rows if row.get("version")})
    if len(regions) > 1 or len(sources) > 1 or len(versions) > 1:
        warnings.append("region/source/version inconsistency detected")
    if future_rows:
        blocking.append("future signal leakage detected")

    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "signals": str(resolve_project_path(signals_path, paths)),
        "start_date": start_date,
        "end_date": end_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "coverage": {
            "expected_days": len(expected_days),
            "observed_signal_days": len(observed_days),
            "missing_signal_days": missing_days,
            "duplicate_signal_days": duplicate_days,
            "coverage_ratio": coverage_ratio,
            "min_coverage": min_coverage,
            "passed": coverage_passed,
        },
        "point_in_time": {
            "future_signal_rows": future_rows,
            "generated_at_after_as_of_date_rows": generated_after_as_of,
            "timezone_ambiguous_rows": timezone_ambiguous,
            "passed": future_rows == 0,
        },
        "consistency": {
            "regions": regions,
            "sources": sources,
            "versions": versions,
        },
        "boundary": {
            "coverage_audit_only": True,
            "replay_started": False,
            "forward_dry_run_started": False,
            "main_ledger_written": False,
            "write_main_ledger": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_package_coverage_audit.json"
    report_path = paths.outputs_dir / "audit" / "GLOBAL_BRIEFING_PACKAGE_COVERAGE_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_coverage_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _expected_days(prices_path: str | None, calendar_path: str | None, start_date: str, end_date: str, paths: ProjectPaths) -> list[str]:
    if prices_path:
        return _load_price_dates(prices_path, start_date, end_date, paths)
    if calendar_path:
        path = resolve_project_path(calendar_path, paths)
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                raw = payload
            elif isinstance(payload, dict):
                raw = payload.get("trading_days") or payload.get("dates") or []
            else:
                raw = []
            return sorted(day for day in raw if isinstance(day, str) and start_date <= day <= end_date)
    return calendar_dates(start_date, end_date)


def build_coverage_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Package Coverage Audit",
            "",
            "## Overall Verdict",
            f"- overall_passed={str(payload['overall_passed']).lower()}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Coverage",
            f"- expected_days={payload['coverage']['expected_days']}",
            f"- observed_signal_days={payload['coverage']['observed_signal_days']}",
            f"- coverage_ratio={payload['coverage']['coverage_ratio']}",
            f"- min_coverage={payload['coverage']['min_coverage']}",
            "",
            "## Point-in-Time Safety",
            f"- future_signal_rows={payload['point_in_time']['future_signal_rows']}",
            f"- passed={str(payload['point_in_time']['passed']).lower()}",
            "",
            "## Missing Days",
            *([f"- {day}" for day in payload["coverage"]["missing_signal_days"]] if payload["coverage"]["missing_signal_days"] else ["- none"]),
            "",
            "## Consistency",
            f"- regions={payload['consistency']['regions']}",
            f"- sources={payload['consistency']['sources']}",
            f"- versions={payload['consistency']['versions']}",
            "",
            "## Boundary",
            "- coverage audit only",
            "- replay not started",
            "- forward dry-run not started",
            "- no orders/trades/portfolio/accounts written",
            "",
        ]
    )
