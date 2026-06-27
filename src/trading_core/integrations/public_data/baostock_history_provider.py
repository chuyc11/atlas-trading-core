"""BaoStock historical price fallback adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from trading_core.equity_data_quality.common import normalize_symbol, safe_float, safe_int, utc_now


PROVIDER_NAME = "baostock_provider"


def fetch_baostock_price_history(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    adjustment_type: str = "raw",
    max_workers: int = 1,
    retry: int = 1,
    rate_limit_per_minute: int | None = None,
) -> dict[str, Any]:
    del max_workers, retry, rate_limit_per_minute
    try:
        import baostock as bs
    except Exception as exc:  # pragma: no cover
        return _unavailable(symbols, f"{type(exc).__name__}: {exc}", external_api_called=False)
    login = bs.login()
    if getattr(login, "error_code", "1") != "0":
        return _unavailable(symbols, f"login_failed: {getattr(login, 'error_msg', '')}", external_api_called=True)
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    try:
        adjustflag = {"raw": "3", "forward_adjusted": "2", "backward_adjusted": "1"}.get(adjustment_type, "3")
        fields = "date,code,open,high,low,close,preclose,volume,amount,turn,pctChg"
        for symbol in symbols:
            provider_symbol = _provider_symbol(symbol)
            result = bs.query_history_k_data_plus(provider_symbol, fields, start_date, end_date, frequency="d", adjustflag=adjustflag)
            parsed: list[dict[str, Any]] = []
            if result.error_code == "0":
                while result.next():
                    parsed.append(_parse_row(result.get_row_data(), adjustment_type=adjustment_type))
            reason = "" if parsed else (result.error_msg or "no historical rows")
            rows.extend(parsed)
            symbol_results.append(_symbol_result(symbol, parsed, reason))
            if not parsed:
                failed.append({"symbol": normalize_symbol(symbol), "reason": reason})
    finally:
        bs.logout()
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
    return f"{suffix.lower()}.{code}"


def _parse_row(values: list[str], *, adjustment_type: str) -> dict[str, Any]:
    date, code, open_, high, low, close, preclose, volume, amount, turn, pct = values
    symbol = normalize_symbol(code.split(".")[-1])
    close_value = safe_float(close)
    pre_close = safe_float(preclose)
    change = close_value - pre_close if close_value is not None and pre_close is not None else None
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "date": date,
        "symbol": symbol,
        "open": safe_float(open_),
        "high": safe_float(high),
        "low": safe_float(low),
        "close": close_value,
        "volume": safe_int(volume),
        "amount": safe_float(amount),
        "turnover": safe_float(turn),
        "pre_close": pre_close,
        "change": change,
        "pct_change": safe_float(pct),
        "adjustment_type": adjustment_type,
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
