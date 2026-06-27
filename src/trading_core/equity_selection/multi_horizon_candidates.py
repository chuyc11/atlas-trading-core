"""Multi-horizon candidate detection."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_selection.candidate_explainer import json_text


def build_multi_horizon_candidates(frame: pd.DataFrame, config, created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        high_horizons = [
            horizon
            for horizon in ["Long", "Mid", "Short"]
            if float(row.get(f"{horizon}Percentile") or 0.0) >= config.multi_horizon_percentile_min
        ]
        composite_hit = float(row.get("CompositePercentile") or 0.0) >= config.composite_percentile_min
        if len(high_horizons) < 2 and not composite_hit:
            continue
        best_horizon = min(
            ["Long", "Mid", "Short"],
            key=lambda horizon: int(row.get(f"{horizon}Rank") or 999999),
        )
        overlap = "composite_top_percentile" if composite_hit and len(high_horizons) < 2 else "+".join(high_horizons)
        rows.append(
            {
                "as_of_date": row["as_of_date"],
                "symbol": row["symbol"],
                "name": row.get("name", ""),
                "exchange": row.get("exchange", ""),
                "board": row.get("board", ""),
                "industry_level_1": row.get("industry_level_1", ""),
                "industry_level_2": row.get("industry_level_2", ""),
                "LongScore": row.get("LongScore"),
                "MidScore": row.get("MidScore"),
                "ShortScore": row.get("ShortScore"),
                "CompositeOpportunityScore": row.get("CompositeOpportunityScore"),
                "CompositeRank": row.get("CompositeRank"),
                "CompositePercentile": row.get("CompositePercentile"),
                "horizon_overlap_type": overlap,
                "best_horizon": best_horizon,
                "primary_strengths": json_text(["multi_horizon_overlap", *[f"high_{h.lower()}_percentile" for h in high_horizons]]),
                "risk_notes": json_text(_risk_notes(row)),
                "candidate_not_investment_advice": True,
                "not_buy_signal": True,
                "not_sell_signal": True,
                "not_order_instruction": True,
                "not_profit_guarantee": True,
                "created_at": created_at,
            }
        )
    return sorted(rows, key=lambda item: int(item.get("CompositeRank") or 999999))[:50]


def _risk_notes(row: pd.Series) -> list[str]:
    notes = []
    if float(row.get("RiskScore") or 0.0) < 40:
        notes.append("low_risk_score")
    if float(row.get("LiquidityScore") or 0.0) < 45:
        notes.append("low_liquidity_score")
    return notes or ["no_major_risk_flag_detected"]
