from tests.a_share_historical_backfill_test_utils import build_v097, recomputed_json, seed_v096_with_historical_inputs


def test_recomputed_evidence_result_preserves_blocked_state_and_non_signal_boundaries(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    build_v097(paths, monkeypatch)
    result = recomputed_json(paths, "recomputed_evidence_result")
    register = recomputed_json(paths, "recomputed_evidence_eligible_day_register")

    assert result["eligible_day_count"] == 2
    assert result["evidence_quality_overall_status"] == "partial"
    assert result["blocker_coverage_ratio"] == 0.5
    assert result["ready_for_future_controlled_reevaluation_prep"] is False
    assert result["known_owner_readiness_state"] == "blocked"
    assert result["source_readiness_score"] == 54
    assert result["minimum_owner_readiness_score"] == 75
    assert result["score_gap"] == 21
    assert all(day["candidate_outputs_not_buy_sell_signals"] for day in register["eligible_days"])
    assert all(day["score_outputs_not_trade_signals"] for day in register["eligible_days"])
    assert all(day["virtual_portfolio_outputs_virtual_only"] for day in register["eligible_days"])
