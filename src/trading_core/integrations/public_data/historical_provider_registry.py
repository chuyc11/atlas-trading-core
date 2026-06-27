"""Historical public data providers for A-share panel backfill."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import normalize_date, normalize_symbol, read_frame, safe_float, safe_int, utc_now
from trading_core.storage.file_paths import ProjectPaths


PRICE_PROVIDER = "eastmoney_kline_public_http"
FINANCIAL_PROVIDER = "eastmoney_quarterly_performance_public_http"
DEFAULT_WORKERS = 32
DEFAULT_FINANCIAL_QUARTERS = 4
DEFAULT_FINANCIAL_PAGES_PER_QUARTER = 1


def history_provider_priority() -> list[str]:
    return [
        PRICE_PROVIDER,
        "akshare_provider",
        "baostock_provider",
        "tushare_provider",
        "local_file_provider",
        FINANCIAL_PROVIDER,
    ]


def select_history_symbols(paths: ProjectPaths, *, max_symbols: int | None = None) -> list[str]:
    master_path = paths.data_dir / "equity_universe" / "equity_master.parquet"
    master = read_frame(master_path)
    if master.empty:
        return []
    frame = master.copy()
    if "market" in frame.columns:
        frame = frame[frame["market"].fillna("A_SHARE").eq("A_SHARE")]
    if "is_active" in frame.columns:
        frame = frame.sort_values(["is_active", "symbol"], ascending=[False, True])
    else:
        frame = frame.sort_values("symbol")
    symbols = frame["symbol"].dropna().map(normalize_symbol).drop_duplicates().tolist()
    if max_symbols and max_symbols > 0:
        return symbols[:max_symbols]
    return symbols


def fetch_price_history(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    adjustment_type: str = "raw",
    max_workers: int = DEFAULT_WORKERS,
    min_rows_for_success: int = 1,
) -> dict[str, Any]:
    fqt = {"raw": "0", "forward_adjusted": "1", "backward_adjusted": "2"}.get(adjustment_type, "0")
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    symbol_results: list[dict[str, Any]] = []
    attempted = symbols
    started = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_symbol_kline, symbol, start_date, end_date, fqt, adjustment_type): symbol for symbol in symbols}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # pragma: no cover - thread-level safeguard
                reason = f"{type(exc).__name__}: {exc}"
                failed.append({"symbol": symbol, "reason": reason})
                symbol_results.append(_symbol_result(symbol, [], reason=reason, provider=PRICE_PROVIDER))
                continue
            rows.extend(result["rows"])
            symbol_results.append(_symbol_result(symbol, result["rows"], reason=result.get("reason", ""), provider=PRICE_PROVIDER))
            if len(result["rows"]) < min_rows_for_success:
                failed.append({"symbol": symbol, "reason": result.get("reason", "no historical rows")})
    succeeded_symbols = sorted({row["symbol"] for row in rows})
    return {
        "provider": PRICE_PROVIDER,
        "attempted_symbols": attempted,
        "succeeded_symbols": succeeded_symbols,
        "failed_symbols": failed,
        "symbol_results": symbol_results,
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "elapsed_seconds": round(time.time() - started, 3),
        "source_timestamp": utc_now(),
    }


def _symbol_result(symbol: str, rows: list[dict[str, Any]], *, reason: str, provider: str) -> dict[str, Any]:
    dates = [row.get("date") for row in rows if row.get("date")]
    return {
        "symbol": normalize_symbol(symbol),
        "provider": provider,
        "provider_attempted": True,
        "provider_succeeded": bool(rows),
        "provider_failed": not bool(rows),
        "row_count": len(rows),
        "first_date": min(dates) if dates else "",
        "last_date": max(dates) if dates else "",
        "failure_reason": reason if not rows else "",
        "last_attempted_at": utc_now(),
    }


def fetch_financial_history(
    *,
    start_date: str,
    end_date: str,
    quarters: list[str] | None = None,
    max_pages_per_quarter: int = DEFAULT_FINANCIAL_PAGES_PER_QUARTER,
) -> dict[str, Any]:
    selected_quarters = quarters or quarter_end_dates(start_date, end_date)[-DEFAULT_FINANCIAL_QUARTERS:]
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    started = time.time()
    for report_date in selected_quarters:
        try:
            rows.extend(_fetch_quarterly_performance(report_date, max_pages=max_pages_per_quarter))
        except Exception as exc:  # pragma: no cover - network failure is environment-specific
            failed.append({"report_date": report_date, "reason": f"{type(exc).__name__}: {exc}"})
    return {
        "provider": FINANCIAL_PROVIDER,
        "attempted_quarters": selected_quarters,
        "succeeded_quarters": sorted({row["report_date"] for row in rows}),
        "failed_quarters": failed,
        "coverage_note": f"limited to {max_pages_per_quarter} page(s) per quarter for daily executability",
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "elapsed_seconds": round(time.time() - started, 3),
        "source_timestamp": utc_now(),
    }


def quarter_end_dates(start_date: str, end_date: str) -> list[str]:
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    dates: list[str] = []
    for year in range(start.year, end.year + 1):
        for month, day in [(3, 31), (6, 30), (9, 30), (12, 31)]:
            value = pd.Timestamp(year=year, month=month, day=day)
            if start <= value <= end:
                dates.append(value.strftime("%Y-%m-%d"))
    return dates


def _fetch_symbol_kline(symbol: str, start_date: str, end_date: str, fqt: str, adjustment_type: str) -> dict[str, Any]:
    last_error = ""
    for attempt in range(3):
        try:
            return _fetch_symbol_kline_once(symbol, start_date, end_date, fqt, adjustment_type)
        except Exception as exc:  # pragma: no cover - network instability is environment-specific
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(0.4 * (attempt + 1))
    return {"symbol": symbol, "rows": [], "reason": last_error or "no historical rows"}


def _fetch_symbol_kline_once(symbol: str, start_date: str, end_date: str, fqt: str, adjustment_type: str) -> dict[str, Any]:
    code, suffix = symbol.split(".")
    secid = f"{'1' if suffix == 'SH' else '0'}.{code}"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",
        "fqt": fqt,
        "beg": start_date.replace("-", ""),
        "end": end_date.replace("-", ""),
    }
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 trading-core historical-backfill/0.7.1.1", "Referer": "https://quote.eastmoney.com/"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data") or {}
    rows = [_parse_kline(symbol, line, adjustment_type=adjustment_type, provider=PRICE_PROVIDER) for line in data.get("klines") or []]
    return {"symbol": symbol, "rows": [row for row in rows if row], "reason": "" if rows else "no historical rows"}


def _parse_kline(symbol: str, line: str, *, adjustment_type: str, provider: str) -> dict[str, Any]:
    parts = line.split(",")
    if len(parts) < 11:
        return {}
    day, open_, close, high, low, volume, amount, _amplitude, pct_change, change, turnover = parts[:11]
    close_value = safe_float(close)
    change_value = safe_float(change)
    pre_close = close_value - change_value if close_value is not None and change_value is not None else None
    return {
        "date": normalize_date(day),
        "symbol": normalize_symbol(symbol),
        "open": safe_float(open_),
        "high": safe_float(high),
        "low": safe_float(low),
        "close": close_value,
        "volume": safe_int(volume),
        "amount": safe_float(amount),
        "turnover": safe_float(turnover),
        "pre_close": pre_close,
        "change": change_value,
        "pct_change": safe_float(pct_change),
        "adjustment_type": adjustment_type,
        "source": provider,
        "source_timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "provider": provider,
        "ingested_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


def _fetch_quarterly_performance(report_date: str, *, max_pages: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    report = pd.Timestamp(report_date).strftime("%Y-%m-%d")
    while True:
        data = _fetch_financial_page(report, page)
        result = data.get("result") or {}
        page_rows = result.get("data") or []
        rows.extend(_parse_financial_row(item) for item in page_rows)
        pages = int(result.get("pages") or page)
        if page >= pages or page >= max_pages:
            break
        page += 1
        time.sleep(0.1)
    return [row for row in rows if row.get("symbol")]


def _fetch_financial_page(report_date: str, page: int) -> dict[str, Any]:
    filter_text = f'(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORTDATE=\'{report_date}\')'
    params = {
        "sortColumns": "UPDATE_DATE,SECURITY_CODE",
        "sortTypes": "-1,-1",
        "pageSize": "500",
        "pageNumber": str(page),
        "reportName": "RPT_LICO_FN_CPD",
        "columns": "ALL",
        "filter": filter_text,
    }
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 trading-core financial-history/0.7.1.1", "Referer": "https://data.eastmoney.com/"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_financial_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_date": normalize_date(item.get("REPORTDATE")),
        "ann_date": normalize_date(item.get("NOTICE_DATE")),
        "symbol": normalize_symbol(item.get("SECUCODE") or item.get("SECURITY_CODE")),
        "revenue": safe_float(item.get("TOTAL_OPERATE_INCOME")),
        "net_profit": safe_float(item.get("PARENT_NETPROFIT")),
        "roe": safe_float(item.get("WEIGHTAVG_ROE")),
        "gross_margin": safe_float(item.get("XSMLL")),
        "net_margin": None,
        "operating_cash_flow": safe_float(item.get("MGJYXJJE")),
        "debt_to_asset": None,
        "eps": safe_float(item.get("BASIC_EPS")),
        "bps": safe_float(item.get("BPS")),
        "source": FINANCIAL_PROVIDER,
        "source_timestamp": utc_now(),
        "provider": FINANCIAL_PROVIDER,
        "ingested_at": utc_now(),
    }
