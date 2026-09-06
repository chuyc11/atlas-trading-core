"""Runtime health files for real-data dry runs."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, UTC
from typing import Any
from uuid import uuid4

from trading_core.calendar.trading_calendar import is_trading_day, parse_date
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_json


def build_runtime_health(result: dict[str, Any], paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or result.get("paths") or project_paths()
    date = str(result["date"])
    account_id = str(result["portfolio"].get("account_id"))
    macro_path = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    price_path = paths.global_briefing_data_dir / f"china-market-snapshot-{date}.json"
    input_files_found = []
    input_files_missing = []
    for path in [macro_path, price_path]:
        if path.exists():
            input_files_found.append(str(path))
        else:
            input_files_missing.append(str(path))

    orders = result.get("orders", [])
    rejected_orders = [order for order in orders if order.get("status") == "rejected"]
    data_counts = result.get("data_quality", {}).get("counts", {})
    warnings = list(result.get("limitations", []))
    if input_files_missing:
        warnings.extend(f"missing_input: {path}" for path in input_files_missing)

    attribution = result.get("attribution", {})
    evolution = result.get("evolution", {})
    errors: list[str] = []
    attribution_status = "ok" if attribution else "missing"
    if attribution and abs(float(attribution.get("residual_pnl", 0.0))) > 0.01:
        attribution_status = "residual"
        errors.append("attribution residual exceeds tolerance")
    evolution_status = "ok" if evolution else "missing"

    report_path = paths.daily_report(date)
    health = {
        "date": date,
        "run_id": f"RUN-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}-{uuid4().hex[:8]}",
        "account_id": account_id,
        "input_files_found": input_files_found,
        "input_files_missing": input_files_missing,
        "macro_signals_count": len(result.get("macro_signals", [])),
        "trading_signals_count": len(result.get("signals", [])),
        "orders_count": len(orders),
        "trades_count": len(result.get("trades", [])),
        "rejected_orders_count": len(rejected_orders),
        "fallback_prices_count": int(data_counts.get("fallback", 0)),
        "stale_prices_count": int(data_counts.get("stale", 0)),
        "missing_prices_count": int(data_counts.get("missing", 0)),
        "portfolio_total_asset": result.get("portfolio", {}).get("total_asset"),
        "cash": result.get("portfolio", {}).get("cash"),
        "market_value": result.get("portfolio", {}).get("market_value"),
        "benchmark_count": len(result.get("benchmark", {}).get("benchmarks", {})),
        "attribution_status": attribution_status,
        "evolution_status": evolution_status,
        "report_path": str(report_path),
        "warnings": warnings,
        "errors": errors,
    }
    write_json(paths.dated_json("runtime", "health", date), health)
    return health


def load_health(date: str, paths: ProjectPaths | None = None) -> dict[str, Any] | None:
    paths = paths or project_paths()
    return read_json(paths.dated_json("runtime", "health", date), default=None)


def summarize_health(start_date: str, end_date: str, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    current = parse_date(start_date)
    end = parse_date(end_date)
    items: list[dict[str, Any]] = []
    while current <= end:
        if is_trading_day(current):
            health = load_health(current.isoformat(), paths)
            if health:
                items.append(health)
        current += timedelta(days=1)

    successful = [item for item in items if not item.get("errors")]
    rejected_reasons = Counter[str]()
    total_orders = total_trades = total_rejected = 0
    missing_inputs = fallback = stale = missing_prices = 0
    assets = []
    max_daily_asset_change = 0.0
    previous_asset: float | None = None
    evolution_proposals = 0
    queue_sizes = []

    for item in items:
        total_orders += int(item.get("orders_count", 0))
        total_trades += int(item.get("trades_count", 0))
        total_rejected += int(item.get("rejected_orders_count", 0))
        missing_inputs += len(item.get("input_files_missing", []))
        fallback += int(item.get("fallback_prices_count", 0))
        stale += int(item.get("stale_prices_count", 0))
        missing_prices += int(item.get("missing_prices_count", 0))
        asset = item.get("portfolio_total_asset")
        if asset is not None:
            asset = float(asset)
            assets.append(asset)
            if previous_asset not in (None, 0):
                max_daily_asset_change = max(max_daily_asset_change, abs((asset / previous_asset) - 1))
            previous_asset = asset
        for warning in item.get("warnings", []):
            if "rejected" in warning:
                rejected_reasons[warning] += 1

        date = item["date"]
        evolution_path = paths.data_dir / "evolution" / f"evolution-summary-{date}.json"
        evolution = read_json(evolution_path, default={})
        evolution_proposals += len(evolution.get("rule_memory", {}).get("rules", []))
        queue_path = paths.data_dir / "experiments" / "experiment_queue.jsonl"
        if queue_path.exists():
            queue_sizes.append(len([line for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]))

    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "total_run_days": len(items),
        "success_days": len(successful),
        "failed_days": len(items) - len(successful),
        "missing_input_count": missing_inputs,
        "fallback_prices_count": fallback,
        "stale_prices_count": stale,
        "missing_prices_count": missing_prices,
        "total_orders_count": total_orders,
        "total_trades_count": total_trades,
        "total_rejected_orders_count": total_rejected,
        "most_common_rejected_reason": rejected_reasons.most_common(1)[0][0] if rejected_reasons else None,
        "total_asset_change": round((assets[-1] / assets[0]) - 1, 8) if len(assets) >= 2 and assets[0] else 0.0,
        "max_daily_asset_change": round(max_daily_asset_change, 8),
        "evolution_proposal_count": evolution_proposals,
        "experiment_queue_growth_count": max(queue_sizes) - min(queue_sizes) if len(queue_sizes) >= 2 else 0,
    }
    write_json(paths.data_dir / "runtime" / f"health-summary-{start_date}-to-{end_date}.json", summary)
    return summary
