"""Accounting consistency checks across daily trading artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.backtest.event_backtester import date_range
from trading_core.calendar.trading_calendar import previous_trading_day
from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


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
) -> dict[str, Any]:
    paths = paths or project_paths()
    results = [check_consistency(day, paths, tolerance) for day in date_range(start_date, end_date)]
    payload = {
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
