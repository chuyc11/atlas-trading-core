from trading_core.equity_owner_readiness_gate.quality_exception_candidates import build_quality_exception_candidates


def test_quality_exception_candidates_generated_without_auto_waiver():
    result = build_quality_exception_candidates(gates={"score": {"blocking_reasons": ["owner_readiness_score_below_threshold"], "warnings": []}})
    assert result["candidate_count"] == 1
    assert result["auto_waiver_allowed"] is False
    assert result["candidates"][0]["auto_waiver_allowed"] is False
