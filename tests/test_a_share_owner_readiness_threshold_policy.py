from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_owner_readiness_threshold_policy_defaults():
    policy = build_owner_readiness_threshold_policy()
    assert policy["minimum_owner_readiness_score"] == 75
    assert policy["allow_forbidden_wording"] is False
    assert policy["owner_readiness_used_as_trade_instruction_required"] is False
