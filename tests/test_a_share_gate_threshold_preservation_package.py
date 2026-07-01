from trading_core.equity_owner_evidence_backed_reevaluation_prep.preservation_packages import build_gate_threshold_preservation_package


def test_gate_threshold_preservation_package_preserves_threshold():
    package = build_gate_threshold_preservation_package(availability={"minimum_owner_readiness_score": 75})
    assert package["threshold_preserved"] is True
    assert package["threshold_lowered"] is False
    assert package["minimum_owner_readiness_score"] == 75

