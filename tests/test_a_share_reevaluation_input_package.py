from trading_core.equity_owner_evidence_backed_reevaluation_prep.reevaluation_input_package import build_reevaluation_input_package


def test_reevaluation_input_package_generated_but_not_executed():
    package = build_reevaluation_input_package(
        availability={"source_gate_decision": "blocked", "source_readiness_score": 54, "minimum_owner_readiness_score": 75},
        sufficiency={"ready_for_controlled_gate_reevaluation": False, "eligibility_decision": "not_eligible"},
        mapping={"mapping_id": "M"},
        source_artifacts={"recovery_evidence_summary": "x"},
    )
    assert package["reevaluation_input_package_generated"] is True
    assert package["reevaluation_executed"] is False
    assert package["new_gate_score_generated"] is False

