"""Isolated historical replay adapter for baseline strategies."""

from __future__ import annotations

from typing import Any

from trading_core.execution.virtual_execution_engine import execute_virtual_order, portfolio_snapshot, settle_available_shares
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import write_json

from .baseline_order_preview import build_baseline_order_preview
from .baseline_signal_engine import generate_baseline_strategy_signals
from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    RESEARCH_NOTICE,
    load_price_history,
    next_execution_date,
    paths_or_default,
    preview_path,
    price_on_or_before,
    read_rows,
    rel,
    replay_report_path,
    replay_root,
    replay_summary_path,
    research_boundary,
    rows_and_paths,
    selected_strategies,
    simulated_price_status,
    trading_dates,
)


def replay_baseline_strategy(
    *,
    strategy: str = "all",
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    execution_mode: str = "isolated",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if execution_mode != "isolated":
        raise ValueError("baseline strategy replay only supports execution_mode=isolated")
    outputs = {}
    for strategy_id in selected_strategies(strategy):
        _ensure_preview(paths, strategy_id, start_date, end_date)
        outputs[strategy_id] = _replay_one(strategy_id, start_date, end_date, paths)
    return {
        "strategy": strategy,
        "execution_mode": execution_mode,
        "paths": outputs,
        "all_replays_complete": all(item["overall_passed"] for item in outputs.values()),
        "boundary": research_boundary("isolated_replay_only"),
    }


def _ensure_preview(paths: ProjectPaths, strategy_id: str, start_date: str, end_date: str) -> None:
    if preview_path(paths, strategy_id, start_date, end_date).exists():
        return
    generate_baseline_strategy_signals(strategy=strategy_id, start_date=start_date, end_date=end_date, paths=paths)
    signal_file = paths.data_dir / "strategies" / "signals" / f"baseline_signals-{strategy_id}-{start_date}-{end_date}.jsonl"
    build_baseline_order_preview(strategy=strategy_id, signals=str(signal_file), execution_mode="isolated", paths=paths)


def _replay_one(strategy_id: str, start_date: str, end_date: str, paths: ProjectPaths) -> dict[str, Any]:
    root = replay_root(paths, strategy_id)
    preview_rows = read_rows(preview_path(paths, strategy_id, start_date, end_date))
    prices, price_source = load_price_history(paths, start_date=start_date, end_date=end_date)
    first_signal_date = min(row["signal_date"] for row in preview_rows)
    first_execution_date = min(row["execution_date"] for row in preview_rows if row["signal_date"] == first_signal_date)
    buy_rows = [row for row in preview_rows if row["signal_date"] == first_signal_date]
    sell_date = next_execution_date(first_execution_date)
    state: dict[str, Any] = {"cash": 1_000_000.0, "positions": {}}
    orders: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    portfolio_rows: list[dict[str, Any]] = []
    valuation_rows: list[dict[str, Any]] = []
    first_filled_symbol: str | None = None
    for day in trading_dates(start_date, end_date)[:10]:
        settle_available_shares(state, day)
        if day == first_execution_date:
            for preview in buy_rows:
                order, trade = _execute_preview(preview, state, prices)
                orders.append(order)
                if trade:
                    trades.append(trade)
                    first_filled_symbol = first_filled_symbol or trade["symbol"]
        if day == sell_date and first_filled_symbol:
            sell_order, sell_trade = _execute_sell(strategy_id, first_filled_symbol, day, state, prices)
            orders.append(sell_order)
            if sell_trade:
                trades.append(sell_trade)
        snapshot = portfolio_snapshot(state, _prices_for_day(prices, day))
        portfolio_rows.append({"date": day, **snapshot})
        valuation_rows.append(
            {
                "date": day,
                "cash": snapshot["cash"],
                "market_value": snapshot["market_value"],
                "total_asset": snapshot["total_asset"],
                "price_source": price_source["source"],
            }
        )
    orders_path = root / "orders" / f"orders-{start_date}-{end_date}.jsonl"
    trades_path = root / "trades" / f"trades-{start_date}-{end_date}.jsonl"
    portfolio_path = root / "portfolio" / f"portfolio-{start_date}-{end_date}.jsonl"
    valuations_path = root / "valuations" / f"valuations-{start_date}-{end_date}.jsonl"
    rows_and_paths(orders_path, orders)
    rows_and_paths(trades_path, trades)
    rows_and_paths(portfolio_path, portfolio_rows)
    rows_and_paths(valuations_path, valuation_rows)
    rejected = [row for row in orders if row.get("status") == "rejected"]
    cost_summary = {
        "commission": round(sum(float(row.get("commission", 0.0)) for row in trades), 6),
        "tax": round(sum(float(row.get("tax", 0.0)) for row in trades), 6),
        "slippage": round(sum(float(row.get("slippage", 0.0)) for row in trades), 6),
    }
    summary = {
        "strategy_id": strategy_id,
        "start_date": start_date,
        "end_date": end_date,
        "execution_mode": "isolated",
        "uses_v059_virtual_execution_contract": True,
        "orders_path": rel(orders_path, paths),
        "trades_path": rel(trades_path, paths),
        "portfolio_path": rel(portfolio_path, paths),
        "valuations_path": rel(valuations_path, paths),
        "orders": len(orders),
        "trades": len(trades),
        "rejected_orders": len(rejected),
        "rejected_order_reasons": sorted({row.get("reject_reason") for row in rejected if row.get("reject_reason")}),
        "cost_summary": cost_summary,
        "daily_valuation_rows": len(valuation_rows),
        "benchmark_comparison_input": rel(valuations_path, paths),
        "no_trade_fallback": False,
        "strategy_effectiveness_proven": False,
        "boundary": research_boundary("isolated_replay_only"),
    }
    summary["overall_passed"] = bool(trades) and bool(valuation_rows) and str(root).startswith(str(paths.data_dir / "replays" / "strategies"))
    summary_path = replay_summary_path(paths, strategy_id, start_date, end_date)
    write_json(summary_path, summary)
    md_path = replay_report_path(paths, strategy_id, start_date, end_date)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_build_markdown(summary, paths), encoding="utf-8")
    return {**summary, "json_path": str(summary_path), "report_path": str(md_path)}


def _execute_preview(
    preview: dict[str, Any],
    state: dict[str, Any],
    prices: dict[str, dict[str, float]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    day = str(preview["execution_date"])
    symbol = str(preview["symbol"])
    _, price = price_on_or_before(prices, symbol, day)
    order = {
        "order_id": preview["order_id"],
        "date": day,
        "execution_date": day,
        "symbol": symbol,
        "market": preview.get("market", "A_SHARE"),
        "side": preview.get("side", "BUY"),
        "quantity": int(preview.get("quantity", 0)),
        "strategy_id": preview["strategy_id"],
    }
    return execute_virtual_order(order, state, {"date": day, "status_date": day, "price": price, "status": simulated_price_status(symbol, day)})


def _execute_sell(
    strategy_id: str,
    symbol: str,
    day: str,
    state: dict[str, Any],
    prices: dict[str, dict[str, float]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    _, price = price_on_or_before(prices, symbol, day)
    position = state.setdefault("positions", {}).get(symbol, {})
    quantity = min(100, int(position.get("available_quantity", 0)))
    order = {
        "order_id": f"ORD-BSP-{strategy_id[:3].upper()}-SELL-0001",
        "date": day,
        "execution_date": day,
        "symbol": symbol,
        "market": "A_SHARE",
        "side": "SELL",
        "quantity": quantity,
        "strategy_id": strategy_id,
    }
    return execute_virtual_order(order, state, {"date": day, "status_date": day, "price": price, "status": "tradable"})


def _prices_for_day(prices: dict[str, dict[str, float]], day: str) -> dict[str, float]:
    values = {}
    symbols = {symbol for row in prices.values() for symbol in row}
    for symbol in symbols:
        _, price = price_on_or_before(prices, symbol, day)
        if price is not None:
            values[symbol] = price
    return values


def _build_markdown(summary: dict[str, Any], paths: ProjectPaths) -> str:
    lines = [
        f"# Baseline Strategy Replay - {summary['strategy_id']}",
        "",
        RESEARCH_NOTICE,
        "",
        "## Summary",
        f"- execution_mode: {summary['execution_mode']}",
        f"- orders: {summary['orders']}",
        f"- trades: {summary['trades']}",
        f"- rejected_orders: {summary['rejected_orders']}",
        f"- valuations: {summary['daily_valuation_rows']}",
        "- no_trade_fallback=false",
        "- not strategy effectiveness proof",
        "",
        "## Boundary",
        "- isolated replay only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
        "",
    ]
    return "\n".join(lines)
