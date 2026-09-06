from __future__ import annotations

import importlib.util
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from trading_core.storage.jsonl_store import read_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_historical_etf_backtest.py"


def _load_runbook_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_historical_etf_backtest", SCRIPT_PATH)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_price_csv(path: Path, days: int = 70) -> None:
    current = date(2026, 1, 1)
    rows = ["date,symbol,open,high,low,close,volume,source,quality"]
    business_days = 0
    while business_days < days:
        if current.weekday() < 5:
            idx = business_days
            for symbol, base, slope in [
                ("510300.SH", 4.0, 0.01),
                ("159915.SZ", 2.0, 0.015),
                ("000300.SH", 5000.0, 6.0),
            ]:
                open_price = base + idx * slope
                close_price = open_price + slope / 2
                rows.append(
                    f"{current.isoformat()},{symbol},{open_price:.4f},{close_price:.4f},{open_price:.4f},{close_price:.4f},100000,test,fresh"
                )
            business_days += 1
        current += timedelta(days=1)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_historical_etf_backtest_runbook_writes_acceptance_artifacts(tmp_path: Path) -> None:
    module = _load_runbook_module()
    csv_path = tmp_path / "prices.csv"
    _write_price_csv(csv_path)

    result = module.run_backtest_runbook(
        csv_path,
        "2026-01-01",
        "2026-04-08",
        workspace_root=tmp_path,
        timestamp="TEST-RUN",
    )

    output_dir = Path(result["output_dir"])
    assert output_dir == tmp_path / "work" / "trading-core" / "outputs" / "backtests" / "TEST-RUN"
    for name in [
        "run_config.json",
        "strategy_results.json",
        "benchmark_results.json",
        "limitations.json",
        "backtest_summary.md",
    ]:
        assert (output_dir / name).exists()

    run_config = read_json(output_dir / "run_config.json")
    strategy_results = read_json(output_dir / "strategy_results.json")
    benchmark_results = read_json(output_dir / "benchmark_results.json")
    limitations = read_json(output_dir / "limitations.json")
    summary = (output_dir / "backtest_summary.md").read_text(encoding="utf-8")

    assert run_config["import_result"]["rows_imported"] == 210
    assert run_config["strategies"] == ["hold_strategy", "macro_etf_strategy_v1", "momentum_strategy_v1"]
    assert run_config["benchmarks"] == ["CASH", "EQUAL_ETF", "CSI300"]
    assert set(strategy_results) == set(run_config["strategies"])
    assert all("admission" in row for row in strategy_results.values())
    assert set(benchmark_results["macro_etf_strategy_v1"]) == set(run_config["benchmarks"])
    assert isinstance(limitations["items"], list)
    assert "Historical ETF Backtest Summary" in summary
