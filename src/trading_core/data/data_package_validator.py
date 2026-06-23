"""Validate local historical ETF CSV packages before backtesting."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from trading_core.calendar.trading_calendar import is_trading_day, parse_date
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


REQUIRED_COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume", "source", "quality"]
VALID_QUALITY = {"fresh", "fallback", "stale", "missing"}


def validate_data_package(
    input_path: Path,
    paths: ProjectPaths | None = None,
    suspicious_return_threshold: float = 0.15,
    timestamp: str | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    files = _csv_files(input_path)
    timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    stats = _empty_stats(input_path, files, suspicious_return_threshold)
    seen: set[tuple[str, str]] = set()
    rows_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing_columns = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
            if missing_columns:
                stats["errors"].append(f"{file_path.name}: missing columns {missing_columns}")
                continue
            for line_number, row in enumerate(reader, 2):
                stats["total_rows"] += 1
                _validate_row(file_path, line_number, row, stats, seen, rows_by_symbol)

    _summarize_coverage(stats, rows_by_symbol, suspicious_return_threshold)
    stats["passed"] = not stats["errors"] and stats["duplicate_records_count"] == 0 and stats["ohlc_anomaly_count"] == 0
    stats["symbols_count"] = len(stats["symbols"])
    stats["symbols"] = sorted(stats["symbols"])
    stats["quality_distribution"] = dict(sorted(stats["quality_distribution"].items()))

    output_dir = paths.outputs_dir / "data-validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "data_validation.json"
    report_path = output_dir / f"DATA_PACKAGE_VALIDATION-{timestamp}.md"
    write_json(json_path, stats)
    report_path.write_text(_markdown_report(stats), encoding="utf-8")
    stats["json_path"] = str(json_path)
    stats["report_path"] = str(report_path)
    return stats


def _csv_files(input_path: Path) -> list[Path]:
    if input_path.is_dir():
        return sorted(path for path in input_path.glob("*.csv") if path.is_file())
    return [input_path]


def _empty_stats(input_path: Path, files: list[Path], threshold: float) -> dict[str, Any]:
    return {
        "input_path": str(input_path),
        "files": [str(path) for path in files],
        "required_columns": REQUIRED_COLUMNS,
        "suspicious_return_threshold": threshold,
        "total_rows": 0,
        "symbols": set(),
        "symbols_count": 0,
        "date_range": {"start": None, "end": None},
        "missing_values_count": 0,
        "duplicate_records_count": 0,
        "ohlc_anomaly_count": 0,
        "suspicious_return_count": 0,
        "quality_distribution": Counter(),
        "missing_trading_days_by_symbol": {},
        "warnings": [],
        "errors": [] if files else ["no CSV files found"],
        "passed": False,
    }


def _validate_row(
    file_path: Path,
    line_number: int,
    row: dict[str, str],
    stats: dict[str, Any],
    seen: set[tuple[str, str]],
    rows_by_symbol: dict[str, list[dict[str, Any]]],
) -> None:
    missing_values = [column for column in REQUIRED_COLUMNS if row.get(column) in (None, "")]
    stats["missing_values_count"] += len(missing_values)
    if missing_values:
        stats["errors"].append(f"{file_path.name}:{line_number}: missing values {missing_values}")

    date_value = str(row.get("date", ""))
    symbol = str(row.get("symbol", "")).strip()
    try:
        parsed_date = parse_date(date_value)
    except ValueError:
        stats["errors"].append(f"{file_path.name}:{line_number}: invalid date {date_value!r}")
        parsed_date = None
    if not symbol:
        stats["errors"].append(f"{file_path.name}:{line_number}: empty symbol")

    numbers = {}
    for field in ["open", "high", "low", "close", "volume"]:
        try:
            numbers[field] = float(row.get(field, ""))
        except (TypeError, ValueError):
            stats["errors"].append(f"{file_path.name}:{line_number}: invalid numeric {field}")
            numbers[field] = None

    if any(numbers[field] is not None and numbers[field] <= 0 for field in ["open", "high", "low", "close"]):
        stats["ohlc_anomaly_count"] += 1
        stats["errors"].append(f"{file_path.name}:{line_number}: non-positive OHLC")
    if numbers["volume"] is not None and numbers["volume"] < 0:
        stats["ohlc_anomaly_count"] += 1
        stats["errors"].append(f"{file_path.name}:{line_number}: negative volume")

    if all(numbers[field] is not None for field in ["open", "high", "low", "close"]):
        if numbers["high"] < max(numbers["open"], numbers["close"], numbers["low"]):
            stats["ohlc_anomaly_count"] += 1
            stats["errors"].append(f"{file_path.name}:{line_number}: high below OHLC max")
        if numbers["low"] > min(numbers["open"], numbers["close"], numbers["high"]):
            stats["ohlc_anomaly_count"] += 1
            stats["errors"].append(f"{file_path.name}:{line_number}: low above OHLC min")

    quality = str(row.get("quality", "")).strip()
    stats["quality_distribution"][quality or "<missing>"] += 1
    if quality not in VALID_QUALITY:
        stats["errors"].append(f"{file_path.name}:{line_number}: invalid quality {quality!r}")

    if parsed_date and symbol:
        key = (symbol, parsed_date.isoformat())
        if key in seen:
            stats["duplicate_records_count"] += 1
            stats["errors"].append(f"{file_path.name}:{line_number}: duplicate symbol/date {symbol} {parsed_date.isoformat()}")
        seen.add(key)
        stats["symbols"].add(symbol)
        _extend_date_range(stats, parsed_date.isoformat())
        if numbers["close"] is not None:
            rows_by_symbol[symbol].append({"date": parsed_date.isoformat(), "close": numbers["close"]})


def _extend_date_range(stats: dict[str, Any], date_value: str) -> None:
    start = stats["date_range"]["start"]
    end = stats["date_range"]["end"]
    stats["date_range"]["start"] = date_value if start is None else min(start, date_value)
    stats["date_range"]["end"] = date_value if end is None else max(end, date_value)


def _summarize_coverage(stats: dict[str, Any], rows_by_symbol: dict[str, list[dict[str, Any]]], threshold: float) -> None:
    for symbol, rows in rows_by_symbol.items():
        rows = sorted(rows, key=lambda row: row["date"])
        observed = {row["date"] for row in rows}
        missing = 0
        if rows:
            current = parse_date(rows[0]["date"])
            end = parse_date(rows[-1]["date"])
            while current <= end:
                if is_trading_day(current) and current.isoformat() not in observed:
                    missing += 1
                current += timedelta(days=1)
        stats["missing_trading_days_by_symbol"][symbol] = missing

        previous_close: float | None = None
        for row in rows:
            close = float(row["close"])
            if previous_close not in (None, 0):
                result_return = (close / previous_close) - 1
                if abs(result_return) > threshold:
                    stats["suspicious_return_count"] += 1
                    stats["warnings"].append(
                        f"{symbol} {row['date']}: suspicious return {round(result_return, 6)}"
                    )
            previous_close = close


def _markdown_report(stats: dict[str, Any]) -> str:
    lines = [
        "# Data Package Validation",
        "",
        f"- Passed: {stats['passed']}",
        f"- Total rows: {stats['total_rows']}",
        f"- Symbol count: {stats['symbols_count']}",
        f"- Date range: {stats['date_range']['start']} to {stats['date_range']['end']}",
        f"- Missing values: {stats['missing_values_count']}",
        f"- Duplicate records: {stats['duplicate_records_count']}",
        f"- OHLC anomalies: {stats['ohlc_anomaly_count']}",
        f"- Suspicious returns: {stats['suspicious_return_count']}",
        f"- Quality distribution: {stats['quality_distribution']}",
        "",
        "## Missing Trading Days",
    ]
    if stats["missing_trading_days_by_symbol"]:
        lines.extend(
            f"- {symbol}: {count}"
            for symbol, count in sorted(stats["missing_trading_days_by_symbol"].items())
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in stats["warnings"]) if stats["warnings"] else lines.append("- none")
    lines.extend(["", "## Errors"])
    lines.extend(f"- {error}" for error in stats["errors"]) if stats["errors"] else lines.append("- none")
    return "\n".join(lines) + "\n"
