"""AkShare historical price fallback adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from trading_core.equity_data_quality.common import normalize_symbol, safe_float, safe_int, utc_now


PROVIDER_NAME = "akshare_provider"


def fetch_akshare_price_history(
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
        import akshare as ak
    except Exception as exc:  # pragma: no cover - dependency availability is environment-specific
        return _unavailable(symbols, f"{type(exc).__name__}: {exc}")
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    adjust = {"raw": "", "forward_adjusted": "qfq", "backward_adjusted": "hfq"}.get(adjustment_type, "")
    for symbol in symbols:
        try:
            code = normalize_symbol(symbol).split(".")[0]
            frame = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust=adjust,
            )
            parsed = [_parse_row(row, adjustment_type=adjustment_type) for row in frame.to_dict("records")]
            parsed = [row for row in parsed if row]
            rows.extend(parsed)
            symbol_results.append(_symbol_result(symbol, parsed, ""))
            if not parsed:
                failed.append({"symbol": normalize_symbol(symbol), "reason": "no historical rows"})
        except Exception as exc:  # pragma: no cover - network failures vary
            reason = f"{type(exc).__name__}: {exc}"
            failed.append({"symbol": normalize_symbol(symbol), "reason": reason})
            symbol_results.append(_symbol_result(symbol, [], reason))
    succeeded = sorted({row["symbol"] for row in rows})
    return {
        "provider": PROVIDER_NAME,
        "attempted_symbols": symbols,
        "succeeded_symbols": succeeded,
        "failed_symbols": failed,
        "symbol_results": symbol_results,
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }


def _parse_row(row: dict[str, Any], *, adjustment_type: str) -> dict[str, Any]:
    symbol = normalize_symbol(row.get("股票代码"))
    close_value = safe_float(row.get("收盘"))
    change_value = safe_float(row.get("涨跌额"))
    pre_close = close_value - change_value if close_value is not None and change_value is not None else None
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "date": str(row.get("日期", ""))[:10],
        "symbol": symbol,
        "open": safe_float(row.get("开盘")),
        "high": safe_float(row.get("最高")),
        "low": safe_float(row.get("最低")),
        "close": close_value,
        "volume": safe_int(row.get("成交量")),
        "amount": safe_float(row.get("成交额")),
        "turnover": safe_float(row.get("换手率")),
        "pre_close": pre_close,
        "change": change_value,
        "pct_change": safe_float(row.get("涨跌幅")),
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


def _unavailable(symbols: list[str], reason: str) -> dict[str, Any]:
    return {
        "provider": PROVIDER_NAME,
        "attempted_symbols": symbols,
        "succeeded_symbols": [],
        "failed_symbols": [{"symbol": normalize_symbol(symbol), "reason": reason} for symbol in symbols],
        "symbol_results": [_symbol_result(symbol, [], reason) for symbol in symbols],
        "rows": [],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "source_timestamp": utc_now(),
    }
