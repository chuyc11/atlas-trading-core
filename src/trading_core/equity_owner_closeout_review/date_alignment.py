"""Date alignment checks for v0.8.21 closeout review."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_date_alignment(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    payloads: dict[str, dict[str, Any]],
    allow_date_mismatch: bool = False,
) -> dict[str, Any]:
    mismatches = []
    for key, payload in payloads.items():
        if not payload:
            continue
        found = payload.get("resolved_as_of_date", payload.get("as_of_date"))
        if found and found != as_of_date:
            mismatches.append({"artifact_key": key, "expected_as_of_date": as_of_date, "actual_as_of_date": found})
    blocking = [] if allow_date_mismatch or not mismatches else ["source_date_mismatch"]
    return {
        "alignment_id": "A-SHARE-OWNER-CLOSEOUT-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["date_mismatch_allowed"] if allow_date_mismatch and mismatches else [],
        "mismatches": mismatches,
        "checked_artifact_count": len(payloads),
    }
