from __future__ import annotations

import pandas as pd

from trading_core.equity_selection.candidate_explainer import inclusion_reasons, risk_reasons


def test_candidate_explainer_returns_inclusion_and_risk_notes() -> None:
    row = pd.Series(
        {
            "symbol": "600001.SH",
            "CompositePercentile": 95.0,
            "IndustryScore": 65.0,
            "LiquidityScore": 70.0,
            "RiskScore": 60.0,
            "FundamentalScore": 58.0,
            "LongConfidence": 0.9,
            "fundamental_confidence": 0.8,
        }
    )

    reasons = inclusion_reasons(row, "Long")
    risks = risk_reasons(row, "Long", {}, low_confidence_threshold=0.4)
    assert len(reasons) >= 2
    assert "high_long_percentile" in reasons
    assert risks == ["no_major_risk_flag_detected"]
