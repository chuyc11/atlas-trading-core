from trading_core.equity_owner_evidence_backed_reevaluation_prep.readiness_checklist import build_evidence_backed_readiness_checklist


def test_evidence_backed_readiness_checklist_generated():
    checklist = build_evidence_backed_readiness_checklist(
        sufficiency={"evidence_sufficient_for_controlled_gate_reevaluation": False, "blocking_reasons": ["missing"]},
        package={"reevaluation_input_package_generated": True},
    )
    assert checklist["checklist_id"] == "A-SHARE-EVIDENCE-BACKED-READINESS-CHECKLIST"
    assert checklist["reevaluation_executed"] is False
    assert checklist["new_gate_decision_generated"] is False

