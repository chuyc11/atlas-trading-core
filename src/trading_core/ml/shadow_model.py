"""ML shadow model scaffold for research-only predictions."""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean
from typing import Any

from trading_core.ml.model_registry import require_lightgbm, require_supported_model_type
from trading_core.ml.walk_forward_dataset import FEATURE_COLUMNS, _resolve_input_path
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_json


def train_ml_shadow_model(
    dataset_path: Path,
    rows_path: Path,
    model_type: str,
    label_column: str,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    require_supported_model_type(model_type)
    if model_type == "lightgbm":
        require_lightgbm()

    dataset = read_json(_resolve_input_path(dataset_path, paths))
    if not dataset:
        raise ValueError(f"Missing dataset: {dataset_path}")
    rows = _read_rows(_resolve_input_path(rows_path, paths))
    start_date = str(dataset["start_date"])
    end_date = str(dataset["end_date"])
    dataset_id = str(dataset["dataset_id"])
    model_id = f"MLSHADOW-{start_date.replace('-', '')}-{end_date.replace('-', '')}-{model_type}"
    model_windows = []
    for window in dataset.get("windows", []):
        window_id = str(window["window_id"])
        model_windows.append(
            {
                "window_id": window_id,
                "train_rows": int(window.get("train_rows", 0)),
                "validation_rows": int(window.get("validation_rows", 0)),
                "test_rows": int(window.get("test_rows", 0)),
                "validation_metric": _mean_label(rows, window_id, "validation"),
                "test_metric": _mean_label(rows, window_id, "test"),
            }
        )
    model = {
        "model_id": model_id,
        "model_type": model_type,
        "label_column": label_column,
        "dataset_id": dataset_id,
        "start_date": start_date,
        "end_date": end_date,
        "feature_columns": FEATURE_COLUMNS,
        "windows": model_windows,
        "status": "trained",
        "shadow_only": True,
        "write_main_ledger": False,
        "limitations": [
            "mock model is for pipeline validation only" if model_type == "mock" else "lightgbm is optional",
            "not used by run-daily",
        ],
    }
    model_path = paths.data_dir / "ml" / "models" / f"ml_shadow_model-{start_date}-{end_date}-{model_type}.json"
    report_path = paths.outputs_dir / "ml" / "models" / f"ML_SHADOW_TRAINING_REPORT-{start_date}-{end_date}-{model_type}.md"
    write_json(model_path, model)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(model), encoding="utf-8")
    return {**model, "model_path": str(model_path), "report_path": str(report_path)}


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _mean_label(rows: list[dict[str, str]], window_id: str, split: str) -> float:
    values = [_as_float(row.get("label_value")) for row in rows if row.get("window_id") == window_id and row.get("split") == split]
    numeric = [value for value in values if value is not None]
    if not numeric:
        return 0.0
    return round(mean(numeric), 10)


def _as_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _markdown_report(model: dict[str, Any]) -> str:
    lines = [
        "# ML Shadow Training Report",
        "",
        "## Model",
        f"- model_id: {model['model_id']}",
        f"- model_type: {model['model_type']}",
        f"- label_column: {model['label_column']}",
        f"- dataset_id: {model['dataset_id']}",
        "",
        "## Windows",
    ]
    for window in model["windows"]:
        lines.append(
            "- "
            f"{window['window_id']}: train rows {window['train_rows']}, validation rows {window['validation_rows']}, "
            f"test rows {window['test_rows']}, metric {window['test_metric']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "- shadow_only=true",
            "- write_main_ledger=false",
            "- not used by run-daily",
            "- no orders/trades/portfolio written",
            "",
            "## Limitations",
            "- mock model is for pipeline validation only",
            "- lightgbm is optional",
        ]
    )
    return "\n".join(lines) + "\n"
