from __future__ import annotations

from a_share_virtual_portfolio_test_utils import relaxed_portfolio_config
from trading_core.equity_portfolios.weighting import assign_target_weights, raw_weight_score


def _row(symbol: str, percentile: float, industry: str) -> dict:
    return {
        "symbol": symbol,
        "industry": industry,
        "LongPercentile": percentile,
        "LongRank": 1,
        "LongConfidence": 1.0,
        "RiskScore": 70.0,
        "LiquidityScore": 70.0,
        "IndustryScore": 70.0,
        "FundamentalScore": 70.0,
        "CompositeOpportunityScore": 70.0,
    }


def test_weighting_sums_to_one_and_respects_cap() -> None:
    rows = [_row("600001.SH", 95.0, "Finance"), _row("600002.SH", 90.0, "Industrial")]
    config = relaxed_portfolio_config(long_max_single_weight=0.60)

    weighted = assign_target_weights(rows, horizon="Long", config=config)

    assert round(sum(row["target_weight"] for row in weighted), 6) == 1.0
    assert max(row["target_weight"] for row in weighted) <= 0.60
    assert raw_weight_score(rows[0], "Long") > raw_weight_score(rows[1], "Long")

