"""Export compact trading summaries for global-briefing ingestion."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


def export_trading_summary(date: str, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    limitations = []
    portfolio_path = paths.dated_json("portfolios", "portfolio", date)
    benchmark_path = paths.dated_json("benchmarks", "benchmark", date)
    attribution_path = paths.dated_json("attribution", "attribution", date)
    evolution_path = paths.data_dir / "evolution" / f"evolution-summary-{date}.json"
    trades_path = paths.dated_jsonl("trades", "trades", date)
    orders_path = paths.dated_jsonl("orders", "orders", date)

    portfolio = read_json(portfolio_path, default={})
    benchmark = read_json(benchmark_path, default={})
    attribution = read_json(attribution_path, default={})
    evolution = read_json(evolution_path, default={})
    trades = read_jsonl(trades_path)
    orders = read_jsonl(orders_path)

    for name, payload in [
        ("portfolio", portfolio),
        ("benchmark", benchmark),
        ("attribution", attribution),
        ("evolution", evolution),
    ]:
        if not payload:
            limitations.append(f"missing_{name}")

    positions = portfolio.get("positions", [])
    top_positions = sorted(positions, key=lambda row: float(row.get("market_value", 0.0)), reverse=True)[:5]
    summary = {
        "date": date,
        "account_id": portfolio.get("account_id"),
        "total_asset": portfolio.get("total_asset"),
        "daily_return": portfolio.get("daily_return"),
        "cumulative_return": portfolio.get("cumulative_return"),
        "cash": portfolio.get("cash"),
        "market_value": portfolio.get("market_value"),
        "positions_count": len(positions),
        "trades_count": len(trades),
        "rejected_orders_count": len([order for order in orders if order.get("status") == "rejected"]),
        "top_positions": top_positions,
        "benchmark_summary": {
            "portfolio_return": benchmark.get("portfolio_return"),
            "excess_return": benchmark.get("excess_return", {}),
        },
        "attribution_summary": {
            "total_pnl": attribution.get("total_pnl"),
            "residual_pnl": attribution.get("residual_pnl"),
            "benchmark_relative": attribution.get("benchmark_relative", {}),
        },
        "evolution_summary": {
            "mistake_count": len(evolution.get("mistakes", [])),
            "experiment_queue_count": evolution.get("experiment_queue_count"),
            "promotion_recommendation": evolution.get("promotion_recommendation"),
        },
        "limitations": limitations,
        "report_path": str(paths.daily_report(date)),
    }
    write_json(paths.dated_json("exports", "trading_summary", date), summary)
    return summary
