"""Score trading signals against portfolio and benchmark outcomes."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json


def score_signals(
    date: str,
    signals: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    valuation: dict[str, Any],
    benchmark: dict[str, Any],
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    traded_signal_ids = {trade.get("signal_id") for trade in trades}
    benchmark_return = float(benchmark.get("benchmarks", {}).get("EQUAL_ETF", {}).get("return", 0.0))
    portfolio_return = float(valuation.get("daily_return", 0.0))
    excess = portfolio_return - benchmark_return
    rows = []
    for signal in signals:
        status = "open"
        if signal.get("side") == "HOLD":
            status = "open"
        elif signal.get("signal_id") in traded_signal_ids:
            if excess > 0:
                status = "validated"
            elif excess <= -0.003:
                status = "wrong"
            elif excess < 0:
                status = "partial"
            else:
                status = "open"
        rows.append(
            {
                "signal_id": signal.get("signal_id"),
                "date": date,
                "strategy_id": signal.get("strategy_id"),
                "symbol": signal.get("symbol"),
                "side": signal.get("side"),
                "confidence": signal.get("confidence", 0.0),
                "portfolio_return": round(portfolio_return, 8),
                "benchmark_return": round(benchmark_return, 8),
                "excess_return": round(excess, 8),
                "status": status,
                "risk_flags": signal.get("risk_flags", []),
            }
        )
    payload = {"date": date, "items": rows}
    paths = paths or project_paths()
    write_json(paths.dated_json("evolution", "signal_scorecard", date), payload)
    return payload
