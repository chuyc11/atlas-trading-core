"""Build read-only strategy leaderboards from backtest artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.config_loader import load_config
from trading_core.evolution.admission_gate import evaluate_admission
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


DEFAULT_INITIAL_CAPITAL = 100000.0


def build_strategy_leaderboard(
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    strategy_ids: list[str] | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    rules = load_config("admission_rules.yaml")
    discovered = strategy_ids or _discover_strategy_ids(paths, start_date, end_date)
    items = [
        _build_strategy_row(paths, start_date, end_date, strategy_id, rules)
        for strategy_id in discovered
    ]
    items = sorted(
        items,
        key=lambda row: (
            bool(row["rank_eligible"]),
            float(row["excess_return"]),
            float(row["total_return"]),
            -float(row["max_drawdown"]),
        ),
        reverse=True,
    )
    for rank, row in enumerate(items, 1):
        row["rank"] = rank

    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "items": items,
        "limitations": _leaderboard_limitations(items),
        "auto_strategy_status_mutation": False,
    }
    json_path = paths.data_dir / "evaluation" / f"strategy_leaderboard-{start_date}-{end_date}.json"
    report_path = paths.outputs_dir / f"strategy-leaderboard-{start_date}-{end_date}.md"
    write_json(json_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    return payload


def _discover_strategy_ids(paths: ProjectPaths, start_date: str, end_date: str) -> list[str]:
    prefix = f"backtest_portfolio-{start_date}-{end_date}-"
    result = []
    for path in sorted((paths.data_dir / "backtests").glob(f"{prefix}*.jsonl")):
        result.append(path.stem.removeprefix(prefix))
    return result


def _build_strategy_row(
    paths: ProjectPaths,
    start_date: str,
    end_date: str,
    strategy_id: str,
    rules: dict[str, Any],
) -> dict[str, Any]:
    suffix = f"{start_date}-{end_date}-{strategy_id}"
    portfolio_path = paths.data_dir / "backtests" / f"backtest_portfolio-{suffix}.jsonl"
    trades_path = paths.data_dir / "backtests" / f"backtest_trades-{suffix}.jsonl"
    benchmark_path = paths.data_dir / "backtests" / f"backtest_benchmark-{suffix}.json"
    portfolios = read_jsonl(portfolio_path)
    trades = read_jsonl(trades_path)
    benchmark = read_json(benchmark_path, default={})

    initial = DEFAULT_INITIAL_CAPITAL
    final = float(portfolios[-1]["total_asset"]) if portfolios else initial
    total_return = (final / initial) - 1 if initial else 0.0
    max_drawdown = abs(min((float(row.get("max_drawdown", 0.0)) for row in portfolios), default=0.0))
    trade_count = len(trades)
    cost = sum(float(row.get("commission", 0.0)) + float(row.get("tax", 0.0)) for row in trades)
    benchmark_available = bool(benchmark and benchmark.get("benchmarks"))
    excess_return = float(benchmark.get("excess_return", {}).get("EQUAL_ETF", 0.0)) if benchmark_available else 0.0
    win_rate = _win_rate(portfolios)
    mistake_rate = _mistake_rate(portfolios, excess_return, benchmark_available)
    cost_ratio = cost / initial if initial else 1.0
    metrics = {
        "backtest_days": len(portfolios),
        "trades": trade_count,
        "excess_return": excess_return,
        "max_drawdown": max_drawdown,
        "mistake_rate": mistake_rate,
        "cost_ratio": cost_ratio,
        "benchmark_comparison": benchmark_available,
        "future_data_flag": False,
    }
    admission = evaluate_admission(strategy_id, end_date, metrics, rules)
    rank_eligible = bool(
        benchmark_available
        and len(portfolios) >= int(rules["min_backtest_days"])
        and trade_count >= int(rules["min_trades"])
    )
    return {
        "strategy_id": strategy_id,
        "total_return": round(total_return, 8),
        "excess_return": round(excess_return, 8),
        "max_drawdown": round(max_drawdown, 8),
        "win_rate": round(win_rate, 6),
        "trade_count": trade_count,
        "cost_ratio": round(cost_ratio, 8),
        "mistake_rate": round(mistake_rate, 6),
        "admission_status": admission["status"],
        "recommendation": _recommendation(benchmark_available, rank_eligible, admission),
        "rank_eligible": rank_eligible,
        "benchmark_available": benchmark_available,
        "backtest_days": len(portfolios),
        "failed_rules": admission["failed_rules"],
        "auto_applied": False,
        "artifact_paths": {
            "portfolio": str(portfolio_path),
            "trades": str(trades_path),
            "benchmark": str(benchmark_path),
        },
    }


def _win_rate(portfolios: list[dict[str, Any]]) -> float:
    if not portfolios:
        return 0.0
    wins = sum(1 for row in portfolios if float(row.get("daily_return", 0.0)) > 0)
    return wins / len(portfolios)


def _mistake_rate(portfolios: list[dict[str, Any]], excess_return: float, benchmark_available: bool) -> float:
    if not portfolios:
        return 1.0
    negative_days = sum(1 for row in portfolios if float(row.get("daily_return", 0.0)) < 0)
    rate = negative_days / len(portfolios)
    if benchmark_available and excess_return <= -0.003:
        rate = max(rate, 1 / len(portfolios))
    return rate


def _recommendation(benchmark_available: bool, rank_eligible: bool, admission: dict[str, Any]) -> str:
    if not benchmark_available:
        return "not_recommended_missing_benchmark"
    if not rank_eligible:
        return "insufficient_sample"
    if admission["passed"]:
        return "candidate_for_shadow_review"
    return "not_recommended_failed_admission"


def _leaderboard_limitations(items: list[dict[str, Any]]) -> list[str]:
    limitations = []
    for item in items:
        if not item["benchmark_available"]:
            limitations.append(f"{item['strategy_id']}: missing_benchmark")
        if not item["rank_eligible"]:
            limitations.append(f"{item['strategy_id']}: not_rank_eligible")
    return limitations


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Strategy Leaderboard {payload['start_date']} to {payload['end_date']}",
        "",
        "| Rank | Strategy | Total return | Excess return | Max drawdown | Win rate | Trades | Cost ratio | Mistake rate | Admission | Recommendation |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in payload["items"]:
        lines.append(
            "| {rank} | {strategy_id} | {total_return} | {excess_return} | {max_drawdown} | {win_rate} | {trade_count} | {cost_ratio} | {mistake_rate} | {admission_status} | {recommendation} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "- Read-only evaluation artifact.",
            "- No strategy status mutation.",
            "- No broker connection or live trading.",
            "",
            "## Limitations",
        ]
    )
    if payload["limitations"]:
        lines.extend(f"- {item}" for item in payload["limitations"])
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
