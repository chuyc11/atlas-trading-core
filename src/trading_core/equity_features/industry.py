"""Industry features for A-share multi-horizon feature engineering."""

from __future__ import annotations

from typing import cast, Any

import pandas as pd


def latest_industry_by_symbol(industry: pd.DataFrame, as_of_date: str) -> dict[str, dict[str, Any]]:
    if industry.empty or "symbol" not in industry.columns:
        return {}
    frame = industry.copy()
    if "effective_date" in frame.columns:
        frame = frame[frame["effective_date"].astype(str) <= as_of_date].copy()
        frame = frame.sort_values(["symbol", "effective_date"])
    return {row["symbol"]: row for row in cast(list[dict[str, Any]], frame.drop_duplicates("symbol", keep="last").to_dict(orient="records"))}


def industry_key(row: dict[str, Any]) -> str:
    level_1 = str(row.get("industry_level_1") or "")
    level_2 = str(row.get("industry_level_2") or "")
    if level_1 and level_1.lower() != "unclassified":
        return level_1
    return level_2 or level_1 or "UNKNOWN"


def build_industry_return_map(return_frame: pd.DataFrame, industry_map: dict[str, dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    if return_frame.empty:
        return {}
    frame = return_frame.copy()
    frame["industry_key"] = frame["symbol"].map(lambda symbol: industry_key(industry_map.get(symbol, {})))
    result: dict[str, dict[str, float | None]] = {}
    for horizon in [5, 20, 60, 120, 250]:
        column = f"return_{horizon}d"
        if column not in frame.columns:
            continue
        means = frame.groupby("industry_key")[column].mean(numeric_only=True)
        for key, value in means.items():
            result.setdefault(str(key), {})[column] = float(value) if pd.notna(value) else None
    return result

