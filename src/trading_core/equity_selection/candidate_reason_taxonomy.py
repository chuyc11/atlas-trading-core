"""Candidate reason taxonomy for v0.7.5."""

from __future__ import annotations


REASON_TAXONOMY = [
    "high_long_percentile",
    "high_mid_percentile",
    "high_short_percentile",
    "strong_composite_percentile",
    "strong_industry_score",
    "strong_liquidity_score",
    "acceptable_risk_score",
    "strong_fundamental_score",
    "strong_trend_component",
    "strong_momentum_component",
    "strong_risk_adjusted_return",
    "multi_horizon_overlap",
    "risk_downgraded",
    "low_risk_score",
    "low_liquidity_score",
    "low_confidence",
    "fundamental_coverage_low",
    "overheat_risk",
    "no_major_risk_flag_detected",
]

RISK_REASONS = {
    "low_risk_score",
    "low_liquidity_score",
    "low_confidence",
    "fundamental_coverage_low",
    "overheat_risk",
    "no_major_risk_flag_detected",
}


def validate_reasons(reasons: list[str]) -> list[str]:
    allowed = set(REASON_TAXONOMY)
    return sorted({reason for reason in reasons if reason not in allowed})
