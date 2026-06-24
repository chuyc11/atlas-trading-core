from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from trading_core.ml.prediction_engine import generate_ml_shadow_predictions
from trading_core.ml.shadow_model import train_ml_shadow_model
from trading_core.ml.shadow_signal_generator import generate_ml_shadow_signals
from trading_core.ml.walk_forward_dataset import build_walk_forward_dataset
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_jsonl


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


def trading_days(count: int, start: date = date(2026, 1, 1)) -> list[str]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def write_feature_label_matrices(
    root: Path,
    *,
    day_count: int = 15,
    symbol_count: int = 3,
    missing_feature: bool = False,
) -> tuple[Path, Path, list[str], list[str]]:
    days = trading_days(day_count)
    symbols = [f"ETF{i + 1}.SH" for i in range(symbol_count)]
    feature_path = root / "feature_matrix.csv"
    label_path = root / "label_matrix.csv"
    with feature_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["date", "symbol", "feature_version", "source", "quality", *FEATURE_COLUMNS],
        )
        writer.writeheader()
        for day_index, day in enumerate(days):
            for symbol_index, symbol in enumerate(symbols):
                score = (symbol_index + 1) * 0.01 + day_index * 0.001
                row: dict[str, Any] = {
                    "date": day,
                    "symbol": symbol,
                    "feature_version": "feature_store_v1",
                    "source": "test",
                    "quality": "fresh",
                    "return_1d": round(score / 3, 6),
                    "return_5d": round(score / 2, 6),
                    "return_20d": round(score, 6),
                    "volatility_20d": 0.01,
                    "volume_change_5d": 0.02,
                    "ma_5": 100 + day_index,
                    "ma_20": 99 + day_index,
                    "price_above_ma20": 1,
                    "drawdown_20d": -0.01,
                }
                if missing_feature and day_index == 0 and symbol_index == 0:
                    row["volatility_20d"] = ""
                writer.writerow(row)
    with label_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "date",
                "symbol",
                "label_version",
                "future_1d_return",
                "future_5d_return",
                "future_20d_return",
                "future_5d_excess_vs_equal_etf",
                "future_20d_excess_vs_equal_etf",
                "label_available",
            ],
        )
        writer.writeheader()
        for day_index, day in enumerate(days):
            for symbol_index, symbol in enumerate(symbols):
                available = not (day_index == len(days) - 1 and symbol_index == 0)
                label = (symbol_index - 1) * 0.01 + day_index * 0.0001
                writer.writerow(
                    {
                        "date": day,
                        "symbol": symbol,
                        "label_version": "etf_label_v1",
                        "future_1d_return": label / 5 if available else "",
                        "future_5d_return": label / 2 if available else "",
                        "future_20d_return": label if available else "",
                        "future_5d_excess_vs_equal_etf": label if available else "",
                        "future_20d_excess_vs_equal_etf": label * 2 if available else "",
                        "label_available": "true" if available else "false",
                    }
                )
    return feature_path, label_path, days, symbols


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def assert_no_main_ledgers(paths: ProjectPaths) -> None:
    assert not (paths.data_dir / "orders").exists()
    assert not (paths.data_dir / "trades").exists()
    assert not (paths.data_dir / "portfolios").exists()


def build_sample_ml_pipeline(root: Path) -> dict[str, Any]:
    paths = project_paths(root)
    features, labels, days, _symbols = write_feature_label_matrices(root, day_count=15, symbol_count=3)
    dataset = build_walk_forward_dataset(
        features,
        labels,
        days[0],
        days[-1],
        5,
        3,
        3,
        3,
        "future_5d_excess_vs_equal_etf",
        paths,
    )
    model = train_ml_shadow_model(
        Path(dataset["output_path"]),
        Path(dataset["rows_path"]),
        "mock",
        "future_5d_excess_vs_equal_etf",
        paths,
    )
    predictions = generate_ml_shadow_predictions(Path(model["model_path"]), Path(dataset["rows_path"]), paths)
    signals = generate_ml_shadow_signals(Path(predictions["output_path"]), 2, 0.05, paths)
    return {
        "paths": paths,
        "features": features,
        "labels": labels,
        "dataset": dataset,
        "model": model,
        "predictions": predictions,
        "signals": signals,
    }


def write_prediction_fixture(
    path: Path,
    *,
    prediction_count: int,
    positive_ic: bool = True,
    signal_side: str = "top",
) -> tuple[Path, Path]:
    path.mkdir(parents=True, exist_ok=True)
    predictions = []
    signals = []
    symbols = ["ETF1.SH", "ETF2.SH", "ETF3.SH"]
    days = trading_days(max(1, prediction_count // len(symbols) + 1))
    for index in range(prediction_count):
        date_value = days[index // len(symbols)]
        symbol_index = index % len(symbols)
        score = 3 - symbol_index
        label = score / 100 if positive_ic else symbol_index / 100
        prediction_id = f"MLPRED-{index + 1:06d}"
        predictions.append(
            {
                "prediction_id": prediction_id,
                "model_id": "MLSHADOW-20260101-20260131-mock",
                "window_id": "WF-0001",
                "split": "test",
                "date": date_value,
                "symbol": symbols[symbol_index],
                "prediction_score": score,
                "prediction_rank": symbol_index + 1,
                "label_column": "future_5d_excess_vs_equal_etf",
                "label_value": label,
                "shadow_only": True,
                "write_main_ledger": False,
            }
        )
    selected_rank = 1 if signal_side == "top" else 3
    for prediction in predictions:
        if int(prediction["prediction_rank"]) == selected_rank:
            signals.append(
                {
                    "shadow_signal_id": f"MLSHADOWSIG-{len(signals) + 1:06d}",
                    "prediction_id": prediction["prediction_id"],
                    "model_id": prediction["model_id"],
                    "date": prediction["date"],
                    "symbol": prediction["symbol"],
                    "side": "LONG",
                    "target_weight": 0.05,
                    "prediction_score": prediction["prediction_score"],
                    "prediction_rank": prediction["prediction_rank"],
                    "shadow_only": True,
                    "write_main_ledger": False,
                    "status": "shadow_candidate",
                }
            )
    predictions_path = path / "predictions.jsonl"
    signals_path = path / "signals.jsonl"
    write_jsonl(predictions_path, predictions)
    write_jsonl(signals_path, signals)
    return predictions_path, signals_path
