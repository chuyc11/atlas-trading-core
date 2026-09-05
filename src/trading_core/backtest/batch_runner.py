"""Batch historical ETF backtest runner for validated local data packages."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.backtest.historical_backtester import run_historical_backtest
from trading_core.calendar.trading_calendar import require_a_share_calendar
from trading_core.data.data_package_validator import validate_data_package
from trading_core.data.historical_prices import import_prices_csv
from trading_core.evaluation.strategy_leaderboard import build_strategy_leaderboard
from trading_core.evolution.admission_gate import evaluate_admission
from trading_core.equity_data.adjusted_price import validate_adjusted_price_status
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


DEFAULT_STRATEGIES = ["hold_strategy", "macro_etf_strategy_v1", "momentum_strategy_v1"]
DEFAULT_BENCHMARKS = ["CASH", "EQUAL_ETF", "CSI300"]
INITIAL_CAPITAL = 100000.0


def run_backtest_batch(
    start_date: str,
    end_date: str,
    data_path: Path,
    paths: ProjectPaths | None = None,
    market: str = "A_SHARE",
    strategies: list[str] | None = None,
    timestamp: str | None = None,
    require_calendar: bool = True,
    allow_raw_price: bool = False,
) -> dict[str, Any]:
    paths = paths or project_paths()
    strategies = strategies or DEFAULT_STRATEGIES
    timestamp = timestamp or datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    output_dir = paths.outputs_dir / "backtests" / f"batch-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    validation = validate_data_package(data_path, paths, timestamp=timestamp)
    calendar_gate = require_a_share_calendar(paths=paths, market=market) if require_calendar else {"passed": True, "status": "degraded_allowed", "warning": None}
    adjusted_price_gate = (
        validate_adjusted_price_status(paths=paths, allow_raw_price=allow_raw_price)
        if market == "A_SHARE"
        else {"passed": True, "status": "not_required", "warning": None}
    )
    formal_gates = {"calendar": calendar_gate, "adjusted_price": adjusted_price_gate}
    gate_failures = [
        gate_name
        for gate_name, gate in formal_gates.items()
        if not bool(gate.get("passed"))
    ]
    gate_warnings = [str(gate["warning"]) for gate in formal_gates.values() if gate.get("warning")]
    effective_validation = {
        **validation,
        "passed": bool(validation["passed"]) and not gate_failures,
        "formal_gates": formal_gates,
        "warnings": sorted({*validation["warnings"], *gate_warnings}),
    }
    batch_config = {
        "start_date": start_date,
        "end_date": end_date,
        "data": str(data_path),
        "market": market,
        "strategies": strategies,
        "benchmarks": DEFAULT_BENCHMARKS,
        "require_calendar": require_calendar,
        "allow_raw_price": allow_raw_price,
        "formal_gates": formal_gates,
    }
    write_json(output_dir / "batch_config.json", batch_config)
    write_json(output_dir / "data_validation.json", effective_validation)

    if not effective_validation["passed"]:
        limitations = []
        if not validation["passed"]:
            limitations.append("data_validation_failed")
        limitations.extend(f"{gate_name}_gate_failed" for gate_name in gate_failures)
        payload = _empty_failed_batch(start_date, end_date, output_dir, effective_validation, batch_config, limitations=limitations)
        _write_batch_outputs(output_dir, payload)
        return payload

    import_result = import_prices_csv(data_path, market, paths)
    strategy_results: dict[str, Any] = {}
    benchmark_results: dict[str, Any] = {}
    admission_results: dict[str, Any] = {}
    limitations = list(effective_validation["warnings"])

    for strategy_id in strategies:
        result = run_historical_backtest(start_date, end_date, strategy_id, market=market, workspace_root=paths.workspace_root)
        portfolios = read_jsonl(Path(result["portfolio_path"]))
        trades = read_jsonl(Path(result["trades_path"]))
        benchmark = read_json(Path(result["benchmark_path"]), default={})
        metrics = _metrics(strategy_id, portfolios, trades, benchmark)
        admission = evaluate_admission(strategy_id, end_date, metrics["admission_metrics"])
        strategy_results[strategy_id] = {**result, **metrics}
        benchmark_results[strategy_id] = {
            benchmark_id: benchmark.get("benchmarks", {}).get(benchmark_id)
            for benchmark_id in DEFAULT_BENCHMARKS
        }
        admission_results[strategy_id] = admission
        limitations.extend(result.get("limitations", []))

    leaderboard = build_strategy_leaderboard(start_date, end_date, paths, strategies)
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "output_dir": str(output_dir),
        "batch_config": {**batch_config, "import_result": import_result},
        "data_validation": effective_validation,
        "strategy_results": strategy_results,
        "benchmark_results": benchmark_results,
        "admission_results": admission_results,
        "leaderboard": leaderboard,
        "best_strategy": _best_strategy(strategy_results),
        "worst_strategy": _worst_strategy(strategy_results),
        "limitations": sorted({str(item) for item in limitations}),
        "warnings": effective_validation["warnings"],
        "passed": True,
    }
    _write_batch_outputs(output_dir, payload)
    return payload


def _empty_failed_batch(
    start_date: str,
    end_date: str,
    output_dir: Path,
    validation: dict[str, Any],
    batch_config: dict[str, Any],
    *,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "start_date": start_date,
        "end_date": end_date,
        "output_dir": str(output_dir),
        "batch_config": batch_config,
        "data_validation": validation,
        "strategy_results": {},
        "benchmark_results": {},
        "admission_results": {},
        "leaderboard": {"items": []},
        "best_strategy": None,
        "worst_strategy": None,
        "limitations": limitations or ["data_validation_failed"],
        "warnings": validation["warnings"],
        "passed": False,
    }


def _metrics(
    strategy_id: str,
    portfolios: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    final = float(portfolios[-1]["total_asset"]) if portfolios else INITIAL_CAPITAL
    cumulative_return = (final / INITIAL_CAPITAL) - 1 if INITIAL_CAPITAL else 0.0
    max_drawdown = abs(min((float(row.get("max_drawdown", 0.0)) for row in portfolios), default=0.0))
    cost_total = sum(float(trade.get("commission", 0.0)) + float(trade.get("tax", 0.0)) for trade in trades)
    turnover = sum(float(trade.get("gross_amount", 0.0)) for trade in trades) / INITIAL_CAPITAL
    win_rate = _win_rate(portfolios)
    benchmark_cumulative = None
    if benchmark:
        benchmark_cumulative = benchmark.get("benchmark_cumulative_return", {}).get("EQUAL_ETF")
        if benchmark_cumulative is None:
            benchmark_cumulative = benchmark.get("benchmarks", {}).get("EQUAL_ETF", {}).get("cumulative_return")
    excess = cumulative_return - float(benchmark_cumulative) if benchmark_cumulative is not None else 0.0
    return {
        "strategy_id": strategy_id,
        "final_asset": round(final, 6),
        "cumulative_return": round(cumulative_return, 8),
        "max_drawdown": round(max_drawdown, 8),
        "trade_count": len(trades),
        "win_rate": round(win_rate, 6),
        "cost_total": round(cost_total, 6),
        "turnover": round(turnover, 8),
        "excess_return_equal_etf": round(excess, 8),
        "admission_metrics": {
            "backtest_days": len(portfolios),
            "trades": len(trades),
            "excess_return": excess,
            "max_drawdown": max_drawdown,
            "mistake_rate": 0.0 if excess >= 0 else min(1.0, 1 / max(1, len(portfolios))),
            "cost_ratio": cost_total / INITIAL_CAPITAL,
            "benchmark_comparison": bool(benchmark),
            "future_data_flag": False,
        },
    }


def _win_rate(portfolios: list[dict[str, Any]]) -> float:
    if not portfolios:
        return 0.0
    return sum(1 for row in portfolios if float(row.get("daily_return", 0.0)) > 0) / len(portfolios)


def _best_strategy(strategy_results: dict[str, Any]) -> str | None:
    if not strategy_results:
        return None
    return max(strategy_results.items(), key=lambda item: float(item[1]["excess_return_equal_etf"]))[0]


def _worst_strategy(strategy_results: dict[str, Any]) -> str | None:
    if not strategy_results:
        return None
    return min(strategy_results.items(), key=lambda item: float(item[1]["excess_return_equal_etf"]))[0]


def _write_batch_outputs(output_dir: Path, payload: dict[str, Any]) -> None:
    write_json(output_dir / "batch_config.json", payload["batch_config"])
    write_json(output_dir / "data_validation.json", payload["data_validation"])
    write_json(output_dir / "strategy_results.json", payload["strategy_results"])
    write_json(output_dir / "benchmark_results.json", payload["benchmark_results"])
    write_json(output_dir / "admission_results.json", payload["admission_results"])
    write_json(output_dir / "leaderboard.json", payload["leaderboard"])
    (output_dir / "BACKTEST_BATCH_REPORT.md").write_text(_markdown_report(payload), encoding="utf-8")


def _markdown_report(payload: dict[str, Any]) -> str:
    validation = payload["data_validation"]
    lines = [
        f"# Backtest Batch Report {payload['start_date']} to {payload['end_date']}",
        "",
        "## Data Coverage",
        f"- Rows: {validation['total_rows']}",
        f"- Symbols: {validation['symbols_count']}",
        f"- Date range: {validation['date_range']['start']} to {validation['date_range']['end']}",
        "",
        "## Data Quality",
        f"- Passed: {validation['passed']}",
        f"- Missing values: {validation['missing_values_count']}",
        f"- Duplicate records: {validation['duplicate_records_count']}",
        f"- OHLC anomalies: {validation['ohlc_anomaly_count']}",
        f"- Suspicious returns: {validation['suspicious_return_count']}",
        f"- Quality distribution: {validation['quality_distribution']}",
        "",
        "## Strategy Results",
    ]
    for strategy_id, result in payload["strategy_results"].items():
        admission = payload["admission_results"].get(strategy_id, {})
        lines.extend(
            [
                f"### {strategy_id}",
                f"- cumulative_return: {result['cumulative_return']}",
                f"- max_drawdown: {result['max_drawdown']}",
                f"- trade_count: {result['trade_count']}",
                f"- win_rate: {result['win_rate']}",
                f"- cost_total: {result['cost_total']}",
                f"- turnover: {result['turnover']}",
                f"- excess_return vs EQUAL_ETF: {result['excess_return_equal_etf']}",
                f"- admission decision: {admission.get('status')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Strategy Leaderboard",
            "| Rank | Strategy | Excess return | Recommendation |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for item in payload["leaderboard"].get("items", []):
        lines.append(f"| {item['rank']} | {item['strategy_id']} | {item['excess_return']} | {item['recommendation']} |")
    lines.extend(
        [
            "",
            f"- Best strategy: {payload['best_strategy']}",
            f"- Worst strategy: {payload['worst_strategy']}",
            "",
            "## Limitations And Warnings",
        ]
    )
    if payload["limitations"] or payload["warnings"]:
        lines.extend(f"- {item}" for item in [*payload["limitations"], *payload["warnings"]])
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"
