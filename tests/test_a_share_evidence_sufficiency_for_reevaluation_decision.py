from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_sufficiency import build_evidence_sufficiency_decision


def _availability(**updates):
    payload = {
        "source_gate_decision": "blocked",
        "source_gate_decision_preserved": True,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "evidence_ready_for_next_reevaluation_prep": True,
    }
    payload.update(updates)
    return payload


def test_evidence_sufficiency_blocks_none_or_remaining_blockers_and_allows_verified():
    blocked = build_evidence_sufficiency_decision(
        availability=_availability(),
        quality={"overall_evidence_quality": "none", "strong_evidence_count": 0, "audit_verified_evidence_count": 0, "missing_evidence_count": 3},
        blockers={"blocker_count": 1},
    )
    assert blocked["ready_for_controlled_gate_reevaluation"] is False
    assert "evidence_quality_too_low" in blocked["blocking_reasons"]
    ready = build_evidence_sufficiency_decision(
        availability=_availability(),
        quality={"overall_evidence_quality": "audit_verified", "strong_evidence_count": 0, "audit_verified_evidence_count": 2, "missing_evidence_count": 0},
        blockers={"blocker_count": 0},
    )
    assert ready["ready_for_controlled_gate_reevaluation"] is True
    assert ready["eligibility_decision"] == "eligible"

