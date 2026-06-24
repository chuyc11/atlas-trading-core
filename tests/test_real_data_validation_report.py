from __future__ import annotations

from pathlib import Path

from trading_core.evaluation.real_data_validation_report import build_real_data_validation_report
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import write_json


START = "2026-01-02"
END = "2026-01-05"
STRATEGY = "test_strategy"


def _seed_report_inputs(
    root: Path,
    *,
    data_passed: bool = True,
    consistency_passed: bool = True,
    symbols_failed: list[str] | None = None,
) -> Path:
    paths = project_paths(root)
    artifact_dir = paths.outputs_dir / "backtests" / "batch-REPORT"
    price_dir = paths.data_dir / "raw" / "prices" / "etf_daily"
    failed = symbols_failed or []
    write_json(
        price_dir / "manifest.json",
        {
            "source": "auto",
            "source_by_symbol": {"510300.SH": "yfinance"},
            "fallback_source": {"510300.SH": "yfinance"},
            "symbols_success": [] if failed else ["510300.SH"],
            "symbols_failed": failed,
            "warnings": ["Yahoo/yfinance data is used for research fallback and should be validated before backtesting."],
        },
    )
    write_json(artifact_dir / "batch_config.json", {"start_date": START, "end_date": END, "data": str(price_dir)})
    write_json(
        artifact_dir / "data_validation.json",
        {
            "input_path": str(price_dir),
            "passed": data_passed,
            "total_rows": 2,
            "symbols_count": 1,
            "date_range": {"start": START, "end": END},
            "ohlc_anomaly_count": 0,
            "suspicious_return_count": 0,
            "warnings": [],
        },
    )
    write_json(
        artifact_dir / "strategy_results.json",
        {
            STRATEGY: {
                "strategy_id": STRATEGY,
                "cumulative_return": 0.01,
                "max_drawdown": 0.02,
                "trade_count": 1,
                "cost_total": 5.0,
                "excess_return_equal_etf": 0.001,
            }
        },
    )
    write_json(artifact_dir / "benchmark_results.json", {STRATEGY: {"EQUAL_ETF": {"return": 0.0}}})
    write_json(artifact_dir / "admission_results.json", {STRATEGY: {"status": "rejected"}})
    write_json(artifact_dir / "leaderboard.json", {"items": [{"strategy_id": STRATEGY, "rank": 1}]})
    write_json(
        paths.data_dir / "evaluation" / f"backtest_consistency-{START}-{END}.json",
        {
            "mode": "backtest",
            "passed": consistency_passed,
            "warnings": [],
            "critical_errors": [] if consistency_passed else ["cash is negative"],
            "report_path": "dummy.md",
        },
    )
    return artifact_dir


def test_real_data_validation_report_writes_outputs_and_warns_on_yfinance_fallback(tmp_path: Path) -> None:
    artifact_dir = _seed_report_inputs(tmp_path)

    result = build_real_data_validation_report(artifact_dir, project_paths(tmp_path))

    assert result["release_candidate_passed"] is True
    assert result["blocking_reasons"] == []
    assert any("yfinance fallback" in warning for warning in result["warnings"])
    assert "yfinance fallback research-only" in result["limitations"]
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "no live trading" in report
    assert "no broker connection" in report
    assert "no ML/RL/LLM decisioning" in report


def test_real_data_validation_report_blocks_on_failed_consistency(tmp_path: Path) -> None:
    artifact_dir = _seed_report_inputs(tmp_path, consistency_passed=False)

    result = build_real_data_validation_report(artifact_dir, project_paths(tmp_path))

    assert result["release_candidate_passed"] is False
    assert "backtest_consistency_failed" in result["blocking_reasons"]


def test_real_data_validation_report_blocks_on_failed_data_validation(tmp_path: Path) -> None:
    artifact_dir = _seed_report_inputs(tmp_path, data_passed=False)

    result = build_real_data_validation_report(artifact_dir, project_paths(tmp_path))

    assert result["release_candidate_passed"] is False
    assert "data_validation_failed" in result["blocking_reasons"]


def test_real_data_validation_report_blocks_on_symbol_failures(tmp_path: Path) -> None:
    artifact_dir = _seed_report_inputs(tmp_path, symbols_failed=["159915.SZ"])

    result = build_real_data_validation_report(artifact_dir, project_paths(tmp_path))

    assert result["release_candidate_passed"] is False
    assert "symbols_failed" in result["blocking_reasons"]
