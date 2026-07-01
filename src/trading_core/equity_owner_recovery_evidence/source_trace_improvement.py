"""Source trace improvement evidence."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_source_trace_improvement_evidence(*, as_of_date: str = DEFAULT_AS_OF_DATE, traces: dict[str, dict]) -> dict[str, Any]:
    required = list(traces)
    present = [key for key, payload in traces.items() if payload.get("source_trace_complete") is True]
    missing = [key for key in required if key not in present]
    ratio = len(present) / len(required) if required else 1.0
    return _evidence("A-SHARE-SOURCE-TRACE-IMPROVEMENT-EVIDENCE", as_of_date, required, present, missing, ratio)


def _evidence(evidence_id: str, as_of_date: str, required: list[str], present: list[str], missing: list[str], ratio: float) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_items": required,
        "present_items": present,
        "missing_items": missing,
        "completeness_ratio": ratio,
        "quality_grade": "audit_verified" if ratio == 1 else "partial" if ratio else "none",
        "evidence_available": ratio == 1,
        "blocking_reasons": [] if ratio == 1 else ["source_trace_gap"],
        "warnings": [],
    }

