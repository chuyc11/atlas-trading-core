"""Offline ETF label store v1 for ML shadow research."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from trading_core.data.data_package_validator import REQUIRED_COLUMNS
from trading_core.storage.file_paths import ProjectPaths, project_paths


LABEL_VERSION = "etf_label_v1"
RETURN_HORIZONS = (1, 5, 20)
EXCESS_HORIZONS = (5, 20)
LABEL_COLUMNS = [
    "future_1d_return",
    "future_5d_return",
    "future_20d_return",
    "future_5d_excess_vs_equal_etf",
    "future_20d_excess_vs_equal_etf",
    "label_available",
]
OUTPUT_COLUMNS = ["date", "symbol", "label_version", "source", "quality", *LABEL_COLUMNS]


def build_label_matrix(
    start_date: str,
    end_date: str,
    data_path: Path,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    rows = _read_price_package(_resolve_data_path(data_path, paths))
    grouped = _group_by_symbol(rows)
    future_returns = _future_returns_by_symbol(grouped)
    basket_returns = _equal_etf_returns(future_returns)

    label_rows: list[dict[str, Any]] = []
    for symbol, symbol_rows in sorted(grouped.items()):
        label_rows.extend(
            _label_rows_for_symbol(symbol, symbol_rows, future_returns[symbol], basket_returns, start_date, end_date)
        )

    label_rows = sorted(label_rows, key=lambda row: (row["date"], row["symbol"]))
    unavailable_counts = _unavailable_label_counts(label_rows)
    output_path = paths.data_dir / "labels" / f"label_matrix-{start_date}-{end_date}.csv"
    report_path = paths.outputs_dir / "labels" / f"LABEL_REPORT-{start_date}-{end_date}.md"
    _write_label_csv(output_path, label_rows)

    report = {
        "start_date": start_date,
        "end_date": end_date,
        "symbols": sorted(grouped.keys()),
        "date_range": {"start": start_date, "end": end_date},
        "rows": len(label_rows),
        "label_version": LABEL_VERSION,
        "unavailable_label_counts": unavailable_counts,
        "future_1d_available_count": _available_count(label_rows, "future_1d_return"),
        "future_5d_available_count": _available_count(label_rows, "future_5d_return"),
        "future_20d_available_count": _available_count(label_rows, "future_20d_return"),
        "leakage_policy": (
            "offline labels use future data by design; labels must not be used in run-daily decision path"
        ),
        "offline_only": True,
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


def _future_returns_by_symbol(
    grouped: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[int, float | None]]]:
    output: dict[str, dict[str, dict[int, float | None]]] = {}
    for symbol, rows in grouped.items():
        closes = [float(row["close"]) for row in rows]
        symbol_returns: dict[str, dict[int, float | None]] = {}
        for index, row in enumerate(rows):
            symbol_returns[str(row["date"])] = {
                horizon: _future_return(closes, index, horizon) for horizon in RETURN_HORIZONS
            }
        output[symbol] = symbol_returns
    return output


def _future_return(values: list[float], index: int, horizon: int) -> float | None:
    future_index = index + horizon
    if future_index >= len(values):
        return None
    current = values[index]
    if current == 0:
        return None
    return (values[future_index] / current) - 1


def _equal_etf_returns(
    future_returns: dict[str, dict[str, dict[int, float | None]]],
) -> dict[str, dict[int, float | None]]:
    by_date: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for symbol_returns in future_returns.values():
        for date, horizon_values in symbol_returns.items():
            for horizon in RETURN_HORIZONS:
                value = horizon_values.get(horizon)
                if value is not None:
                    by_date[date][horizon].append(value)
    return {
        date: {horizon: mean(values) if values else None for horizon, values in horizon_values.items()}
        for date, horizon_values in by_date.items()
    }


def _label_rows_for_symbol(
    symbol: str,
    rows: list[dict[str, Any]],
    symbol_future_returns: dict[str, dict[int, float | None]],
    basket_returns: dict[str, dict[int, float | None]],
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        date = str(row["date"])
        if date < start_date or date > end_date:
            continue
        future_1d = symbol_future_returns.get(date, {}).get(1)
        future_5d = symbol_future_returns.get(date, {}).get(5)
        future_20d = symbol_future_returns.get(date, {}).get(20)
        excess_5d = _excess_return(future_5d, basket_returns.get(date, {}).get(5))
        excess_20d = _excess_return(future_20d, basket_returns.get(date, {}).get(20))
        values = [future_1d, future_5d, future_20d, excess_5d, excess_20d]
        output.append(
            {
                "date": date,
                "symbol": symbol,
                "label_version": LABEL_VERSION,
                "source": row["source"],
                "quality": row["quality"],
                "future_1d_return": future_1d,
                "future_5d_return": future_5d,
                "future_20d_return": future_20d,
                "future_5d_excess_vs_equal_etf": excess_5d,
                "future_20d_excess_vs_equal_etf": excess_20d,
                "label_available": all(value is not None for value in values),
            }
        )
    return output


def _excess_return(symbol_return: float | None, basket_return: float | None) -> float | None:
    if symbol_return is None or basket_return is None:
        return None
    return symbol_return - basket_return


def _unavailable_label_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for column in LABEL_COLUMNS:
            if column == "label_available":
                if not row.get(column):
                    counter[column] += 1
            elif row.get(column) is None:
                counter[column] += 1
    return {column: int(counter.get(column, 0)) for column in LABEL_COLUMNS}


def _available_count(rows: list[dict[str, Any]], column: str) -> int:
    return len([row for row in rows if row.get(column) is not None])


def _write_label_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_value(row.get(column)) for column in OUTPUT_COLUMNS})


def _format_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        return round(value, 10)
    return value


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Label Report {report['start_date']} to {report['end_date']}",
        "",
        "- labels are offline-only",
        "- labels use future data by design",
        "- labels must not be used in run-daily decision path",
        f"- symbols: {report['symbols']}",
        f"- date range: {report['date_range']['start']} to {report['date_range']['end']}",
        f"- rows: {report['rows']}",
        f"- label_version: {report['label_version']}",
        f"- unavailable label counts: {report['unavailable_label_counts']}",
        f"- future_1d available count: {report['future_1d_available_count']}",
        f"- future_5d available count: {report['future_5d_available_count']}",
        f"- future_20d available count: {report['future_20d_available_count']}",
        f"- leakage_policy: {report['leakage_policy']}",
        f"- offline_only={str(report['offline_only']).lower()}",
    ]
    return "\n".join(lines) + "\n"
