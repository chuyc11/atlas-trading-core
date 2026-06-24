"""Historical global-briefing signal package validation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from trading_core.global_briefing.signal_schema import (
    DEFAULT_DECISION_TIME,
    calendar_dates,
    read_signal_package,
    validate_signal_row,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


def validate_global_briefing_signals(
    input_path: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    validation_id, created_at = timestamp_id("GB-SIGNAL-VALIDATION")
    package = read_signal_package(input_path, paths)
    blocking = list(package.blocking_reasons)
    warnings = list(package.warnings)
    valid_rows: list[dict[str, Any]] = []
    invalid_rows = 0
    future_rows = 0

    for row_number, row in enumerate(package.rows, 1):
        clean, row_blocking, row_warnings = validate_signal_row(
            row,
            row_number,
            start_date=start_date,
            end_date=end_date,
            decision_time=DEFAULT_DECISION_TIME,
            check_point_in_time=True,
        )
        warnings.extend(row_warnings)
        if row_blocking:
            invalid_rows += 1
            blocking.extend(row_blocking)
            if any("future signal leakage" in item for item in row_blocking):
                future_rows += 1
        elif clean is not None:
            valid_rows.append(clean)

    if not package.rows:
        blocking.append("empty signal package")

    date_counts = Counter(row["as_of_date"] for row in valid_rows)
    duplicate_dates = sorted(day for day, count in date_counts.items() if count > 1)
    if duplicate_dates:
        warnings.append(f"duplicate as_of_date rows available for point-in-time selection: {duplicate_dates}")

    observed_dates = sorted(date_counts)
    inferred_start = start_date or (observed_dates[0] if observed_dates else None)
    inferred_end = end_date or (observed_dates[-1] if observed_dates else None)
    expected_dates = calendar_dates(inferred_start, inferred_end) if inferred_start and inferred_end else []
    missing_dates = [day for day in expected_dates if day not in date_counts]
    if missing_dates:
        warnings.append(f"missing signal dates: {missing_dates}")
        if strict:
            blocking.append(f"strict coverage failure: missing signal dates {missing_dates}")

    coverage_ratio = (len(observed_dates) / len(expected_dates)) if expected_dates else None
    payload: dict[str, Any] = {
        "validation_id": validation_id,
        "created_at": created_at,
        "input": str(package.input_path),
        "input_format": package.input_format,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "row_count": len(package.rows),
        "valid_row_count": len(valid_rows),
        "invalid_row_count": invalid_rows,
        "date_range": {
            "start": inferred_start,
            "end": inferred_end,
        },
        "coverage": {
            "expected_trading_days": len(expected_dates) if expected_dates else None,
            "observed_signal_days": len(observed_dates),
            "coverage_ratio": coverage_ratio,
            "missing_dates": missing_dates,
        },
        "point_in_time": {
            "future_signal_rows": future_rows,
            "passed": future_rows == 0,
        },
        "duplicates": {
            "duplicate_as_of_dates": duplicate_dates,
            "handling": "point-in-time selection uses latest generated_at at or before decision timestamp",
        },
        "boundary": {
            "validation_only": True,
            "replay_started": False,
            "write_main_ledger": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_signal_validation.json"
    report_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_SIGNAL_VALIDATION.md"
    write_json_markdown(json_path, payload, report_path, build_validation_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_validation_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Signal Validation",
            "",
            "## Overall Verdict",
            f"- overall_passed={str(payload['overall_passed']).lower()}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Coverage",
            f"- expected_trading_days={payload['coverage']['expected_trading_days']}",
            f"- observed_signal_days={payload['coverage']['observed_signal_days']}",
            f"- coverage_ratio={payload['coverage']['coverage_ratio']}",
            f"- missing_dates={payload['coverage']['missing_dates']}",
            "",
            "## Point-in-Time Safety",
            f"- passed={str(payload['point_in_time']['passed']).lower()}",
            f"- future_signal_rows={payload['point_in_time']['future_signal_rows']}",
            "",
            "## Warnings",
            *([f"- {item}" for item in payload["warnings"]] if payload["warnings"] else ["- none"]),
            "",
            "## Boundary",
            "- validation only",
            "- replay not started",
            "- no orders/trades/portfolio/accounts written",
            "- run-daily not called",
            "",
        ]
    )
