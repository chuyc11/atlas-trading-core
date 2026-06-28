"""Holding-level mark-to-market series."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PORTFOLIO_IDS, PORTFOLIO_KEYS, PerformanceConfig


FORBIDDEN_HOLDING_FIELDS = {
    "order_id",
    "broker_order_id",
    "trade_id",
    "fill_id",
    "buy_signal",
    "sell_signal",
    "execution_status",
}


def holding_records_from_tracking_snapshot(
    *,
    config: PerformanceConfig,
    tracking_snapshot: dict[str, Any],
    snapshot_date: str,
    source_ledgers: dict[str, str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in PORTFOLIO_KEYS:
        snapshot = tracking_snapshot.get(f"{key}_holdings_snapshot", {})
        portfolio_id = str(snapshot.get("portfolio_id") or PORTFOLIO_IDS[key])
        for holding in snapshot.get("holdings", []):
            mark_price = float(holding.get("mark_price") or 0.0)
            shares = float(holding.get("virtual_shares") or 0.0)
            position_value = float(holding.get("virtual_position_value") or shares * mark_price)
            entry_price = float(holding.get("entry_price") or mark_price or 0.0)
            records.append(
                {
                    "portfolio_key": key,
                    "portfolio_id": portfolio_id,
                    "symbol": holding.get("symbol"),
                    "name": holding.get("name"),
                    "as_of_date": snapshot_date,
                    "virtual_shares": shares,
                    "mark_price": mark_price,
                    "position_value": position_value,
                    "target_weight": float(holding.get("target_weight") or 0.0),
                    "actual_weight": float(holding.get("actual_weight") or 0.0),
                    "unrealized_pnl": float(holding.get("unrealized_pnl") or position_value - shares * entry_price),
                    "unrealized_return": float(holding.get("unrealized_return") or (mark_price / entry_price - 1.0 if entry_price else 0.0)),
                    "source_tracking_ledger": source_ledgers[key],
                    "not_real_trade": True,
                    **PERFORMANCE_FLAGS,
                }
            )
    return records


def build_holding_mark_to_market_series(config: PerformanceConfig, records: list[dict[str, Any]]) -> dict[str, Any]:
    forbidden_hits = _forbidden_field_hits(records)
    counts: dict[str, int] = {}
    for row in records:
        counts[str(row["portfolio_id"])] = counts.get(str(row["portfolio_id"]), 0) + 1
    return {
        "series_id": "A-SHARE-HOLDING-MARK-TO-MARKET-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "records": sorted(records, key=lambda item: (item["portfolio_id"], item["symbol"], item["as_of_date"])),
        "holding_record_counts": counts,
        "forbidden_fields_present": forbidden_hits,
        "not_real_trade": True,
        **PERFORMANCE_FLAGS,
    }


def _forbidden_field_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for row in records:
        for key in FORBIDDEN_HOLDING_FIELDS:
            if key in row:
                hits.append(f"{row.get('portfolio_id')}:{row.get('symbol')}:{key}")
    return sorted(set(hits))
