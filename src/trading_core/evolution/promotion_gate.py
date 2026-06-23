"""Promotion recommendations without automatic active-normal changes."""

from __future__ import annotations

from typing import Any


VALID_STATES = ("candidate", "shadow", "active_small", "active_normal", "paused", "retired")


def recommend_promotion(state: str, metrics: dict[str, Any]) -> dict[str, Any]:
    if state not in VALID_STATES:
        raise ValueError(f"Invalid strategy state: {state}")
    days = int(metrics.get("days", 0))
    signals = int(metrics.get("signals", 0))
    excess = float(metrics.get("excess_return", 0.0))
    mistake_rate = float(metrics.get("mistake_rate", 0.0))
    max_drawdown = float(metrics.get("max_drawdown", 0.0))

    recommendation = "keep_current_state"
    target_state = state
    if state == "candidate" and metrics.get("definition_complete", True):
        recommendation = "promote_to_shadow"
        target_state = "shadow"
    elif state == "shadow" and days >= 20 and signals >= 10 and excess > 0 and mistake_rate < 0.30 and max_drawdown > -0.03:
        recommendation = "promote_to_active_small"
        target_state = "active_small"
    elif state == "active_small" and days >= 60 and excess > 0 and mistake_rate < 0.30:
        recommendation = "suggest_active_normal_manual_review"
        target_state = "active_small"
    elif state in {"active_small", "active_normal"} and (excess < -0.003 or mistake_rate > 0.30 or max_drawdown < -0.03):
        recommendation = "pause"
        target_state = "paused"

    return {
        "current_state": state,
        "recommended_state": target_state,
        "recommendation": recommendation,
        "auto_applied": False,
    }
