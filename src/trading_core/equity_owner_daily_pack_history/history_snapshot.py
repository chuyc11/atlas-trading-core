"""Daily pack history snapshot."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_history_snapshot(*, as_of_date: str, history_index: dict[str, Any], minimum_required_observations: int) -> dict[str, Any]:
    records = list(history_index.get("records", []))
    return {
        "snapshot_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "daily_pack_history_observation_count": len(records),
        "minimum_required_observations": minimum_required_observations,
        "first_observation_date": records[0].get("as_of_date") if records else None,
        "latest_observation_date": records[-1].get("as_of_date") if records else None,
        "records": records,
        "trend_analysis_available": len(records) >= minimum_required_observations,
        "synthetic_history_used": False,
        "future_dates_used": False,
    }
