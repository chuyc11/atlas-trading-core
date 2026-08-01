"""Isolated global-briefing historical replay runner."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from typing import Any

from trading_core.global_briefing.isolated_replay_execution import (
    ReplayCostModel,
    process_isolated_replay_day,
    summarize_replay_price_coverage,
)
from trading_core.global_briefing.isolated_replay_state import ReplayState
from trading_core.global_briefing.replay_signal_adapter import ADAPTER_ID, adapt_bundle_row_to_replay_signals
from trading_core.global_briefing.signal_schema import compact_date, resolve_project_path
from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl
from trading_core.system.common import default_paths, protected_diff, write_json_markdown


def replay_global_briefing_history(
    bundle_path: str,
    prices_path: str,
    *,
    start_date: str,
    end_date: str,
    initial_cash: float = 1_000_000.0,
    execution_mode: str = "isolated",
    max_symbol_weight: float = 0.15,
    max_total_weight: float = 0.50,
    lot_size: int = 100,
    commission_rate: float = 0.0005,
    slippage_bps: float = 0.0,
    max_price_staleness_days: int = 3,
    isolated_output_root: str | None = None,
    report_output_root: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    bundle_file = resolve_project_path(bundle_path, paths)
    prices_file = resolve_project_path(prices_path, paths)
    if not bundle_file.exists():
        raise ValueError(f"bundle file missing: {bundle_file}")
    if not prices_file.exists():
        raise ValueError(f"prices file missing: {prices_file}")

    bundle = read_json(bundle_file, default={})
    if not isinstance(bundle, dict) or not isinstance(bundle.get("rows"), list):
        raise ValueError("bundle must be a JSON object with rows")
    selected_rows = [row for row in bundle["rows"] if start_date <= str(row.get("replay_date")) <= end_date]
    if not selected_rows:
        raise ValueError("bundle contains no replay rows for requested range")
    if execution_mode not in {"isolated", "no-trade"}:
        raise ValueError("execution-mode must be isolated or no-trade")
    replay_id = f"GB-HIST-REPLAY-{compact_date(start_date)}-{compact_date(end_date)}"
    data_root = resolve_project_path(isolated_output_root, paths) if isolated_output_root else paths.data_dir / "replays" / "global_briefing"
    output_root = resolve_project_path(report_output_root, paths) if report_output_root else paths.outputs_dir / "replays" / "global_briefing"

    missing_signal_days = [
        str(row.get("replay_date"))
        for row in selected_rows
        if not row.get("selected_signal_generated_at")
    ]
    if execution_mode == "isolated":
        ledger = _run_isolated_replay_adapter(
            replay_id,
            selected_rows,
            start_date=start_date,
            end_date=end_date,
            initial_cash=initial_cash,
            max_symbol_weight=max_symbol_weight,
            max_total_weight=max_total_weight,
            lot_size=lot_size,
            commission_rate=commission_rate,
            slippage_bps=slippage_bps,
            max_price_staleness_days=max_price_staleness_days,
            prices_path=prices_path,
            paths=paths,
        )
        warnings = ledger["warnings"]
        price_coverage = summarize_replay_price_coverage(ledger["valuations"], ledger["trades"])
    else:
        ledger = _run_no_trade_replay(
            replay_id,
            selected_rows,
            start_date=start_date,
            end_date=end_date,
            initial_cash=initial_cash,
        )
        warnings = ledger["warnings"]
        price_coverage = summarize_replay_price_coverage(ledger["valuations"], ledger["trades"])

    isolated_paths = _write_isolated_replay_ledger(data_root, ledger)
    protected_changes = protected_diff(paths, before)
    payload: dict[str, Any] = {
        "replay_id": replay_id,
        "start_date": start_date,
        "end_date": end_date,
        "isolated": True,
        "input_bundle": str(bundle_file),
        "input_prices": str(prices_file),
        "warnings": warnings,
        "summary": {
            "replay_days": len(selected_rows),
            "days_processed": len(selected_rows),
            "signals": len(ledger["signals"]),
            "orders": len(ledger["orders"]),
            "trades": len(ledger["trades"]),
            "valuations": len(ledger["valuations"]),
            "ending_cash": ledger["account"]["cash"],
            "ending_equity": ledger["account"]["equity"],
            "errors": len(price_coverage["invalid_valuation_days"]),
        },
        "execution": {
            "mode": execution_mode,
            "no_trade_fallback": execution_mode == "no-trade",
            "adapter": ADAPTER_ID if execution_mode == "isolated" else "global_briefing_no_trade_replay_v1",
            "cost_model": {
                "commission_rate": commission_rate,
                "slippage_bps": slippage_bps,
            },
            "max_price_staleness_days": max_price_staleness_days,
        },
        "data_quality": {
            "missing_signal_days": missing_signal_days,
            **price_coverage,
        },
        "isolated_outputs": isolated_paths,
        "isolated_output_paths": isolated_paths,
        "day_results": ledger["day_results"],
        "protected_path_changes": protected_changes,
        "boundary": {
            "historical_replay_only": True,
            "forward_dry_run": False,
            "live_trading": False,
            "broker_connected": False,
            "main_ledger_written": bool(protected_changes),
            "isolated_replay_ledger_written": True,
            "run_daily_called": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
        },
    }
    json_path = data_root / f"global_briefing_replay-{start_date}-{end_date}.json"
    report_path = output_root / f"GLOBAL_BRIEFING_HISTORICAL_REPLAY-{start_date}-{end_date}.md"
    write_json_markdown(json_path, payload, report_path, build_replay_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _run_isolated_replay_adapter(
    replay_id: str,
    rows: list[dict[str, Any]],
    *,
    start_date: str,
    end_date: str,
    initial_cash: float,
    max_symbol_weight: float,
    max_total_weight: float,
    lot_size: int,
    commission_rate: float,
    slippage_bps: float,
    max_price_staleness_days: int,
    prices_path: str,
    paths: ProjectPaths,
) -> dict[str, Any]:
    state = ReplayState.initialize(replay_id, initial_cash)
    price_rows = _load_price_rows(
        prices_path,
        start_date,
        end_date,
        paths,
        lookback_days=max_price_staleness_days,
    )
    cost_model = ReplayCostModel(commission_rate=commission_rate, slippage_bps=slippage_bps)
    all_signals: list[dict[str, Any]] = []
    all_orders: list[dict[str, Any]] = []
    all_trades: list[dict[str, Any]] = []
    all_valuations: list[dict[str, Any]] = []
    day_results: list[dict[str, Any]] = []
    warnings: list[str] = []
    visible_prices: dict[str, dict[str, Any]] = {}
    price_dates = sorted(price_rows)
    next_price_date = 0

    for row in rows:
        replay_date = str(row.get("replay_date"))
        while next_price_date < len(price_dates) and price_dates[next_price_date] <= replay_date:
            visible_prices.update(price_rows[price_dates[next_price_date]])
            next_price_date += 1
        signals, signal_warnings = adapt_bundle_row_to_replay_signals(
            row,
            replay_id=replay_id,
            max_symbol_weight=max_symbol_weight,
            max_total_weight=max_total_weight,
        )
        warnings.extend(signal_warnings)
        orders, trades, valuation, day_result = process_isolated_replay_day(
            state,
            replay_date,
            signals,
            visible_prices,
            cost_model=cost_model,
            lot_size=lot_size,
            max_price_staleness_days=max_price_staleness_days,
        )
        all_signals.extend(signal.to_dict() for signal in signals)
        all_orders.extend(order.to_dict() for order in orders)
        all_trades.extend(trade.to_dict() for trade in trades)
        all_valuations.append(valuation.to_dict())
        day_results.append(day_result.to_dict())
        warnings.extend(day_result.warnings)

    account = {
        **state.account.to_dict(),
        "start_date": start_date,
        "end_date": end_date,
        "positions": [position.to_dict() for position in state.active_positions()],
    }
    return {
        "account": account,
        "signals": all_signals,
        "orders": all_orders,
        "trades": all_trades,
        "portfolio": [
            {
                "replay_id": replay_id,
                "date": row["date"],
                "cash": row["cash"],
                "market_value": row["market_value"],
                "total_asset": row["equity"],
                "positions": row["positions"],
                "isolated": True,
            }
            for row in all_valuations
        ],
        "valuations": all_valuations,
        "day_results": day_results,
        "warnings": warnings,
    }


def _run_no_trade_replay(
    replay_id: str,
    rows: list[dict[str, Any]],
    *,
    start_date: str,
    end_date: str,
    initial_cash: float,
) -> dict[str, Any]:
    valuations = [
        {
            "replay_id": replay_id,
            "date": str(row.get("replay_date")),
            "cash": initial_cash,
            "market_value": 0.0,
            "equity": initial_cash,
            "positions": [],
            "warnings": ["no-trade replay mode"],
            "isolated": True,
        }
        for row in rows
    ]
    return {
        "account": {
            "replay_id": replay_id,
            "start_date": start_date,
            "end_date": end_date,
            "cash": initial_cash,
            "equity": initial_cash,
            "currency": "CNY",
            "positions": [],
            "isolated": True,
        },
        "signals": [],
        "orders": [],
        "trades": [],
        "portfolio": [
            {
                "replay_id": item["replay_id"],
                "date": item["date"],
                "cash": item["cash"],
                "market_value": 0.0,
                "total_asset": item["equity"],
                "positions": [],
                "isolated": True,
            }
            for item in valuations
        ],
        "valuations": valuations,
        "day_results": [
            {
                "replay_id": replay_id,
                "date": str(row.get("replay_date")),
                "signals": 0,
                "orders": 0,
                "trades": 0,
                "cash": initial_cash,
                "equity": initial_cash,
                "warnings": ["no-trade replay mode"],
                "isolated": True,
            }
            for row in rows
        ],
        "warnings": ["execution-mode no-trade selected; no isolated orders generated"],
    }


def _write_isolated_replay_ledger(data_root, ledger: dict[str, Any]) -> dict[str, str]:
    replay_id = str(ledger["account"]["replay_id"])
    account_path = data_root / "accounts" / f"account-{replay_id}.json"
    signals_path = data_root / "signals" / f"signals-{replay_id}.jsonl"
    orders_path = data_root / "orders" / f"orders-{replay_id}.jsonl"
    trades_path = data_root / "trades" / f"trades-{replay_id}.jsonl"
    portfolio_path = data_root / "portfolio" / f"portfolio-{replay_id}.jsonl"
    valuations_path = data_root / "valuations" / f"valuations-{replay_id}.jsonl"

    write_json(account_path, ledger["account"])
    write_jsonl(signals_path, ledger["signals"])
    write_jsonl(orders_path, ledger["orders"])
    write_jsonl(trades_path, ledger["trades"])
    write_jsonl(portfolio_path, ledger["portfolio"])
    write_jsonl(valuations_path, ledger["valuations"])
    return {
        "account": str(account_path),
        "signals": str(signals_path),
        "orders": str(orders_path),
        "trades": str(trades_path),
        "portfolio": str(portfolio_path),
        "valuations": str(valuations_path),
    }


def _load_price_rows(
    prices_path: str,
    start_date: str,
    end_date: str,
    paths: ProjectPaths,
    *,
    lookback_days: int,
) -> dict[str, dict[str, dict[str, Any]]]:
    path = resolve_project_path(prices_path, paths)
    if not path.exists():
        raise ValueError(f"prices file missing: {path}")
    files = sorted(path.glob("*.csv")) if path.is_dir() else [path]
    rows: dict[str, dict[str, dict[str, Any]]] = {}
    earliest_source_date = (date.fromisoformat(start_date) - timedelta(days=lookback_days)).isoformat()
    for file_path in files:
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "date" not in reader.fieldnames or "symbol" not in reader.fieldnames:
                raise ValueError(f"prices file missing date or symbol column: {file_path}")
            for raw in reader:
                day = str(raw.get("date", "")).strip()
                symbol = str(raw.get("symbol", "")).strip()
                if earliest_source_date <= day <= end_date and symbol:
                    rows.setdefault(day, {})[symbol] = raw
    return rows


def build_replay_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Historical Replay",
            "",
            "## Scope",
            "This is isolated historical replay.",
            "It is not forward dry-run.",
            "It is not live trading validation.",
            "It does not prove strategy effectiveness.",
            "",
            "## Inputs",
            f"- bundle={payload['input_bundle']}",
            f"- prices={payload['input_prices']}",
            "",
            "## Replay Summary",
            f"- replay_days={payload['summary']['replay_days']}",
            f"- days_processed={payload['summary']['days_processed']}",
            f"- signals={payload['summary']['signals']}",
            f"- orders={payload['summary']['orders']}",
            f"- trades={payload['summary']['trades']}",
            f"- valuations={payload['summary']['valuations']}",
            f"- ending_cash={payload['summary']['ending_cash']}",
            f"- ending_equity={payload['summary']['ending_equity']}",
            f"- warnings={payload['warnings']}",
            "",
            "## Execution Mode",
            f"- {payload['execution']['mode']}",
            f"- no_trade_fallback={str(payload['execution']['no_trade_fallback']).lower()}",
            f"- adapter={payload['execution']['adapter']}",
            "",
            "## Data Quality",
            f"- missing_price_days={payload['data_quality']['missing_price_days']}",
            f"- price_coverage_ratio={payload['data_quality']['price_coverage_ratio']}",
            f"- required_price_observations={payload['data_quality']['required_price_observations']}",
            f"- resolved_price_observations={payload['data_quality']['resolved_price_observations']}",
            f"- missing_signal_days={payload['data_quality']['missing_signal_days']}",
            "",
            "## Isolated Replay Ledger",
            *[f"- {name} path: {path}" for name, path in payload["isolated_outputs"].items()],
            "",
            "## Boundary",
            "- isolated replay ledger only",
            "- main ledger not written",
            "- run-daily CLI not called",
            "- not forward dry-run",
            "- not live trading",
            "- not strategy effectiveness proof",
            "- no broker",
            "- no labels",
            "- no ML shadow",
            "- no promotion",
            "",
        ]
    )
