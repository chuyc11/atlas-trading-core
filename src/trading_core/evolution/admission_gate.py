"""Strategy admission gate for active-state protection."""

from __future__ import annotations

from typing import Any

from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_json


def evaluate_admission(
    strategy_id: str,
    date: str,
    metrics: dict[str, Any],
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = rules or load_config("admission_rules.yaml")
    failed = []
    if int(metrics.get("backtest_days", 0)) < int(rules["min_backtest_days"]):
        failed.append("min_backtest_days")
    if int(metrics.get("trades", 0)) < int(rules["min_trades"]):
        failed.append("min_trades")
    if rules["require_positive_excess_return"] and float(metrics.get("excess_return", 0.0)) <= 0:
        failed.append("require_positive_excess_return")
    if abs(float(metrics.get("max_drawdown", 0.0))) > float(rules["max_drawdown"]):
        failed.append("max_drawdown")
    if float(metrics.get("mistake_rate", 0.0)) > float(rules["max_mistake_rate"]):
        failed.append("max_mistake_rate")
    if float(metrics.get("cost_ratio", 0.0)) > float(rules["max_cost_ratio"]):
        failed.append("max_cost_ratio")
    if rules["require_benchmark_comparison"] and not metrics.get("benchmark_comparison"):
        failed.append("require_benchmark_comparison")
    if rules["require_no_future_data_flag"] and bool(metrics.get("future_data_flag", True)):
        failed.append("require_no_future_data_flag")

    passed = not failed
    status = "shadow_allowed" if passed else "rejected"
    recommendation = "allow_shadow_only" if passed else "keep_candidate"
    return {
        "strategy_id": strategy_id,
        "date": date,
        "status": status,
        "passed": passed,
        "failed_rules": failed,
        "metrics": metrics,
        "recommendation": recommendation,
        "auto_applied": False,
    }


def run_admission(
    strategy_id: str,
    date: str,
    metrics: dict[str, Any] | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    metrics = metrics or _load_metrics_from_files(strategy_id, date, paths)
    decision = evaluate_admission(strategy_id, date, metrics)
    write_json(paths.data_dir / "evolution" / f"admission_decision-{date}.json", decision)
    return decision


def _load_metrics_from_files(strategy_id: str, date: str, paths: ProjectPaths) -> dict[str, Any]:
    scorecard = read_json(paths.dated_json("evolution", "strategy_scorecard", date), default={})
    strategy_row = next((row for row in scorecard.get("items", []) if row.get("strategy_id") == strategy_id), {})
    return {
        "backtest_days": int(strategy_row.get("backtest_days", 0)),
        "trades": int(strategy_row.get("trade_count", strategy_row.get("signal_count", 0))),
        "excess_return": float(strategy_row.get("avg_excess_return", 0.0)),
        "max_drawdown": abs(float(strategy_row.get("max_drawdown", 0.0))),
        "mistake_rate": float(strategy_row.get("error_rate", 1.0)),
        "cost_ratio": float(strategy_row.get("cost_ratio", 1.0)),
        "benchmark_comparison": bool(strategy_row.get("benchmark_comparison", False)),
        "future_data_flag": bool(strategy_row.get("future_data_flag", True)),
    }
