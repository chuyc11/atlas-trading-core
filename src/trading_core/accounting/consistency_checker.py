"""Accounting consistency checks across daily and backtest artifacts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from trading_core.backtest.event_backtester import date_range
from trading_core.calendar.trading_calendar import previous_trading_day
from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json

DEFAULT_BACKTEST_INITIAL_CAPITAL = 100000.0
BACKTEST_REQUIRED_FILES = [
    "strategy_results.json",
    "benchmark_results.json",
    "admission_results.json",
    "leaderboard.json",
]


def check_consistency(
    date: str,
    paths: ProjectPaths | None = None,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    paths = paths or project_paths()
    errors: list[str] = []
    warnings: list[str] = []
    portfolio = read_json(paths.dated_json("portfolios", "portfolio", date), default={})
    previous = read_json(paths.dated_json("portfolios", "portfolio", previous_trading_day(date)), default=None)
    orders = read_jsonl(paths.dated_jsonl("orders", "orders", date))
    trades = read_jsonl(paths.dated_jsonl("trades", "trades", date))
    signals = read_jsonl(paths.dated_jsonl("signals", "trading_signals", date))
    valuations = read_jsonl(paths.dated_jsonl("valuations", "valuations", date))
    attribution = read_json(paths.dated_json("attribution", "attribution", date), default={})

    if not portfolio:
        errors.append("missing portfolio")
    else:
        _check_portfolio(portfolio, tolerance, errors)
        _check_cash_ledger(date, portfolio, previous, trades, tolerance, errors, warnings)
        _check_daily_return(portfolio, previous, tolerance, errors)
    _check_valuation(portfolio, valuations, tolerance, errors)
    _check_attribution(portfolio, previous, attribution, tolerance, errors, warnings)
    _check_order_trade_links(orders, trades, signals, errors)

    payload = {
        "date": date,
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "cash_non_negative": not any("cash" in error and "negative" in error for error in errors),
            "asset_identity": not any("total_asset" in error for error in errors),
            "positions_valid": not any("position" in error for error in errors),
            "cash_ledger": not any("cash ledger" in error for error in errors),
            "valuation_attribution": not any("valuation" in error or "attribution" in error for error in errors),
            "order_trade_links": not any("orphan" in error for error in errors),
        },
    }
    json_path = paths.data_dir / "evaluation" / f"consistency-{date}.json"
    report_path = paths.outputs_dir / "consistency" / f"CONSISTENCY-{date}.md"
    write_json(json_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    return payload


def check_consistency_range(
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    tolerance: float = 0.01,
    mode: str = "daily",
    artifact_dir: Path | str | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    normalized_mode = mode.lower()
    if normalized_mode == "auto":
        normalized_mode = "backtest" if artifact_dir else "daily"
    if normalized_mode == "backtest":
        return check_backtest_consistency_range(start_date, end_date, artifact_dir, paths, tolerance)
    if normalized_mode != "daily":
        raise ValueError(f"Unsupported consistency mode: {mode}")
    results = [check_consistency(day, paths, tolerance) for day in date_range(start_date, end_date)]
    payload = {
        "mode": "daily",
        "start_date": start_date,
        "end_date": end_date,
        "passed": all(result["passed"] for result in results),
        "items": results,
        "critical_errors": [error for result in results for error in result["errors"]],
    }
    json_path = paths.data_dir / "evaluation" / f"consistency-{start_date}-{end_date}.json"
    write_json(json_path, payload)
    payload["json_path"] = str(json_path)
    return payload


def check_backtest_consistency_range(
    start_date: str,
    end_date: str,
    artifact_dir: Path | str | None,
    paths: ProjectPaths | None = None,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifact_path = _resolve_artifact_dir(artifact_dir, paths) if artifact_dir else None
    warnings: list[str] = []
    critical_errors: list[str] = []
    strategies_checked = 0
    days_checked = 0
    trades_checked = 0
    benchmark_checked = 0

    if artifact_path is None:
        critical_errors.append("artifact-dir is required for backtest consistency mode")
        return _write_backtest_consistency_outputs(
            _backtest_payload(
                start_date,
                end_date,
                None,
                warnings,
                critical_errors,
                strategies_checked,
                days_checked,
                trades_checked,
                benchmark_checked,
            ),
            paths,
        )
    if not artifact_path.exists() or not artifact_path.is_dir():
        critical_errors.append(f"artifact-dir does not exist or is not a directory: {artifact_path}")
        return _write_backtest_consistency_outputs(
            _backtest_payload(
                start_date,
                end_date,
                artifact_path,
                warnings,
                critical_errors,
                strategies_checked,
                days_checked,
                trades_checked,
                benchmark_checked,
            ),
            paths,
        )

    strategy_results = _read_required_backtest_json(artifact_path, "strategy_results.json", critical_errors)
    benchmark_results = _read_required_backtest_json(artifact_path, "benchmark_results.json", critical_errors)
    admission_results = _read_required_backtest_json(artifact_path, "admission_results.json", critical_errors)
    leaderboard = _read_required_backtest_json(artifact_path, "leaderboard.json", critical_errors)
    for file_name in BACKTEST_REQUIRED_FILES:
        if not (artifact_path / file_name).exists():
            critical_errors.append(f"missing required backtest artifact: {file_name}")

    if critical_errors:
        return _write_backtest_consistency_outputs(
            _backtest_payload(
                start_date,
                end_date,
                artifact_path,
                warnings,
                critical_errors,
                strategies_checked,
                days_checked,
                trades_checked,
                benchmark_checked,
            ),
            paths,
        )

    if not isinstance(strategy_results, dict) or not strategy_results:
        critical_errors.append("strategy_results.json is empty or invalid")
    else:
        for strategy_id, result in strategy_results.items():
            strategy_errors: list[str] = []
            strategy_warnings: list[str] = []
            stats = _check_single_backtest_strategy(
                str(strategy_id),
                result if isinstance(result, dict) else {},
                start_date,
                end_date,
                artifact_path,
                paths,
                tolerance,
                benchmark_results if isinstance(benchmark_results, dict) else {},
                admission_results if isinstance(admission_results, dict) else {},
                leaderboard if isinstance(leaderboard, dict) else {},
                strategy_errors,
                strategy_warnings,
            )
            strategies_checked += 1
            days_checked += stats["days_checked"]
            trades_checked += stats["trades_checked"]
            benchmark_checked += stats["benchmark_checked"]
            critical_errors.extend(strategy_errors)
            warnings.extend(strategy_warnings)

    payload = _backtest_payload(
        start_date,
        end_date,
        artifact_path,
        warnings,
        critical_errors,
        strategies_checked,
        days_checked,
        trades_checked,
        benchmark_checked,
    )
    return _write_backtest_consistency_outputs(payload, paths)


def _check_portfolio(portfolio: dict[str, Any], tolerance: float, errors: list[str]) -> None:
    cash = float(portfolio.get("cash", 0.0))
    market_value = float(portfolio.get("market_value", 0.0))
    total_asset = float(portfolio.get("total_asset", 0.0))
    if cash < -tolerance:
        errors.append("cash is negative")
    if abs(total_asset - (cash + market_value)) > tolerance:
        errors.append("total_asset does not equal cash + market_value")
    for position in portfolio.get("positions", []):
        symbol = position.get("symbol")
        quantity = int(position.get("quantity", 0))
        available = int(position.get("available_quantity", 0))
        current_price = float(position.get("current_price", 0.0))
        position_value = float(position.get("market_value", 0.0))
        if quantity < 0:
            errors.append(f"position quantity is negative: {symbol}")
        if available > quantity:
            errors.append(f"position available_quantity exceeds quantity: {symbol}")
        if abs(position_value - quantity * current_price) > tolerance:
            errors.append(f"position market_value mismatch: {symbol}")


def _check_cash_ledger(
    date: str,
    portfolio: dict[str, Any],
    previous: dict[str, Any] | None,
    trades: list[dict[str, Any]],
    tolerance: float,
    errors: list[str],
    warnings: list[str],
) -> None:
    if previous:
        expected_cash = float(previous.get("cash", 0.0))
    else:
        expected_cash = float(load_config("settings.yaml")["initial_account"]["initial_cash"])
    for trade in trades:
        side = str(trade.get("side", "")).upper()
        net_amount = float(trade.get("net_amount", 0.0))
        if side == "BUY":
            expected_cash -= net_amount
        elif side == "SELL":
            expected_cash += net_amount
        else:
            warnings.append(f"{date}: unsupported trade side in cash ledger {side}")
    actual_cash = float(portfolio.get("cash", 0.0))
    if abs(actual_cash - expected_cash) > tolerance:
        errors.append(f"cash ledger mismatch: expected {round(expected_cash, 6)} actual {round(actual_cash, 6)}")


def _check_daily_return(
    portfolio: dict[str, Any],
    previous: dict[str, Any] | None,
    tolerance: float,
    errors: list[str],
) -> None:
    if not previous:
        return
    previous_total = float(previous.get("total_asset", 0.0))
    if not previous_total:
        return
    expected = (float(portfolio.get("total_asset", 0.0)) / previous_total) - 1
    actual = float(portfolio.get("daily_return", 0.0))
    if abs(actual - expected) > max(tolerance, 0.000001):
        errors.append(f"daily_return mismatch: expected {round(expected, 8)} actual {round(actual, 8)}")


def _check_valuation(
    portfolio: dict[str, Any],
    valuations: list[dict[str, Any]],
    tolerance: float,
    errors: list[str],
) -> None:
    if not valuations or not portfolio:
        return
    valuation = valuations[0]
    if abs(float(valuation.get("total_asset", 0.0)) - float(portfolio.get("total_asset", 0.0))) > tolerance:
        errors.append("valuation total_asset mismatch")


def _check_attribution(
    portfolio: dict[str, Any],
    previous: dict[str, Any] | None,
    attribution: dict[str, Any],
    tolerance: float,
    errors: list[str],
    warnings: list[str],
) -> None:
    if not attribution or not portfolio:
        return
    if previous:
        expected_pnl = float(portfolio.get("total_asset", 0.0)) - float(previous.get("total_asset", 0.0))
    else:
        daily_return = float(portfolio.get("daily_return", 0.0))
        total_asset = float(portfolio.get("total_asset", 0.0))
        previous_total = total_asset / (1 + daily_return) if daily_return else total_asset
        expected_pnl = total_asset - previous_total
    actual_pnl = float(attribution.get("total_pnl", 0.0))
    if abs(actual_pnl - expected_pnl) > tolerance:
        errors.append(f"attribution total_pnl mismatch: expected {round(expected_pnl, 6)} actual {round(actual_pnl, 6)}")
    if abs(float(attribution.get("residual_pnl", 0.0))) > tolerance:
        warnings.append("attribution residual_pnl exceeds tolerance")


def _check_order_trade_links(
    orders: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    errors: list[str],
) -> None:
    order_ids = {order.get("order_id") for order in orders}
    signal_ids = {signal.get("signal_id") for signal in signals}
    for trade in trades:
        if trade.get("order_id") not in order_ids:
            errors.append(f"orphan trade without order: {trade.get('trade_id')}")
    for order in orders:
        signal_id = order.get("signal_id")
        if signal_id not in signal_ids and not order.get("risk_reason"):
            errors.append(f"orphan order without signal or rejection reason: {order.get('order_id')}")


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Consistency Check {payload['date']}",
        "",
        f"- Passed: {payload['passed']}",
        "",
        "## Errors",
    ]
    lines.extend(f"- {item}" for item in payload["errors"]) if payload["errors"] else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in payload["warnings"]) if payload["warnings"] else lines.append("- none")
    return "\n".join(lines) + "\n"


def _resolve_artifact_dir(artifact_dir: Path | str, paths: ProjectPaths) -> Path:
    path = Path(artifact_dir)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return (paths.project_root / path).resolve() if not path.exists() else path.resolve()


def _read_required_backtest_json(artifact_path: Path, file_name: str, errors: list[str]) -> Any:
    path = artifact_path / file_name
    try:
        return read_json(path, default={})
    except ValueError as exc:
        errors.append(str(exc))
        return {}


def _check_single_backtest_strategy(
    strategy_id: str,
    result: dict[str, Any],
    start_date: str,
    end_date: str,
    artifact_path: Path,
    paths: ProjectPaths,
    tolerance: float,
    benchmark_results: dict[str, Any],
    admission_results: dict[str, Any],
    leaderboard: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> dict[str, int]:
    portfolio_path = _strategy_artifact_path(
        result,
        "portfolio_path",
        artifact_path,
        paths,
        f"data/backtests/backtest_portfolio-{start_date}-{end_date}-{strategy_id}.jsonl",
    )
    trades_path = _strategy_artifact_path(
        result,
        "trades_path",
        artifact_path,
        paths,
        f"data/backtests/backtest_trades-{start_date}-{end_date}-{strategy_id}.jsonl",
    )
    benchmark_path = _strategy_artifact_path(
        result,
        "benchmark_path",
        artifact_path,
        paths,
        f"data/backtests/backtest_benchmark-{start_date}-{end_date}-{strategy_id}.json",
    )

    portfolios = _read_jsonl_artifact(portfolio_path, strategy_id, "portfolio", errors)
    trades = _read_jsonl_artifact(trades_path, strategy_id, "trades", errors)
    benchmark = _read_json_artifact(benchmark_path, strategy_id, "benchmark", errors)
    if not portfolios:
        errors.append(f"{strategy_id}: missing backtest portfolio artifacts")
        return {"days_checked": 0, "trades_checked": len(trades), "benchmark_checked": int(bool(benchmark))}

    _check_backtest_portfolio_dates(strategy_id, portfolios, start_date, end_date, result, errors, warnings)
    previous: dict[str, Any] | None = None
    for portfolio in portfolios:
        _prefix_errors(strategy_id, _check_portfolio, portfolio, tolerance, errors)
        _check_backtest_market_value(strategy_id, portfolio, tolerance, errors)
        _prefix_errors(strategy_id, _check_daily_return, portfolio, previous, tolerance, errors)
        previous = portfolio

    _check_strategy_result_matches_portfolio(strategy_id, result, portfolios[-1], tolerance, errors, warnings)
    _check_backtest_trades(strategy_id, trades, errors, warnings)
    _check_backtest_benchmark(strategy_id, benchmark, portfolios[-1], tolerance, errors)
    _check_batch_benchmark_result(strategy_id, benchmark_results, errors)
    _check_admission_metrics(strategy_id, result, admission_results, tolerance, errors)
    _check_leaderboard_mentions_strategy(strategy_id, leaderboard, warnings)
    return {"days_checked": len(portfolios), "trades_checked": len(trades), "benchmark_checked": int(bool(benchmark))}


def _strategy_artifact_path(
    result: dict[str, Any],
    key: str,
    artifact_path: Path,
    paths: ProjectPaths,
    fallback_relative: str,
) -> Path:
    raw = result.get(key)
    if raw:
        candidate = Path(str(raw))
        if candidate.is_absolute():
            return candidate
        direct = artifact_path / candidate
        if direct.exists():
            return direct
        parts = [part.lower() for part in candidate.parts]
        if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
            return paths.workspace_root / candidate
        return paths.project_root / candidate
    return paths.project_root / fallback_relative


def _read_jsonl_artifact(path: Path, strategy_id: str, label: str, errors: list[str]) -> list[dict[str, Any]]:
    try:
        rows = read_jsonl(path)
    except ValueError as exc:
        errors.append(f"{strategy_id}: invalid {label} artifact: {exc}")
        return []
    if not path.exists():
        errors.append(f"{strategy_id}: missing {label} artifact: {path}")
    return rows


def _read_json_artifact(path: Path, strategy_id: str, label: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = read_json(path, default={})
    except ValueError as exc:
        errors.append(f"{strategy_id}: invalid {label} artifact: {exc}")
        return {}
    if not path.exists():
        errors.append(f"{strategy_id}: missing {label} artifact: {path}")
    return payload if isinstance(payload, dict) else {}


def _prefix_errors(strategy_id: str, check_fn: Any, *args: Any) -> None:
    errors = args[-1]
    before = len(errors)
    check_fn(*args)
    for index in range(before, len(errors)):
        errors[index] = f"{strategy_id}: {errors[index]}"


def _check_backtest_portfolio_dates(
    strategy_id: str,
    portfolios: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    result: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    dates = [str(row.get("date", "")) for row in portfolios]
    if len(dates) != len(set(dates)):
        errors.append(f"{strategy_id}: duplicate portfolio dates")
    if dates != sorted(dates):
        errors.append(f"{strategy_id}: portfolio dates are not sorted")
    out_of_range = [date for date in dates if date < start_date or date > end_date]
    if out_of_range:
        errors.append(f"{strategy_id}: portfolio dates outside requested range: {out_of_range[:3]}")
    expected_days = result.get("days")
    if expected_days is not None and int(expected_days) != len(portfolios):
        errors.append(f"{strategy_id}: strategy_results days does not match portfolio rows")
    if dates and (dates[0] > start_date or dates[-1] < end_date):
        warnings.append(f"{strategy_id}: portfolio covers {dates[0]} to {dates[-1]} inside requested {start_date} to {end_date}")


def _check_backtest_market_value(
    strategy_id: str,
    portfolio: dict[str, Any],
    tolerance: float,
    errors: list[str],
) -> None:
    market_value = float(portfolio.get("market_value", 0.0))
    position_total = sum(float(position.get("market_value", 0.0)) for position in portfolio.get("positions", []))
    if abs(market_value - position_total) > tolerance:
        errors.append(f"{strategy_id}: market_value does not equal positions market_value sum on {portfolio.get('date')}")


def _check_strategy_result_matches_portfolio(
    strategy_id: str,
    result: dict[str, Any],
    final_portfolio: dict[str, Any],
    tolerance: float,
    errors: list[str],
    warnings: list[str],
) -> None:
    final_asset = _result_final_asset(result)
    actual_final = float(final_portfolio.get("total_asset", 0.0))
    if final_asset is None:
        warnings.append(f"{strategy_id}: strategy_results has no final_asset or cumulative_return")
    elif abs(final_asset - actual_final) > tolerance:
        errors.append(f"{strategy_id}: final_asset mismatch: expected {round(final_asset, 6)} actual {round(actual_final, 6)}")


def _result_final_asset(result: dict[str, Any]) -> float | None:
    if result.get("final_asset") is not None:
        return float(result["final_asset"])
    if result.get("cumulative_return") is not None:
        return DEFAULT_BACKTEST_INITIAL_CAPITAL * (1 + float(result["cumulative_return"]))
    return None


def _check_backtest_trades(
    strategy_id: str,
    trades: list[dict[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> None:
    seen_trade_ids: set[str] = set()
    for trade in trades:
        trade_id = str(trade.get("trade_id", ""))
        if trade_id in seen_trade_ids:
            errors.append(f"{strategy_id}: duplicate trade_id {trade_id}")
        if trade_id:
            seen_trade_ids.add(trade_id)
        has_order = bool(trade.get("order_id"))
        has_signal_reference = bool(trade.get("signal_id") or trade.get("signal_date"))
        if not has_order and not has_signal_reference:
            errors.append(f"{strategy_id}: trade missing order or backtest signal reference: {trade_id}")
        signal_date = _trade_signal_date(trade)
        trade_date = str(trade.get("date", ""))
        if signal_date and trade_date and trade_date <= signal_date:
            errors.append(f"{strategy_id}: T+1 violation, trade executed on or before signal date: {trade_id}")
        if not signal_date:
            warnings.append(f"{strategy_id}: trade cannot prove T+1 timing without signal_date/signal_id: {trade_id}")


def _trade_signal_date(trade: dict[str, Any]) -> str | None:
    if trade.get("signal_date"):
        return str(trade["signal_date"])
    signal_id = str(trade.get("signal_id", ""))
    match = re.search(r"BT-SIG-(\d{8})", signal_id)
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


def _check_backtest_benchmark(
    strategy_id: str,
    benchmark: dict[str, Any],
    final_portfolio: dict[str, Any],
    tolerance: float,
    errors: list[str],
) -> None:
    if not benchmark:
        errors.append(f"{strategy_id}: benchmark artifact is empty")
        return
    portfolio_return = _as_float(benchmark.get("portfolio_return"), f"{strategy_id}: benchmark portfolio_return", errors)
    if portfolio_return is not None:
        actual = float(final_portfolio.get("daily_return", 0.0))
        if abs(portfolio_return - actual) > max(tolerance, 0.000001):
            errors.append(f"{strategy_id}: benchmark portfolio_return does not match final portfolio daily_return")
    for benchmark_id, row in benchmark.get("benchmarks", {}).items():
        result_return = _as_float(row.get("return") if isinstance(row, dict) else None, f"{strategy_id}: benchmark {benchmark_id} return", errors)
        excess = benchmark.get("excess_return", {}).get(benchmark_id)
        excess_return = _as_float(excess, f"{strategy_id}: benchmark {benchmark_id} excess_return", errors)
        if portfolio_return is not None and result_return is not None and excess_return is not None:
            if abs(excess_return - (portfolio_return - result_return)) > max(tolerance, 0.000001):
                errors.append(f"{strategy_id}: benchmark {benchmark_id} excess_return mismatch")


def _check_batch_benchmark_result(
    strategy_id: str,
    benchmark_results: dict[str, Any],
    errors: list[str],
) -> None:
    row = benchmark_results.get(strategy_id)
    if not isinstance(row, dict):
        errors.append(f"{strategy_id}: benchmark_results missing strategy row")
        return
    for benchmark_id, benchmark in row.items():
        if not isinstance(benchmark, dict):
            errors.append(f"{strategy_id}: benchmark_results {benchmark_id} is invalid")
            continue
        _as_float(benchmark.get("return"), f"{strategy_id}: benchmark_results {benchmark_id} return", errors)


def _check_admission_metrics(
    strategy_id: str,
    result: dict[str, Any],
    admission_results: dict[str, Any],
    tolerance: float,
    errors: list[str],
) -> None:
    expected = result.get("admission_metrics")
    admission = admission_results.get(strategy_id)
    if not isinstance(expected, dict):
        errors.append(f"{strategy_id}: strategy_results missing admission_metrics")
        return
    if not isinstance(admission, dict):
        errors.append(f"{strategy_id}: admission_results missing strategy decision")
        return
    actual = admission.get("metrics")
    if not isinstance(actual, dict):
        errors.append(f"{strategy_id}: admission decision missing metrics")
        return
    for key, expected_value in expected.items():
        if key not in actual:
            errors.append(f"{strategy_id}: admission metrics missing {key}")
            continue
        actual_value = actual[key]
        if isinstance(expected_value, bool) or isinstance(actual_value, bool):
            if bool(expected_value) != bool(actual_value):
                errors.append(f"{strategy_id}: admission metric mismatch {key}")
            continue
        try:
            if abs(float(expected_value) - float(actual_value)) > max(tolerance, 0.000001):
                errors.append(f"{strategy_id}: admission metric mismatch {key}")
        except (TypeError, ValueError):
            if expected_value != actual_value:
                errors.append(f"{strategy_id}: admission metric mismatch {key}")


def _check_leaderboard_mentions_strategy(strategy_id: str, leaderboard: dict[str, Any], warnings: list[str]) -> None:
    items = leaderboard.get("items", [])
    if not isinstance(items, list):
        warnings.append("leaderboard items are invalid")
        return
    if not any(isinstance(item, dict) and item.get("strategy_id") == strategy_id for item in items):
        warnings.append(f"{strategy_id}: leaderboard does not mention strategy")


def _as_float(value: Any, label: str, errors: list[str]) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{label} is not numeric")
        return None


def _backtest_payload(
    start_date: str,
    end_date: str,
    artifact_path: Path | None,
    warnings: list[str],
    critical_errors: list[str],
    strategies_checked: int,
    days_checked: int,
    trades_checked: int,
    benchmark_checked: int,
) -> dict[str, Any]:
    passed = not critical_errors
    return {
        "mode": "backtest",
        "start_date": start_date,
        "end_date": end_date,
        "artifact_dir": str(artifact_path) if artifact_path else None,
        "passed": passed,
        "warnings": warnings,
        "critical_errors": critical_errors,
        "strategies_checked": strategies_checked,
        "days_checked": days_checked,
        "trades_checked": trades_checked,
        "benchmark_checked": benchmark_checked,
        "recommendation": "ready_for_validation_report" if passed else "fix_backtest_artifacts_before_validation_report",
    }


def _write_backtest_consistency_outputs(payload: dict[str, Any], paths: ProjectPaths) -> dict[str, Any]:
    start_date = payload["start_date"]
    end_date = payload["end_date"]
    json_path = paths.data_dir / "evaluation" / f"backtest_consistency-{start_date}-{end_date}.json"
    report_path = paths.outputs_dir / "consistency" / f"BACKTEST_CONSISTENCY-{start_date}-{end_date}.md"
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    write_json(json_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_backtest_report(payload), encoding="utf-8")
    return payload


def _markdown_backtest_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Backtest Consistency {payload['start_date']} to {payload['end_date']}",
        "",
        f"- Mode: {payload['mode']}",
        f"- Artifact dir: {payload['artifact_dir']}",
        f"- Passed: {payload['passed']}",
        f"- Strategies checked: {payload['strategies_checked']}",
        f"- Days checked: {payload['days_checked']}",
        f"- Trades checked: {payload['trades_checked']}",
        f"- Benchmarks checked: {payload['benchmark_checked']}",
        f"- Recommendation: {payload['recommendation']}",
        "",
        "## Critical Errors",
    ]
    lines.extend(f"- {item}" for item in payload["critical_errors"]) if payload["critical_errors"] else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in payload["warnings"]) if payload["warnings"] else lines.append("- none")
    return "\n".join(lines) + "\n"
