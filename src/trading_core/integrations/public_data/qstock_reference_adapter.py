"""qstock-style public HTTP adapter for A-share snapshot data.

This module does not import or vendor qstock. It uses a small public HTTP
adapter inspired by the qstock-style public data priority from v0.7.0.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Any


EASTMONEY_CLIST_URLS = [
    "https://push2delay.eastmoney.com/api/qt/clist/get",
    "https://push2.eastmoney.com/api/qt/clist/get",
]
EASTMONEY_SEGMENTS = [
    ("SSE", "m:1+t:2,m:1+t:23"),
    ("SZSE", "m:0+t:6,m:0+t:80"),
    ("BSE", "m:0+t:81+s:2048"),
]
PAGE_SIZE = 100
MAX_RETRIES_PER_PAGE = 6


def fetch_public_snapshot(timeout: int = 20) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    raw_total = 0
    reasons: list[str] = []
    try:
        for segment, fs in EASTMONEY_SEGMENTS:
            segment_rows, segment_total, segment_reason = _fetch_segment(segment=segment, fs=fs, timeout=timeout)
            rows.extend(segment_rows)
            raw_total += segment_total
            if segment_reason:
                reasons.append(segment_reason)
    except Exception as exc:  # pragma: no cover - network failure is environment-specific
        if rows:
            reasons.append(f"partial_fetch_after_{len(rows)}_rows_due_to_{type(exc).__name__}: {exc}")
        else:
            return {
                "provider": "qstock_reference_public_http",
                "succeeded": False,
                "rows": rows,
                "external_api_called": True,
                "real_time_market_data_downloaded": False,
                "reason": f"{type(exc).__name__}: {exc}",
                "raw_total": raw_total,
            }
    rows = _dedupe_rows(rows)
    if raw_total and len(rows) < int(raw_total) and not reasons:
        reasons.append(f"partial_fetch_limited_to_{len(rows)}_of_{raw_total}_rows")
    reason = "; ".join(reasons)
    if reason:
        return {
            "provider": "qstock_reference_public_http",
            "succeeded": bool(rows),
            "rows": rows,
            "external_api_called": True,
            "real_time_market_data_downloaded": False,
            "reason": reason,
            "raw_total": raw_total,
            "raw_coverage_ratio": round(len(rows) / raw_total, 6) if raw_total else None,
        }
    return {
        "provider": "qstock_reference_public_http",
        "succeeded": bool(rows),
        "rows": rows,
        "external_api_called": True,
        "real_time_market_data_downloaded": False,
        "reason": "" if rows else "empty response",
        "raw_total": raw_total,
        "raw_coverage_ratio": round(len(rows) / raw_total, 6) if raw_total else None,
    }


def _fetch_segment(*, segment: str, fs: str, timeout: int) -> tuple[list[dict[str, Any]], int, str]:
    rows: list[dict[str, Any]] = []
    raw_total = 0
    page = 1
    while True:
        try:
            payload = _fetch_page(page=page, page_size=PAGE_SIZE, fs=fs, timeout=min(timeout, 12))
        except Exception as exc:  # pragma: no cover - network instability is environment-specific
            return rows, raw_total, f"{segment}_partial_fetch_after_{len(rows)}_rows_due_to_{type(exc).__name__}: {exc}"
        data = payload.get("data") or {}
        raw_total = int(data.get("total") or raw_total or 0)
        page_rows = data.get("diff") or []
        for row in page_rows:
            row["_segment"] = segment
        rows.extend(page_rows)
        if not page_rows or (raw_total and len(rows) >= raw_total):
            break
        page += 1
        time.sleep(0.2)
    return rows, raw_total, ""


def _fetch_page(*, page: int, page_size: int, fs: str, timeout: int) -> dict[str, Any]:
    query = urllib.parse.urlencode(
        {
            "pn": str(page),
            "pz": str(page_size),
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": fs,
            "fields": "f12,f13,f14,f2,f3,f4,f5,f6,f8,f9,f15,f16,f17,f18,f20,f21,f23,f26",
        }
    )
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES_PER_PAGE):
        for url in EASTMONEY_CLIST_URLS:
            request = urllib.request.Request(
                f"{url}?{query}",
                headers={"User-Agent": "Mozilla/5.0 trading-core data-ingestion/0.7.1", "Referer": "https://quote.eastmoney.com/"},
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as exc:  # pragma: no cover - host fallback is environment-specific
                last_error = exc
        time.sleep(0.7 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("no eastmoney clist hosts configured")


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in rows:
        code = str(row.get("f12") or "")
        segment = str(row.get("_segment") or "")
        key = f"{segment}:{code}"
        if not code or key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped
