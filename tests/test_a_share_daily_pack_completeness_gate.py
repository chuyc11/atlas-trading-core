from trading_core.equity_owner_readiness_gate.quality_gates import build_daily_pack_completeness_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_daily_pack_completeness_gate_pass_fail():
    policy = build_owner_readiness_threshold_policy()
    assert build_daily_pack_completeness_gate(completeness={"required_json_complete": True, "markdown_reports_complete": True}, policy=policy)["passed"] is True
    failed = build_daily_pack_completeness_gate(completeness={"required_json_complete": False, "markdown_reports_complete": True}, policy=policy)
    assert "required_json_artifacts_incomplete" in failed["blocking_reasons"]
