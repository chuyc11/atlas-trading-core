"""Benchmark comparison for baseline strategy isolated replays."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import write_json_markdown

from .baseline_strategy_replay import replay_baseline_strategy
from .common import (
    DEFAULT_BENCHMARKS,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    RESEARCH_NOTICE,
    annualized_return,
    annualized_volatility,
    benchmark_path,
    benchmark_report_path,
    load_price_history,
    max_drawdown,
    paths_or_default,
    price_on_or_before,
    read_dict,
    read_rows,
    rel,
    replay_summary_path,
    research_boundary,
    selected_strategies,
    trading_dates,
)


BENCHMARK_PROXIES = {
    "CSI300": ["510300.SH"],
    "CSI500": ["512880.SH"],
    "CSI1000": ["512660.SH"],
    "CHINEXT": ["159915.SZ"],
    "HSI": ["2800.HK"],
    "HSTECH": ["3033.HK"],
    "EQUAL_ETF": ["510300.SH", "159915.SZ", "588000.SH", "512480.SH", "512660.SH", "512880.SH", "2800.HK", "3033.HK"],
}


def compare_baseline_strategy_benchmarks(
    *,
    strategy: str = "all",
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    for strategy_id in selected_strategies(strategy):
        if not replay_summary_path(paths, strategy_id, start_date, end_date).exists():
            replay_baseline_strategy(strategy=strategy_id, start_date=start_date, end_date=end_date, execution_mode="isolated", paths=paths)
    prices, price_source = load_price_history(paths, start_date=start_date, end_date=end_date)
    benchmark_results = _benchmarks(prices, start_date, end_date)
    strategy_results = {}
    for strategy_id in selected_strategies(strategy):
        summary = read_dict(replay_summary_path(paths, strategy_id, start_date, end_date))
        valuations = read_rows(paths.project_root / str(summary.get("valuations_path", "")))
        strategy_results[strategy_id] = _strategy_metrics(strategy_id, summary, valuations, benchmark_results)
    payload: dict[str, Any] = {
        "comparison_id": f"BASELINE-BENCHMARK-COMPARISON-{start_date}-{end_date}",
        "start_date": start_date,
        "end_date": end_date,
        "strategies": strategy_results,
        "benchmarks": benchmark_results,
        "benchmark_source": price_source,
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
        "live_trading_ready": False,
        "boundary": research_boundary("benchmark_comparison_only"),
    }
    json_path = benchmark_path(paths, start_date, end_date)
    md_path = benchmark_report_path(paths, start_date, end_date)
    write_json_markdown(json_path, payload, md_path, build_markdown(payload, paths))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _strategy_metrics(strategy_id: str, summary: dict[str, Any], valuations: list[dict[str, Any]], benchmarks: dict[str, Any]) -> dict[str, Any]:
    assets = [float(row.get("total_asset", 0.0)) for row in valuations if float(row.get("total_asset", 0.0)) > 0]
    returns = [current / previous - 1.0 for previous, current in zip(assets, assets[1:]) if previous]
    cumulative = assets[-1] / assets[0] - 1.0 if len(assets) >= 2 and assets[0] else 0.0
    cost_summary = summary.get("cost_summary", {})
    initial_asset = assets[0] if assets else 1.0
    cost_drag = sum(float(cost_summary.get(key, 0.0)) for key in ["commission", "tax", "slippage"]) / initial_asset
    comparison = {
        "cumulative_return": round(cumulative, 8),
        "annualized_return": round(annualized_return(cumulative, len(assets)), 8),
        "annualized_volatility": round(annualized_volatility(returns), 8),
        "max_drawdown": round(max_drawdown(assets), 8),
        "turnover": round(float(summary.get("trades", 0)) / max(float(summary.get("orders", 1)), 1.0), 8),
        "cost_drag": round(cost_drag, 8),
        "benchmark_relative_return": {},
        "active_days": len(assets),
        "rejected_order_count": int(summary.get("rejected_orders", 0)),
        "no_trade_days": max(len(assets) - int(summary.get("trades", 0)), 0),
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
    }
    for name, benchmark in benchmarks.items():
        comparison["benchmark_relative_return"][name] = (
            round(cumulative - float(benchmark.get("cumulative_return", 0.0)), 8)
            if benchmark.get("available")
            else {"missing_reason": benchmark.get("missing_reason")}
        )
    return comparison


def _benchmarks(prices: dict[str, dict[str, float]], start_date: str, end_date: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in DEFAULT_BENCHMARKS:
        if name == "CASH":
            output[name] = {"available": True, "cumulative_return": 0.0, "annualized_return": 0.0, "annualized_volatility": 0.0, "max_drawdown": 0.0}
            continue
        proxies = BENCHMARK_PROXIES.get(name, [])
        values = []
        for day in trading_dates(start_date, end_date):
            day_prices = []
            for symbol in proxies:
                _, price = price_on_or_before(prices, symbol, day)
                if price is not None:
                    day_prices.append(price)
            if day_prices:
                values.append(sum(day_prices) / len(day_prices))
        if len(values) < 2:
            output[name] = {"available": False, "missing_reason": "insufficient_proxy_price_history"}
            continue
        returns = [current / previous - 1.0 for previous, current in zip(values, values[1:]) if previous]
        cumulative = values[-1] / values[0] - 1.0
        output[name] = {
            "available": True,
            "proxy_symbols": proxies,
            "cumulative_return": round(cumulative, 8),
            "annualized_return": round(annualized_return(cumulative, len(values)), 8),
            "annualized_volatility": round(annualized_volatility(returns), 8),
            "max_drawdown": round(max_drawdown(values), 8),
        }
    return output


def build_markdown(payload: dict[str, Any], paths: ProjectPaths) -> str:
    lines = [
        "# Baseline Benchmark Comparison",
        "",
        RESEARCH_NOTICE,
        "",
        "## Strategies",
    ]
    for strategy_id, metrics in payload["strategies"].items():
        lines.append(f"- {strategy_id}: cumulative_return={metrics['cumulative_return']}, max_drawdown={metrics['max_drawdown']}")
    lines.extend(
        [
            "",
            "## Benchmarks",
            ", ".join(payload["benchmarks"].keys()),
            "",
            "## Boundary",
            "- benchmark comparison only",
            "- run-daily not called",
            "- forward dry-run not started",
            "- main ledger not written",
            "- no promotion",
            "- not strategy effectiveness proof",
            "- not live trading readiness",
            "",
        ]
    )
    return "\n".join(lines)

