from __future__ import annotations

from collections import Counter
from pathlib import Path

from trading_core import cli
from trading_core.ml.shadow_signal_generator import generate_ml_shadow_signals
from trading_core.storage.jsonl_store import read_jsonl

from ml_shadow_test_utils import assert_no_main_ledgers, build_sample_ml_pipeline


def test_shadow_signal_generator_respects_top_k_and_boundaries(tmp_path: Path) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)
    result = generate_ml_shadow_signals(Path(pipeline["predictions"]["output_path"]), 2, 0.05, pipeline["paths"])

    signals = read_jsonl(Path(result["output_path"]))
    per_date = Counter(signal["date"] for signal in signals)
    assert signals
    assert max(per_date.values()) <= 2
    assert all(signal["shadow_only"] is True for signal in signals)
    assert all(signal["write_main_ledger"] is False for signal in signals)
    assert all(signal["status"] == "shadow_candidate" for signal in signals)
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "no orders generated" in report
    assert "no trades generated" in report
    assert_no_main_ledgers(pipeline["paths"])


def test_generate_ml_shadow_signals_cli_smoke(tmp_path: Path, capsys) -> None:
    pipeline = build_sample_ml_pipeline(tmp_path)

    exit_code = cli.main(
        [
            "generate-ml-shadow-signals",
            "--predictions",
            pipeline["predictions"]["output_path"],
            "--top-k",
            "2",
            "--target-weight",
            "0.05",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "signals" in captured.out
