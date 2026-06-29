"""Warning and blocker aggregation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION


def build_warning_and_blocker_card(
    *,
    as_of_date: str,
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    items = []
    for stage, payload in sources.items():
        source_path = str(payload.get("_path") or "")
        for reason in payload.get("blocking_reasons", []) or []:
            items.append(_item(stage, source_path, "blocking", str(reason), True))
        for warning in payload.get("warnings", []) or []:
            severity = "known_non_blocking" if str(warning) in {
                "daily_basic:required_field_all_null",
                "trading_calendar:exchange_level_calendar_collapsed_to_trade_date",
            } else "warning"
            items.append(_item(stage, source_path, severity, str(warning), False))
    blocking_count = sum(1 for item in items if item["blocking"])
    return {
        "card_id": "WARNING_AND_BLOCKER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "items": items,
        "blocking_count": blocking_count,
        "warning_count": len([item for item in items if not item["blocking"]]),
        "critical_warning_count": 0,
        "overall_passed": blocking_count == 0,
        "blocking_reasons": [item["code"] for item in items if item["blocking"]],
    }


def _item(stage: str, source_path: str, severity: str, message: str, blocking: bool) -> dict[str, Any]:
    return {
        "source_stage": stage,
        "source_artifact": source_path,
        "severity": severity,
        "code": message.split(":", 1)[0],
        "message": message,
        "owner_action": "review" if blocking else "monitor",
        "blocking": blocking,
        "known_non_blocking": severity == "known_non_blocking",
    }

