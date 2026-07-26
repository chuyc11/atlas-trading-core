"""Parameter sweep runner for shadow strategy experiments.

This module implements an offline parameter sweep evaluator for rule-based
strategies. It is designed for shadow experiments only and does NOT write
to the main ledger, orders, trades, or portfolio.

IMPORTANT: This is an approximate shadow evaluator, not a formal backtest.
Results are heuristic and should not be used for strategy promotion.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any

from trading_core.experiments.experiment_registry import (
    ALLOWED_MODES,
    REQUIRED_FALSE_CONSTRAINTS,
    REQUIRED_TRUE_CONSTRAINTS,
    ExperimentValidationError,
    _contains_forbidden_keyword,
)

# Safety constants
ALLOWED_STRATEGY_IDS = {"momentum_strategy_v1"}
MAX_PARAMETER_COMBINATIONS = 500
MAX_TARGET_WEIGHT = 0.20

# Cost assumptions (approximate)
COMMISSION_PER_TRADE = 5.0  # CNY per trade
SPREAD_RATE = 0.001  # 0.1% spread cost


class ParameterSweepValidationError(ExperimentValidationError):
    """Raised when parameter sweep config is invalid."""
    pass


@dataclass
class SweepRunResult:
    """Result of a single parameter sweep run."""
    run_id: str
    parameters: dict[str, Any]
    total_return: float
    excess_return_vs_equal_etf: float
    max_drawdown: float
    trade_count: int
    turnover: float
    cost_total: float
    cost_ratio: float
    score: float
    status: str = "shadow_result"


def load_price_data(data_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Load daily price data from CSV files.

    Args:
        data_path: Path to directory containing symbol CSV files.

    Returns:
        Dictionary mapping symbol to list of price records sorted by date.
    """
    data_path = Path(data_path)
    prices: dict[str, list[dict[str, Any]]] = {}

    for csv_file in sorted(data_path.glob("*.csv")):
        symbol = csv_file.stem
        rows: list[dict[str, Any]] = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({
                    "date": row["date"],
                    "close": float(row["close"]),
                    "open": float(row["open"]),
                })
        rows.sort(key=lambda r: r["date"])
        if rows:
            prices[symbol] = rows

    return prices


def filter_by_date_range(
    prices: dict[str, list[dict[str, Any]]],
    start_date: str,
    end_date: str,
) -> dict[str, list[dict[str, Any]]]:
    """Filter price data to a date range.

    Args:
        prices: Full price data.
        start_date: Start date (inclusive).
        end_date: End date (inclusive).

    Returns:
        Filtered price data.
    """
    filtered: dict[str, list[dict[str, Any]]] = {}
    for symbol, rows in prices.items():
        filtered_rows = [r for r in rows if start_date <= r["date"] <= end_date]
        if len(filtered_rows) >= 2:  # Need at least 2 days for returns
            filtered[symbol] = filtered_rows
    return filtered


def expand_parameter_grid(parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Expand parameter lists into all combinations.

    Args:
        parameters: Dict mapping parameter name to list of values.

    Returns:
        List of parameter combination dicts.
    """
    keys = sorted(parameters.keys())
    values_lists = [parameters[k] for k in keys]
    combinations = []
    for combo in product(*values_lists):
        combinations.append(dict(zip(keys, combo, strict=False)))
    return combinations


def validate_sweep_config(config: dict[str, Any]) -> None:
    """Validate a parameter sweep configuration.

    Args:
        config: The sweep configuration dictionary.

    Raises:
        ParameterSweepValidationError: If config is invalid.
    """
    errors: list[str] = []

    # Required fields
    for field in ["experiment_id", "strategy_id", "mode", "parameters"]:
        if field not in config:
            errors.append(f"{field} is required")

    # Strategy ID validation
    strategy_id = config.get("strategy_id", "")
    if strategy_id not in ALLOWED_STRATEGY_IDS:
        errors.append(
            f"strategy_id must be one of {sorted(ALLOWED_STRATEGY_IDS)}, got '{strategy_id}'"
        )
    if _contains_forbidden_keyword(strategy_id):
        errors.append(f"strategy_id '{strategy_id}' contains forbidden keyword")

    # Mode validation
    mode = config.get("mode", "shadow")
    if mode not in ALLOWED_MODES:
        errors.append(
            f"mode must be one of {sorted(ALLOWED_MODES)}, got '{mode}'"
        )

    # Constraints validation
    constraints = config.get("constraints", {})
    for key in REQUIRED_FALSE_CONSTRAINTS:
        if constraints.get(key, False) is not False:
            errors.append(f"constraints.{key} must be false")
    for key in REQUIRED_TRUE_CONSTRAINTS:
        if constraints.get(key, True) is not True:
            errors.append(f"constraints.{key} must be true")

    # Parameter validation
    parameters = config.get("parameters", {})

    # lookback_days
    lookback_values = parameters.get("lookback_days", [])
    for v in lookback_values:
        if not isinstance(v, int) or v <= 0:
            errors.append(f"lookback_days must be positive integers, got {v}")
            break

    # top_k
    top_k_values = parameters.get("top_k", [])
    for v in top_k_values:
        if not isinstance(v, int) or v <= 0:
            errors.append(f"top_k must be positive integers, got {v}")
            break

    # target_weight
    tw_values = parameters.get("target_weight", [])
    for v in tw_values:
        if not isinstance(v, (int, float)) or v <= 0 or v > MAX_TARGET_WEIGHT:
            errors.append(
                f"target_weight must be > 0 and <= {MAX_TARGET_WEIGHT}, got {v}"
            )
            break

    # Grid size check
    grid = expand_parameter_grid(parameters)
    if len(grid) > MAX_PARAMETER_COMBINATIONS:
        errors.append(
            f"Parameter grid size {len(grid)} exceeds maximum {MAX_PARAMETER_COMBINATIONS}"
        )

    if errors:
        raise ParameterSweepValidationError("; ".join(errors))


def calculate_momentum(prices: list[dict[str, Any]], index: int, lookback: int) -> float:
    """Calculate momentum return for a symbol at a given index.

    Args:
        prices: List of price records.
        index: Current index.
        lookback: Lookback period in days.

    Returns:
        Momentum return (fraction), or -inf if insufficient data.
    """
    if index < lookback:
        return float("-inf")
    current_price = prices[index]["close"]
    past_price = prices[index - lookback]["close"]
    if past_price == 0:
        return float("-inf")
    return current_price / past_price - 1.0


def run_momentum_sweep_evaluator(
    prices: dict[str, list[dict[str, Any]]],
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Run approximate shadow evaluator for momentum strategy.

    This is a simplified offline evaluator, NOT a formal backtest.
    It uses daily close prices and approximate cost assumptions.

    Args:
        prices: Filtered price data.
        parameters: Strategy parameters (lookback_days, top_k, target_weight).

    Returns:
        Dict with performance metrics.
    """
    lookback_days = parameters["lookback_days"]
    top_k = parameters["top_k"]
    target_weight = parameters["target_weight"]

    symbols = list(prices.keys())
    if not symbols:
        return {
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "turnover": 0.0,
            "cost_total": 0.0,
            "cost_ratio": 0.0,
        }

    # Find common date range
    all_dates = set()
    for sym_prices in prices.values():
        all_dates.update(r["date"] for r in sym_prices)
    sorted_dates = sorted(all_dates)

    if len(sorted_dates) <= lookback_days + 1:
        return {
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "turnover": 0.0,
            "cost_total": 0.0,
            "cost_ratio": 0.0,
        }

    # Build date -> index mapping for each symbol
    date_index: dict[str, dict[str, int]] = {}
    for symbol, sym_prices in prices.items():
        date_index[symbol] = {r["date"]: i for i, r in enumerate(sym_prices)}

    # Portfolio state
    portfolio_value = 10000.0  # Start with 10k
    peak_value = portfolio_value
    max_drawdown = 0.0
    current_holdings: dict[str, float] = {}  # symbol -> weight
    trade_count = 0
    total_turnover = 0.0
    total_cost = 0.0

    # Equal weight benchmark
    equal_weight = 1.0 / len(symbols) if symbols else 0.0
    benchmark_value = 10000.0

    # Rebalance periodically (approx monthly = every 21 trading days)
    rebalance_interval = 21

    for i, date in enumerate(sorted_dates):
        # Skip until we have enough lookback data
        if i < lookback_days:
            continue

        # Calculate daily returns for benchmark
        day_return = 0.0
        for symbol in symbols:
            idx = date_index[symbol].get(date)
            if idx is not None and idx > 0:
                sym_prices = prices[symbol]
                day_ret = sym_prices[idx]["close"] / sym_prices[idx - 1]["close"] - 1
                day_return += equal_weight * day_ret
        benchmark_value *= (1 + day_return)

        # Rebalance on interval
        if (i - lookback_days) % rebalance_interval == 0:
            # Calculate momentum for each symbol
            momentum_scores: list[tuple[str, float]] = []
            for symbol in symbols:
                idx = date_index[symbol].get(date)
                if idx is not None:
                    mom = calculate_momentum(prices[symbol], idx, lookback_days)
                    if mom != float("-inf"):
                        momentum_scores.append((symbol, mom))

            # Sort by momentum descending
            momentum_scores.sort(key=lambda x: x[1], reverse=True)

            # Select top_k
            selected = [s for s, _ in momentum_scores[:top_k]]

            # Calculate new target weights
            if selected:
                weight_per = min(target_weight, 1.0 / len(selected))
                new_holdings = {s: weight_per for s in selected}
            else:
                new_holdings = {}

            # Calculate turnover
            all_symbols = set(current_holdings.keys()) | set(new_holdings.keys())
            turnover = 0.0
            for s in all_symbols:
                old_w = current_holdings.get(s, 0.0)
                new_w = new_holdings.get(s, 0.0)
                turnover += abs(new_w - old_w)

            if turnover > 0:
                total_turnover += turnover
                # Approximate trade count: number of symbols with weight change
                changed = sum(
                    1 for s in all_symbols
                    if abs(current_holdings.get(s, 0.0) - new_holdings.get(s, 0.0)) > 0.0001
                )
                trade_count += changed

                # Cost calculation (approximate)
                trade_value = portfolio_value * turnover
                spread_cost = trade_value * SPREAD_RATE
                commission_cost = changed * COMMISSION_PER_TRADE
                cost = spread_cost + commission_cost
                total_cost += cost
                portfolio_value -= cost

            current_holdings = new_holdings

        # Calculate daily portfolio return
        portfolio_return = 0.0
        for symbol, weight in current_holdings.items():
            idx = date_index[symbol].get(date)
            if idx is not None and idx > 0:
                sym_prices = prices[symbol]
                day_ret = sym_prices[idx]["close"] / sym_prices[idx - 1]["close"] - 1
                portfolio_return += weight * day_ret

        portfolio_value *= (1 + portfolio_return)

        # Update drawdown
        if portfolio_value > peak_value:
            peak_value = portfolio_value
        drawdown = (peak_value - portfolio_value) / peak_value if peak_value > 0 else 0.0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    total_return = portfolio_value / 10000.0 - 1.0
    benchmark_return = benchmark_value / 10000.0 - 1.0
    excess_return = total_return - benchmark_return

    # Cost ratio: total cost / initial portfolio
    cost_ratio = total_cost / 10000.0

    # Turnover ratio: total turnover / number of periods
    num_periods = max(1, (len(sorted_dates) - lookback_days) // rebalance_interval)
    avg_turnover = total_turnover / num_periods

    return {
        "total_return": total_return,
        "excess_return_vs_equal_etf": excess_return,
        "max_drawdown": max_drawdown,
        "trade_count": trade_count,
        "turnover": avg_turnover,
        "cost_total": total_cost,
        "cost_ratio": cost_ratio,
    }


def calculate_score(metrics: dict[str, Any]) -> float:
    """Calculate heuristic shadow score.

    Score formula:
        score = excess_return * 100
              - max_drawdown * 50
              - turnover * 5
              - cost_ratio * 10

    Higher is better. This is a heuristic score, not an admission gate.
    """
    excess = metrics.get("excess_return_vs_equal_etf", 0.0)
    mdd = metrics.get("max_drawdown", 0.0)
    turnover = metrics.get("turnover", 0.0)
    cost_ratio = metrics.get("cost_ratio", 0.0)

    score = (
        excess * 100
        - mdd * 50
        - turnover * 5
        - cost_ratio * 10
    )
    return round(score, 2)


def run_parameter_sweep(
    config: dict[str, Any],
    paths: Any,
) -> dict[str, Any]:
    """Run a full parameter sweep experiment.

    Args:
        config: Sweep configuration dictionary.
        paths: ProjectPaths instance.

    Returns:
        Complete sweep result dictionary.
    """
    # Validate config
    validate_sweep_config(config)

    experiment_id = config["experiment_id"]
    strategy_id = config["strategy_id"]
    mode = config["mode"]
    start_date = config.get("start_date", "2024-01-01")
    end_date = config.get("end_date", "2026-06-23")
    data_path = config.get("data_path", "work/trading-core/data/raw/prices/etf_daily")
    constraints = config.get("constraints", {})

    # Resolve data path
    if not Path(data_path).is_absolute():
        data_path = paths.workspace_root / data_path

    # Load price data
    prices = load_price_data(data_path)
    prices = filter_by_date_range(prices, start_date, end_date)

    warnings: list[str] = []
    if not prices:
        warnings.append("insufficient_data: no price data found for date range")

    # Expand parameter grid
    parameters = config.get("parameters", {})
    param_grid = expand_parameter_grid(parameters)
    grid_size = len(param_grid)

    # Run each combination
    runs: list[SweepRunResult] = []
    for i, params in enumerate(param_grid, 1):
        run_id = f"{experiment_id}-RUN-{i:03d}"

        if prices:
            metrics = run_momentum_sweep_evaluator(prices, params)
        else:
            metrics = {
                "total_return": 0.0,
                "excess_return_vs_equal_etf": 0.0,
                "max_drawdown": 0.0,
                "trade_count": 0,
                "turnover": 0.0,
                "cost_total": 0.0,
                "cost_ratio": 0.0,
            }

        score = calculate_score(metrics)

        run_result = SweepRunResult(
            run_id=run_id,
            parameters=params,
            total_return=round(metrics["total_return"], 6),
            excess_return_vs_equal_etf=round(metrics["excess_return_vs_equal_etf"], 6),
            max_drawdown=round(metrics["max_drawdown"], 6),
            trade_count=metrics["trade_count"],
            turnover=round(metrics["turnover"], 6),
            cost_total=round(metrics["cost_total"], 2),
            cost_ratio=round(metrics["cost_ratio"], 6),
            score=score,
        )
        runs.append(run_result)

    # Find best candidate
    best_candidate = None
    if runs and prices:
        sorted_runs = sorted(runs, key=lambda r: r.score, reverse=True)
        best = sorted_runs[0]
        # Only consider as candidate if score is reasonable (not deeply negative)
        if best.score > -50:
            best_candidate = {
                "run_id": best.run_id,
                "parameters": best.parameters,
                "score": best.score,
                "total_return": best.total_return,
                "excess_return_vs_equal_etf": best.excess_return_vs_equal_etf,
                "max_drawdown": best.max_drawdown,
            }
        else:
            warnings.append("all_runs_performed_poorly: no strong shadow candidate")

    # Build result
    result = {
        "experiment_id": experiment_id,
        "strategy_id": strategy_id,
        "mode": mode,
        "start_date": start_date,
        "end_date": end_date,
        "parameter_grid_size": grid_size,
        "runs": [
            {
                "run_id": r.run_id,
                "strategy_id": strategy_id,
                "parameters": r.parameters,
                "total_return": r.total_return,
                "excess_return_vs_equal_etf": r.excess_return_vs_equal_etf,
                "max_drawdown": r.max_drawdown,
                "trade_count": r.trade_count,
                "turnover": r.turnover,
                "cost_total": r.cost_total,
                "cost_ratio": r.cost_ratio,
                "score": r.score,
                "status": r.status,
            }
            for r in runs
        ],
        "best_shadow_candidate": best_candidate,
        "warnings": warnings,
        "constraints": constraints,
        "evaluator": {
            "type": "approximate_shadow_evaluator",
            "benchmark": "EQUAL_ETF",
            "note": "heuristic score only, not a formal backtest",
        },
    }

    return result


def save_sweep_json(result: dict[str, Any], paths: Any) -> Path:
    """Save sweep result to JSON file.

    Args:
        result: Sweep result dictionary.
        paths: ProjectPaths instance.

    Returns:
        Path to the saved JSON file.
    """
    exp_id = result["experiment_id"]
    output_path = paths.data_dir / "experiments" / f"parameter_sweep-{exp_id}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return output_path


def build_sweep_markdown(result: dict[str, Any]) -> str:
    """Build markdown report for parameter sweep.

    Args:
        result: Sweep result dictionary.

    Returns:
        Markdown string.
    """
    exp_id = result["experiment_id"]
    strategy_id = result["strategy_id"]
    mode = result["mode"]
    grid_size = result["parameter_grid_size"]
    runs = result["runs"]
    best = result.get("best_shadow_candidate")
    warnings = result.get("warnings", [])

    # Sort runs by score for top 10
    sorted_runs = sorted(runs, key=lambda r: r["score"], reverse=True)
    top_10 = sorted_runs[:10]

    lines = [
        f"# Parameter Sweep Report: {exp_id}",
        "",
        "## Scope",
        "",
        f"- **Experiment ID**: {exp_id}",
        f"- **Strategy**: {strategy_id}",
        f"- **Mode**: {mode}",
        f"- **Start Date**: {result['start_date']}",
        f"- **End Date**: {result['end_date']}",
        f"- **Parameter Grid Size**: {grid_size}",
        "",
        "## Safety Boundary",
        "",
        "- `shadow_only: true`",
        "- `write_main_ledger: false`",
        "- `allow_active: false`",
        "- **No orders/trades/portfolio written**",
        "- **Not active**",
        "- **Not an admission gate**",
        "",
        "## Method",
        "",
        "- **Evaluator**: approximate shadow evaluator",
        "- **Score**: heuristic score only",
        "- **Benchmark**: EQUAL_ETF (equal weight of all ETFs)",
        "",
        "## Results",
        "",
        f"- **Total Runs**: {len(runs)}",
    ]

    if best:
        lines.extend([
            "",
            "### Best Shadow Candidate",
            "",
            f"- **Run ID**: {best['run_id']}",
            f"- **Score**: {best['score']}",
            f"- **Total Return**: {best['total_return']:.2%}",
            f"- **Excess Return**: {best['excess_return_vs_equal_etf']:.2%}",
            f"- **Max Drawdown**: {best['max_drawdown']:.2%}",
            f"- **Parameters**: {json.dumps(best['parameters'])}",
        ])
    else:
        lines.extend([
            "",
            "### Best Shadow Candidate",
            "",
            "- None (all runs performed poorly or insufficient data)",
        ])

    lines.extend([
        "",
        "### Top 10 Runs by Score",
        "",
        "| Rank | Run ID | Score | Total Return | Excess Return | Max DD | Turnover | Trades |",
        "|------|--------|-------|--------------|---------------|--------|----------|--------|",
    ])

    for i, run in enumerate(top_10, 1):
        lines.append(
            f"| {i} | {run['run_id']} | {run['score']:.1f} "
            f"| {run['total_return']:.2%} | {run['excess_return_vs_equal_etf']:.2%} "
            f"| {run['max_drawdown']:.2%} | {run['turnover']:.3f} | {run['trade_count']} |"
        )

    if warnings:
        lines.extend([
            "",
            "### Warnings",
            "",
        ])
        for w in warnings:
            lines.append(f"- ⚠️ {w}")

    lines.extend([
        "",
        "## Limitations",
        "",
        "- **Not a formal backtest** - approximate shadow evaluator only",
        "- **Not a live trading result**",
        "- **Not sufficient for promotion**",
        "- **heuristic score only**",
        "- **not an admission gate**",
        "- **no orders/trades/portfolio written**",
        "",
        "---",
        f"*Generated at {datetime.now().isoformat()}*",
    ])

    return "\n".join(lines)


def save_sweep_markdown(result: dict[str, Any], paths: Any) -> Path:
    """Save sweep markdown report.

    Args:
        result: Sweep result dictionary.
        paths: ProjectPaths instance.

    Returns:
        Path to the saved markdown file.
    """
    exp_id = result["experiment_id"]
    output_path = paths.outputs_dir / "experiments" / f"PARAMETER_SWEEP-{exp_id}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = build_sweep_markdown(result)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return output_path


def run_parameter_sweep_from_config(
    config_path: str | Path,
    paths: Any,
) -> dict[str, Any]:
    """Run parameter sweep from a config file.

    Args:
        config_path: Path to YAML or JSON config file.
        paths: ProjectPaths instance.

    Returns:
        Sweep result dictionary.
    """
    from trading_core.experiments.experiment_registry import load_experiment_config

    config = load_experiment_config(config_path)
    result = run_parameter_sweep(config, paths)

    # Save outputs
    save_sweep_json(result, paths)
    save_sweep_markdown(result, paths)

    return result
