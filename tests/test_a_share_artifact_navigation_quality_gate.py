from trading_core.equity_owner_readiness_gate.quality_gates import build_artifact_navigation_quality_gate


def test_artifact_navigation_gate_requires_sources_and_outputs():
    gate = build_artifact_navigation_quality_gate(manifest={"output_artifacts": {"x": "y"}}, source_trace={"source_artifacts": [{"path": "x"}]})
    assert gate["passed"] is True
    failed = build_artifact_navigation_quality_gate(manifest={"output_artifacts": {}}, source_trace={"source_artifacts": []})
    assert failed["passed"] is False
