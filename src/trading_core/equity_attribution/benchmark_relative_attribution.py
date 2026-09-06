"""Benchmark-relative structural attribution."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, BENCHMARK_IDS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows


INDEX_BENCHMARKS = {"CSI300", "CSI500", "CSI1000"}


def build_benchmark_relative_attribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    holding_rows = build_holding_rows(inputs)
    portfolio_industries = _portfolio_industry_weights(holding_rows)
    candidate_benchmark = _candidate_pool_industry_weights(inputs)
    strict_benchmark = _strict_universe_industry_weights(inputs)
    records = []
    for portfolio_id, portfolio_weights in portfolio_industries.items():
        for benchmark_id in BENCHMARK_IDS:
            benchmark_weights, exposure_status, limitation = _benchmark_weights(benchmark_id, strict_benchmark, candidate_benchmark)
            records.append(
                {
                    "portfolio_id": portfolio_id,
                    "benchmark_id": benchmark_id,
                    "portfolio_weight_by_industry": portfolio_weights,
                    "benchmark_weight_by_industry": benchmark_weights,
                    "active_industry_weight": _active_weights(portfolio_weights, benchmark_weights) if benchmark_weights is not None else None,
                    "active_score_bucket_weight": None,
                    "active_risk_bucket_weight": None,
                    "active_liquidity_bucket_weight": None,
                    "relative_performance_status": "insufficient_history",
                    "limited_history": True,
                    "benchmark_constituent_exposure_status": exposure_status,
                    "limitation": limitation,
                }
            )
    return {
        "snapshot_id": "A-SHARE-BENCHMARK-RELATIVE-ATTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "benchmark_ids": list(BENCHMARK_IDS),
        "records": records,
        "index_constituent_exposure_unavailable": sorted(INDEX_BENCHMARKS),
        "equal_weight_benchmark_exposure_available": True,
        **ATTRIBUTION_FLAGS,
    }


def _portfolio_industry_weights(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        result[str(row["portfolio_id"])][str(row.get("industry_level_1") or "Unclassified")] += float(row.get("actual_weight") or 0.0)
    return {portfolio_id: dict(weights) for portfolio_id, weights in result.items()}


def _candidate_pool_industry_weights(inputs: Any) -> dict[str, float]:
    rows: list[dict[str, Any]] = []
    for key in ["long_candidates", "mid_candidates", "short_candidates", "multi_horizon_candidates"]:
        payload = inputs.candidates.get(key, [])
        rows.extend(payload if isinstance(payload, list) else payload.get("records", []))
    return _equal_weight_industries(rows)


def _strict_universe_industry_weights(inputs: Any) -> dict[str, float]:
    payload = inputs.candidates.get("strict_tradable_universe", [])
    rows = payload if isinstance(payload, list) else payload.get("records", [])
    return _equal_weight_industries(rows)


def _equal_weight_industries(rows: list[dict[str, Any]]) -> dict[str, float]:
    unique: dict[str, str] = {}
    for row in rows:
        symbol = row.get("symbol")
        if symbol:
            unique[str(symbol)] = str(row.get("industry_level_1") or "Unclassified")
    if not unique:
        return {}
    weight = 1.0 / len(unique)
    result: dict[str, float] = defaultdict(float)
    for industry in unique.values():
        result[industry] += weight
    return dict(result)


def _benchmark_weights(benchmark_id: str, strict: dict[str, float], candidate: dict[str, float]) -> tuple[dict[str, float] | None, str, str | None]:
    if benchmark_id in INDEX_BENCHMARKS:
        return None, "unavailable", "Benchmark index constituent exposure is unavailable; index return data is available but holdings are not fabricated."
    if benchmark_id == "CASH":
        return {}, "not_applicable", "Cash benchmark has no industry constituent exposure."
    if benchmark_id == "EQUAL_WEIGHT_STRICT_TRADABLE":
        return strict, "available", None
    if benchmark_id == "EQUAL_WEIGHT_CANDIDATE_POOL":
        return candidate, "available", None
    return None, "unavailable", "Unknown benchmark exposure."


def _active_weights(portfolio: dict[str, float], benchmark: dict[str, float]) -> dict[str, float]:
    keys = set(portfolio) | set(benchmark)
    return {key: portfolio.get(key, 0.0) - benchmark.get(key, 0.0) for key in sorted(keys)}
