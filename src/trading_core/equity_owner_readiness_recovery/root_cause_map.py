"""Quality exception root cause map."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_exception_root_cause_map(*, as_of_date: str = DEFAULT_AS_OF_DATE, classification: dict[str, Any], developer_tracker: dict[str, Any]) -> dict[str, Any]:
    developer_ids = {item.get("source_exception_id") for item in developer_tracker.get("items", [])}
    items: list[dict[str, Any]] = []
    for row in classification.get("classifications", []):
        category = row["category"]
        requires_more_history = category == "insufficient_history"
        requires_developer = row["exception_id"] in developer_ids or row.get("developer_follow_up_required") is True
        task_id = f"RECOVERY-TASK-{len(items)+1:03d}"
        items.append(
            {
                "exception_id": row["exception_id"],
                "target_version": TARGET_VERSION,
                "as_of_date": as_of_date,
                "category": category,
                "severity": row["severity"],
                "source_gate": row["source_gate"],
                "source_artifact": "quality_exception_classification.json",
                "root_cause_hypothesis": _hypothesis(category),
                "evidence": ["quality_exception_classification.json", "owner_readiness_gap_analysis.json"],
                "confidence": "high",
                "recoverable": not requires_more_history,
                "requires_developer_follow_up": requires_developer,
                "requires_owner_review": row.get("owner_follow_up_required") is True,
                "requires_more_history": requires_more_history,
                "waiver_candidate": row.get("waiver_candidate") is True,
                "non_waivable_reason": "score threshold failure cannot be waived" if category == "readiness_score_below_threshold" else "",
                "proposed_recovery_task_ids": [task_id],
            }
        )
    return {"map_id": "A-SHARE-QUALITY-EXCEPTION-ROOT-CAUSE-MAP", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "items": items, "mapped_count": len(items)}


def _hypothesis(category: str) -> str:
    return {
        "readiness_score_below_threshold": "warning load and manual safe-action burden keep readiness below threshold",
        "warning_issue_threshold_issue": "warnings require mapping or source clarification before score can improve",
        "insufficient_history": "trend evidence needs more real observations before readiness trend can be interpreted",
    }.get(category, "quality issue requires manual review")
