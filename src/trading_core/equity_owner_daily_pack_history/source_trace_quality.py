"""Source trace quality trend."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_source_trace_quality_trend(*, as_of_date: str, records: list[dict[str, Any]], source_trace: dict[str, Any]) -> dict[str, Any]:
    return {
        "trend_id": "A-SHARE-SOURCE-TRACE-QUALITY-TREND",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "required_source_count": len([row for row in source_trace.get("source_artifacts", []) if row.get("required") is True]),
        "missing_required_sources": [row.get("artifact_id") for row in source_trace.get("source_artifacts", []) if row.get("required") is True and not row.get("exists")],
    }
