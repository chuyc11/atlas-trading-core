"""Event-driven daily backtester."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from trading_core.accounting.account import Account
from trading_core.accounting.valuation import value_account
from trading_core.calendar.trading_calendar import is_trading_day, parse_date
from trading_core.broker.virtual_broker import process_signals
from trading_core.config_loader import load_config
from trading_core.data.price_loader import load_china_prices, simple_price_map
from trading_core.signals.macro_signal_loader import filter_china_macro_signals, load_macro_signals
from trading_core.signals.signal_generator import generate_trading_signals, hold_signal
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import write_json
from trading_core.universe.universe_loader import load_universe


def date_range(start_date: str, end_date: str, paths: Any | None = None) -> list[str]:
    current = parse_date(start_date)
    end = parse_date(end_date)
    dates = []
    while current <= end:
        if is_trading_day(current, paths=paths):
            dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates


def run_event_backtest(
    start_date: str,
    end_date: str,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    paths = project_paths(workspace_root)
    dates = date_range(start_date, end_date, paths=paths)
    settings = load_config("settings.yaml")
    universe = load_universe()
    account_id = settings["default_account_id"]
    account = Account(account_id, cash=float(settings["initial_account"]["initial_cash"]))
    previous_total = account.total_asset
    daily = []
    pending_signals: list[dict[str, Any]] = []
    pending_signal_date: str | None = None
    for date in dates:
        account.settle_t_plus_one()
        prices, price_limitations = load_china_prices(date, paths)
        executed_signals = pending_signals
        executed_signal_date = pending_signal_date
        orders, trades = process_signals(executed_signals, date, account, prices) if executed_signals else ([], [])
        valuation = value_account(account, date, simple_price_map(prices), previous_total)
        portfolio = account.to_portfolio(date, previous_total)
        previous_total = float(valuation["total_asset"])

        macro_rows, macro_limitations = load_macro_signals(date, paths)
        filtered_macro = filter_china_macro_signals(macro_rows, universe)
        if filtered_macro:
            generated_signals = generate_trading_signals(filtered_macro, date, account_id, universe=universe)
        else:
            generated_signals = [hold_signal(date, account_id, "no CHINA macro signal available")]
        pending_signals = generated_signals
        pending_signal_date = date

        daily.append(
            {
                "date": date,
                "total_asset": valuation["total_asset"],
                "daily_return": valuation["daily_return"],
                "generated_signal_count": len(generated_signals),
                "executed_signal_count": len(executed_signals),
                "trade_count": len(trades),
                "orders": orders,
                "trades": trades,
                "cash": portfolio["cash"],
                "positions": portfolio["positions"],
                "executed_signal_date": executed_signal_date if executed_signals else None,
                "limitations": price_limitations + macro_limitations,
            }
        )
    start_asset = daily[0]["total_asset"] if daily else 0.0
    end_asset = daily[-1]["total_asset"] if daily else 0.0
    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "days": len(daily),
        "start_asset": start_asset,
        "end_asset": end_asset,
        "total_return": round((end_asset / start_asset) - 1, 8) if start_asset else 0.0,
        "daily": daily,
        "execution_model": "T day generates signals; next trading day executes pending signals.",
        "pit_note": "Backtest uses only files available for each loop date; no future-dated file is read.",
    }
    write_json(paths.outputs_dir / "backtests" / f"event-backtest-{start_date}-to-{end_date}.json", summary)
    return summary
