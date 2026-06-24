"""Generate research-only ML shadow predictions."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from trading_core.ml.shadow_model import _as_float
from trading_core.ml.walk_forward_dataset import _resolve_input_path
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_jsonl


def generate_ml_shadow_predictions(
    model_path: Path,
    rows_path: Path,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    model = read_json(_resolve_input_path(model_path, paths))
    if not model:
        raise ValueError(f"Missing model: {model_path}")
    rows = _read_rows(_resolve_input_path(rows_path, paths))
    test_rows = [row for row in rows if row.get("split") == "test"]
    scored = [{**row, "prediction_score": _mock_score(row)} for row in test_rows]
    ranked = _rank_by_date(scored)
    model_id = str(model["model_id"])
    start_date = str(model["start_date"])
    end_date = str(model["end_date"])
    predictions = []
    for index, row in enumerate(ranked, 1):
        predictions.append(
            {
                "prediction_id": f"MLPRED-{index:06d}",
                "model_id": model_id,
                "window_id": row["window_id"],
                "split": row["split"],
                "date": row["date"],
                "symbol": row["symbol"],
                "prediction_score": round(float(row["prediction_score"]), 10),
                "prediction_rank": int(row["prediction_rank"]),
                "label_column": row["label_column"],
                "label_value": _as_float(row.get("label_value")),
                "shadow_only": True,
                "write_main_ledger": False,
            }
        )
    output_path = paths.data_dir / "shadow" / f"ml_predictions-{start_date}-{end_date}-{model_id}.jsonl"
    report_path = paths.outputs_dir / "shadow" / f"ML_PREDICTION_REPORT-{start_date}-{end_date}-{model_id}.md"
    write_jsonl(output_path, predictions)
    report = _prediction_report(model_id, predictions)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return {
        "model_id": model_id,
        "start_date": start_date,
        "end_date": end_date,
        "prediction_count": len(predictions),
        "output_path": str(output_path),
        "report_path": str(report_path),
    }


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _mock_score(row: dict[str, str]) -> float:
    return (
        3.0 * (_as_float(row.get("return_20d")) or 0.0)
        + 2.0 * (_as_float(row.get("return_5d")) or 0.0)
        + 1.0 * (_as_float(row.get("return_1d")) or 0.0)
        - 0.5 * abs(_as_float(row.get("drawdown_20d")) or 0.0)
    )


def _rank_by_date(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["window_id"]), str(row["date"]))].append(row)
    ranked: list[dict[str, Any]] = []
    for (_window_id, _date), items in sorted(grouped.items()):
        sorted_items = sorted(items, key=lambda row: (-float(row["prediction_score"]), str(row["symbol"])))
        for rank, row in enumerate(sorted_items, 1):
            ranked.append({**row, "prediction_rank": rank})
    return sorted(ranked, key=lambda row: (row["window_id"], row["date"], int(row["prediction_rank"]), row["symbol"]))


def _prediction_report(model_id: str, predictions: list[dict[str, Any]]) -> str:
    dates = sorted({row["date"] for row in predictions})
    symbols = sorted({row["symbol"] for row in predictions})
    top_counts = Counter(row["symbol"] for row in predictions if int(row["prediction_rank"]) == 1)
    lines = [
        "# ML Prediction Report",
        "",
        f"- total predictions: {len(predictions)}",
        f"- dates: {len(dates)}",
        f"- symbols: {symbols}",
        f"- model_id: {model_id}",
        f"- top ranked symbols by date count: {dict(sorted(top_counts.items()))}",
        "- shadow_only=true",
        "- write_main_ledger=false",
        "- not used by run-daily",
    ]
    return "\n".join(lines) + "\n"
