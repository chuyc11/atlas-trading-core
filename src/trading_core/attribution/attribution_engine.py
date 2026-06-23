"""Basic return attribution."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


def build_attribution(
    date: str,
    portfolio: dict[str, Any],
    trades: list[dict[str, Any]],
    benchmark: dict[str, Any],
    previous_portfolio: dict[str, Any] | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    total_asset = float(portfolio.get("total_asset") or 0.0)
    previous_total_asset = _previous_total_asset(portfolio, previous_portfolio)
    total_pnl = total_asset - previous_total_asset
    holding_contrib = {}
    strategy_contrib: dict[str, float] = defaultdict(float)
    previous_positions = {
        str(position["symbol"]): position
        for position in (previous_portfolio or {}).get("positions", [])
    }
    holding_pnl = 0.0
    for position in portfolio.get("positions", []):
        symbol = position["symbol"]
        previous = previous_positions.get(str(symbol))
        if previous:
            symbol_holding_pnl = (
                float(position.get("current_price", 0.0)) - float(previous.get("current_price", 0.0))
            ) * int(previous.get("quantity", 0))
        else:
            symbol_holding_pnl = 0.0
        holding_pnl += symbol_holding_pnl
        contribution = symbol_holding_pnl / previous_total_asset if previous_total_asset else 0.0
        holding_contrib[symbol] = round(contribution, 8)
        strategy_contrib[str(position.get("strategy_id", "unknown"))] += contribution

    trading_cost = sum(float(trade.get("commission", 0.0)) + float(trade.get("tax", 0.0)) for trade in trades)
    cost_impact = -trading_cost
    cash_and_flow_impact = total_pnl - holding_pnl - cost_impact
    explained_pnl = holding_pnl + cash_and_flow_impact + cost_impact
    residual = total_pnl - explained_pnl
    payload = {
        "date": date,
        "account_id": portfolio.get("account_id"),
        "portfolio_return": portfolio.get("daily_return", 0.0),
        "previous_total_asset": round(previous_total_asset, 6),
        "total_pnl": round(total_pnl, 6),
        "holding_pnl": round(holding_pnl, 6),
        "cash_and_flow_impact": round(cash_and_flow_impact, 6),
        "trading_cost": round(trading_cost, 6),
        "cost_impact": round(cost_impact, 6),
        "explained_pnl": round(explained_pnl, 6),
        "residual_pnl": round(residual, 6),
        "holding_contribution": holding_contrib,
        "strategy_contribution": {key: round(value, 8) for key, value in strategy_contrib.items()},
        "benchmark_relative": benchmark.get("excess_return", {}),
    }
    paths = paths or project_paths()
    write_json(paths.dated_json("attribution", "attribution", date), payload)
    return payload


def _previous_total_asset(
    portfolio: dict[str, Any],
    previous_portfolio: dict[str, Any] | None,
) -> float:
    if previous_portfolio and previous_portfolio.get("total_asset") not in (None, 0):
        return float(previous_portfolio["total_asset"])
    daily_return = float(portfolio.get("daily_return", 0.0))
    total_asset = float(portfolio.get("total_asset") or 0.0)
    if daily_return == -1:
        return total_asset
    return total_asset / (1 + daily_return) if daily_return else total_asset
