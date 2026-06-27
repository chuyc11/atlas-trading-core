"""Risk and liquidity constraints for research-only virtual portfolios."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_portfolios.portfolio_config import PortfolioConstructionConfig


def passes_horizon_risk_constraints(row: dict[str, Any] | pd.Series, horizon: str, config: PortfolioConstructionConfig) -> bool:
    risk = float(row.get("RiskScore") or 0.0)
    liquidity = float(row.get("LiquidityScore") or 0.0)
    if horizon == "Long":
        return risk >= config.long_min_risk_score and liquidity >= config.long_min_liquidity_score
    if horizon == "Mid":
        return risk >= config.mid_min_risk_score and liquidity >= config.mid_min_liquidity_score
    return risk >= config.short_min_risk_score and liquidity >= config.short_min_liquidity_score


def risk_notes(row: dict[str, Any] | pd.Series, horizon: str) -> list[str]:
    notes: list[str] = []
    risk = float(row.get("RiskScore") or 0.0)
    liquidity = float(row.get("LiquidityScore") or 0.0)
    confidence = float(row.get(f"{horizon}Confidence") or row.get("CompositeConfidence") or 0.0)
    if risk < 40:
        notes.append("risk_score_watch")
    if liquidity < 50:
        notes.append("liquidity_score_watch")
    if confidence < 0.5:
        notes.append("confidence_watch")
    if not notes:
        notes.append("no_major_risk_flag_detected")
    return notes


def liquidity_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(row.get("LiquidityScore") or 0.0) for row in records]
    risk_values = [float(row.get("RiskScore") or 0.0) for row in records]
    return {
        "min_liquidity_score": round(min(values), 6) if values else 0.0,
        "avg_liquidity_score": round(sum(values) / len(values), 6) if values else 0.0,
        "min_risk_score": round(min(risk_values), 6) if risk_values else 0.0,
        "avg_risk_score": round(sum(risk_values) / len(risk_values), 6) if risk_values else 0.0,
    }

