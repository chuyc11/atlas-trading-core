"""Daily pack completeness trend."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import FILES, REPORTS, TARGET_VERSION


def build_completeness_trend(*, as_of_date: str, artifacts: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    json_missing = [key for key in FILES if key not in artifacts]
    report_missing = [key for key in REPORTS if key not in artifacts]
    return {
        "trend_id": "A-SHARE-DAILY-PACK-COMPLETENESS-TREND",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "observation_count": len(records),
        "required_json_complete": not json_missing,
        "markdown_reports_complete": not report_missing,
        "missing_json_artifacts": json_missing,
        "missing_markdown_reports": report_missing,
    }
