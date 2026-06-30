"""Exception workflow audit trail."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_exception_audit_trail(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    source_artifacts: dict[str, Path],
    exception_registry: dict[str, Any],
    waiver_record: dict[str, Any],
    escalation: dict[str, Any],
    owner_notice: dict[str, Any],
    developer_tracker: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "audit_trail_id": "A-SHARE-EXCEPTION-AUDIT-TRAIL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "input_artifacts_read": sorted(source_artifacts),
        "exception_records_generated": exception_registry.get("exception_count", 0),
        "waiver_status": waiver_record.get("manual_waiver_decision_status"),
        "escalation_routes": [step["route"] for step in escalation.get("steps", [])],
        "owner_notice_generated": owner_notice.get("notice_id") == "A-SHARE-BLOCKED-DAILY-PACK-OWNER-NOTICE",
        "developer_tracker_generated": developer_tracker.get("tracker_id") == "A-SHARE-DEVELOPER-FOLLOW-UP-TRACKER",
        "boundary_checks": boundary,
        "manual_decisions": waiver_record,
        "audit_results": [],
        "external_notifications_sent": False,
    }
