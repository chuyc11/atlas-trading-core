from __future__ import annotations

from pathlib import Path

from trading_core import cli
from trading_core.ml.shadow_leaderboard import build_ml_shadow_leaderboard
from trading_core.ml.shadow_report import build_ml_shadow_report

from ml_shadow_test_utils import assert_no_main_ledgers, build_sample_ml_pipeline


def test_ml_shadow_report_outputs_summary_and_markdown(tmp_path: Path) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)
    leaderboard = build_ml_shadow_leaderboard(
        Path(pipeline["predictions"]["output_path"]),
        Path(pipeline["signals"]["output_path"]),
        "EQUAL_ETF",
        pipeline["paths"],
    )

    result = build_ml_shadow_report(
        Path(pipeline["dataset"]["output_path"]),
        Path(pipeline["model"]["model_path"]),
        Path(pipeline["predictions"]["output_path"]),
        Path(pipeline["signals"]["output_path"]),
        Path(leaderboard["output_path"]),
        pipeline["paths"],
    )

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert Path(result["summary_path"]).exists()
    assert "shadow_only=true" in report
    assert "not used by run-daily" in report
    assert "no orders/trades generated" in report
    assert_no_main_ledgers(pipeline["paths"])


def test_ml_shadow_report_cli_smoke(tmp_path: Path, capsys) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)
    leaderboard = build_ml_shadow_leaderboard(
        Path(pipeline["predictions"]["output_path"]),
        Path(pipeline["signals"]["output_path"]),
        "EQUAL_ETF",
        pipeline["paths"],
    )

    exit_code = cli.main(
        [
            "ml-shadow-report",
            "--dataset",
            pipeline["dataset"]["output_path"],
            "--model",
            pipeline["model"]["model_path"],
            "--predictions",
            pipeline["predictions"]["output_path"],
            "--signals",
            pipeline["signals"]["output_path"],
            "--leaderboard",
            leaderboard["output_path"],
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "MLSHADOW" in captured.out
