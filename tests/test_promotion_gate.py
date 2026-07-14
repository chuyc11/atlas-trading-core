from trading_core.evolution.promotion_gate import recommend_promotion


def test_promotion_gate_never_auto_applies_active_normal() -> None:
    result = recommend_promotion(
        "active_small",
        {"days": 60, "signals": 20, "excess_return": 0.1, "mistake_rate": 0.1, "max_drawdown": 0},
    )
    assert result["recommendation"] == "suggest_active_normal_manual_review"
    assert result["recommended_state"] == "active_small"
    assert result["auto_applied"] is False


def test_shadow_requires_drawdown_within_positive_magnitude_limit() -> None:
    result = recommend_promotion(
        "shadow",
        {"days": 60, "signals": 20, "excess_return": 0.1, "mistake_rate": 0.1, "max_drawdown": 0.10},
    )
    assert result["recommendation"] == "keep_current_state"
    assert result["recommended_state"] == "shadow"
