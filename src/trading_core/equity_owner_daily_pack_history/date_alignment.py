"""Date alignment for daily pack history inputs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_date_alignment(*, as_of_date: str, input_availability: dict[str, Any], allow_date_mismatch: bool = False) -> dict[str, Any]:
    mismatches = []
    for entry in input_availability.get("entries", []):
        actual = entry.get("as_of_date")
        if actual and actual != as_of_date:
            mismatches.append({"artifact_id": entry.get("artifact_id"), "expected": as_of_date, "actual": actual})
    blocking = [] if allow_date_mismatch or not mismatches else ["date_mismatch"]
    return {
        "alignment_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "mismatches": mismatches,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["date_mismatch_allowed"] if allow_date_mismatch and mismatches else [],
    }
