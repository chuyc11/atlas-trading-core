from trading_core.equity_owner_readiness_gate.release_recommendation import build_owner_release_recommendation


def test_owner_release_recommendation_excludes_trade_recommendations():
    result = build_owner_release_recommendation(decision={"decision": "blocked", "blocking_reasons": ["score"], "warnings": []})
    assert result["recommendation"] == "block_daily_pack"
    assert result["not_investment_recommendation"] is True
    assert result["not_trade_instruction"] is True
