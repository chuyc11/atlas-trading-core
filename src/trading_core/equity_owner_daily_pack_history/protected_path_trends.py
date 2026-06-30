"""Protected path trends."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_protected_path_trend_baseline(*, as_of_date: str, records: list[dict[str, Any]], protected_digest: dict[str, Any]) -> dict[str, Any]:
    modified = protected_digest.get("protected_path_modifications_detected") is True
    return {
        "baseline_id": "A-SHARE-PROTECTED-PATH-TREND-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "protected_path_modifications_detected": modified,
        "modified_observation_count": sum(1 for row in records if row.get("protected_path_modifications_detected") is True),
        "protected_path_trend_clean": not modified and all(row.get("protected_path_modifications_detected") is not True for row in records),
    }
