from __future__ import annotations

import pandas as pd

from trading_core.equity_selection.candidate_config import CandidateGenerationConfig
from trading_core.equity_selection.risk_downgraded_candidates import build_risk_downgraded_candidates


def test_risk_downgraded_candidate_detection() -> None:
    frame = pd.DataFrame(
        [
            {
                "as_of_date": "2026-06-26",
                "symbol": "600001.SH",
                "name": "Alpha",
                "LongPercentile": 95.0,
                "LongScore": 70.0,
                "LongConfidence": 0.9,
                "MidPercentile": 10.0,
                "ShortPercentile": 10.0,
                "RiskScore": 20.0,
                "LiquidityScore": 80.0,
            }
        ]
    )
    rows = build_risk_downgraded_candidates(frame, CandidateGenerationConfig(), set(), "now")

    assert len(rows) == 1
    assert rows[0]["trigger_horizon"] == "Long"
    assert rows[0]["not_in_strict_candidates"] is True
    assert "low_risk_score" in rows[0]["downgrade_reason"]
