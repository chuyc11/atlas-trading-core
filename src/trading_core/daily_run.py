"""End-to-end daily pipeline for the virtual trading core."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.accounting.account import account_from_portfolio
from trading_core.accounting.valuation import value_account
from trading_core.attribution.attribution_engine import build_attribution
from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.broker.virtual_broker import process_signals
from trading_core.calendar.trading_calendar import previous_trading_day
from trading_core.config_loader import load_config
from trading_core.data.price_loader import load_china_prices, simple_price_map
from trading_core.evolution.evolution_engine import run_evolution
from trading_core.evolution.shadow_runner import run_shadow
from trading_core.reports.daily_report import generate_daily_report
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.runtime.health import build_runtime_health
from trading_core.signals.macro_signal_loader import filter_china_macro_signals, load_macro_signals
from trading_core.signals.signal_generator import generate_trading_signals, hold_signal
from trading_core.storage.file_paths import ProjectPaths, ensure_project_dirs, project_paths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl
from trading_core.universe.universe_loader import load_universe


def _data_quality_counts(
    prices: dict[str, dict[str, Any]],
    required_symbols: list[str] | None = None,
) -> dict[str, int]:
    counts = {"fresh": 0, "fallback": 0, "stale": 0, "missing": 0}
    for row in prices.values():
        quality = str(row.get("quality", "missing"))
        counts[quality] = counts.get(quality, 0) + 1
    required_symbols = required_symbols or []
    for symbol in required_symbols:
        if symbol not in prices:
            counts["missing"] += 1
    if not prices and not required_symbols:
        counts["missing"] += 1
    return counts


def _previous_portfolio(paths: ProjectPaths, date: str) -> dict[str, Any] | None:
    previous = previous_trading_day(date, paths=paths)
    return read_json(paths.dated_json("portfolios", "portfolio", previous), default=None)


def _required_signal_symbols(signals: list[dict[str, Any]]) -> list[str]:
    return [
        str(signal["symbol"])
        for signal in signals
        if signal.get("symbol") not in (None, "CASH") and signal.get("side") != "HOLD"
    ]


def _append_price_quality_limitations(
    limitations: list[str],
    signals: list[dict[str, Any]],
    prices: dict[str, dict[str, Any]],
) -> None:
    for signal in signals:
        symbol = str(signal.get("symbol"))
        if symbol in ("None", "CASH") or signal.get("side") == "HOLD":
            continue
        row = prices.get(symbol)
        if row is None or row.get("price") is None:
            limitations.append(f"missing_price: {symbol}")
            continue
        quality = str(row.get("quality", "missing"))
        side = str(signal.get("side", "")).upper()
        if quality != "fresh" and side in {"LONG", "BUY"}:
            limitations.append(f"{quality}_price_blocks_buy: {symbol}")


def run_daily(date: str, workspace_root: Path | None = None) -> dict[str, Any]:
    paths = project_paths(workspace_root)
    ensure_project_dirs(paths)

    settings = load_config("settings.yaml")
    universe = load_universe()
    account_id = settings["default_account_id"]
    initial_cash = float(settings["initial_account"]["initial_cash"])
    previous_portfolio = _previous_portfolio(paths, date)
    account = account_from_portfolio(previous_portfolio, account_id, initial_cash, paths=paths)
    account.settle_t_plus_one(date, paths=paths)
    previous_total = float(previous_portfolio["total_asset"]) if previous_portfolio else account.total_asset

    limitations: list[str] = []
    prices, price_limitations = load_china_prices(date, paths)
    limitations.extend(price_limitations)

    macro_rows, macro_limitations = load_macro_signals(date, paths)
    limitations.extend(macro_limitations)
    filtered_macro = filter_china_macro_signals(macro_rows, universe)

    if filtered_macro:
        signals = generate_trading_signals(filtered_macro, date, account_id, universe=universe)
        if not signals:
            signals = [hold_signal(date, account_id, "macro signals did not pass confidence/universe filters")]
            limitations.append("macro signals produced no tradable ETF signal")
    else:
        signals = [hold_signal(date, account_id, "no CHINA macro signal available")]

    _append_price_quality_limitations(limitations, signals, prices)
    data_quality_summary = {
        "date": date,
        "counts": _data_quality_counts(prices, _required_signal_symbols(signals)),
        "limitations": [
            item
            for item in limitations
            if "price" in item or "snapshot" in item
        ],
    }
    write_json(paths.dated_json("snapshots", "data_quality", date), data_quality_summary)

    write_jsonl(paths.dated_jsonl("signals", "trading_signals", date), signals)
    orders, trades = process_signals(signals, date, account, prices, paths=paths)
    write_jsonl(paths.dated_jsonl("orders", "orders", date), orders)
    write_jsonl(paths.dated_jsonl("trades", "trades", date), trades)

    valuation = value_account(account, date, simple_price_map(prices), previous_total)
    write_jsonl(paths.dated_jsonl("valuations", "valuations", date), [valuation])
    portfolio = account.to_portfolio(date, previous_total)
    write_json(paths.dated_json("portfolios", "portfolio", date), portfolio)

    benchmark = build_benchmark(date, portfolio, prices, paths)
    attribution = build_attribution(date, portfolio, trades, benchmark, previous_portfolio, paths)
    shadow_signals = run_shadow(date, account_id, prices, paths)
    evolution = run_evolution(date, signals, trades, valuation, benchmark, paths)

    report_markdown = generate_daily_report(
        date=date,
        portfolio=portfolio,
        data_quality=data_quality_summary["counts"],
        macro_signals=filtered_macro,
        signals=signals,
        orders=orders,
        trades=trades,
        benchmark=benchmark,
        attribution=attribution,
        evolution=evolution,
        limitations=limitations,
        paths=paths,
    )
    health = build_runtime_health(
        {
            "date": date,
            "paths": paths,
            "limitations": limitations,
            "macro_signals": filtered_macro,
            "signals": signals,
            "orders": orders,
            "trades": trades,
            "portfolio": portfolio,
            "benchmark": benchmark,
            "attribution": attribution,
            "data_quality": data_quality_summary,
            "evolution": evolution,
        },
        paths,
    )
    trading_summary = export_trading_summary(date, paths)

    return {
        "date": date,
        "paths": paths,
        "limitations": limitations,
        "macro_signals": filtered_macro,
        "signals": signals,
        "orders": orders,
        "trades": trades,
        "portfolio": portfolio,
        "valuation": valuation,
        "benchmark": benchmark,
        "attribution": attribution,
        "data_quality": data_quality_summary,
        "shadow_signals": shadow_signals,
        "evolution": evolution,
        "health": health,
        "trading_summary": trading_summary,
        "report_markdown": report_markdown,
    }
