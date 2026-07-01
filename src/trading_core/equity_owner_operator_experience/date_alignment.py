"""Date alignment checks for owner/operator experience inputs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_date_alignment(*, as_of_date: str = DEFAULT_AS_OF_DATE, payloads: dict[str, dict[str, Any]], allow_date_mismatch: bool = False) -> dict[str, Any]:
    mismatches = []
    for key, payload in payloads.items():
        source_date = payload.get("as_of_date")
        if source_date and source_date != as_of_date:
            mismatches.append({"artifact_key": key, "as_of_date": source_date})
    blocking = [] if allow_date_mismatch or not mismatches else ["input_date_mismatch"]
    return {
        "alignment_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "mismatches": mismatches,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["date_mismatch_allowed"] if allow_date_mismatch and mismatches else [],
    }
