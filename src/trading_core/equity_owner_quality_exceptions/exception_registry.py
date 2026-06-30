"""Quality exception registry."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_exception_registry(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any]) -> dict[str, Any]:
    records = []
    for candidate in intake.get("quality_exception_candidates", []):
        records.append(
            {
                "exception_id": candidate["exception_id"],
                "source_gate": candidate["source_gate"],
                "description": candidate["description"],
                "raw_severity": candidate["severity"],
                "owner_visibility": candidate.get("owner_visibility", True),
                "developer_follow_up_required": candidate.get("developer_follow_up_required", False),
                "waiver_allowed": candidate.get("waiver_allowed", False),
                "auto_waiver_allowed": False,
                "trade_related": False,
                "broker_related": False,
                "order_related": False,
                "status": "open",
            }
        )
    return {
        "registry_id": "A-SHARE-QUALITY-EXCEPTION-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "exception_count": len(records),
        "records": records,
        "blocked_gate_decision_preserved": intake.get("blocked_state_preserved") is True,
    }
