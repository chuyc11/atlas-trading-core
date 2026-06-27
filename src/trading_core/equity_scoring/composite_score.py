"""CompositeOpportunityScore construction."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_scoring.component_scores import weighted_score_frame
from trading_core.equity_scoring.score_config import COMMON_COLUMNS


def build_composite_scores(horizon_scores: pd.DataFrame, base_scores: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = horizon_scores.merge(
        base_scores[["symbol", "RiskScore", "risk_confidence", "LiquidityScore", "liquidity_confidence", "IndustryScore", "FundamentalScore"]],
        on="symbol",
        how="left",
    )
    values = {
        "LongScore": frame["LongScore"],
        "MidScore": frame["MidScore"],
        "ShortScore": frame["ShortScore"],
        "RiskScore": frame["RiskScore"],
        "LiquidityScore": frame["LiquidityScore"],
    }
    confidences = {
        "LongScore": frame["LongConfidence"],
        "MidScore": frame["MidConfidence"],
        "ShortScore": frame["ShortConfidence"],
        "RiskScore": frame["risk_confidence"],
        "LiquidityScore": frame["liquidity_confidence"],
    }
    result, breakdown = weighted_score_frame(
        frame[COMMON_COLUMNS],
        score_name="CompositeOpportunityScore",
        rank_name="CompositeRank",
        percentile_name="CompositePercentile",
        confidence_name="CompositeConfidence",
        component_values=values,
        component_confidences=confidences,
        component_weights=config["component_weights"]["composite"],
        created_at=created_at,
    )
    result = result.merge(
        frame[["symbol", "LongScore", "MidScore", "ShortScore", "RiskScore", "LiquidityScore", "IndustryScore", "FundamentalScore"]],
        on="symbol",
        how="left",
    )
    columns = [
        "as_of_date",
        "symbol",
        "CompositeOpportunityScore",
        "CompositeRank",
        "CompositePercentile",
        "CompositeConfidence",
        "LongScore",
        "MidScore",
        "ShortScore",
        "RiskScore",
        "LiquidityScore",
        "IndustryScore",
        "FundamentalScore",
        "source",
        "created_at",
    ]
    return result[columns], breakdown
