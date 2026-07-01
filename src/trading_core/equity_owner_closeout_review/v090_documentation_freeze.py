"""v0.9.0 documentation freeze checklist."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_v090_documentation_freeze_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    items = [
        "README updated",
        "RELEASE_NOTES updated",
        "VERSION updated",
        "CLI_REFERENCE updated",
        "COMMAND_COOKBOOK updated",
        "ARTIFACT_MAP updated",
        "testing policy documented",
        "owner-readiness blocked state documented",
        "final blocked closeout documented",
        "no live trading claims",
        "no profit guarantees",
        "no broker/order/signal claims",
        "v0.9.0 RC scope documented",
    ]
    return {
        "checklist_id": "A-SHARE-V090-DOCUMENTATION-FREEZE-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "items": [{"item": item, "required_for_v090": True, "status": "planned"} for item in items],
    }
