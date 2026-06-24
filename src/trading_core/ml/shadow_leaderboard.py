"""Offline leaderboard for ML shadow predictions and signals."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from trading_core.ml.shadow_model import _as_float
from trading_core.ml.walk_forward_dataset import _resolve_input_path
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_json


def build_ml_shadow_leaderboard(
    predictions_path: Path,
    signals_path: Path,
    benchmark: str = "EQUAL_ETF",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    resolved_predictions_path = _resolve_input_path(predictions_path, paths)
    predictions = read_jsonl(resolved_predictions_path)
    signals = read_jsonl(_resolve_input_path(signals_path, paths))
    if not predictions:
        raise ValueError("predictions are required")
    model_id = str(predictions[0]["model_id"])
    dates = sorted({str(row["date"]) for row in predictions})
    symbols = sorted({str(row["symbol"]) for row in predictions})
    signal_prediction_ids = {str(row["prediction_id"]) for row in signals}
    all_labels = [_as_float(row.get("label_value")) for row in predictions]
    top_labels = [_as_float(row.get("label_value")) for row in predictions if str(row.get("prediction_id")) in signal_prediction_ids]
    all_numeric = [value for value in all_labels if value is not None]
    top_numeric = [value for value in top_labels if value is not None]
    avg_all = mean(all_numeric) if all_numeric else 0.0
    avg_top = mean(top_numeric) if top_numeric else 0.0
    rank_ic_by_date = _rank_ic_by_date(predictions)
    rank_values = [value for value in rank_ic_by_date.values() if value is not None]
    mean_rank_ic = mean(rank_values) if rank_values else 0.0
    hit_rate = len([value for value in top_numeric if value > 0]) / len(top_numeric) if top_numeric else 0.0
    payload = {
        "model_id": model_id,
        "benchmark": benchmark,
        "prediction_count": len(predictions),
        "signal_count": len(signals),
        "dates": dates,
        "symbols": symbols,
        "avg_label_value_top_k": round(avg_top, 10),
        "avg_label_value_all": round(avg_all, 10),
        "top_k_excess_vs_all": round(avg_top - avg_all, 10),
        "hit_rate_positive_label": round(hit_rate, 10),
        "rank_ic_by_date": {date: None if value is None else round(value, 10) for date, value in rank_ic_by_date.items()},
        "mean_rank_ic": round(mean_rank_ic, 10),
        "shadow_recommendation": _recommendation(len(predictions), mean_rank_ic, avg_top, avg_all),
        "shadow_only": True,
        "write_main_ledger": False,
        "not_active": True,
    }
    start_date, end_date = _range_from_predictions_path(resolved_predictions_path, model_id) or (dates[0], dates[-1])
    output_path = paths.data_dir / "shadow" / f"ml_shadow_leaderboard-{start_date}-{end_date}-{model_id}.json"
    report_path = paths.outputs_dir / "shadow" / f"ML_SHADOW_LEADERBOARD-{start_date}-{end_date}-{model_id}.md"
    write_json(output_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    return {**payload, "output_path": str(output_path), "report_path": str(report_path)}


def _rank_ic_by_date(predictions: list[dict[str, Any]]) -> dict[str, float | None]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for prediction in predictions:
        grouped[(str(prediction["window_id"]), str(prediction["date"]))].append(prediction)
    output: dict[str, float | None] = {}
    for (window_id, date), rows in sorted(grouped.items()):
        pairs = [
            (_as_float(row.get("prediction_score")), _as_float(row.get("label_value")))
            for row in rows
        ]
        numeric_pairs = [(score, label) for score, label in pairs if score is not None and label is not None]
        key = f"{window_id}:{date}"
        if len(numeric_pairs) < 3:
            output[key] = None
            continue
        score_ranks = _ranks([score for score, _label in numeric_pairs])
        label_ranks = _ranks([label for _score, label in numeric_pairs])
        output[key] = _pearson(score_ranks, label_ranks)
    return output


def _ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        next_index = index + 1
        while next_index < len(indexed) and indexed[next_index][1] == indexed[index][1]:
            next_index += 1
        average_rank = (index + 1 + next_index) / 2
        for original_index, _value in indexed[index:next_index]:
            ranks[original_index] = average_rank
        index = next_index
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    left_denominator = sum((x - left_mean) ** 2 for x in left) ** 0.5
    right_denominator = sum((y - right_mean) ** 2 for y in right) ** 0.5
    denominator = left_denominator * right_denominator
    if denominator == 0:
        return None
    return numerator / denominator


def _recommendation(prediction_count: int, mean_rank_ic: float, avg_top: float, avg_all: float) -> str:
    if prediction_count < 30:
        return "insufficient_data"
    if mean_rank_ic > 0.05 and avg_top > avg_all:
        return "promising"
    if mean_rank_ic > 0:
        return "watch"
    return "weak"


def _range_from_predictions_path(path: Path, model_id: str) -> tuple[str, str] | None:
    stem = path.stem
    prefix = "ml_predictions-"
    suffix = f"-{model_id}"
    if not stem.startswith(prefix) or not stem.endswith(suffix):
        return None
    date_range = stem[len(prefix) : -len(suffix)]
    if len(date_range) != 21 or date_range[10] != "-":
        return None
    return date_range[:10], date_range[11:]


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# ML Shadow Leaderboard",
        "",
        f"- model_id: {payload['model_id']}",
        f"- benchmark: {payload['benchmark']}",
        f"- prediction_count: {payload['prediction_count']}",
        f"- signal_count: {payload['signal_count']}",
        f"- symbols: {payload['symbols']}",
        f"- avg_label_value_top_k: {payload['avg_label_value_top_k']}",
        f"- avg_label_value_all: {payload['avg_label_value_all']}",
        f"- top_k_excess_vs_all: {payload['top_k_excess_vs_all']}",
        f"- hit_rate_positive_label: {payload['hit_rate_positive_label']}",
        f"- mean_rank_ic: {payload['mean_rank_ic']}",
        f"- shadow_recommendation: {payload['shadow_recommendation']}",
        "- shadow-only: recommendation means continue observation only",
        "- not active",
        "- write_main_ledger=false",
        "- no orders/trades/portfolio written",
        "- not used by run-daily",
    ]
    return "\n".join(lines) + "\n"
