from __future__ import annotations

from pathlib import Path

from trading_core import cli
from trading_core.ml.prediction_engine import generate_ml_shadow_predictions
from trading_core.storage.jsonl_store import read_jsonl

from ml_shadow_test_utils import assert_no_main_ledgers, build_sample_ml_pipeline


def test_prediction_engine_writes_ranked_predictions_and_report(tmp_path: Path) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)
    result = generate_ml_shadow_predictions(
        Path(pipeline["model"]["model_path"]),
        Path(pipeline["dataset"]["rows_path"]),
        pipeline["paths"],
    )

    predictions = read_jsonl(Path(result["output_path"]))
    first_date = predictions[0]["date"]
    same_date = [row for row in predictions if row["date"] == first_date and row["window_id"] == predictions[0]["window_id"]]
    assert predictions
    assert [row["prediction_rank"] for row in same_date] == [1, 2, 3]
    assert all(row["split"] == "test" for row in predictions)
    assert all(row["shadow_only"] is True for row in predictions)
    assert Path(result["report_path"]).exists()
    assert_no_main_ledgers(pipeline["paths"])


def test_predict_ml_shadow_cli_smoke(tmp_path: Path, capsys) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)

    exit_code = cli.main(
        [
            "predict-ml-shadow",
            "--model",
            pipeline["model"]["model_path"],
            "--rows",
            pipeline["dataset"]["rows_path"],
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "predictions" in captured.out
