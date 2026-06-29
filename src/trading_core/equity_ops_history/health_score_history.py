"""Health score history artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_history.ops_history_config import TARGET_VERSION


def build_ops_health_score_history(*, as_of_date: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "as_of_date": row.get("as_of_date"),
            "score": row.get("ops_health_score"),
            "grade": row.get("ops_health_grade"),
            "overall_status": row.get("overall_status"),
            "blocking_issue_count": row.get("blocking_issue_count", 0),
            "warning_issue_count": row.get("warning_issue_count", 0),
            "known_non_blocking_issue_count": row.get("known_non_blocking_issue_count", 0),
            "source_ops_manifest": row.get("ops_manifest_path"),
            "source_ops_audit": row.get("ops_audit_path"),
        }
        for row in records
    ]
    return {"history_id": "A-SHARE-OPS-HEALTH-SCORE-HISTORY", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "records": rows}
