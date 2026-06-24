"""Aggregate ML shadow research artifacts into one report."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from trading_core.ml.walk_forward_dataset import _resolve_input_path
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


def build_ml_shadow_report(
    dataset_path: Path,
    model_path: Path,
    predictions_path: Path,
    signals_path: Path,
    leaderboard_path: Path,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    dataset = read_json(_resolve_input_path(dataset_path, paths))
    model = read_json(_resolve_input_path(model_path, paths))
    predictions = read_jsonl(_resolve_input_path(predictions_path, paths))
    signals = read_jsonl(_resolve_input_path(signals_path, paths))
    leaderboard = read_json(_resolve_input_path(leaderboard_path, paths))
    if not dataset or not model or leaderboard is None:
        raise ValueError("dataset, model, and leaderboard are required")
    start_date = str(dataset["start_date"])
    end_date = str(dataset["end_date"])
    model_id = str(model["model_id"])
    top_symbols = Counter(row["symbol"] for row in predictions if int(row.get("prediction_rank", 0)) == 1)
    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "model_id": model_id,
        "model_type": model["model_type"],
        "label_column": model["label_column"],
        "dataset_id": dataset["dataset_id"],
        "window_count": len(dataset.get("windows", [])),
        "train_rows": sum(int(window.get("train_rows", 0)) for window in dataset.get("windows", [])),
        "validation_rows": sum(int(window.get("validation_rows", 0)) for window in dataset.get("windows", [])),
        "test_rows": sum(int(window.get("test_rows", 0)) for window in dataset.get("windows", [])),
        "leakage_check": dataset.get("leakage_check", {}),
        "feature_columns": model.get("feature_columns", []),
        "windows_trained": len(model.get("windows", [])),
        "prediction_count": len(predictions),
        "prediction_date_count": len({row["date"] for row in predictions}),
        "prediction_symbol_count": len({row["symbol"] for row in predictions}),
        "top_symbols": dict(sorted(top_symbols.items())),
        "signal_count": len(signals),
        "top_k": _infer_top_k(signals),
        "target_weight": signals[0].get("target_weight") if signals else None,
        "leaderboard": leaderboard,
        "shadow_only": True,
        "write_main_ledger": False,
        "not_active": True,
    }
    summary_path = paths.data_dir / "shadow" / f"ml_shadow_research_summary-{start_date}-{end_date}-{model_id}.json"
    report_path = paths.outputs_dir / "shadow" / f"ML_SHADOW_RESEARCH_REPORT-{start_date}-{end_date}-{model_id}.md"
    write_json(summary_path, summary)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(summary), encoding="utf-8")
    return {**summary, "summary_path": str(summary_path), "report_path": str(report_path)}


def _infer_top_k(signals: list[dict[str, Any]]) -> int:
    per_date: Counter[str] = Counter(str(row["date"]) for row in signals)
    return max(per_date.values(), default=0)


def _markdown_report(summary: dict[str, Any]) -> str:
    leaderboard = summary["leaderboard"]
    lines = [
        "# ML Shadow Research Report",
        "",
        "## 1. Scope",
        f"- start_date: {summary['start_date']}",
        f"- end_date: {summary['end_date']}",
        f"- model_id: {summary['model_id']}",
        f"- model_type: {summary['model_type']}",
        f"- label_column: {summary['label_column']}",
        "",
        "## 2. Dataset",
        f"- dataset_id: {summary['dataset_id']}",
        f"- window count: {summary['window_count']}",
        f"- train rows: {summary['train_rows']}",
        f"- validation rows: {summary['validation_rows']}",
        f"- test rows: {summary['test_rows']}",
        f"- leakage check: {summary['leakage_check']}",
        "",
        "## 3. Model",
        f"- model_type: {summary['model_type']}",
        f"- feature columns: {summary['feature_columns']}",
        f"- windows trained: {summary['windows_trained']}",
        "- limitations: mock model is for pipeline validation only; lightgbm is optional",
        "",
        "## 4. Predictions",
        f"- prediction count: {summary['prediction_count']}",
        f"- date count: {summary['prediction_date_count']}",
        f"- symbol count: {summary['prediction_symbol_count']}",
        f"- top symbols: {summary['top_symbols']}",
        "",
        "## 5. Shadow Signals",
        f"- signal count: {summary['signal_count']}",
        f"- top_k: {summary['top_k']}",
        f"- target_weight: {summary['target_weight']}",
        "- no orders generated",
        "- no trades generated",
        "",
        "## 6. Shadow Leaderboard",
        f"- mean_rank_ic: {leaderboard.get('mean_rank_ic')}",
        f"- avg_label_value_top_k: {leaderboard.get('avg_label_value_top_k')}",
        f"- avg_label_value_all: {leaderboard.get('avg_label_value_all')}",
        f"- hit_rate_positive_label: {leaderboard.get('hit_rate_positive_label')}",
        f"- recommendation: {leaderboard.get('shadow_recommendation')}",
        "",
        "## 7. Boundary",
        "- shadow_only=true",
        "- write_main_ledger=false",
        "- not active",
        "- not used by run-daily",
        "- not allowed to generate real orders",
        "- not allowed to affect CHINA_PAPER",
        "- no orders/trades generated",
        "",
        "## 8. Next Steps",
        "- continue shadow observation",
        "- compare with momentum_strategy_v1",
        "- require admission gate before any promotion",
    ]
    return "\n".join(lines) + "\n"
