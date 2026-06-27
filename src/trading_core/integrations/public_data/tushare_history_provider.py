"""Tushare historical price fallback adapter."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from trading_core.equity_data_quality.common import normalize_date, normalize_symbol, safe_float, safe_int, utc_now


PROVIDER_NAME = "tushare_provider"


def fetch_tushare_price_history(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    adjustment_type: str = "raw",
    max_workers: int = 1,
    retry: int = 1,
    rate_limit_per_minute: int | None = None,
) -> dict[str, Any]:
    del adjustment_type, max_workers, retry, rate_limit_per_minute
    token = os.environ.get("TUSHARE_TOKEN") or os.environ.get("TUSHARE_API_TOKEN") or os.environ.get("TS_TOKEN")
    if not token:
        return _unavailable(symbols, "missing Tushare token", external_api_called=False)
    try:
        import tushare as ts
    except Exception as exc:  # pragma: no cover
        return _unavailable(symbols, f"{type(exc).__name__}: {exc}", external_api_called=False)
    ts.set_token(token)
    pro = ts.pro_api()
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    for symbol in symbols:
        try:
            ts_code = _provider_symbol(symbol)
            frame = pro.daily(ts_code=ts_code, start_date=start_date.replace("-", ""), end_date=end_date.replace("-", ""))
            parsed = [_parse_row(row) for row in frame.to_dict("records")]
            parsed = [row for row in parsed if row]
            rows.extend(parsed)
            symbol_results.append(_symbol_result(symbol, parsed, ""))
            if not parsed:
                failed.append({"symbol": normalize_symbol(symbol), "reason": "no historical rows"})
        except Exception as exc:  # pragma: no cover
            reason = f"{type(exc).__name__}: {exc}"
            failed.append({"symbol": normalize_symbol(symbol), "reason": reason})
            symbol_results.append(_symbol_result(symbol, [], reason))
    return {
        "provider": PROVIDER_NAME,
        "attempted_symbols": symbols,
        "succeeded_symbols": sorted({row["symbol"] for row in rows}),
        "failed_symbols": failed,
        "symbol_results": symbol_results,
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }


def _provider_symbol(symbol: str) -> str:
    normalized = normalize_symbol(symbol)
    code, suffix = normalized.split(".")
    return f"{code}.{suffix}"


def _parse_row(row: dict[str, Any]) -> dict[str, Any]:
    close_value = safe_float(row.get("close"))
    change_value = safe_float(row.get("change"))
    pre_close = close_value - change_value if close_value is not None and change_value is not None else None
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "date": normalize_date(row.get("trade_date")),
        "symbol": normalize_symbol(row.get("ts_code")),
        "open": safe_float(row.get("open")),
        "high": safe_float(row.get("high")),
        "low": safe_float(row.get("low")),
        "close": close_value,
        "volume": safe_int(row.get("vol")),
        "amount": safe_float(row.get("amount")),
        "turnover": None,
        "pre_close": pre_close,
        "change": change_value,
        "pct_change": safe_float(row.get("pct_chg")),
        "adjustment_type": "raw",
        "source": PROVIDER_NAME,
        "source_timestamp": now,
        "provider": PROVIDER_NAME,
        "ingested_at": now,
    }


def _symbol_result(symbol: str, rows: list[dict[str, Any]], reason: str) -> dict[str, Any]:
    dates = [row["date"] for row in rows if row.get("date")]
    return {
        "symbol": normalize_symbol(symbol),
        "provider": PROVIDER_NAME,
        "provider_attempted": True,
        "provider_succeeded": bool(rows),
        "provider_failed": not bool(rows),
        "row_count": len(rows),
        "first_date": min(dates) if dates else "",
        "last_date": max(dates) if dates else "",
        "failure_reason": "" if rows else reason,
        "last_attempted_at": utc_now(),
    }


def _unavailable(symbols: list[str], reason: str, *, external_api_called: bool) -> dict[str, Any]:
    return {
        "provider": PROVIDER_NAME,
        "attempted_symbols": symbols,
        "succeeded_symbols": [],
        "failed_symbols": [{"symbol": normalize_symbol(symbol), "reason": reason} for symbol in symbols],
        "symbol_results": [_symbol_result(symbol, [], reason) for symbol in symbols],
        "rows": [],
        "external_api_called": external_api_called,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }
