from trading_core.equity_owner_evidence_backed_reevaluation_prep.score_impact_readiness import build_score_impact_readiness_summary


def test_score_impact_readiness_is_not_official_score():
    summary = build_score_impact_readiness_summary(
        availability={"source_readiness_score": 54, "minimum_owner_readiness_score": 75, "score_gap": 21},
        source_score_estimate={"evidence_supported_score_delta_estimate": 0},
        sufficiency={"ready_for_controlled_gate_reevaluation": False},
    )
    assert summary["score_impact_readiness_is_not_official_score"] is True
    assert summary["actual_audited_score_changed"] is False
    assert summary["new_gate_score_generated"] is False

