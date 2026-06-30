from trading_core.equity_owner_controlled_gate_reevaluation.preservation_checks import build_source_gate_preservation_check, build_threshold_preservation_check, build_waiver_preservation_check


def test_controlled_gate_reevaluation_preservation_checks():
    source = {"source_gate_decision": "blocked", "blocked_gate_decision_preserved": True, "minimum_owner_readiness_score": 75, "actual_owner_readiness_score": 54}
    gate = {"decision": "blocked"}
    assert build_source_gate_preservation_check(source_summary=source, gate_decision=gate)["overall_passed"] is True
    assert build_threshold_preservation_check(source_summary=source)["threshold_lowered"] is False
    assert build_waiver_preservation_check()["auto_waiver_allowed"] is False

