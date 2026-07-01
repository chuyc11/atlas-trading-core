"""Readiness improvement evidence ledger."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_readiness_improvement_evidence_ledger(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_readiness_score: int, minimum_owner_readiness_score: int, task_evidence: dict[str, Any], quality_grading: dict[str, Any] | None = None) -> dict[str, Any]:
    quality_grading = quality_grading or {}
    supported_items = [item for item in task_evidence.get("items", []) if item.get("evidence_quality") in {"strong", "audit_verified"} and item.get("completion_claim_allowed")]
    delta = sum(0 for _ in supported_items)
    return {
        "ledger_id": "A-SHARE-READINESS-IMPROVEMENT-EVIDENCE-LEDGER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_readiness_score": source_readiness_score,
        "minimum_owner_readiness_score": minimum_owner_readiness_score,
        "score_gap": max(minimum_owner_readiness_score - source_readiness_score, 0),
        "evidence_records": task_evidence.get("items", []),
        "evidence_supported_improvement_items": supported_items,
        "evidence_supported_score_delta_estimate": delta,
        "speculative_score_delta_estimate": 0,
        "actual_audited_score_changed": False,
        "new_audited_score": None,
        "readiness_improvement_claim_allowed": bool(supported_items) and quality_grading.get("evidence_ready_for_next_reevaluation_prep") is True,
    }

