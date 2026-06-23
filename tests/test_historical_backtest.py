from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from trading_core.backtest.historical_backtester import run_historical_backtest
from trading_core.data.historical_prices import import_prices_csv
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl


def _write_price_csv(path: Path, days: int = 30) -> None:
    start = date(2026, 1, 1)
    current = start
    rows = ["date,symbol,open,high,low,close,volume,source,quality"]
    business_days = 0
    while business_days < days:
        if current.weekday() < 5:
            idx = business_days
            for symbol, base, slope in [
                ("510300.SH", 4.0, 0.01),
                ("159915.SZ", 2.0, 0.02),
                ("000300.SH", 5000.0, 5.0),
            ]:
                open_price = base + idx * slope
                close_price = open_price + slope / 2
                rows.append(
                    f"{current.isoformat()},{symbol},{open_price:.4f},{close_price:.4f},{open_price:.4f},{close_price:.4f},100000,test,fresh"
                )
            business_days += 1
        current += timedelta(days=1)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_import_prices_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    _write_price_csv(csv_path, days=3)
    result = import_prices_csv(csv_path, "A_SHARE", project_paths(tmp_path))
    assert result["rows_imported"] == 9
    assert Path(result["output_path"]).exists()


def test_historical_backtest_t_plus_one_outputs_and_no_future_data(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    _write_price_csv(csv_path, days=30)
    paths = project_paths(tmp_path)
    import_prices_csv(csv_path, "A_SHARE", paths)

    result = run_historical_backtest("2026-01-01", "2026-02-11", "momentum_strategy_v1", workspace_root=tmp_path)

    trades = read_jsonl(Path(result["trades_path"]))
    portfolios = read_jsonl(Path(result["portfolio_path"]))
    benchmark = read_json(Path(result["benchmark_path"]))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert Path(result["trades_path"]).name == "backtest_trades-2026-01-01-2026-02-11-momentum_strategy_v1.jsonl"
    assert portfolios
    assert benchmark["benchmarks"]["EQUAL_ETF"]["return"] is not None
    assert "Cumulative return" in report
    assert "Benchmark comparison" in report
    assert all(trade["signal_date"] < trade["date"] for trade in trades)


def test_historical_backtest_strategy_outputs_are_separate(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    _write_price_csv(csv_path, days=25)
    import_prices_csv(csv_path, "A_SHARE", project_paths(tmp_path))

    macro = run_historical_backtest("2026-01-01", "2026-02-04", "macro_etf_strategy_v1", workspace_root=tmp_path)
    hold = run_historical_backtest("2026-01-01", "2026-02-04", "hold_strategy", workspace_root=tmp_path)

    assert macro["trades_path"] != hold["trades_path"]
    assert Path(macro["report_path"]).exists()
    assert Path(hold["report_path"]).exists()
