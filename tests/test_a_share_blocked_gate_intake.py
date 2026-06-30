from trading_core.equity_owner_quality_exceptions.blocked_gate_intake import build_blocked_gate_intake


def test_blocked_gate_intake_preserves_blocked_state_and_gap():
    decision = {"decision": "blocked", "owner_operationally_acceptable": False, "required_gates_passed": False, "minimum_owner_readiness_score": 75, "actual_owner_readiness_score": 54, "actual_owner_readiness_grade": "D", "blocking_reasons": ["owner_readiness_score_below_threshold"], "warnings": []}
    evaluation = {"failed_gates": ["owner_readiness_score_gate"]}
    candidates = {"candidates": []}
    intake = build_blocked_gate_intake(decision=decision, evaluation=evaluation, candidates=candidates)
    assert intake["blocked_state_preserved"] is True
    assert intake["readiness_score_gap"] == 21
