"""Walk-forward dataset builder for offline ML shadow research."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


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
ROWS_COLUMNS = [
    "window_id",
    "split",
    "date",
    "symbol",
    "label_column",
    "label_value",
    "feature_version",
    "label_version",
    *FEATURE_COLUMNS,
]
REQUIRED_FEATURE_COLUMNS = ["date", "symbol", "feature_version", "source", "quality", *FEATURE_COLUMNS]
REQUIRED_LABEL_COLUMNS = [
    "date",
    "symbol",
    "label_version",
    "future_1d_return",
    "future_5d_return",
    "future_20d_return",
    "future_5d_excess_vs_equal_etf",
    "future_20d_excess_vs_equal_etf",
    "label_available",
]
SPLIT_ORDER = {"train": 0, "validation": 1, "test": 2}


def build_walk_forward_dataset(
    features_path: Path,
    labels_path: Path,
    start_date: str,
    end_date: str,
    train_days: int,
    validation_days: int,
    test_days: int,
    step_days: int,
    label_column: str,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    features = _read_csv(_resolve_input_path(features_path, paths), REQUIRED_FEATURE_COLUMNS)
    labels = _read_csv(_resolve_input_path(labels_path, paths), REQUIRED_LABEL_COLUMNS)
    if label_column not in REQUIRED_LABEL_COLUMNS:
        raise ValueError(f"Unsupported label_column: {label_column}")

    joined_rows, label_unavailable_rows = _join_rows(features, labels, start_date, end_date, label_column)
    available_rows = [row for row in joined_rows if row["_label_row_available"]]
    dates = sorted({row["date"] for row in available_rows})
    windows = _build_windows(dates, train_days, validation_days, test_days, step_days)
    output_rows = _rows_for_windows(available_rows, windows, label_column)
    leakage_check = _leakage_check(windows)

    dataset_id = f"WF-{_compact_date(start_date)}-{_compact_date(end_date)}-{label_column}"
    output_path = paths.data_dir / "ml" / "datasets" / f"walk_forward_dataset-{start_date}-{end_date}.json"
    rows_path = paths.data_dir / "ml" / "datasets" / f"walk_forward_rows-{start_date}-{end_date}.csv"
    report_path = paths.outputs_dir / "ml" / "datasets" / f"WALK_FORWARD_DATASET_REPORT-{start_date}-{end_date}.md"
    feature_version = _single_version((row.get("feature_version", "") for row in joined_rows), "feature_version")
    label_version = _single_version((row.get("label_version", "") for row in joined_rows), "label_version")
    dataset = {
        "dataset_id": dataset_id,
        "start_date": start_date,
        "end_date": end_date,
        "label_column": label_column,
        "feature_version": feature_version,
        "label_version": label_version,
        "windows": [
            {
                "window_id": window["window_id"],
                "train_start": window["train_start"],
                "train_end": window["train_end"],
                "validation_start": window["validation_start"],
                "validation_end": window["validation_end"],
                "test_start": window["test_start"],
                "test_end": window["test_end"],
                "train_rows": window["train_rows"],
                "validation_rows": window["validation_rows"],
                "test_rows": window["test_rows"],
            }
            for window in windows
        ],
        "leakage_check": leakage_check,
        "rows_path": str(rows_path),
        "report_path": str(report_path),
        "shadow_only": True,
        "write_main_ledger": False,
    }
    write_json(output_path, dataset)
    _write_rows_csv(rows_path, output_rows)
    report = {
        **dataset,
        "total_joined_rows": len(joined_rows),
        "label_unavailable_rows": label_unavailable_rows,
        "missing_feature_counts": _missing_feature_counts(joined_rows),
        "symbols": sorted({row["symbol"] for row in joined_rows}),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(report), encoding="utf-8")
    return {
        **dataset,
        "output_path": str(output_path),
        "rows_path": str(rows_path),
        "report_path": str(report_path),
        "rows": len(output_rows),
        "total_joined_rows": len(joined_rows),
        "label_unavailable_rows": label_unavailable_rows,
    }


def _resolve_input_path(path: Path, paths: ProjectPaths) -> Path:
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _read_csv(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in required_columns if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path.name}: missing columns {missing}")
        return [dict(row) for row in reader]


def _join_rows(
    features: list[dict[str, str]],
    labels: list[dict[str, str]],
    start_date: str,
    end_date: str,
    label_column: str,
) -> tuple[list[dict[str, Any]], int]:
    label_by_key = {(row["date"], row["symbol"]): row for row in labels}
    joined: list[dict[str, Any]] = []
    label_unavailable = 0
    for feature in features:
        date = feature["date"]
        if date < start_date or date > end_date:
            continue
        label = label_by_key.get((date, feature["symbol"]))
        if label is None:
            continue
        raw_label = str(label.get(label_column, ""))
        is_available = _is_true(label.get("label_available")) and raw_label.strip() != ""
        if not is_available:
            label_unavailable += 1
        row = {
            "date": date,
            "symbol": feature["symbol"],
            "label_column": label_column,
            "label_value": raw_label,
            "feature_version": feature["feature_version"],
            "label_version": label["label_version"],
            "_label_row_available": is_available,
        }
        for column in FEATURE_COLUMNS:
            row[column] = feature.get(column, "")
        joined.append(row)
    return sorted(joined, key=lambda row: (row["date"], row["symbol"])), label_unavailable


def _is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _build_windows(
    dates: list[str],
    train_days: int,
    validation_days: int,
    test_days: int,
    step_days: int,
) -> list[dict[str, Any]]:
    if min(train_days, validation_days, test_days, step_days) <= 0:
        raise ValueError("window day counts must be positive")
    windows: list[dict[str, Any]] = []
    span = train_days + validation_days + test_days
    start_index = 0
    while start_index + span <= len(dates):
        train_start_index = start_index
        train_end_index = start_index + train_days - 1
        validation_start_index = train_end_index + 1
        validation_end_index = validation_start_index + validation_days - 1
        test_start_index = validation_end_index + 1
        test_end_index = test_start_index + test_days - 1
        windows.append(
            {
                "window_id": f"WF-{len(windows) + 1:04d}",
                "train_start": dates[train_start_index],
                "train_end": dates[train_end_index],
                "validation_start": dates[validation_start_index],
                "validation_end": dates[validation_end_index],
                "test_start": dates[test_start_index],
                "test_end": dates[test_end_index],
                "train_rows": 0,
                "validation_rows": 0,
                "test_rows": 0,
            }
        )
        start_index += step_days
    return windows


def _rows_for_windows(
    available_rows: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    label_column: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for window in windows:
        for row in available_rows:
            split = _split_for_date(row["date"], window)
            if split is None:
                continue
            window[f"{split}_rows"] += 1
            output_row = {
                "window_id": window["window_id"],
                "split": split,
                "date": row["date"],
                "symbol": row["symbol"],
                "label_column": label_column,
                "label_value": row["label_value"],
                "feature_version": row["feature_version"],
                "label_version": row["label_version"],
            }
            for column in FEATURE_COLUMNS:
                output_row[column] = row.get(column, "")
            output.append(output_row)
    return sorted(output, key=lambda row: (row["window_id"], SPLIT_ORDER[row["split"]], row["date"], row["symbol"]))


def _split_for_date(date: str, window: dict[str, Any]) -> str | None:
    if window["train_start"] <= date <= window["train_end"]:
        return "train"
    if window["validation_start"] <= date <= window["validation_end"]:
        return "validation"
    if window["test_start"] <= date <= window["test_end"]:
        return "test"
    return None


def _leakage_check(windows: list[dict[str, Any]]) -> dict[str, Any]:
    checks: list[str] = []
    for window in windows:
        if not window["train_end"] < window["validation_start"]:
            checks.append(f"{window['window_id']}: train_end must be before validation_start")
        if not window["validation_end"] < window["test_start"]:
            checks.append(f"{window['window_id']}: validation_end must be before test_start")
    return {"passed": not checks, "checks": checks}


def _single_version(values: Any, name: str) -> str:
    versions = sorted({str(value) for value in values if str(value).strip()})
    if not versions:
        return "unknown"
    if len(versions) == 1:
        return versions[0]
    return f"mixed_{name}"


def _missing_feature_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for column in FEATURE_COLUMNS:
            if row.get(column) in (None, ""):
                counter[column] += 1
    return {column: int(counter.get(column, 0)) for column in FEATURE_COLUMNS}


def _write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROWS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in ROWS_COLUMNS})


def _compact_date(value: str) -> str:
    return value.replace("-", "")


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Walk-forward Dataset Report",
        "",
        "## Scope",
        f"- start_date: {report['start_date']}",
        f"- end_date: {report['end_date']}",
        f"- label_column: {report['label_column']}",
        f"- feature_version: {report['feature_version']}",
        f"- label_version: {report['label_version']}",
        "",
        "## Windows",
        f"- window count: {len(report['windows'])}",
    ]
    for window in report["windows"]:
        lines.append(
            "- "
            f"{window['window_id']}: train {window['train_start']} to {window['train_end']} "
            f"({window['train_rows']} rows), validation {window['validation_start']} to {window['validation_end']} "
            f"({window['validation_rows']} rows), test {window['test_start']} to {window['test_end']} "
            f"({window['test_rows']} rows)"
        )
    lines.extend(
        [
            "",
            "## Data Quality",
            f"- total joined rows: {report['total_joined_rows']}",
            f"- label unavailable rows: {report['label_unavailable_rows']}",
            f"- missing feature counts: {report['missing_feature_counts']}",
            f"- symbols: {report['symbols']}",
            "",
            "## Leakage Check",
            f"- passed: {report['leakage_check']['passed']}",
            f"- details: {report['leakage_check']['checks']}",
            "- features are past/current only",
            "- labels are future returns for offline ML only",
            "",
            "## Boundary",
            "- offline only",
            "- shadow research only",
            "- not used by run-daily",
            "- not allowed to write orders/trades/portfolio",
        ]
    )
    return "\n".join(lines) + "\n"
