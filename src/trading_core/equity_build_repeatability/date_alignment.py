"""Date alignment for v0.8.8 repeatability inputs."""

from __future__ import annotations

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION


def build_repeatability_date_alignment(
    *,
    as_of_date: str,
    input_availability: dict,
    allow_date_mismatch: bool = False,
) -> dict:
    mismatches = []
    for entry in input_availability.get("entries", []):
        entry_date = entry.get("as_of_date")
        if entry_date and entry_date != as_of_date:
            mismatches.append({
                "artifact_id": entry.get("artifact_id"),
                "expected": as_of_date,
                "actual": entry_date,
            })
    blocking = [] if allow_date_mismatch or not mismatches else ["date_mismatch"]
    return {
        "alignment_id": "A-SHARE-BUILD-REPEATABILITY-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "mismatches": mismatches,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["date_mismatch_allowed"] if allow_date_mismatch and mismatches else [],
    }

