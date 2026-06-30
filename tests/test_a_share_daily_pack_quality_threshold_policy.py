from trading_core.equity_owner_readiness_gate.threshold_policy import build_daily_pack_quality_threshold_policy


def test_daily_pack_quality_threshold_policy_defaults():
    policy = build_daily_pack_quality_threshold_policy()
    assert policy["minimum_required_artifact_completeness"] == 1.0
    assert policy["required_source_trace_complete"] is True
    assert policy["allow_remediation_execution"] is False
