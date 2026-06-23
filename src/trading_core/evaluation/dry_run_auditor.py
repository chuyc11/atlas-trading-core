"""Audit consecutive dry-run artifacts for operational drift."""

from __future__ import annotations

from collections import Counter
from typing import Any

from trading_core.backtest.event_backtester import date_range
from trading_core.config_loader import load_config
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json


def audit_dry_run(
    start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    asset_jump_threshold: float = 0.20,
) -> dict[str, Any]:
    paths = paths or project_paths()
    dates = date_range(start_date, end_date)
    warnings: list[str] = []
    critical_errors: list[str] = []
    rejection_reasons: Counter[str] = Counter()
    duplicate_order_ids: set[str] = set()
    duplicate_trade_ids: set[str] = set()
    seen_order_ids: set[str] = set()
    seen_trade_ids: set[str] = set()
    missing_input_days: list[str] = []
    consecutive_failures = 0
    max_consecutive_failures = 0
    previous_portfolio: dict[str, Any] | None = None
    daily: list[dict[str, Any]] = []

    for day in dates:
        health = read_json(paths.dated_json("runtime", "health", day), default={})
        portfolio = read_json(paths.dated_json("portfolios", "portfolio", day), default={})
        previous_day_portfolio = previous_portfolio
        orders = read_jsonl(paths.dated_jsonl("orders", "orders", day))
        trades = read_jsonl(paths.dated_jsonl("trades", "trades", day))
        data_quality = read_json(paths.dated_json("snapshots", "data_quality", day), default={})
        evolution = read_json(paths.data_dir / "evolution" / f"evolution-summary-{day}.json", default={})

        if not health:
            warnings.append(f"{day}: missing health file")
            consecutive_failures += 1
        elif health.get("errors"):
            consecutive_failures += 1
        else:
            consecutive_failures = 0
        max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)

        if health.get("input_files_missing"):
            missing_input_days.append(day)
        if not portfolio:
            critical_errors.append(f"{day}: missing portfolio")
        else:
            _audit_portfolio(day, portfolio, previous_day_portfolio, asset_jump_threshold, warnings, critical_errors)
            previous_portfolio = portfolio

        _audit_orders_and_trades(
            day,
            orders,
            trades,
            data_quality,
            rejection_reasons,
            seen_order_ids,
            seen_trade_ids,
            duplicate_order_ids,
            duplicate_trade_ids,
            warnings,
            critical_errors,
        )
        _audit_shadow(day, paths, critical_errors)
        _audit_evolution(day, evolution, warnings, critical_errors)
        daily.append(
            {
                "date": day,
                "orders": len(orders),
                "trades": len(trades),
                "rejections": len([order for order in orders if order.get("status") == "rejected"]),
                "health_errors": health.get("errors", []),
                "missing_inputs": health.get("input_files_missing", []),
            }
        )

    _audit_experiment_queue(paths, warnings, critical_errors)
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "passed": not critical_errors,
        "warnings": warnings,
        "critical_errors": critical_errors,
        "recommendation": "continue_dry_run" if not critical_errors else "stop_and_fix_critical_errors",
        "rejection_reason_distribution": dict(rejection_reasons),
        "max_consecutive_failures": max_consecutive_failures,
        "missing_input_days": missing_input_days,
        "duplicate_order_ids": sorted(duplicate_order_ids),
        "duplicate_trade_ids": sorted(duplicate_trade_ids),
        "daily": daily,
    }
    json_path = paths.data_dir / "evaluation" / f"dry_run_audit-{start_date}-{end_date}.json"
    report_path = paths.outputs_dir / "dry-runs" / f"DRY_RUN_AUDIT-{start_date}-{end_date}.md"
    write_json(json_path, payload)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["report_path"] = str(report_path)
    return payload


def _audit_portfolio(
    day: str,
    portfolio: dict[str, Any],
    previous_portfolio: dict[str, Any] | None,
    asset_jump_threshold: float,
    warnings: list[str],
    critical_errors: list[str],
) -> None:
    cash = float(portfolio.get("cash", 0.0))
    market_value = float(portfolio.get("market_value", 0.0))
    total_asset = float(portfolio.get("total_asset", 0.0))
    if cash < 0:
        critical_errors.append(f"{day}: cash is negative")
    if abs(total_asset - (cash + market_value)) > 0.01:
        critical_errors.append(f"{day}: total_asset does not equal cash + market_value")
    if previous_portfolio:
        previous_total = float(previous_portfolio.get("total_asset", 0.0))
        if previous_total and abs((total_asset / previous_total) - 1) > asset_jump_threshold:
            warnings.append(f"{day}: total_asset jump exceeds threshold")
    for position in portfolio.get("positions", []):
        quantity = int(position.get("quantity", 0))
        available = int(position.get("available_quantity", 0))
        current_price = float(position.get("current_price", 0.0))
        market = float(position.get("market_value", 0.0))
        symbol = position.get("symbol")
        if quantity < 0:
            critical_errors.append(f"{day}: negative position quantity {symbol}")
        if available > quantity:
            critical_errors.append(f"{day}: available_quantity exceeds quantity {symbol}")
        if market and abs(market - quantity * current_price) > 0.01:
            warnings.append(f"{day}: position market value drift {symbol}")


def _audit_orders_and_trades(
    day: str,
    orders: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    data_quality: dict[str, Any],
    rejection_reasons: Counter[str],
    seen_order_ids: set[str],
    seen_trade_ids: set[str],
    duplicate_order_ids: set[str],
    duplicate_trade_ids: set[str],
    warnings: list[str],
    critical_errors: list[str],
) -> None:
    trade_keys: set[tuple[str, str, str, int]] = set()
    blocked_symbols = _blocked_buy_symbols(data_quality)
    for order in orders:
        order_id = str(order.get("order_id"))
        if order_id in seen_order_ids:
            duplicate_order_ids.add(order_id)
            critical_errors.append(f"{day}: duplicate order_id {order_id}")
        seen_order_ids.add(order_id)
        if order.get("status") == "rejected":
            rejection_reasons[str(order.get("risk_reason", "unknown"))] += 1
        quality = str(order.get("price_quality", "fresh"))
        if order.get("side") == "BUY" and order.get("status") in {"submitted", "filled"}:
            if quality in {"fallback", "stale", "missing"} or order.get("symbol") in blocked_symbols:
                critical_errors.append(f"{day}: BUY created on blocked data quality for {order.get('symbol')}")
    for trade in trades:
        trade_id = str(trade.get("trade_id"))
        if trade_id in seen_trade_ids:
            duplicate_trade_ids.add(trade_id)
            critical_errors.append(f"{day}: duplicate trade_id {trade_id}")
        seen_trade_ids.add(trade_id)
        key = (
            str(trade.get("symbol")),
            str(trade.get("side")),
            str(trade.get("filled_price")),
            int(trade.get("filled_quantity", 0)),
        )
        if key in trade_keys:
            warnings.append(f"{day}: repeated same-day trade {key[0]} {key[1]}")
        trade_keys.add(key)


def _blocked_buy_symbols(data_quality: dict[str, Any]) -> set[str]:
    blocked = set()
    for limitation in data_quality.get("limitations", []):
        text = str(limitation)
        for marker in ["fallback_price_blocks_buy:", "stale_price_blocks_buy:", "missing_price:"]:
            if marker in text:
                blocked.add(text.split(marker, 1)[1].strip())
    return blocked


def _audit_shadow(day: str, paths: ProjectPaths, critical_errors: list[str]) -> None:
    for row in read_jsonl(paths.data_dir / "experiments" / f"shadow_signals-{day}.jsonl"):
        if row.get("account_mutation") or any(key in row for key in ["cash", "positions", "portfolio"]):
            critical_errors.append(f"{day}: shadow artifact contains main-account mutation fields")


def _audit_evolution(day: str, evolution: dict[str, Any], warnings: list[str], critical_errors: list[str]) -> None:
    if not evolution:
        return
    config = load_config("evolution.yaml")["evolution"]["rule_memory"]
    max_new = int(config["max_new_rules_per_day"])
    proposals = evolution.get("rule_memory", {}).get("rules", [])
    today_proposals = [rule for rule in proposals if rule.get("created_date") == day or rule.get("date") == day]
    if len(today_proposals) > max_new:
        critical_errors.append(f"{day}: evolution proposals exceed throttle")
    elif len(proposals) > max_new and not today_proposals:
        warnings.append(f"{day}: evolution rule memory contains more rules than daily throttle")


def _audit_experiment_queue(paths: ProjectPaths, warnings: list[str], critical_errors: list[str]) -> None:
    rows = read_jsonl(paths.data_dir / "experiments" / "experiment_queue.jsonl")
    experiment_ids = [str(row.get("experiment_id")) for row in rows]
    rule_ids = [str(row.get("rule_id")) for row in rows]
    for value, count in Counter(experiment_ids).items():
        if value != "None" and count > 1:
            critical_errors.append(f"duplicate experiment_id {value}")
    for value, count in Counter(rule_ids).items():
        if value != "None" and count > 1:
            warnings.append(f"duplicate experiment rule_id {value}")


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        f"# Dry Run Audit {payload['start_date']} to {payload['end_date']}",
        "",
        f"- Passed: {payload['passed']}",
        f"- Recommendation: {payload['recommendation']}",
        f"- Max consecutive failures: {payload['max_consecutive_failures']}",
        f"- Missing input days: {payload['missing_input_days']}",
        f"- Rejection reason distribution: {payload['rejection_reason_distribution']}",
        "",
        "## Critical Errors",
    ]
    lines.extend(f"- {item}" for item in payload["critical_errors"]) if payload["critical_errors"] else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in payload["warnings"]) if payload["warnings"] else lines.append("- none")
    return "\n".join(lines) + "\n"
