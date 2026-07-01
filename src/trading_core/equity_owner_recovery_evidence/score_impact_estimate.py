"""Evidence-backed score impact estimate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_backed_score_impact_estimate(*, as_of_date: str = DEFAULT_AS_OF_DATE, ledger: dict[str, Any]) -> dict[str, Any]:
    source = ledger.get("source_readiness_score", 0)
    delta = ledger.get("evidence_supported_score_delta_estimate", 0)
    return {
        "estimate_id": "A-SHARE-EVIDENCE-BACKED-SCORE-IMPACT-ESTIMATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_readiness_score": source,
        "minimum_owner_readiness_score": ledger.get("minimum_owner_readiness_score", 0),
        "score_gap": ledger.get("score_gap", 0),
        "evidence_supported_score_delta_estimate": delta,
        "speculative_score_delta_estimate": ledger.get("speculative_score_delta_estimate", 0),
        "projected_score_if_evidence_accepted": source + delta,
        "projection_confidence": "low" if delta == 0 else "medium",
        "actual_audited_score_changed": False,
        "new_audited_score": None,
        "not_a_gate_score": True,
        "not_trade_instruction": True,
    }

