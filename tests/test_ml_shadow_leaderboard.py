from __future__ import annotations

from pathlib import Path

from trading_core import cli
from trading_core.ml.shadow_leaderboard import build_ml_shadow_leaderboard
from trading_core.storage.file_paths import project_paths

from ml_shadow_test_utils import assert_no_main_ledgers, write_prediction_fixture


def test_shadow_leaderboard_outputs_metrics_and_report(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    predictions, signals = write_prediction_fixture(tmp_path, prediction_count=30, positive_ic=True, signal_side="top")

    result = build_ml_shadow_leaderboard(predictions, signals, "EQUAL_ETF", paths)

    assert Path(result["output_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["mean_rank_ic"] > 0
    assert result["shadow_recommendation"] == "promising"
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "shadow-only" in report
    assert_no_main_ledgers(paths)


def test_shadow_leaderboard_recommendation_rules(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    small_predictions, small_signals = write_prediction_fixture(tmp_path / "small", prediction_count=12)
    assert build_ml_shadow_leaderboard(small_predictions, small_signals, "EQUAL_ETF", paths)["shadow_recommendation"] == "insufficient_data"

    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()
    watch_predictions, watch_signals = write_prediction_fixture(watch_dir, prediction_count=30, positive_ic=True, signal_side="bottom")
    assert build_ml_shadow_leaderboard(watch_predictions, watch_signals, "EQUAL_ETF", paths)["shadow_recommendation"] == "watch"

    weak_dir = tmp_path / "weak"
    weak_dir.mkdir()
    weak_predictions, weak_signals = write_prediction_fixture(weak_dir, prediction_count=30, positive_ic=False, signal_side="top")
    assert build_ml_shadow_leaderboard(weak_predictions, weak_signals, "EQUAL_ETF", paths)["shadow_recommendation"] == "weak"


def test_ml_shadow_leaderboard_cli_smoke(tmp_path: Path, capsys) -> None:
    predictions, signals = write_prediction_fixture(tmp_path, prediction_count=30)

    exit_code = cli.main(
        [
            "ml-shadow-leaderboard",
            "--predictions",
            str(predictions),
            "--signals",
            str(signals),
            "--benchmark",
            "EQUAL_ETF",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "recommendation" in captured.out
