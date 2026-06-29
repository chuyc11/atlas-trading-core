"""Date alignment for build-output dashboard."""

from __future__ import annotations

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION


def build_date_alignment(*, as_of_date: str, input_availability: dict, allow_date_mismatch: bool = False) -> dict:
    mismatches = []
    for entry in input_availability.get("entries", []):
        actual = entry.get("as_of_date")
        if actual and actual != as_of_date:
            mismatches.append({"artifact_id": entry.get("artifact_id"), "expected": as_of_date, "actual": actual})
    blocking = [] if allow_date_mismatch or not mismatches else ["date_mismatch"]
    return {
        "alignment_id": "A-SHARE-BUILD-OUTPUT-DASHBOARD-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "mismatches": mismatches,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": ["date_mismatch_allowed"] if allow_date_mismatch and mismatches else [],
    }

