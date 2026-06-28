"""Portfolio NAV series construction."""

from __future__ import annotations

from typing import Any

from trading_core.equity_performance.performance_config import PERFORMANCE_FLAGS, PORTFOLIO_IDS, PORTFOLIO_KEYS, PerformanceConfig


def nav_records_from_tracking_snapshot(
    *,
    config: PerformanceConfig,
    tracking_snapshot: dict[str, Any],
    snapshot_date: str,
    source_tracking_snapshot: str,
) -> list[dict[str, Any]]:
    nav_snapshot = tracking_snapshot.get("portfolio_nav_snapshot", {})
    portfolios = nav_snapshot.get("portfolios", {})
    records: list[dict[str, Any]] = []
    for key in PORTFOLIO_KEYS:
        source = portfolios.get(key, {})
        portfolio_id = str(source.get("portfolio_id") or PORTFOLIO_IDS[key])
        nav = float(source.get("portfolio_nav") or source.get("nav") or 0.0)
        records.append(
            {
                "portfolio_key": key,
                "portfolio_id": portfolio_id,
                "portfolio_horizon": source.get("portfolio_horizon"),
                "as_of_date": snapshot_date,
                "nav": nav,
                "cash_balance": float(source.get("cash_balance") or 0.0),
                "gross_exposure": float(source.get("gross_exposure") or 0.0),
                "net_exposure": float(source.get("net_exposure") or 0.0),
                "holding_count": int(source.get("holding_count") or 0),
                "source_tracking_snapshot": source_tracking_snapshot,
                "first_day_initialization": bool(source.get("first_day_initialization", snapshot_date == config.tracking_start_date)),
                "performance_not_yet_observed": bool(source.get("performance_not_yet_observed", snapshot_date == config.tracking_start_date)),
                **PERFORMANCE_FLAGS,
            }
        )
    return records


def build_portfolio_nav_series(config: PerformanceConfig, records: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_records = _sorted_records(records)
    counts = _observation_counts(sorted_records)
    sufficient = all(count >= config.minimum_required_observations for count in counts.values()) if counts else False
    return {
        "series_id": "A-SHARE-PORTFOLIO-NAV-SERIES",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "tracking_start_date": config.tracking_start_date,
        "mode": config.mode,
        "records": sorted_records,
        "observation_counts": counts,
        "multi_day_observations": min(counts.values()) if counts else 0,
        "multi_day_performance_available": sufficient,
        "sufficient_history": sufficient,
        "insufficient_history": not sufficient,
        "first_day_initialization": any(row["first_day_initialization"] for row in sorted_records),
        "performance_not_yet_observed": not sufficient,
        **PERFORMANCE_FLAGS,
    }


def merge_series_records(
    *,
    existing: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
    allow_idempotent_append: bool,
    key_fields: tuple[str, ...] = ("portfolio_id", "as_of_date"),
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicate_keys: list[str] = []
    idempotent_keys: list[str] = []
    for row in existing:
        merged[tuple(row.get(field) for field in key_fields)] = row
    for row in incoming:
        key = tuple(row.get(field) for field in key_fields)
        if key in merged:
            duplicate_keys.append("|".join(str(part) for part in key))
            if merged[key] == row and allow_idempotent_append:
                idempotent_keys.append("|".join(str(part) for part in key))
                continue
            raise ValueError(f"duplicate performance date requires identical idempotent append: {key}")
        merged[key] = row
    return _sorted_records(list(merged.values())), sorted(set(duplicate_keys)), sorted(set(idempotent_keys))


def _observation_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, set[str]] = {}
    for row in records:
        counts.setdefault(str(row["portfolio_id"]), set()).add(str(row["as_of_date"]))
    return {key: len(value) for key, value in sorted(counts.items())}


def _sorted_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda row: (str(row.get("portfolio_id")), str(row.get("as_of_date"))))
