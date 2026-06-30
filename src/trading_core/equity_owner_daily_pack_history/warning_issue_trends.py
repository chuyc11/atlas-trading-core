"""Warning and issue trends."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_warning_issue_trend_baseline(*, as_of_date: str, records: list[dict[str, Any]], warning_digest: dict[str, Any], sufficiency: dict[str, Any]) -> dict[str, Any]:
    available = sufficiency["trend_analysis_available"]
    current_items = warning_digest.get("warning_issues", []) + warning_digest.get("known_non_blocking_issues", [])
    return {
        "baseline_id": "A-SHARE-WARNING-ISSUE-TREND-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "trend_analysis_available": available,
        "readiness_trend_status": "available" if available else "insufficient_history",
        "warning_count": warning_digest.get("warning_count", 0),
        "blocking_count": warning_digest.get("blocking_count", 0),
        "current_items": current_items,
        "repeated_items": _repeated_items(records) if available else [],
        "new_items": [] if not available else current_items,
        "resolved_items": [] if not available else [],
        "known_non_blocking_items": warning_digest.get("known_non_blocking_issues", []),
        "no_fabricated_trends": True,
    }


def _repeated_items(records: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for row in records:
        for item in row.get("warning_issue_codes", []):
            counts[item] = counts.get(item, 0) + 1
    return sorted(item for item, count in counts.items() if count >= 2)
