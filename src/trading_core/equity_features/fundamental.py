"""Fundamental features for A-share multi-horizon feature engineering."""

from __future__ import annotations

from datetime import date
from typing import cast, Any

import pandas as pd


def latest_daily_basic(daily_basic_history: pd.DataFrame, daily_basic_snapshot: pd.DataFrame, as_of_date: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for frame, fallback in [(daily_basic_history, False), (daily_basic_snapshot, True)]:
        if frame.empty or "symbol" not in frame.columns:
            continue
        data = frame.copy()
        if "date" in data.columns:
            data = data[data["date"].astype(str) <= as_of_date].sort_values(["symbol", "date"])
        data = data.drop_duplicates("symbol", keep="last")
        for row in data.to_dict(orient="records"):
            symbol = row["symbol"]
            if fallback or symbol not in rows or _missing_market_data(rows[symbol]):
                rows[symbol] = {**cast(dict[str, Any], row), "used_daily_basic_snapshot_fallback": fallback}
    return rows


def build_fundamental_row(symbol: str, basic_row: dict[str, Any], financial_rows: pd.DataFrame, as_of_date: str) -> dict[str, Any]:
    financial = financial_rows.sort_values(["report_date", "ann_date"]) if not financial_rows.empty else financial_rows
    latest = financial.iloc[-1].to_dict() if not financial.empty else {}
    previous_year = financial.iloc[-5].to_dict() if len(financial) >= 5 else {}
    revenue_growth = _growth(latest.get("revenue"), previous_year.get("revenue"))
    net_profit_growth = _growth(latest.get("net_profit"), previous_year.get("net_profit"))
    roe_ttm = _mean_last(financial, "roe", 4)
    ann_date = str(latest.get("ann_date") or "")[:10]
    report_age = (date.fromisoformat(as_of_date) - date.fromisoformat(ann_date)).days if ann_date else None
    net_margin = _number(latest.get("net_margin"))
    revenue = _number(latest.get("revenue"))
    net_profit = _number(latest.get("net_profit"))
    if net_margin is None and revenue not in (None, 0) and net_profit is not None:
        net_margin = net_profit / revenue * 100.0
    return {
        "pe_ttm": _coalesce(basic_row.get("pe_ttm"), basic_row.get("pe")),
        "pb": _number(basic_row.get("pb")),
        "ps_ttm": _coalesce(basic_row.get("ps_ttm"), basic_row.get("ps")),
        "dv_ttm": _coalesce(basic_row.get("dv_ttm"), basic_row.get("dv_ratio")),
        "pe_ttm_percentile_3y": None,
        "pb_percentile_3y": None,
        "ps_ttm_percentile_3y": None,
        "total_mv": _number(basic_row.get("total_mv")),
        "circ_mv": _number(basic_row.get("circ_mv")),
        "revenue_growth_yoy": revenue_growth,
        "net_profit_growth_yoy": net_profit_growth,
        "roe_latest": _number(latest.get("roe")),
        "roe_ttm": roe_ttm,
        "gross_margin_latest": _number(latest.get("gross_margin")),
        "net_margin_latest": net_margin,
        "operating_cash_flow_latest": _number(latest.get("operating_cash_flow")),
        "debt_to_asset_latest": _number(latest.get("debt_to_asset")),
        "eps_latest": _number(latest.get("eps")),
        "bps_latest": _number(latest.get("bps")),
        "financial_report_age_days": report_age,
        "financial_quarters_available": int(len(financial)),
    }


def _missing_market_data(row: dict[str, Any]) -> bool:
    return _number(row.get("total_mv")) is None or _number(row.get("circ_mv")) is None or _number(row.get("pb")) is None


def _growth(current: Any, previous: Any) -> float | None:
    current_value = _number(current)
    previous_value = _number(previous)
    if current_value is None or previous_value in (None, 0):
        return None
    return current_value / previous_value - 1.0


def _mean_last(frame: pd.DataFrame, column: str, count: int) -> float | None:
    if frame.empty or column not in frame.columns:
        return None
    values = pd.to_numeric(frame[column].tail(count), errors="coerce").dropna()
    return float(values.mean()) if not values.empty else None


def _coalesce(*values: Any) -> float | None:
    for value in values:
        number = _number(value)
        if number is not None:
            return number
    return None


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "-", "--") or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

