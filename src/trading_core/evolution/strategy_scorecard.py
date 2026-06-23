"""Aggregate strategy-level performance."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


def score_strategies(
    date: str,
    scorecard: dict[str, Any],
    trades: list[dict[str, Any]],
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    by_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in scorecard.get("items", []):
        by_strategy[str(item.get("strategy_id"))].append(item)

    costs_by_signal = {
        trade.get("signal_id"): float(trade.get("commission", 0.0)) + float(trade.get("tax", 0.0))
        for trade in trades
    }

    items = []
    for strategy_id, rows in by_strategy.items():
        returns = [float(row.get("excess_return", 0.0)) for row in rows]
        wrong_count = sum(1 for row in rows if row.get("status") == "wrong")
        win_count = sum(1 for row in rows if row.get("status") == "validated")
        cost = sum(costs_by_signal.get(row.get("signal_id"), 0.0) for row in rows)
        error_rate = wrong_count / len(rows) if rows else 0.0
        avg_excess = mean(returns) if returns else 0.0
        if error_rate > 0.3 or avg_excess < -0.003:
            recommendation = "pause_or_shadow"
        elif avg_excess > 0 and len(rows) >= 10:
            recommendation = "consider_promotion"
        else:
            recommendation = "keep_observing"
        items.append(
            {
                "strategy_id": strategy_id,
                "signal_count": len(rows),
                "win_rate": round(win_count / len(rows), 6) if rows else 0.0,
                "avg_excess_return": round(avg_excess, 8),
                "error_rate": round(error_rate, 6),
                "cost": round(cost, 6),
                "status_recommendation": recommendation,
            }
        )
    payload = {"date": date, "items": items}
    paths = paths or project_paths()
    write_json(paths.dated_json("evolution", "strategy_scorecard", date), payload)
    return payload
