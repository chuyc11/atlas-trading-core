"""LongScore, MidScore, and ShortScore construction."""

from __future__ import annotations

import pandas as pd

from trading_core.equity_scoring.component_scores import component_values_from_fields, weighted_score_frame
from trading_core.equity_scoring.score_config import COMMON_COLUMNS, COMPONENT_FIELDS


def build_horizon_scores(features: dict[str, pd.DataFrame], base_scores: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    long, long_breakdown = _build_long_scores(features, base_scores, config, created_at)
    mid, mid_breakdown = _build_mid_scores(features, base_scores, config, created_at)
    short, short_breakdown = _build_short_scores(features, base_scores, config, created_at)
    result = long[COMMON_COLUMNS + ["LongScore", "LongRank", "LongPercentile", "LongConfidence"]].merge(
        mid[["symbol", "MidScore", "MidRank", "MidPercentile", "MidConfidence"]],
        on="symbol",
        how="left",
    )
    result = result.merge(short[["symbol", "ShortScore", "ShortRank", "ShortPercentile", "ShortConfidence"]], on="symbol", how="left")
    result["source"] = "strict_tradable_universe+v0.7.3_feature_scores"
    result["created_at"] = created_at
    return result, pd.concat([long_breakdown, mid_breakdown, short_breakdown], ignore_index=True)


def _build_long_scores(features: dict[str, pd.DataFrame], base_scores: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _score_feature_frame(base_scores, features["long_horizon"], features["fundamental"])
    component_values, component_confidences = component_values_from_fields(frame, COMPONENT_FIELDS["long"], config)
    _attach_existing_score_components(frame, component_values, component_confidences, ["FundamentalScore", "IndustryScore", "RiskScore", "LiquidityScore"])
    return weighted_score_frame(
        frame[COMMON_COLUMNS],
        score_name="LongScore",
        rank_name="LongRank",
        percentile_name="LongPercentile",
        confidence_name="LongConfidence",
        component_values=component_values,
        component_confidences=component_confidences,
        component_weights=config["component_weights"]["long"],
        created_at=created_at,
    )


def _build_mid_scores(features: dict[str, pd.DataFrame], base_scores: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _score_feature_frame(base_scores, features["mid_horizon"], features["fundamental"])
    component_values, component_confidences = component_values_from_fields(frame, COMPONENT_FIELDS["mid"], config)
    _attach_existing_score_components(frame, component_values, component_confidences, ["IndustryScore", "RiskScore", "LiquidityScore"])
    component_values["FundamentalScore"] = frame["FundamentalScore"]
    component_confidences["FundamentalScore"] = frame["fundamental_confidence"]
    return weighted_score_frame(
        frame[COMMON_COLUMNS],
        score_name="MidScore",
        rank_name="MidRank",
        percentile_name="MidPercentile",
        confidence_name="MidConfidence",
        component_values=component_values,
        component_confidences=component_confidences,
        component_weights=config["component_weights"]["mid"],
        created_at=created_at,
    )


def _build_short_scores(features: dict[str, pd.DataFrame], base_scores: pd.DataFrame, config: dict, created_at: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = _score_feature_frame(base_scores, features["short_horizon"], features["risk"])
    frame["overheat_return_20d"] = frame.get("return_20d")
    component_values, component_confidences = component_values_from_fields(frame, COMPONENT_FIELDS["short"], config)
    _attach_existing_score_components(frame, component_values, component_confidences, ["LiquidityScore", "RiskScore", "IndustryScore"])
    return weighted_score_frame(
        frame[COMMON_COLUMNS],
        score_name="ShortScore",
        rank_name="ShortRank",
        percentile_name="ShortPercentile",
        confidence_name="ShortConfidence",
        component_values=component_values,
        component_confidences=component_confidences,
        component_weights=config["component_weights"]["short"],
        created_at=created_at,
    )


def _score_feature_frame(base_scores: pd.DataFrame, *feature_frames: pd.DataFrame) -> pd.DataFrame:
    result = base_scores.copy()
    for frame in feature_frames:
        payload_columns = [column for column in frame.columns if column not in set(COMMON_COLUMNS + ["feature_group", "source", "created_at"]) and column != "symbol"]
        result = result.merge(frame[["symbol", *payload_columns]], on="symbol", how="left")
    return result


def _attach_existing_score_components(frame: pd.DataFrame, values: dict[str, pd.Series], confidences: dict[str, pd.Series], score_columns: list[str]) -> None:
    confidence_map = {
        "FundamentalScore": "fundamental_confidence",
        "IndustryScore": "industry_confidence",
        "RiskScore": "risk_confidence",
        "LiquidityScore": "liquidity_confidence",
    }
    for column in score_columns:
        values[column] = frame[column]
        confidences[column] = frame[confidence_map[column]]
