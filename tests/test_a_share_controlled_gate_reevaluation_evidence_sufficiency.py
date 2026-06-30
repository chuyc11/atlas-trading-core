from trading_core.equity_owner_controlled_gate_reevaluation.evidence_sufficiency import build_evidence_sufficiency_check


def test_controlled_gate_reevaluation_evidence_sufficiency_false_without_evidence():
    check = build_evidence_sufficiency_check(evidence_registry={"evidence_available_count": 0}, status_tracker={"completed_count": 0, "verified_by_audit_only_count": 0})
    assert check["evidence_sufficient_for_gate_reevaluation"] is False
    assert check["overall_passed"] is True

