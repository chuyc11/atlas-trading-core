"""Run-history snapshot construction."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_history_snapshot(*, as_of_date: str, history_index: dict[str, Any], minimum_required_observations: int) -> dict[str, Any]:
    records = sorted(history_index.get("records", []), key=lambda row: row.get("as_of_date", ""))
    count = len(records)
    return {
        "snapshot_id": "A-SHARE-OPS-HISTORY-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "run_history_observation_count": count,
        "minimum_required_observations": minimum_required_observations,
        "trend_analysis_available": count >= minimum_required_observations,
        "baseline_status": "available" if count >= minimum_required_observations else "insufficient_history",
        "records": records,
        "latest_record": records[-1] if records else None,
    }
