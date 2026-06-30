"""Owner readiness history."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_owner_readiness_history(*, as_of_date: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "as_of_date": row.get("as_of_date"),
            "history_record_id": row.get("history_record_id"),
            "owner_readiness_score": row.get("owner_readiness_score"),
            "owner_readiness_grade": row.get("owner_readiness_grade"),
            "overall_status": row.get("overall_status"),
            "boundary_clean": row.get("boundary_clean"),
        }
        for row in records
    ]
    return {
        "history_id": "A-SHARE-OWNER-READINESS-HISTORY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "records": rows,
        "observation_count": len(rows),
        "owner_readiness_used_as_trade_instruction": False,
    }
