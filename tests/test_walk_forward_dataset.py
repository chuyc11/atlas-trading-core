from __future__ import annotations

from pathlib import Path

from trading_core import cli
from trading_core.ml.walk_forward_dataset import build_walk_forward_dataset
from trading_core.storage.file_paths import project_paths

from ml_shadow_test_utils import assert_no_main_ledgers, read_csv_rows, write_feature_label_matrices


def test_walk_forward_dataset_outputs_json_rows_and_report(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    features, labels, days, _symbols = write_feature_label_matrices(tmp_path, missing_feature=True)

    result = build_walk_forward_dataset(
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

    rows = read_csv_rows(Path(result["rows_path"]))
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert Path(result["output_path"]).exists()
    assert rows
    assert "Walk-forward Dataset Report" in report
    assert "shadow research only" in report
    assert result["leakage_check"]["passed"] is True
    assert result["windows"][0]["train_end"] < result["windows"][0]["validation_start"]
    assert result["windows"][0]["validation_end"] < result["windows"][0]["test_start"]
    assert "1" in report
    assert_no_main_ledgers(paths)


def test_label_unavailable_rows_are_excluded_and_label_column_is_configurable(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    features, labels, days, _symbols = write_feature_label_matrices(tmp_path)

    result = build_walk_forward_dataset(
        features,
        labels,
        days[0],
        days[-1],
        5,
        3,
        3,
        3,
        "future_20d_excess_vs_equal_etf",
        paths,
    )

    rows = read_csv_rows(Path(result["rows_path"]))
    assert result["label_unavailable_rows"] == 1
    assert {row["label_column"] for row in rows} == {"future_20d_excess_vs_equal_etf"}
    assert all(row["label_value"] != "" for row in rows)


def test_build_ml_dataset_cli_smoke(tmp_path: Path, capsys) -> None:
    features, labels, days, _symbols = write_feature_label_matrices(tmp_path)

    exit_code = cli.main(
        [
            "build-ml-dataset",
            "--features",
            str(features),
            "--labels",
            str(labels),
            "--start-date",
            days[0],
            "--end-date",
            days[-1],
            "--train-days",
            "5",
            "--validation-days",
            "3",
            "--test-days",
            "3",
            "--step-days",
            "3",
            "--label-column",
            "future_5d_excess_vs_equal_etf",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "windows" in captured.out
