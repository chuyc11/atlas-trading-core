"""Risk-downgraded candidate detection."""

from __future__ import annotations

from typing import Any

import pandas as pd


def build_risk_downgraded_candidates(frame: pd.DataFrame, config, strict_candidate_symbols: set[str], created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        symbol = str(row.get("symbol"))
        if symbol in strict_candidate_symbols:
            continue
        trigger_horizon = _trigger_horizon(row, config.risk_downgrade_percentile_min)
        if not trigger_horizon:
            continue
        reasons = _downgrade_reasons(row, trigger_horizon, config)
        if not reasons:
            continue
        rows.append(
            {
                "as_of_date": row["as_of_date"],
                "symbol": symbol,
                "name": row.get("name", ""),
                "exchange": row.get("exchange", ""),
                "board": row.get("board", ""),
                "industry_level_1": row.get("industry_level_1", ""),
                "industry_level_2": row.get("industry_level_2", ""),
                "trigger_horizon": trigger_horizon,
                "trigger_score": row.get(f"{trigger_horizon}Score"),
                "trigger_percentile": row.get(f"{trigger_horizon}Percentile"),
                "downgrade_reason": ";".join(reasons),
                "RiskScore": row.get("RiskScore"),
                "LiquidityScore": row.get("LiquidityScore"),
                "confidence": row.get(f"{trigger_horizon}Confidence"),
                "not_in_strict_candidates": True,
                "candidate_not_investment_advice": True,
                "not_buy_signal": True,
                "not_sell_signal": True,
                "not_order_instruction": True,
                "not_profit_guarantee": True,
                "created_at": created_at,
            }
        )
    return sorted(rows, key=lambda item: float(item.get("trigger_percentile") or 0.0), reverse=True)


def _trigger_horizon(row: pd.Series, threshold: float) -> str:
    candidates = [
        (horizon, float(row.get(f"{horizon}Percentile") or 0.0))
        for horizon in ["Long", "Mid", "Short"]
        if float(row.get(f"{horizon}Percentile") or 0.0) >= threshold
    ]
    if not candidates:
        return ""
    return max(candidates, key=lambda item: item[1])[0]


def _downgrade_reasons(row: pd.Series, horizon: str, config) -> list[str]:
    reasons = []
    if float(row.get("RiskScore") or 0.0) < config.risk_downgrade_risk_score_max:
        reasons.append("low_risk_score")
    if float(row.get("LiquidityScore") or 0.0) < config.risk_downgrade_liquidity_score_max:
        reasons.append("low_liquidity_score")
    if float(row.get(f"{horizon}Confidence") or 0.0) < config.minimum_candidate_confidence:
        reasons.append("low_confidence")
    return reasons
