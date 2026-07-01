"""Score impact readiness summary, explicitly not an official gate score."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_score_impact_readiness_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], source_score_estimate: dict[str, Any], sufficiency: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-SCORE-IMPACT-READINESS-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_readiness_score": availability.get("source_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "evidence_supported_score_delta_estimate": source_score_estimate.get("evidence_supported_score_delta_estimate", 0),
        "projected_score_if_evidence_accepted": source_score_estimate.get("projected_score_if_evidence_accepted"),
        "score_impact_readiness_is_not_official_score": True,
        "actual_audited_score_changed": False,
        "new_audited_score": None,
        "ready_for_controlled_gate_reevaluation": sufficiency.get("ready_for_controlled_gate_reevaluation"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
    }

