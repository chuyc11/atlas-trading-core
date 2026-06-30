from trading_core.equity_owner_readiness_gate.score_gate import build_owner_readiness_score_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_owner_readiness_score_gate_pass_fail():
    policy = build_owner_readiness_threshold_policy()
    assert build_owner_readiness_score_gate(score={"score": 80, "grade": "B", "owner_readiness_used_as_trade_instruction": False}, policy=policy)["passed"] is True
    failed = build_owner_readiness_score_gate(score={"score": 54, "grade": "D", "owner_readiness_used_as_trade_instruction": False}, policy=policy)
    assert failed["passed"] is False
    assert "owner_readiness_score_below_threshold" in failed["blocking_reasons"]
