"""Industry exposure helpers for research-only A-share virtual portfolios."""

from __future__ import annotations

from typing import Any

import pandas as pd


UNCLASSIFIED_VALUES = {"", "unclassified", "unknown", "nan", "none", "null"}
BOARD_LIKE_VALUES = {"sse_main", "szse_main", "star", "chinext", "bse", "unknown"}


def industry_bucket(row: dict[str, Any] | pd.Series) -> str:
    level_1 = str(row.get("industry_level_1") or "").strip()
    level_2 = str(row.get("industry_level_2") or "").strip()
    board = str(row.get("board") or "").strip()
    symbol = str(row.get("symbol") or "").strip()
    if level_1.lower() not in UNCLASSIFIED_VALUES:
        return level_1
    if level_2 and level_2.lower() not in BOARD_LIKE_VALUES:
        return f"Unclassified/{level_2}"
    prefix = symbol.split(".")[0][:3] if symbol else "UNK"
    segment = level_2 or board or "UNKNOWN"
    return f"Unclassified/{segment}/{prefix}"


def industry_exposure(records: list[dict[str, Any]], *, weight_column: str = "target_weight") -> dict[str, Any]:
    by_level_1: dict[str, float] = {}
    by_level_2: dict[str, float] = {}
    by_bucket: dict[str, float] = {}
    for row in records:
        weight = float(row.get(weight_column) or 0.0)
        level_1 = str(row.get("industry_level_1") or "UNKNOWN")
        level_2 = str(row.get("industry_level_2") or "UNKNOWN")
        bucket = str(row.get("industry") or row.get("industry_bucket") or industry_bucket(row))
        by_level_1[level_1] = by_level_1.get(level_1, 0.0) + weight
        by_level_2[level_2] = by_level_2.get(level_2, 0.0) + weight
        by_bucket[bucket] = by_bucket.get(bucket, 0.0) + weight
    return {
        "industry_weight_by_level_1": _sorted_weights(by_bucket),
        "raw_industry_weight_by_level_1": _sorted_weights(by_level_1),
        "industry_weight_by_level_2": _sorted_weights(by_level_2),
        "top_industry_exposures": _top(by_bucket),
    }


def industry_cap_violations(records: list[dict[str, Any]], cap: float) -> list[dict[str, Any]]:
    exposure = industry_exposure(records)["industry_weight_by_level_1"]
    return [
        {"industry": industry, "weight": weight, "cap": cap}
        for industry, weight in exposure.items()
        if float(weight) > cap + 1e-9
    ]


def max_industry_weight(records: list[dict[str, Any]]) -> float:
    exposure = industry_exposure(records)["industry_weight_by_level_1"]
    return max([float(value) for value in exposure.values()] or [0.0])


def _sorted_weights(values: dict[str, float]) -> dict[str, float]:
    return {key: round(float(value), 6) for key, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))}


def _top(values: dict[str, float], limit: int = 5) -> list[dict[str, Any]]:
    return [
        {"industry": key, "weight": round(float(value), 6)}
        for key, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]
