"""Historical ETF backtesting over imported daily bars."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.accounting.account import Account
from trading_core.accounting.valuation import value_account
from trading_core.backtest.event_backtester import date_range
from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.broker.virtual_broker import process_signals
from trading_core.config_loader import load_config
from trading_core.data.historical_prices import load_imported_prices, prices_by_date
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json, write_jsonl
from trading_core.universe.universe_loader import universe_symbols


def run_historical_backtest(
    start_date: str,
    end_date: str,
    strategy_id: str,
    market: str = "A_SHARE",
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    paths = project_paths(workspace_root)
    settings = load_config("settings.yaml")
    account = Account(
        account_id=settings["default_account_id"],
        cash=float(settings["initial_account"]["initial_cash"]),
    )
    rows = load_imported_prices(market, paths)
    grouped_prices = prices_by_date(rows)
    dates = [date for date in date_range(start_date, end_date) if date in grouped_prices]
    pending_signals: list[dict[str, Any]] = []
    pending_signal_date: str | None = None
    previous_total = account.total_asset
    all_trades: list[dict[str, Any]] = []
    portfolio_rows: list[dict[str, Any]] = []
    daily_benchmarks: list[dict[str, Any]] = []
    limitations: list[str] = []
    turnover = 0.0

    for date in dates:
        close_prices = _close_price_rows(grouped_prices[date])
        open_prices = _open_price_rows(grouped_prices[date])
        orders, trades = process_signals(pending_signals, date, account, open_prices) if pending_signals else ([], [])
        all_trades.extend(_stamp_backtest_trade(trade, strategy_id, pending_signal_date) for trade in trades)
        turnover += sum(float(trade.get("gross_amount", 0.0)) for trade in trades)
        valuation = value_account(account, date, {symbol: row["price"] for symbol, row in close_prices.items()}, previous_total)
        portfolio = account.to_portfolio(date, previous_total)
        portfolio["strategy_id"] = strategy_id
        portfolio["executed_signal_date"] = pending_signal_date if trades else None
        portfolio_rows.append(portfolio)
        benchmark = build_benchmark(date, portfolio, close_prices, paths)
        daily_benchmarks.append(benchmark)
        previous_total = float(portfolio["total_asset"])

        generated = _generate_strategy_signals(strategy_id, date, grouped_prices, settings["default_account_id"])
        if strategy_id == "momentum_strategy_v1" and generated and generated[0].get("history_days", 0) < 20:
            limitations.append(f"{date}: insufficient_20d_history")
            generated = []
        pending_signals = generated
        pending_signal_date = date

    suffix = f"{start_date}-{end_date}-{strategy_id}"
    trades_path = paths.data_dir / "backtests" / f"backtest_trades-{suffix}.jsonl"
    portfolio_path = paths.data_dir / "backtests" / f"backtest_portfolio-{suffix}.jsonl"
    benchmark_path = paths.data_dir / "backtests" / f"backtest_benchmark-{suffix}.json"
    report_path = paths.outputs_dir / "backtests" / f"backtest_report-{suffix}.md"
    benchmark_summary = daily_benchmarks[-1] if daily_benchmarks else {}
    write_jsonl(trades_path, all_trades)
    write_jsonl(portfolio_path, portfolio_rows)
    write_json(benchmark_path, benchmark_summary)
    report = _build_backtest_report(
        start_date,
        end_date,
        strategy_id,
        portfolio_rows,
        all_trades,
        benchmark_summary,
        turnover,
        limitations,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return {
        "start_date": start_date,
        "end_date": end_date,
        "strategy_id": strategy_id,
        "days": len(portfolio_rows),
        "trades_count": len(all_trades),
        "trades_path": str(trades_path),
        "portfolio_path": str(portfolio_path),
        "benchmark_path": str(benchmark_path),
        "report_path": str(report_path),
        "limitations": limitations,
    }


def _close_price_rows(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        symbol: {
            **row,
            "price": row["close"],
            "change_pct": (row["close"] / row["previous_close"] - 1) if row["previous_close"] else 0.0,
        }
        for symbol, row in rows.items()
    }


def _open_price_rows(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        symbol: {
            **row,
            "price": row["open"],
            "quality": row.get("quality", "fresh"),
        }
        for symbol, row in rows.items()
    }


def _generate_strategy_signals(
    strategy_id: str,
    date: str,
    grouped_prices: dict[str, dict[str, dict[str, Any]]],
    account_id: str,
) -> list[dict[str, Any]]:
    if strategy_id == "hold_strategy":
        return []
    if strategy_id == "macro_etf_strategy_v1":
        symbols = [symbol for symbol in universe_symbols(market="A_SHARE") if symbol in grouped_prices.get(date, {})]
        symbol = symbols[0] if symbols else None
        return [_signal(date, account_id, strategy_id, symbol, history_days=0)] if symbol else []
    if strategy_id == "momentum_strategy_v1":
        history = _momentum_history(date, grouped_prices)
        if not history:
            return []
        ranked = sorted(history.items(), key=lambda item: item[1]["return"], reverse=True)
        return [
            _signal(date, account_id, strategy_id, symbol, history_days=values["days"])
            for symbol, values in ranked[:2]
        ]
    raise ValueError(f"Unsupported strategy_id: {strategy_id}")


def _momentum_history(date: str, grouped_prices: dict[str, dict[str, dict[str, Any]]]) -> dict[str, dict[str, float]]:
    dates = sorted(d for d in grouped_prices if d <= date)
    if date not in dates:
        return {}
    end_index = dates.index(date)
    start_index = max(0, end_index - 19)
    window_dates = dates[start_index : end_index + 1]
    result = {}
    for symbol in universe_symbols(market="A_SHARE"):
        values = [grouped_prices[d][symbol]["close"] for d in window_dates if symbol in grouped_prices[d]]
        if len(values) >= 2:
            result[symbol] = {"return": (values[-1] / values[0]) - 1, "days": len(values)}
    return result


def _signal(date: str, account_id: str, strategy_id: str, symbol: str, history_days: int) -> dict[str, Any]:
    return {
        "signal_id": f"BT-SIG-{date.replace('-', '')}-{strategy_id}-{symbol}",
        "macro_signal_id": None,
        "date": date,
        "strategy_id": strategy_id,
        "account_id": account_id,
        "symbol": symbol,
        "market": "A_SHARE",
        "signal_time": f"{date} 15:10:00",
        "side": "LONG",
        "target_weight": 0.05,
        "confidence": 0.60,
        "reason": f"{strategy_id} historical rule",
        "risk_flags": [],
        "status": "candidate",
        "history_days": history_days,
    }


def _stamp_backtest_trade(trade: dict[str, Any], strategy_id: str, signal_date: str | None) -> dict[str, Any]:
    row = dict(trade)
    row["strategy_id"] = strategy_id
    row["signal_date"] = signal_date
    return row


def _build_backtest_report(
    start_date: str,
    end_date: str,
    strategy_id: str,
    portfolios: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    benchmark: dict[str, Any],
    turnover: float,
    limitations: list[str],
) -> str:
    initial = 100000.0
    final = float(portfolios[-1]["total_asset"]) if portfolios else initial
    returns = [(float(row["total_asset"]) / initial) - 1 for row in portfolios] if portfolios else [0.0]
    max_drawdown = min((float(row.get("max_drawdown", 0.0)) for row in portfolios), default=0.0)
    wins = len([trade for trade in trades if float(trade.get("net_amount", 0.0)) > 0])
    cost = sum(float(trade.get("commission", 0.0)) + float(trade.get("tax", 0.0)) for trade in trades)
    turnover_rate = turnover / initial if initial else 0.0
    excess = benchmark.get("excess_return", {}) if benchmark else {}
    lines = [
        f"# Backtest Report {start_date} to {end_date} {strategy_id}",
        "",
        f"- Initial capital: {initial}",
        f"- Final capital: {round(final, 6)}",
        f"- Cumulative return: {round((final / initial) - 1, 8)}",
        f"- Max drawdown: {round(max_drawdown, 8)}",
        f"- Win rate: {round(wins / len(trades), 6) if trades else 0.0}",
        f"- Trade count: {len(trades)}",
        f"- Turnover: {round(turnover_rate, 8)}",
        f"- Total cost: {round(cost, 6)}",
        f"- Benchmark comparison: {benchmark.get('benchmarks', {}) if benchmark else {}}",
        f"- Excess return: {excess}",
        f"- Limitation: {limitations if limitations else 'none'}",
    ]
    return "\n".join(lines) + "\n"
