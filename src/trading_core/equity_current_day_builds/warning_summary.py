"""Warning summary for v0.8.7 gated build."""

from __future__ import annotations

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
)


def build_gated_build_warning_summary(
    *,
    as_of_date: str,
    input_availability: dict,
    date_alignment: dict,
    preflight_gate: dict,
    execution_record: dict,
    comparison: dict,
    drift_summary: dict,
) -> dict:
    all_warnings = []
    all_warnings.extend(input_availability.get("warnings", []))
    all_warnings.extend(date_alignment.get("warnings", []))
    all_warnings.extend(preflight_gate.get("warnings", []))
    all_warnings.extend(execution_record.get("warnings", []))
    all_warnings.extend(comparison.get("warnings", []))
    all_warnings.extend(drift_summary.get("warnings", []))

    return {
        "summary_id": "A-SHARE-GATED-BUILD-WARNING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "total_warnings": len(all_warnings),
        "warnings": sorted(set(all_warnings)),
        "sources": {
            "input_availability": len(input_availability.get("warnings", [])),
            "date_alignment": len(date_alignment.get("warnings", [])),
            "preflight_gate": len(preflight_gate.get("warnings", [])),
            "execution_record": len(execution_record.get("warnings", [])),
            "comparison": len(comparison.get("warnings", [])),
            "drift_summary": len(drift_summary.get("warnings", [])),
        },
    }
