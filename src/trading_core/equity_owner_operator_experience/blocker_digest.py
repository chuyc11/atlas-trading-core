"""Unresolved blocker digest."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_unresolved_blocker_digest(*, as_of_date: str = DEFAULT_AS_OF_DATE, register: dict[str, Any]) -> dict[str, Any]:
    blockers = [
        {
            "blocker_id": row.get("blocker_id"),
            "category": row.get("category"),
            "short_summary": row.get("description"),
            "owner_visible": row.get("owner_visible", True),
            "blocks_owner_readiness_acceptance": row.get("blocks_owner_readiness_acceptance"),
            "blocks_current_rc": row.get("blocks_v090_rc"),
            "recommended_future_resolution": row.get("recommended_resolution"),
        }
        for row in register.get("blockers", [])
    ]
    return {
        "digest_id": "A-SHARE-UNRESOLVED-BLOCKER-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "unresolved_blocker_count": register.get("unresolved_blocker_count", len(blockers)),
        "blockers_that_block_owner_readiness_acceptance": register.get("blockers_that_block_owner_readiness_acceptance"),
        "blockers_that_block_v090_rc": register.get("blockers_that_block_v090_rc"),
        "blockers": blockers,
        "overall_passed": register.get("blockers_that_block_v090_rc") == 0,
        "blocking_reasons": [] if register.get("blockers_that_block_v090_rc") == 0 else ["blockers_that_block_current_rc"],
        "warnings": [],
    }
