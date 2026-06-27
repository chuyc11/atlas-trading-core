"""IndustryScore construction."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_scoring.component_scores import component_values_from_fields, weighted_score_frame
from trading_core.equity_scoring.score_config import COMPONENT_FIELDS, COMMON_COLUMNS


def build_industry_scores(frame: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = frame[COMMON_COLUMNS].copy()
    values, confidences = component_values_from_fields(frame, COMPONENT_FIELDS["industry"], config)
    return weighted_score_frame(
        base,
        score_name="IndustryScore",
        percentile_name="industry_percentile",
        confidence_name="industry_confidence",
        component_values=values,
        component_confidences=confidences,
        component_weights=config["component_weights"]["industry"],
        created_at=created_at,
    )
