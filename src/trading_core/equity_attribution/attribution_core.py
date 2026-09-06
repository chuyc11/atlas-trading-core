"""Shared attribution aggregation helpers."""

from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any

from trading_core.equity_attribution.attribution_config import (
    ATTRIBUTION_FLAGS,
    BUCKET_EDGES,
    PORTFOLIO_IDS,
    SCORE_NAMES,
)


def all_holdings(inputs: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    returns = _returns_by_portfolio(inputs.performance.get("portfolio_return_series", {}).get("records", []))
    for key, holdings in inputs.holdings_by_key.items():
        portfolio_id = PORTFOLIO_IDS[key]
        return_row = returns.get(portfolio_id, {})
        for holding in holdings:
            row = dict(holding)
            row["portfolio_key"] = key
            row["portfolio_id"] = portfolio_id
            row["position_value"] = float(row.get("virtual_position_value") or row.get("position_value") or 0.0)
            row["target_weight"] = float(row.get("target_weight") or 0.0)
            row["actual_weight"] = float(row.get("actual_weight") or 0.0)
            row["daily_return"] = float(return_row.get("daily_return") or 0.0)
            row["cumulative_return"] = float(return_row.get("cumulative_return") or 0.0)
            row["first_day_initialization"] = bool(return_row.get("first_day_initialization", True))
            row["contribution_status"] = "insufficient_history" if row["first_day_initialization"] else "available"
            row["daily_contribution"] = 0.0 if row["contribution_status"] == "insufficient_history" else row["actual_weight"] * row["daily_return"]
            row["cumulative_contribution"] = 0.0 if row["contribution_status"] == "insufficient_history" else row["actual_weight"] * row["cumulative_return"]
            row["industry_level_1"] = row.get("industry_level_1") or "Unclassified"
            row["industry_level_2"] = row.get("industry_level_2") or ""
            row["industry"] = row.get("industry") or row["industry_level_1"]
            row["candidate_source"] = row.get("candidate_source") or "other_or_unknown"
            rows.append(row)
    return rows


def build_holding_rows(inputs: Any) -> list[dict[str, Any]]:
    rows = []
    for row in all_holdings(inputs):
        scores = row.get("score_snapshot") or {}
        rows.append(
            {
                "portfolio_id": row["portfolio_id"],
                "symbol": row.get("symbol"),
                "name": row.get("name"),
                "industry_level_1": row.get("industry_level_1"),
                "candidate_source": row.get("candidate_source"),
                "target_weight": row["target_weight"],
                "actual_weight": row["actual_weight"],
                "position_value": row["position_value"],
                "daily_return": row["daily_return"],
                "cumulative_return": row["cumulative_return"],
                "daily_contribution": row["daily_contribution"],
                "cumulative_contribution": row["cumulative_contribution"],
                "score_snapshot": scores,
                "risk_score": _score(row, "RiskScore"),
                "liquidity_score": _score(row, "LiquidityScore"),
                "composite_score": _score(row, "CompositeOpportunityScore"),
                "contribution_status": row["contribution_status"],
                "first_day_initialization": row["first_day_initialization"],
                **ATTRIBUTION_FLAGS,
            }
        )
    return sorted(rows, key=lambda item: (item["portfolio_id"], -float(item["actual_weight"]), str(item["symbol"])))


def group_by_field(rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field) or "other_or_unknown")].append(row)
    return dict(grouped)


def aggregate_groups(rows: list[dict[str, Any]], *, field: str, label_field: str) -> dict[str, Any]:
    portfolios = {}
    for portfolio_id, portfolio_rows in group_by_field(rows, "portfolio_id").items():
        portfolio_weight = _sum(portfolio_rows, "actual_weight")
        records: list[dict[str, Any]] = []
        for label, group_rows in group_by_field(portfolio_rows, field).items():
            weight = _sum(group_rows, "actual_weight")
            records.append(
                {
                    "portfolio_id": portfolio_id,
                    label_field: label,
                    "holding_count": len(group_rows),
                    "weight": weight,
                    "position_value": _sum(group_rows, "position_value"),
                    "daily_contribution": _sum(group_rows, "daily_contribution"),
                    "cumulative_contribution": _sum(group_rows, "cumulative_contribution"),
                    "average_score": _weighted_score(group_rows, "CompositeOpportunityScore"),
                    "average_risk_score": _weighted_score(group_rows, "RiskScore"),
                    "average_liquidity_score": _weighted_score(group_rows, "LiquidityScore"),
                    "concentration_share": 0.0 if not portfolio_weight else weight / portfolio_weight,
                    "daily_contribution_status": _status(group_rows),
                }
            )
        portfolios[portfolio_id] = sorted(records, key=lambda item: -float(item["weight"]))
    return portfolios


def bucket_records(rows: list[dict[str, Any]], *, score_name: str) -> dict[str, list[dict[str, Any]]]:
    by_portfolio: dict[str, list[dict[str, Any]]] = {}
    for portfolio_id, portfolio_rows in group_by_field(rows, "portfolio_id").items():
        records = []
        for low, high in zip(BUCKET_EDGES[:-1], BUCKET_EDGES[1:], strict=False):
            label = f"{low}-{high}"
            bucket_rows = [row for row in portfolio_rows if _in_bucket(_score(row, score_name), low, high)]
            records.append(
                {
                    "portfolio_id": portfolio_id,
                    "bucket_label": label,
                    "bucket_min": low,
                    "bucket_max": high,
                    "holding_count": len(bucket_rows),
                    "weight": _sum(bucket_rows, "actual_weight"),
                    "position_value": _sum(bucket_rows, "position_value"),
                    "average_actual_weight": _avg(bucket_rows, "actual_weight"),
                    "average_risk_score": _weighted_score(bucket_rows, "RiskScore"),
                    "average_liquidity_score": _weighted_score(bucket_rows, "LiquidityScore"),
                    "daily_contribution": _sum(bucket_rows, "daily_contribution"),
                    "daily_contribution_status": _status(bucket_rows) if bucket_rows else "not_applicable",
                }
            )
        by_portfolio[portfolio_id] = records
    return by_portfolio


def score_bucket_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "score_types": {score_name: bucket_records(rows, score_name=score_name) for score_name in SCORE_NAMES},
        "portfolios": bucket_records(rows, score_name="CompositeOpportunityScore"),
        "bucket_edges": list(BUCKET_EDGES),
    }


def risk_bucket_payload(rows: list[dict[str, Any]], risk_downgraded_symbols: set[str]) -> dict[str, Any]:
    portfolios = bucket_records(rows, score_name="RiskScore")
    downgraded_in_portfolio = sorted({str(row.get("symbol")) for row in rows if str(row.get("symbol")) in risk_downgraded_symbols})
    diagnostics = {}
    for portfolio_id, records in portfolios.items():
        diagnostics[portfolio_id] = {
            "low_risk_bucket_exposure": sum(row["weight"] for row in records if row["bucket_max"] <= 40),
            "medium_risk_bucket_exposure": sum(row["weight"] for row in records if row["bucket_min"] >= 40 and row["bucket_max"] <= 80),
            "high_risk_bucket_exposure": sum(row["weight"] for row in records if row["bucket_min"] >= 80),
        }
    return {
        "portfolios": portfolios,
        "risk_diagnostics": diagnostics,
        "risk_downgraded_exposure": sum(row["actual_weight"] for row in rows if str(row.get("symbol")) in risk_downgraded_symbols),
        "risk_downgraded_symbols_in_portfolio": downgraded_in_portfolio,
    }


def liquidity_bucket_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    portfolios = bucket_records(rows, score_name="LiquidityScore")
    diagnostics = {}
    for portfolio_id, portfolio_rows in group_by_field(rows, "portfolio_id").items():
        low = [row for row in portfolio_rows if (_score(row, "LiquidityScore") or 0.0) < 40]
        high = [row for row in portfolio_rows if (_score(row, "LiquidityScore") or 0.0) >= 80]
        minimum = min(portfolio_rows, key=lambda row: _score(row, "LiquidityScore") or 101.0) if portfolio_rows else {}
        diagnostics[portfolio_id] = {
            "low_liquidity_exposure": _sum(low, "actual_weight"),
            "high_liquidity_exposure": _sum(high, "actual_weight"),
            "weighted_average_liquidity_score": _weighted_score(portfolio_rows, "LiquidityScore"),
            "minimum_liquidity_score_holding": {"symbol": minimum.get("symbol"), "score": _score(minimum, "LiquidityScore"), "weight": minimum.get("actual_weight")},
            "top_illiquidity_contributors": [
                {"symbol": row.get("symbol"), "liquidity_score": _score(row, "LiquidityScore"), "weight": row.get("actual_weight")}
                for row in sorted(portfolio_rows, key=lambda item: (_score(item, "LiquidityScore") or 101.0, -float(item.get("actual_weight") or 0.0)))[:5]
            ],
        }
    return {"portfolios": portfolios, "liquidity_diagnostics": diagnostics}


def concentration_payload(rows: list[dict[str, Any]], *, risk_downgraded_symbols: set[str], excluded_symbols: set[str]) -> dict[str, Any]:
    portfolios = {}
    for portfolio_id, portfolio_rows in group_by_field(rows, "portfolio_id").items():
        weights = sorted([float(row.get("actual_weight") or 0.0) for row in portfolio_rows], reverse=True)
        industries = aggregate_groups(portfolio_rows, field="industry_level_1", label_field="industry_level_1")[portfolio_id]
        hhi = sum(weight * weight for weight in weights)
        effective = 0.0 if hhi == 0 else 1.0 / hhi
        max_industry = max([row["weight"] for row in industries], default=0.0)
        risk_exposure = sum(float(row.get("actual_weight") or 0.0) for row in portfolio_rows if str(row.get("symbol")) in risk_downgraded_symbols)
        excluded_exposure = sum(float(row.get("actual_weight") or 0.0) for row in portfolio_rows if str(row.get("symbol")) in excluded_symbols)
        low_liquidity_exposure = sum(float(row.get("actual_weight") or 0.0) for row in portfolio_rows if (_score(row, "LiquidityScore") or 0.0) < 40)
        high_risk_exposure = sum(float(row.get("actual_weight") or 0.0) for row in portfolio_rows if (_score(row, "RiskScore") or 0.0) >= 80)
        unclassified = sum(float(row.get("actual_weight") or 0.0) for row in portfolio_rows if str(row.get("industry_level_1") or "").lower() == "unclassified")
        flags = {
            "concentrated_top5": sum(weights[:5]) > 0.35,
            "concentrated_industry": max_industry > 0.35,
            "contains_risk_downgraded": risk_exposure > 0,
            "contains_excluded_universe": excluded_exposure > 0,
            "low_liquidity_cluster": low_liquidity_exposure > 0.20,
            "unclassified_industry_high": unclassified > 0.50,
        }
        portfolios[portfolio_id] = {
            "holding_count": len(portfolio_rows),
            "weighted_average_risk_score": _weighted_score(portfolio_rows, "RiskScore"),
            "weighted_average_liquidity_score": _weighted_score(portfolio_rows, "LiquidityScore"),
            "weighted_average_composite_score": _weighted_score(portfolio_rows, "CompositeOpportunityScore"),
            "max_single_weight": weights[0] if weights else 0.0,
            "top_5_weight": sum(weights[:5]),
            "top_10_weight": sum(weights[:10]),
            "max_industry_weight": max_industry,
            "industry_count": len(industries),
            "effective_number_of_holdings": effective,
            "herfindahl_index": hhi,
            "risk_downgraded_exposure": risk_exposure,
            "excluded_universe_exposure": excluded_exposure,
            "unclassified_industry_exposure": unclassified,
            "low_liquidity_exposure": low_liquidity_exposure,
            "high_risk_exposure": high_risk_exposure,
            "diagnostic_flags": flags,
        }
    return {"portfolios": portfolios}


def factor_exposure_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    portfolios = {}
    for portfolio_id, portfolio_rows in group_by_field(rows, "portfolio_id").items():
        portfolios[portfolio_id] = {score_name: _weighted_score(portfolio_rows, score_name) for score_name in SCORE_NAMES + ["RiskScore", "LiquidityScore", "IndustryScore", "FundamentalScore"]}
    return {"portfolios": portfolios}


def symbol_set(records: Any) -> set[str]:
    if isinstance(records, dict):
        records = records.get("records") or records.get("candidates") or records.get("holdings") or []
    return {str(row.get("symbol")) for row in records if isinstance(row, dict) and row.get("symbol")}


def _returns_by_portfolio(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("portfolio_id")): row for row in records}


def _score(row: dict[str, Any], name: str) -> float | None:
    value = (row.get("score_snapshot") or {}).get(name, row.get(name))
    if value is None:
        return None
    try:
        number = float(value)
        return number if isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _sum(rows: list[dict[str, Any]], field: str) -> float:
    return float(sum(float(row.get(field) or 0.0) for row in rows))


def _avg(rows: list[dict[str, Any]], field: str) -> float | None:
    return None if not rows else _sum(rows, field) / len(rows)


def _weighted_score(rows: list[dict[str, Any]], score_name: str) -> float | None:
    numerator = 0.0
    denominator = 0.0
    for row in rows:
        score = _score(row, score_name)
        weight = float(row.get("actual_weight") or 0.0)
        if score is not None:
            numerator += score * weight
            denominator += weight
    return None if denominator == 0 else numerator / denominator


def _in_bucket(value: float | None, low: int, high: int) -> bool:
    if value is None:
        return False
    if high == 100:
        return low <= value <= high
    return low <= value < high


def _status(rows: list[dict[str, Any]]) -> str:
    statuses = {row.get("contribution_status") for row in rows}
    if not rows:
        return "not_applicable"
    if statuses == {"available"}:
        return "available"
    if "available" in statuses:
        return "mixed"
    return "insufficient_history"
