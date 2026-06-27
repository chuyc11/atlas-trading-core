"""Cross-sectional scoring normalization helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


VALID_DIRECTIONS = {"higher", "lower", "magnitude_lower", "moderate", "boolean_higher"}


def winsorize_series(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    finite = values[np.isfinite(values)]
    if finite.empty:
        return values
    lower_value = finite.quantile(lower)
    upper_value = finite.quantile(upper)
    return values.clip(lower=lower_value, upper=upper_value)


def percentile_score(
    series: pd.Series,
    *,
    direction: str = "higher",
    lower: float = 0.01,
    upper: float = 0.99,
    neutral_score: float = 50.0,
) -> pd.Series:
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"unsupported feature direction: {direction}")
    transformed = _transform(series, direction)
    values = winsorize_series(transformed, lower, upper)
    result = pd.Series(neutral_score, index=series.index, dtype=float)
    finite_mask = values.notna() & np.isfinite(values)
    finite = values[finite_mask]
    if finite.empty:
        return result
    if finite.nunique(dropna=True) <= 1:
        result.loc[finite_mask] = neutral_score
        return result
    ascending = direction in {"higher", "boolean_higher"}
    if direction in {"lower", "magnitude_lower", "moderate"}:
        ascending = False
    result.loc[finite_mask] = finite.rank(method="average", pct=True, ascending=ascending) * 100.0
    return result.clip(0.0, 100.0)


def component_score(
    frame: pd.DataFrame,
    fields: list[str],
    directions: dict[str, str],
    *,
    lower: float = 0.01,
    upper: float = 0.99,
    neutral_score: float = 50.0,
) -> tuple[pd.Series, pd.Series, dict[str, float]]:
    if not fields:
        neutral = pd.Series(neutral_score, index=frame.index, dtype=float)
        return neutral, pd.Series(0.0, index=frame.index, dtype=float), {}
    field_scores = []
    valid_counts = pd.Series(0.0, index=frame.index, dtype=float)
    field_coverage = {}
    for field in fields:
        if field not in frame.columns:
            field_scores.append(pd.Series(neutral_score, index=frame.index, dtype=float))
            field_coverage[field] = 0.0
            continue
        values = frame[field]
        valid = pd.to_numeric(values, errors="coerce").notna()
        if str(values.dtype) == "bool":
            valid = values.notna()
        valid_counts = valid_counts + valid.astype(float)
        field_coverage[field] = round(float(valid.mean()), 6) if len(values) else 0.0
        field_scores.append(
            percentile_score(
                values,
                direction=directions.get(field, "higher"),
                lower=lower,
                upper=upper,
                neutral_score=neutral_score,
            )
        )
    score_matrix = pd.concat(field_scores, axis=1)
    score = score_matrix.mean(axis=1).fillna(neutral_score).clip(0.0, 100.0)
    confidence = (valid_counts / len(fields)).clip(0.0, 1.0)
    return score, confidence, field_coverage


def rank_and_percentile(symbols: pd.Series, scores: pd.Series) -> tuple[pd.Series, pd.Series]:
    frame = pd.DataFrame({"symbol": symbols.astype(str), "score": pd.to_numeric(scores, errors="coerce").fillna(0.0)})
    ordered = frame.sort_values(["score", "symbol"], ascending=[False, True]).reset_index()
    ordered["rank"] = range(1, len(ordered) + 1)
    count = len(ordered)
    if count <= 1:
        ordered["percentile"] = 100.0
    else:
        ordered["percentile"] = (count - ordered["rank"]) / (count - 1) * 100.0
    ranks = pd.Series(index=frame.index, dtype=int)
    percentiles = pd.Series(index=frame.index, dtype=float)
    for _, row in ordered.iterrows():
        ranks.loc[row["index"]] = int(row["rank"])
        percentiles.loc[row["index"]] = float(row["percentile"])
    return ranks.astype(int), percentiles.clip(0.0, 100.0)


def score_range(frame: pd.DataFrame, column: str) -> dict[str, float | None]:
    if column not in frame.columns or frame.empty:
        return {"min": None, "max": None}
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        return {"min": None, "max": None}
    return {"min": float(values.min()), "max": float(values.max())}


def _transform(series: pd.Series, direction: str) -> pd.Series:
    if direction == "boolean_higher":
        return series.map(lambda value: np.nan if pd.isna(value) else 1.0 if bool(value) else 0.0)
    values = pd.to_numeric(series, errors="coerce")
    if direction == "magnitude_lower":
        return values.abs()
    if direction == "moderate":
        finite = values[np.isfinite(values)]
        if finite.empty:
            return values
        target = finite.median()
        return (values - target).abs()
    return values


def json_breakdown(values: dict[str, Any]) -> str:
    import json

    clean = {}
    for key, value in values.items():
        try:
            number = float(value)
            clean[key] = round(number, 6) if np.isfinite(number) else None
        except (TypeError, ValueError):
            clean[key] = value
    return json.dumps(clean, ensure_ascii=False, sort_keys=True)
