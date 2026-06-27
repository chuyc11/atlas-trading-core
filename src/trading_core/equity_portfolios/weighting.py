"""Deterministic target-weight construction for A-share virtual portfolios."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_portfolios.industry_constraints import industry_bucket
from trading_core.equity_portfolios.portfolio_config import PortfolioConstructionConfig


def raw_weight_score(row: dict[str, Any] | pd.Series, horizon: str) -> float:
    percentile = float(row.get(f"{horizon}Percentile") or row.get("CompositePercentile") or 0.0)
    rank = float(row.get(f"{horizon}Rank") or row.get("candidate_rank") or row.get("CompositeRank") or 9999.0)
    confidence = float(row.get(f"{horizon}Confidence") or row.get("CompositeConfidence") or 0.5)
    risk = float(row.get("RiskScore") or 0.0)
    liquidity = float(row.get("LiquidityScore") or 0.0)
    industry = float(row.get("IndustryScore") or 0.0)
    fundamental = float(row.get("FundamentalScore") or 0.0)
    composite = float(row.get("CompositeOpportunityScore") or 0.0)
    rank_component = max(0.0, 100.0 - min(rank, 1000.0) / 10.0)
    if horizon == "Long":
        value = 0.34 * percentile + 0.16 * rank_component + 0.18 * fundamental + 0.14 * risk + 0.10 * industry + 0.08 * composite
    elif horizon == "Mid":
        value = 0.36 * percentile + 0.14 * rank_component + 0.18 * industry + 0.14 * liquidity + 0.10 * composite + 0.08 * risk
    else:
        value = 0.40 * percentile + 0.14 * rank_component + 0.20 * liquidity + 0.12 * industry + 0.08 * composite + 0.06 * risk
    return max(value * max(confidence, 0.05), 0.0001)


def assign_target_weights(
    rows: list[dict[str, Any]],
    *,
    horizon: str,
    config: PortfolioConstructionConfig,
) -> list[dict[str, Any]]:
    if not rows:
        return []
    single_cap = _single_cap(config, horizon)
    industry_cap = _industry_cap(config, horizon)
    total_target = float(config.total_target_weight) - float(config.minimum_cash_buffer)
    raw = {row["symbol"]: raw_weight_score(row, horizon) for row in rows}
    total_raw = sum(raw.values()) or 1.0
    weights = {row["symbol"]: raw[row["symbol"]] / total_raw * total_target for row in rows}
    buckets = {row["symbol"]: str(row.get("industry") or row.get("industry_bucket") or industry_bucket(row)) for row in rows}
    weights = _cap_and_redistribute(weights, raw, buckets, single_cap, industry_cap, total_target)
    result = []
    for rank, row in enumerate(sorted(rows, key=lambda item: (-weights[item["symbol"]], item["symbol"])), start=1):
        weighted = dict(row)
        weighted["target_weight"] = round(float(weights[row["symbol"]]), 10)
        weighted["weight_rank"] = rank
        weighted["weight_reason"] = _weight_reason(weighted, horizon, single_cap, industry_cap)
        result.append(weighted)
    return result


def _cap_and_redistribute(weights: dict[str, float], raw: dict[str, float], buckets: dict[str, str], single_cap: float, industry_cap: float, target: float) -> dict[str, float]:
    weights = dict(weights)
    for _ in range(200):
        before = dict(weights)
        for symbol, value in list(weights.items()):
            if value > single_cap:
                weights[symbol] = single_cap
        for bucket in sorted(set(buckets.values())):
            symbols = [symbol for symbol, item_bucket in buckets.items() if item_bucket == bucket]
            group_total = sum(weights[symbol] for symbol in symbols)
            if group_total > industry_cap and group_total > 0:
                scale = industry_cap / group_total
                for symbol in symbols:
                    weights[symbol] *= scale
        deficit = target - sum(weights.values())
        if abs(deficit) <= 1e-10:
            break
        if deficit > 0:
            room = {
                symbol: min(single_cap - weights[symbol], industry_cap - sum(weights[item] for item, bucket in buckets.items() if bucket == buckets[symbol]))
                for symbol in weights
            }
            room = {symbol: value for symbol, value in room.items() if value > 1e-12}
            if not room:
                break
            raw_room_total = sum(raw[symbol] for symbol in room) or 1.0
            for symbol in room:
                add = min(deficit * raw[symbol] / raw_room_total, room[symbol])
                weights[symbol] += add
        elif sum(weights.values()) > 0:
            scale = target / sum(weights.values())
            for symbol in weights:
                weights[symbol] *= scale
        if max(abs(weights[symbol] - before.get(symbol, 0.0)) for symbol in weights) <= 1e-12:
            break
    residual = target - sum(weights.values())
    if abs(residual) > 1e-10:
        for symbol in sorted(weights, key=lambda item: raw[item], reverse=True):
            bucket_room = industry_cap - sum(weights[item] for item, item_bucket in buckets.items() if item_bucket == buckets[symbol])
            room = min(single_cap - weights[symbol], bucket_room)
            if residual > 0 and room > 0:
                add = min(residual, room)
                weights[symbol] += add
                residual -= add
            elif residual < 0 and weights[symbol] > 0:
                take = min(-residual, weights[symbol] - 1e-12)
                weights[symbol] -= take
                residual += take
            if abs(residual) <= 1e-10:
                break
    return weights


def _single_cap(config: PortfolioConstructionConfig, horizon: str) -> float:
    return float(getattr(config, f"{horizon.lower()}_max_single_weight"))


def _industry_cap(config: PortfolioConstructionConfig, horizon: str) -> float:
    return float(getattr(config, f"{horizon.lower()}_max_industry_weight"))


def _weight_reason(row: dict[str, Any], horizon: str, single_cap: float, industry_cap: float) -> str:
    return (
        f"research-only {horizon} target weight from {horizon} percentile/rank, "
        f"risk/liquidity/industry adjustments, single cap {single_cap:.2%}, industry cap {industry_cap:.2%}"
    )

