from trading_core.equity_owner_readiness_gate.quality_gates import build_source_trace_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_source_trace_incomplete_blocks_gate():
    gate = build_source_trace_quality_gate(trace={"source_trace_complete": False, "missing_required_sources": ["x"]}, policy=build_owner_readiness_threshold_policy())
    assert gate["passed"] is False
    assert "source_trace_incomplete" in gate["blocking_reasons"]
