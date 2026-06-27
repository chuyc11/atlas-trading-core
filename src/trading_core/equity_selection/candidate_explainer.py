"""Explanation helpers for A-share candidate records."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def inclusion_reasons(row: pd.Series, horizon: str) -> list[str]:
    reasons: list[str] = [f"high_{horizon.lower()}_percentile"]
    if _number(row.get("CompositePercentile")) >= 85:
        reasons.append("strong_composite_percentile")
    if _number(row.get("IndustryScore")) >= 60:
        reasons.append("strong_industry_score")
    if _number(row.get("LiquidityScore")) >= 60:
        reasons.append("strong_liquidity_score")
    if _number(row.get("RiskScore")) >= 50:
        reasons.append("acceptable_risk_score")
    if _number(row.get("FundamentalScore")) >= 55:
        reasons.append("strong_fundamental_score")
    if horizon == "Long" and "strong_fundamental_score" not in reasons:
        reasons.append("acceptable_risk_score")
    if horizon == "Mid":
        reasons.append("strong_trend_component")
    if horizon == "Short":
        reasons.append("strong_momentum_component")
    return _dedupe(reasons)[:6]


def risk_reasons(row: pd.Series, horizon: str, component_map: dict[tuple[str, str], dict[str, float]], *, low_confidence_threshold: float = 0.40) -> list[str]:
    reasons: list[str] = []
    if _number(row.get("RiskScore")) < 40:
        reasons.append("low_risk_score")
    if _number(row.get("LiquidityScore")) < 45:
        reasons.append("low_liquidity_score")
    if _number(row.get(f"{horizon}Confidence")) < low_confidence_threshold:
        reasons.append("low_confidence")
    if horizon == "Long" and _number(row.get("fundamental_confidence")) < low_confidence_threshold:
        reasons.append("fundamental_coverage_low")
    if horizon == "Short":
        overheat_value = component_map.get((str(row.get("symbol")), "ShortScore"), {}).get("overheat_penalty_component")
        if overheat_value is not None and float(overheat_value) < 35:
            reasons.append("overheat_risk")
    return reasons or ["no_major_risk_flag_detected"]


def confidence_notes(row: pd.Series, horizon: str) -> list[str]:
    values = {
        f"{horizon}Confidence": _number(row.get(f"{horizon}Confidence")),
        "CompositeConfidence": _number(row.get("CompositeConfidence")),
        "fundamental_confidence": _number(row.get("fundamental_confidence")),
        "risk_confidence": _number(row.get("risk_confidence")),
        "liquidity_confidence": _number(row.get("liquidity_confidence")),
    }
    return [f"{key}={round(value, 4)}" for key, value in values.items()]


def component_highlights(symbol: str, score_name: str, component_map: dict[tuple[str, str], dict[str, float]]) -> list[str]:
    components = component_map.get((symbol, score_name), {})
    if not components:
        return []
    ordered = sorted(components.items(), key=lambda item: item[1], reverse=True)
    return [f"{name}:{round(value, 4)}" for name, value in ordered[:4]]


def _number(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _dedupe(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
