"""Convert ML predictions into shadow-only signal candidates."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from trading_core.ml.walk_forward_dataset import _resolve_input_path
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_jsonl


def generate_ml_shadow_signals(
    predictions_path: Path,
    top_k: int,
    target_weight: float,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    resolved_predictions_path = _resolve_input_path(predictions_path, paths)
    predictions = read_jsonl(resolved_predictions_path)
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for prediction in predictions:
        grouped[(str(prediction["window_id"]), str(prediction["date"]))].append(prediction)

    signals: list[dict[str, Any]] = []
    for (_window_id, _date), rows in sorted(grouped.items()):
        top_rows = sorted(rows, key=lambda row: (int(row["prediction_rank"]), str(row["symbol"])))[:top_k]
        for prediction in top_rows:
            signals.append(
                {
                    "shadow_signal_id": f"MLSHADOWSIG-{len(signals) + 1:06d}",
                    "prediction_id": prediction["prediction_id"],
                    "model_id": prediction["model_id"],
                    "date": prediction["date"],
                    "symbol": prediction["symbol"],
                    "side": "LONG",
                    "target_weight": target_weight,
                    "prediction_score": prediction["prediction_score"],
                    "prediction_rank": prediction["prediction_rank"],
                    "shadow_only": True,
                    "write_main_ledger": False,
                    "status": "shadow_candidate",
                }
            )

    start_date, end_date, model_id = _range_and_model_id(predictions, resolved_predictions_path)
    output_path = paths.data_dir / "shadow" / f"ml_shadow_signals-{start_date}-{end_date}-{model_id}.jsonl"
    report_path = paths.outputs_dir / "shadow" / f"ML_SHADOW_SIGNAL_REPORT-{start_date}-{end_date}-{model_id}.md"
    write_jsonl(output_path, signals)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(model_id, signals, top_k, target_weight), encoding="utf-8")
    return {
        "model_id": model_id,
        "start_date": start_date,
        "end_date": end_date,
        "signal_count": len(signals),
        "output_path": str(output_path),
        "report_path": str(report_path),
    }


def _range_and_model_id(rows: list[dict[str, Any]], predictions_path: Path) -> tuple[str, str, str]:
    dates = sorted({str(row["date"]) for row in rows})
    model_ids = sorted({str(row["model_id"]) for row in rows})
    model_id = model_ids[0] if model_ids else "UNKNOWN"
    parsed = _parse_range_from_predictions_path(predictions_path, model_id)
    if parsed is not None:
        return parsed[0], parsed[1], model_id
    return dates[0], dates[-1], model_id


def _parse_range_from_predictions_path(path: Path, model_id: str) -> tuple[str, str] | None:
    stem = path.stem
    prefix = "ml_predictions-"
    suffix = f"-{model_id}"
    if not stem.startswith(prefix) or not stem.endswith(suffix):
        return None
    date_range = stem[len(prefix) : -len(suffix)]
    if len(date_range) != 21 or date_range[10] != "-":
        return None
    return date_range[:10], date_range[11:]


def _markdown_report(model_id: str, signals: list[dict[str, Any]], top_k: int, target_weight: float) -> str:
    lines = [
        "# ML Shadow Signal Report",
        "",
        f"- model_id: {model_id}",
        f"- signal count: {len(signals)}",
        f"- top_k: {top_k}",
        f"- target_weight: {target_weight}",
        "- shadow_only=true",
        "- not active",
        "- no orders generated",
        "- no trades generated",
        "- write_main_ledger=false",
        "- not used by run-daily",
    ]
    return "\n".join(lines) + "\n"
