"""Historical dry-run replay over local ETF price packages."""

from __future__ import annotations

import csv
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading_core.accounting.account import Account
from trading_core.accounting.valuation import value_account
from trading_core.attribution.attribution_engine import build_attribution
from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.broker.virtual_broker import process_signals
from trading_core.config_loader import load_config
from trading_core.evolution.evolution_engine import run_evolution
from trading_core.evolution.shadow_runner import run_shadow
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.signals.macro_signal_loader import filter_china_macro_signals, load_macro_signals
from trading_core.signals.signal_generator import generate_trading_signals, hold_signal
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl
from trading_core.universe.universe_loader import load_universe, universe_by_symbol


REPLAY_INITIAL_CAPITAL = 100000.0


@dataclass(frozen=True)
class ReplayPaths:
    base_paths: ProjectPaths
    replay_id: str

    @property
    def workspace_root(self) -> Path:
        return self.base_paths.workspace_root

    @property
    def project_root(self) -> Path:
        return self.base_paths.project_root

    @property
    def data_dir(self) -> Path:
        return self.base_paths.data_dir / "replays" / self.replay_id

    @property
    def outputs_dir(self) -> Path:
        return self.base_paths.outputs_dir / "replays" / self.replay_id

    @property
    def global_briefing_data_dir(self) -> Path:
        return self.base_paths.global_briefing_data_dir

    def dated_jsonl(self, bucket: str, stem: str, date: str) -> Path:
        return self.data_dir / bucket / f"{stem}-{date}.jsonl"

    def dated_json(self, bucket: str, stem: str, date: str) -> Path:
        return self.data_dir / bucket / f"{stem}-{date}.json"

    def daily_report(self, date: str) -> Path:
        return self.outputs_dir / "daily" / f"virtual-trading-report-{date}.md"


def replay_last_trading_days(
    days: int,
    end_date: str,
    data_path: Path,
    paths: ProjectPaths | None = None,
    write_main_ledger: bool = False,
) -> dict[str, Any]:
    paths = paths or project_paths()
    grouped = _load_price_package(data_path, paths)
    trading_days = [day for day in sorted(grouped) if day <= end_date]
    selected = trading_days[-days:]
    if not selected:
        raise ValueError("no trading days found in data package")
    return replay_dry_run(selected[0], selected[-1], data_path, paths, write_main_ledger=write_main_ledger)


def replay_dry_run(
    start_date: str,
    end_date: str,
    data_path: Path,
    paths: ProjectPaths | None = None,
    write_main_ledger: bool = False,
) -> dict[str, Any]:
    paths = paths or project_paths()
    grouped = _load_price_package(data_path, paths)
    days = [day for day in sorted(grouped) if start_date <= day <= end_date]
    replay_id = f"replay-{start_date}-{end_date}"
    replay_paths = ReplayPaths(paths, replay_id)
    _reset_replay_dirs(replay_paths)
    if write_main_ledger:
        raise ValueError("--write-main-ledger is intentionally unsupported for historical replay")

    settings = load_config("settings.yaml")
    account_id = str(settings["default_account_id"])
    account = Account(account_id=account_id, cash=float(settings["initial_account"]["initial_cash"]))
    universe = load_universe()
    previous_portfolio: dict[str, Any] | None = None
    previous_total = account.total_asset
    day_results: list[dict[str, Any]] = []
    missing_global_briefing_days: list[str] = []
    missing_price_days = _missing_price_days(start_date, end_date, grouped)
    macro_signal_days = 0
    price_only_replay = True

    for day in days:
        account.settle_t_plus_one()
        close_prices = _close_price_rows(grouped[day])
        macro_rows, macro_limitations = load_macro_signals(day, replay_paths)
        input_missing = _missing_global_inputs(day, paths)
        if input_missing:
            missing_global_briefing_days.append(day)
        filtered_macro = filter_china_macro_signals(macro_rows, universe)
        if filtered_macro:
            macro_signal_days += 1
            price_only_replay = False
            signals = generate_trading_signals(filtered_macro, day, account_id, universe=universe)
            if not signals:
                signals = [hold_signal(day, account_id, "macro signals did not pass confidence/universe filters")]
        else:
            signals = [hold_signal(day, account_id, "historical replay no_signal/HOLD due to missing or empty macro_signals")]
        write_jsonl(replay_paths.dated_jsonl("signals", "trading_signals", day), signals)

        orders, trades = process_signals(signals, day, account, close_prices)
        _stamp_quality(orders, close_prices)
        write_jsonl(replay_paths.dated_jsonl("orders", "orders", day), orders)
        write_jsonl(replay_paths.dated_jsonl("trades", "trades", day), trades)

        valuation = value_account(account, day, {symbol: row["price"] for symbol, row in close_prices.items()}, previous_total)
        write_jsonl(replay_paths.dated_jsonl("valuations", "valuations", day), [valuation])
        portfolio = account.to_portfolio(day, previous_total)
        write_json(replay_paths.dated_json("portfolios", "portfolio", day), portfolio)
        benchmark = build_benchmark(day, portfolio, close_prices, replay_paths)
        attribution = build_attribution(day, portfolio, trades, benchmark, previous_portfolio, replay_paths)
        shadow = run_shadow(day, account_id, close_prices, replay_paths)
        evolution = run_evolution(day, signals, trades, valuation, benchmark, replay_paths)
        export_trading_summary(day, replay_paths)
        _write_replay_health(
            day,
            replay_paths,
            input_missing,
            macro_rows,
            signals,
            orders,
            trades,
            portfolio,
            close_prices,
            attribution,
            evolution,
        )
        day_results.append(
            {
                "date": day,
                "status": "success",
                "signals": len(signals),
                "orders": len(orders),
                "trades": len(trades),
                "macro_signals": len(macro_rows),
                "shadow_signals": len(shadow),
                "input_missing": input_missing,
            }
        )
        previous_total = float(portfolio["total_asset"])
        previous_portfolio = portfolio

    audit = _build_replay_audit(
        replay_paths,
        start_date,
        end_date,
        days,
        day_results,
        missing_global_briefing_days,
        missing_price_days,
        macro_signal_days,
        price_only_replay,
    )
    return audit


def _load_price_package(data_path: Path, paths: ProjectPaths) -> dict[str, dict[str, dict[str, Any]]]:
    data_path = _resolve_data_path(data_path, paths)
    rows = []
    files = sorted(data_path.glob("*.csv")) if data_path.is_dir() else [data_path]
    for file_path in files:
        if file_path.name in {"manifest.json", "merge_manifest.json"}:
            continue
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(row)
    by_symbol = universe_by_symbol()
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    previous_close: dict[str, float] = {}
    for row in sorted(rows, key=lambda item: (str(item["symbol"]), str(item["date"]))):
        symbol = str(row["symbol"])
        day = str(row["date"])
        close = float(row["close"])
        prior = previous_close.get(symbol, close)
        market = by_symbol.get(symbol, {}).get("market", "A_SHARE")
        grouped.setdefault(day, {})[symbol] = {
            "symbol": symbol,
            "market": market,
            "open": float(row["open"]),
            "price": close,
            "close": close,
            "previous_close": prior,
            "volume": float(row["volume"]),
            "source": row.get("source"),
            "quality": row.get("quality", "fresh"),
        }
        previous_close[symbol] = close
    return grouped


def _resolve_data_path(data_path: Path, paths: ProjectPaths) -> Path:
    if data_path.is_absolute():
        return data_path
    parts = [part.lower() for part in data_path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / data_path
    return paths.project_root / data_path


def _reset_replay_dirs(replay_paths: ReplayPaths) -> None:
    for path in [replay_paths.data_dir, replay_paths.outputs_dir]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def _close_price_rows(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {symbol: {**row, "price": float(row["close"])} for symbol, row in rows.items()}


def _missing_price_days(start_date: str, end_date: str, grouped: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    from trading_core.backtest.event_backtester import date_range

    return [day for day in date_range(start_date, end_date) if day not in grouped]


def _missing_global_inputs(day: str, paths: ProjectPaths) -> list[str]:
    expected = [
        paths.global_briefing_data_dir / f"macro_signals-{day}.jsonl",
        paths.global_briefing_data_dir / f"china-market-snapshot-{day}.json",
    ]
    return [str(path) for path in expected if not path.exists()]


def _stamp_quality(orders: list[dict[str, Any]], prices: dict[str, dict[str, Any]]) -> None:
    for order in orders:
        row = prices.get(str(order.get("symbol")))
        order["price_quality"] = str(row.get("quality", "missing")) if row else "missing"


def _write_replay_health(
    day: str,
    replay_paths: ReplayPaths,
    input_missing: list[str],
    macro_rows: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    orders: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    portfolio: dict[str, Any],
    prices: dict[str, dict[str, Any]],
    attribution: dict[str, Any],
    evolution: dict[str, Any],
) -> None:
    counts = Counter(str(row.get("quality", "missing")) for row in prices.values())
    write_json(
        replay_paths.dated_json("runtime", "health", day),
        {
            "date": day,
            "input_files_missing": input_missing,
            "macro_signals_count": len(macro_rows),
            "trading_signals_count": len(signals),
            "orders_count": len(orders),
            "trades_count": len(trades),
            "rejected_orders_count": len([order for order in orders if order.get("status") == "rejected"]),
            "fallback_prices_count": int(counts.get("fallback", 0)),
            "stale_prices_count": int(counts.get("stale", 0)),
            "missing_prices_count": int(counts.get("missing", 0)),
            "portfolio_total_asset": portfolio.get("total_asset"),
            "cash": portfolio.get("cash"),
            "market_value": portfolio.get("market_value"),
            "attribution_status": "ok" if attribution else "missing",
            "evolution_status": "ok" if evolution else "missing",
            "errors": [],
        },
    )


def _build_replay_audit(
    replay_paths: ReplayPaths,
    start_date: str,
    end_date: str,
    days: list[str],
    day_results: list[dict[str, Any]],
    missing_global_briefing_days: list[str],
    missing_price_days: list[str],
    macro_signal_days: int,
    price_only_replay: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if missing_global_briefing_days:
        warnings.append("missing global-briefing inputs; affected dates used no_signal/HOLD")
    if price_only_replay:
        warnings.append("price-only replay: no real macro_signals were available")
    stats = _audit_replay_days(replay_paths, days, errors, warnings)
    consistency_status = {"passed": not errors, "critical_errors": errors}
    historical_replay_passed = len(days) >= 30 and not errors
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "trading_days_expected": len(days),
        "trading_days_replayed": len(day_results),
        "missing_global_briefing_days": sorted(set(missing_global_briefing_days)),
        "missing_price_days": missing_price_days,
        "successful_days": [row["date"] for row in day_results if row["status"] == "success"],
        "failed_days": [row["date"] for row in day_results if row["status"] != "success"],
        "total_signals": stats["total_signals"],
        "total_orders": stats["total_orders"],
        "total_trades": stats["total_trades"],
        "rejected_orders": stats["rejected_orders"],
        "most_common_rejection_reasons": dict(stats["rejection_reasons"].most_common()),
        "portfolio_continuity_status": stats["portfolio_continuity_status"],
        "duplicate_order_status": stats["duplicate_order_status"],
        "duplicate_trade_status": stats["duplicate_trade_status"],
        "T+1_status": stats["t_plus_one_status"],
        "benchmark_status": stats["benchmark_status"],
        "attribution_status": stats["attribution_status"],
        "consistency_status": consistency_status,
        "evolution_throttling_status": stats["evolution_throttling_status"],
        "historical_replay_passed": historical_replay_passed,
        "forward_30d_dry_run_passed": False,
        "macro_signal_days": macro_signal_days,
        "price_only_replay": price_only_replay,
        "warnings": warnings,
        "release_recommendation": "historical_replay_candidate" if historical_replay_passed else "do_not_release_fix_replay_issues",
    }
    write_json(replay_paths.outputs_dir / "replay_audit.json", payload)
    replay_paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    (replay_paths.outputs_dir / "REPLAY_AUDIT.md").write_text(_replay_audit_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(replay_paths.outputs_dir / "replay_audit.json")
    payload["report_path"] = str(replay_paths.outputs_dir / "REPLAY_AUDIT.md")
    return payload


def _audit_replay_days(replay_paths: ReplayPaths, days: list[str], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    seen_orders: set[str] = set()
    seen_trades: set[str] = set()
    duplicate_orders: list[str] = []
    duplicate_trades: list[str] = []
    rejection_reasons: Counter[str] = Counter()
    total_signals = total_orders = total_trades = rejected_orders = 0
    previous_portfolio: dict[str, Any] | None = None
    portfolio_missing: list[str] = []
    benchmark_errors: list[str] = []
    attribution_errors: list[str] = []
    t1_errors: list[str] = []
    evolution_errors: list[str] = []
    blocked_quality_errors: list[str] = []

    for day in days:
        signals = read_jsonl(replay_paths.dated_jsonl("signals", "trading_signals", day))
        orders = read_jsonl(replay_paths.dated_jsonl("orders", "orders", day))
        trades = read_jsonl(replay_paths.dated_jsonl("trades", "trades", day))
        portfolio = read_json(replay_paths.dated_json("portfolios", "portfolio", day), default={})
        benchmark = read_json(replay_paths.dated_json("benchmarks", "benchmark", day), default={})
        attribution = read_json(replay_paths.dated_json("attribution", "attribution", day), default={})
        evolution = read_json(replay_paths.data_dir / "evolution" / f"evolution-summary-{day}.json", default={})
        total_signals += len(signals)
        total_orders += len(orders)
        total_trades += len(trades)
        rejected_orders += len([order for order in orders if order.get("status") == "rejected"])
        for order in orders:
            order_id = str(order.get("order_id"))
            if order_id in seen_orders:
                duplicate_orders.append(order_id)
            seen_orders.add(order_id)
            if order.get("status") == "rejected":
                rejection_reasons[str(order.get("risk_reason", "unknown"))] += 1
            if order.get("side") == "BUY" and order.get("status") in {"submitted", "filled"}:
                if order.get("price_quality") in {"fallback", "stale", "missing"}:
                    blocked_quality_errors.append(f"{day}: BUY on {order.get('price_quality')} price {order.get('symbol')}")
        for trade in trades:
            trade_id = str(trade.get("trade_id"))
            if trade_id in seen_trades:
                duplicate_trades.append(trade_id)
            seen_trades.add(trade_id)
        if not portfolio:
            portfolio_missing.append(day)
        else:
            _audit_portfolio(day, portfolio, previous_portfolio, errors)
            previous_portfolio = portfolio
            _audit_t_plus_one(day, portfolio, t1_errors)
        if not benchmark or not benchmark.get("benchmarks"):
            benchmark_errors.append(f"{day}: missing benchmark")
        if not attribution or abs(float(attribution.get("residual_pnl", 0.0))) > 0.01:
            attribution_errors.append(f"{day}: attribution missing or residual")
        _audit_evolution(day, evolution, evolution_errors, warnings)

    if duplicate_orders:
        errors.extend(f"duplicate order_id {item}" for item in sorted(set(duplicate_orders)))
    if duplicate_trades:
        errors.extend(f"duplicate trade_id {item}" for item in sorted(set(duplicate_trades)))
    errors.extend(blocked_quality_errors)
    errors.extend(t1_errors)
    errors.extend(benchmark_errors)
    errors.extend(attribution_errors)
    errors.extend(evolution_errors)
    if portfolio_missing:
        errors.extend(f"missing replay portfolio {day}" for day in portfolio_missing)
    shadow_errors = _audit_shadow(replay_paths)
    errors.extend(shadow_errors)
    return {
        "total_signals": total_signals,
        "total_orders": total_orders,
        "total_trades": total_trades,
        "rejected_orders": rejected_orders,
        "rejection_reasons": rejection_reasons,
        "portfolio_continuity_status": {"passed": not portfolio_missing, "missing_days": portfolio_missing},
        "duplicate_order_status": {"passed": not duplicate_orders, "duplicate_order_ids": sorted(set(duplicate_orders))},
        "duplicate_trade_status": {"passed": not duplicate_trades, "duplicate_trade_ids": sorted(set(duplicate_trades))},
        "t_plus_one_status": {"passed": not t1_errors, "errors": t1_errors},
        "benchmark_status": {"passed": not benchmark_errors, "errors": benchmark_errors},
        "attribution_status": {"passed": not attribution_errors, "errors": attribution_errors},
        "evolution_throttling_status": {"passed": not evolution_errors, "errors": evolution_errors},
    }


def _audit_portfolio(day: str, portfolio: dict[str, Any], previous_portfolio: dict[str, Any] | None, errors: list[str]) -> None:
    cash = float(portfolio.get("cash", 0.0))
    market_value = float(portfolio.get("market_value", 0.0))
    total_asset = float(portfolio.get("total_asset", 0.0))
    if cash < -0.01:
        errors.append(f"{day}: cash is negative")
    if abs(total_asset - (cash + market_value)) > 0.01:
        errors.append(f"{day}: total_asset mismatch")
    if previous_portfolio and float(previous_portfolio.get("total_asset", 0.0)) <= 0:
        errors.append(f"{day}: previous portfolio invalid")
    for position in portfolio.get("positions", []):
        quantity = int(position.get("quantity", 0))
        available = int(position.get("available_quantity", 0))
        if quantity < 0:
            errors.append(f"{day}: negative quantity {position.get('symbol')}")
        if available > quantity:
            errors.append(f"{day}: available exceeds quantity {position.get('symbol')}")


def _audit_t_plus_one(day: str, portfolio: dict[str, Any], errors: list[str]) -> None:
    for position in portfolio.get("positions", []):
        market = str(position.get("market", "A_SHARE"))
        last_buy = position.get("last_buy_date")
        if market == "A_SHARE" and last_buy == day and int(position.get("available_quantity", 0)) > 0:
            errors.append(f"{day}: T+1 violation {position.get('symbol')}")


def _audit_evolution(day: str, evolution: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if not evolution:
        warnings.append(f"{day}: missing evolution summary")
        return
    max_new = int(load_config("evolution.yaml")["evolution"]["rule_memory"]["max_new_rules_per_day"])
    rules = evolution.get("rule_memory", {}).get("rules", [])
    today = [rule for rule in rules if rule.get("created_date") == day or rule.get("date") == day]
    if len(today) > max_new:
        errors.append(f"{day}: evolution proposals exceed throttle")


def _audit_shadow(replay_paths: ReplayPaths) -> list[str]:
    errors = []
    for path in (replay_paths.data_dir / "experiments").glob("shadow_signals-*.jsonl"):
        day = path.stem.removeprefix("shadow_signals-")
        for row in read_jsonl(path):
            if row.get("account_mutation") or any(key in row for key in ["cash", "positions", "portfolio"]):
                errors.append(f"{day}: shadow artifact contains main-account mutation fields")
    return errors


def _replay_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Historical Dry-Run Replay {payload['start_date']} to {payload['end_date']}",
        "",
        f"- historical_replay_passed: {payload['historical_replay_passed']}",
        f"- forward_30d_dry_run_passed: {payload['forward_30d_dry_run_passed']}",
        "- This is a historical replay and must not be represented as future 30-day forward dry-run validation.",
        f"- release_recommendation: {payload['release_recommendation']}",
        f"- trading_days_expected: {payload['trading_days_expected']}",
        f"- trading_days_replayed: {payload['trading_days_replayed']}",
        f"- missing_global_briefing_days: {payload['missing_global_briefing_days']}",
        f"- missing_price_days: {payload['missing_price_days']}",
        f"- successful_days: {payload['successful_days']}",
        f"- failed_days: {payload['failed_days']}",
        f"- total_signals: {payload['total_signals']}",
        f"- total_orders: {payload['total_orders']}",
        f"- total_trades: {payload['total_trades']}",
        f"- rejected_orders: {payload['rejected_orders']}",
        f"- most_common_rejection_reasons: {payload['most_common_rejection_reasons']}",
        f"- portfolio_continuity_status: {payload['portfolio_continuity_status']}",
        f"- duplicate_order_status: {payload['duplicate_order_status']}",
        f"- duplicate_trade_status: {payload['duplicate_trade_status']}",
        f"- T+1_status: {payload['T+1_status']}",
        f"- benchmark_status: {payload['benchmark_status']}",
        f"- attribution_status: {payload['attribution_status']}",
        f"- consistency_status: {payload['consistency_status']}",
        f"- evolution_throttling_status: {payload['evolution_throttling_status']}",
        f"- price_only_replay: {payload['price_only_replay']}",
        "",
        "## Warnings",
    ]
    lines.extend(f"- {item}" for item in payload["warnings"]) if payload["warnings"] else lines.append("- none")
    lines.extend(["", "## Critical Errors"])
    critical_errors = payload["consistency_status"]["critical_errors"]
    lines.extend(f"- {item}" for item in critical_errors) if critical_errors else lines.append("- none")
    return "\n".join(lines) + "\n"
