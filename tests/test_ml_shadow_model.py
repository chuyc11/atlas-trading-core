from __future__ import annotations

from pathlib import Path

import pytest

from trading_core import cli
from trading_core.ml.model_registry import LIGHTGBM_REQUIRED_MESSAGE
from trading_core.ml.shadow_model import train_ml_shadow_model
from trading_core.storage.file_paths import project_paths

from ml_shadow_test_utils import assert_no_main_ledgers, build_sample_ml_pipeline


def test_mock_model_trains_and_writes_shadow_metadata(tmp_path: Path) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)
    model = pipeline["model"]

    assert Path(model["model_path"]).exists()
    assert Path(model["report_path"]).exists()
    assert model["shadow_only"] is True
    assert model["write_main_ledger"] is False
    assert model["windows"]
    report = Path(model["report_path"]).read_text(encoding="utf-8")
    assert "shadow_only=true" in report
    assert_no_main_ledgers(pipeline["paths"])


def test_lightgbm_missing_dependency_error_is_clear(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)

    def fail_lightgbm() -> object:
        raise RuntimeError(LIGHTGBM_REQUIRED_MESSAGE)

    monkeypatch.setattr("trading_core.ml.shadow_model.require_lightgbm", fail_lightgbm)
    with pytest.raises(RuntimeError, match="lightgbm is required"):
        train_ml_shadow_model(
            Path(pipeline["dataset"]["output_path"]),
            Path(pipeline["dataset"]["rows_path"]),
            "lightgbm",
            "future_5d_excess_vs_equal_etf",
            project_paths(tmp_path),
        )


def test_train_ml_shadow_cli_smoke(tmp_path: Path, capsys) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)

    exit_code = cli.main(
        [
            "train-ml-shadow",
            "--dataset",
            pipeline["dataset"]["output_path"],
            "--rows",
            pipeline["dataset"]["rows_path"],
            "--model-type",
            "mock",
            "--label-column",
            "future_5d_excess_vs_equal_etf",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "MLSHADOW" in captured.out
