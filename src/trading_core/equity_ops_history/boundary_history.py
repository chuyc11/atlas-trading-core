"""Boundary history snapshot."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import BASELINE_OPS_VERSION, TARGET_VERSION


BOUNDARY_FIELDS = [
    "run_daily_called",
    "old_run_daily_called",
    "day2_executed",
    "broker_connected",
    "real_orders_placed",
    "buy_sell_signals_generated",
    "order_preview_generated",
    "model_profit_guaranteed",
    "live_trading_ready",
    "real_account_data_read",
]


def build_ops_boundary_history_snapshot(*, as_of_date: str, ops_boundary: dict[str, Any]) -> dict[str, Any]:
    row = {
        "as_of_date": as_of_date,
        "source_version": BASELINE_OPS_VERSION,
        "boundary_clean": ops_boundary.get("overall_passed") is True,
        **{field: ops_boundary.get(field, False) for field in BOUNDARY_FIELDS},
    }
    return {"snapshot_id": "A-SHARE-OPS-BOUNDARY-HISTORY-SNAPSHOT", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "records": [row]}
