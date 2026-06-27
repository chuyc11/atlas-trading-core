from __future__ import annotations

from trading_core.equity_selection.candidate_reason_taxonomy import REASON_TAXONOMY, validate_reasons


def test_candidate_reason_taxonomy_contains_required_reasons() -> None:
    required = {
        "high_long_percentile",
        "high_mid_percentile",
        "high_short_percentile",
        "multi_horizon_overlap",
        "risk_downgraded",
        "low_risk_score",
        "low_liquidity_score",
        "low_confidence",
        "overheat_risk",
    }
    assert required.issubset(REASON_TAXONOMY)
    assert validate_reasons(["high_long_percentile"]) == []
    assert validate_reasons(["unknown_reason"]) == ["unknown_reason"]
