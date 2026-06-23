from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from trading_core.backtest.historical_backtester import run_historical_backtest
from trading_core.data.historical_prices import import_prices_csv, load_imported_prices
from trading_core.evolution.admission_gate import evaluate_admission
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


STRATEGIES = ["hold_strategy", "macro_etf_strategy_v1", "momentum_strategy_v1"]
BENCHMARKS = ["CASH", "EQUAL_ETF", "CSI300"]


def run_backtest_runbook(
    input_path: Path,
    start_date: str,
    end_date: str,
    market: str = "A_SHARE",
    workspace_root: Path | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    paths = project_paths(workspace_root)
    timestamp = timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = paths.outputs_dir / "backtests" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    import_result = import_prices_csv(input_path, market, paths)
    imported = load_imported_prices(market, paths)
    coverage = _coverage(imported)
    strategy_results: dict[str, Any] = {}
    benchmark_results: dict[str, Any] = {}
    limitations: dict[str, Any] = {"items": []}

    for strategy in STRATEGIES:
        result = run_historical_backtest(start_date, end_date, strategy, market=market, workspace_root=paths.workspace_root)
        portfolio_rows = read_jsonl(Path(result["portfolio_path"]))
        trades = read_jsonl(Path(result["trades_path"]))
        benchmark = read_json(Path(result["benchmark_path"]), default={})
        metrics = _strategy_metrics(strategy, portfolio_rows, trades, benchmark)
        admission = evaluate_admission(strategy, end_date, metrics["admission_metrics"])
        strategy_results[strategy] = {
            **result,
            **metrics,
            "admission": admission,
        }
        benchmark_results[strategy] = {key: benchmark.get("benchmarks", {}).get(key) for key in BENCHMARKS}
        limitations["items"].extend(result.get("limitations", []))

    run_config = {
        "input": str(input_path),
        "start_date": start_date,
        "end_date": end_date,
        "market": market,
        "strategies": STRATEGIES,
        "benchmarks": BENCHMARKS,
        "import_result": import_result,
        "data_coverage": coverage,
    }
    write_json(output_dir / "run_config.json", run_config)
    write_json(output_dir / "strategy_results.json", strategy_results)
    write_json(output_dir / "benchmark_results.json", benchmark_results)
    write_json(output_dir / "limitations.json", limitations)
    (output_dir / "backtest_summary.md").write_text(
        _summary_markdown(start_date, end_date, coverage, strategy_results, benchmark_results, limitations),
        encoding="utf-8",
    )
    return {"output_dir": str(output_dir), "run_config": run_config, "strategy_results": strategy_results}


def _coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dates = sorted({row["date"] for row in rows})
    symbols = sorted({row["symbol"] for row in rows})
    missing = 0
    for date in dates:
        present = {row["symbol"] for row in rows if row["date"] == date}
        missing += len(set(symbols) - present)
    return {"start": dates[0] if dates else None, "end": dates[-1] if dates else None, "rows": len(rows), "symbols": symbols, "missing_symbol_days": missing}


def _strategy_metrics(strategy: str, portfolios: list[dict[str, Any]], trades: list[dict[str, Any]], benchmark: dict[str, Any]) -> dict[str, Any]:
    initial = 100000.0
    final = float(portfolios[-1]["total_asset"]) if portfolios else initial
    total_return = (final / initial) - 1 if initial else 0.0
    max_drawdown = abs(min((float(row.get("max_drawdown", 0.0)) for row in portfolios), default=0.0))
    cost = sum(float(trade.get("commission", 0.0)) + float(trade.get("tax", 0.0)) for trade in trades)
    trade_count = len(trades)
    excess = benchmark.get("excess_return", {}).get("EQUAL_ETF", 0.0) if benchmark else 0.0
    metrics = {
        "total_return": round(total_return, 8),
        "max_drawdown": round(max_drawdown, 8),
        "trade_count": trade_count,
        "total_cost": round(cost, 6),
        "excess_return": excess,
        "admission_metrics": {
            "backtest_days": len(portfolios),
            "trades": trade_count,
            "excess_return": excess,
            "max_drawdown": max_drawdown,
            "mistake_rate": 0.0,
            "cost_ratio": cost / initial if initial else 1.0,
            "benchmark_comparison": bool(benchmark),
            "future_data_flag": False,
        },
    }
    return metrics


def _summary_markdown(start_date: str, end_date: str, coverage: dict[str, Any], strategy_results: dict[str, Any], benchmark_results: dict[str, Any], limitations: dict[str, Any]) -> str:
    lines = [
        f"# Historical ETF Backtest Summary {start_date} to {end_date}",
        "",
        "## Data Coverage",
        f"- Rows: {coverage['rows']}",
        f"- Symbols: {coverage['symbols']}",
        f"- Missing symbol-days: {coverage['missing_symbol_days']}",
        "",
        "## Strategy Results",
    ]
    for strategy, result in strategy_results.items():
        lines.extend(
            [
                f"### {strategy}",
                f"- Total return: {result['total_return']}",
                f"- Max drawdown: {result['max_drawdown']}",
                f"- Trade count: {result['trade_count']}",
                f"- Cost: {result['total_cost']}",
                f"- Admission: {result['admission']['status']}",
            ]
        )
    lines.extend(["", "## Benchmark Results", json.dumps(benchmark_results, ensure_ascii=False, indent=2), "", "## Limitations", json.dumps(limitations, ensure_ascii=False, indent=2)])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--market", default="A_SHARE")
    args = parser.parse_args()
    result = run_backtest_runbook(Path(args.input), args.start_date, args.end_date, args.market)
    print(result["output_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
