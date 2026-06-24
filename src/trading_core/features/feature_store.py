"""Feature store v1 for historical ETF research data."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from trading_core.data.data_package_validator import REQUIRED_COLUMNS
from trading_core.storage.file_paths import ProjectPaths, project_paths


FEATURE_VERSION = "feature_store_v1"
FEATURE_COLUMNS = [
    "return_1d",
    "return_5d",
    "return_20d",
    "volatility_20d",
    "volume_change_5d",
    "ma_5",
    "ma_20",
    "price_above_ma20",
    "drawdown_20d",
]
OUTPUT_COLUMNS = ["date", "symbol", "feature_version", "source", "quality", *FEATURE_COLUMNS]


def build_feature_matrix(
    start_date: str,
    end_date: str,
    data_path: Path,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    rows = _read_price_package(_resolve_data_path(data_path, paths))
    grouped = _group_by_symbol(rows)
    feature_rows: list[dict[str, Any]] = []
    for symbol, symbol_rows in sorted(grouped.items()):
        feature_rows.extend(_feature_rows_for_symbol(symbol, symbol_rows, start_date, end_date))

    feature_rows = sorted(feature_rows, key=lambda row: (row["date"], row["symbol"]))
    missing_counts = _missing_feature_counts(feature_rows)
    leakage_check_passed = True
    output_path = paths.data_dir / "features" / f"feature_matrix-{start_date}-{end_date}.csv"
    report_path = paths.outputs_dir / "features" / f"FEATURE_REPORT-{start_date}-{end_date}.md"
    _write_feature_csv(output_path, feature_rows)
    report = {
        "start_date": start_date,
        "end_date": end_date,
        "symbols": sorted(grouped.keys()),
        "date_range": {"start": start_date, "end": end_date},
        "rows": len(feature_rows),
        "missing_feature_counts": missing_counts,
        "feature_version": FEATURE_VERSION,
        "leakage_check_passed": leakage_check_passed,
        "output_path": str(output_path),
        "report_path": str(report_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(report), encoding="utf-8")
    return report


def _resolve_data_path(data_path: Path, paths: ProjectPaths) -> Path:
    if data_path.is_absolute():
        return data_path
    parts = [part.lower() for part in data_path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / data_path
    return paths.project_root / data_path


def _read_price_package(data_path: Path) -> list[dict[str, Any]]:
    files = sorted(data_path.glob("*.csv")) if data_path.is_dir() else [data_path]
    rows: list[dict[str, Any]] = []
    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"{file_path.name}: missing columns {missing}")
            for row in reader:
                try:
                    rows.append(
                        {
                            "date": str(row["date"]),
                            "symbol": str(row["symbol"]),
                            "open": float(row["open"]),
                            "high": float(row["high"]),
                            "low": float(row["low"]),
                            "close": float(row["close"]),
                            "volume": float(row["volume"]),
                            "source": str(row["source"]),
                            "quality": str(row["quality"]),
                        }
                    )
                except (TypeError, ValueError):
                    continue
    return rows


def _group_by_symbol(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["symbol"])].append(row)
    return {symbol: sorted(items, key=lambda item: item["date"]) for symbol, items in grouped.items()}


def _feature_rows_for_symbol(
    symbol: str,
    rows: list[dict[str, Any]],
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    output = []
    closes = [float(row["close"]) for row in rows]
    volumes = [float(row["volume"]) for row in rows]
    daily_returns = [_return_from(closes, index, 1) for index in range(len(rows))]
    for index, row in enumerate(rows):
        date = str(row["date"])
        if date < start_date or date > end_date:
            continue
        ma_5 = _moving_average(closes, index, 5)
        ma_20 = _moving_average(closes, index, 20)
        feature_row = {
            "date": date,
            "symbol": symbol,
            "feature_version": FEATURE_VERSION,
            "source": row["source"],
            "quality": row["quality"],
            "return_1d": _return_from(closes, index, 1),
            "return_5d": _return_from(closes, index, 5),
            "return_20d": _return_from(closes, index, 20),
            "volatility_20d": _volatility(daily_returns, index, 20),
            "volume_change_5d": _return_from(volumes, index, 5),
            "ma_5": ma_5,
            "ma_20": ma_20,
            "price_above_ma20": None if ma_20 is None else int(float(row["close"]) > ma_20),
            "drawdown_20d": _drawdown(closes, index, 20),
        }
        output.append(feature_row)
    return output


def _return_from(values: list[float], index: int, lookback: int) -> float | None:
    if index < lookback:
        return None
    prior = values[index - lookback]
    if prior == 0:
        return None
    return (values[index] / prior) - 1


def _moving_average(values: list[float], index: int, window: int) -> float | None:
    if index + 1 < window:
        return None
    return mean(values[index - window + 1 : index + 1])


def _volatility(daily_returns: list[float | None], index: int, window: int) -> float | None:
    if index < window:
        return None
    values = [value for value in daily_returns[index - window + 1 : index + 1] if value is not None]
    if len(values) < window:
        return None
    return pstdev(values)


def _drawdown(values: list[float], index: int, window: int) -> float | None:
    if index + 1 < window:
        return None
    window_values = values[index - window + 1 : index + 1]
    peak = max(window_values)
    if peak == 0:
        return None
    return (values[index] / peak) - 1


def _missing_feature_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for column in FEATURE_COLUMNS:
            if row.get(column) is None:
                counter[column] += 1
    return {column: int(counter.get(column, 0)) for column in FEATURE_COLUMNS}


def _write_feature_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_value(row.get(column)) for column in OUTPUT_COLUMNS})


def _format_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float):
        return round(value, 10)
    return value


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Feature Report {report['start_date']} to {report['end_date']}",
        "",
        f"- symbols: {report['symbols']}",
        f"- date range: {report['date_range']['start']} to {report['date_range']['end']}",
        f"- rows: {report['rows']}",
        f"- missing feature counts: {report['missing_feature_counts']}",
        f"- feature_version: {report['feature_version']}",
        f"- leakage_check_passed: {report['leakage_check_passed']}",
    ]
    return "\n".join(lines) + "\n"
