"""Boundary trends."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_boundary_trend_baseline(*, as_of_date: str, records: list[dict[str, Any]], boundary_check: dict[str, Any]) -> dict[str, Any]:
    clean = boundary_check.get("overall_passed") is True and not boundary_check.get("blocking_reasons")
    return {
        "baseline_id": "A-SHARE-BOUNDARY-TREND-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "boundary_clean": clean,
        "unclean_observation_count": sum(1 for row in records if row.get("boundary_clean") is False),
        "boundary_trend_clean": clean and all(row.get("boundary_clean") is not False for row in records),
    }
