from trading_core.equity_owner_readiness_gate.quality_gates import build_markdown_report_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_markdown_report_quality_gate():
    gate = build_markdown_report_quality_gate(completeness={"markdown_reports_complete": False}, policy=build_owner_readiness_threshold_policy())
    assert gate["passed"] is False
    assert "markdown_report_incomplete" in gate["blocking_reasons"]
