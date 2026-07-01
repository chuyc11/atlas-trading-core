"""Date alignment for owner recovery evidence."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_date_alignment(*, as_of_date: str = DEFAULT_AS_OF_DATE, payloads: dict[str, dict[str, Any]], allow_date_mismatch: bool = False) -> dict[str, Any]:
    mismatches = {
        key: payload.get("as_of_date")
        for key, payload in payloads.items()
        if payload and payload.get("as_of_date") and payload.get("as_of_date") != as_of_date
    }
    blocking = ["source_date_mismatch"] if mismatches and not allow_date_mismatch else []
    return {
        "alignment_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "resolved_as_of_date": as_of_date,
        "mismatches": mismatches,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["source_date_mismatch_allowed"] if mismatches and allow_date_mismatch else [],
    }

