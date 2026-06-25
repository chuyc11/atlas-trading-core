"""Repair the policy uncertainty / EPU historical package."""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Callable
from urllib.parse import urlencode

from trading_core.global_briefing.historical_data_packages import read_csv_rows
from trading_core.storage.file_paths import ProjectPaths


HttpGet = Callable[[str, int], bytes]
TARGET_SERIES = ["global_epu", "china_epu", "us_epu", "europe_epu"]
DEFAULT_FRED_SERIES = {
    "USEPUINDXD": "us_epu",
}


def build_epu_rows(
    *,
    paths: ProjectPaths,
    start_date: str,
    end_date: str,
    timeout: int,
    retries: int,
    http_get: HttpGet,
) -> tuple[list[dict[str, Any]], str, str, list[str], dict[str, Any]]:
    warnings: list[str] = []
    rows = _authorized_api_rows(start_date, end_date, timeout, retries, http_get, warnings)
    source = "epu_authorized_api"
    if not rows:
        rows = _fred_epu_rows(start_date, end_date, min(timeout, 5), retries, http_get, warnings)
        source = "fred"
    if not rows:
        rows = _policy_uncertainty_proxy_rows(paths, start_date, end_date, warnings)
        source = "authorized_policy_uncertainty_proxy"
    elif not ({"global_epu", "china_epu"} & {str(row.get("series_id")) for row in rows}):
        proxy_rows = _policy_uncertainty_proxy_rows(paths, start_date, end_date, warnings)
        if proxy_rows:
            rows.extend(proxy_rows)
            source = "authorized_policy_uncertainty_proxy"
    if not rows:
        return [], source, "failed_soft", warnings or ["no EPU source available"], {"policy_uncertainty_proxy": False}
    available = {str(row.get("series_id")) for row in rows}
    has_anchor = bool({"global_epu", "china_epu"} & available)
    complete = all(series_id in available for series_id in TARGET_SERIES)
    status = "downloaded" if complete else "partial_downloaded"
    if not has_anchor:
        status = "failed_soft"
        warnings.append("EPU package lacks Global or China anchor series")
    metadata = {
        "required_series": TARGET_SERIES,
        "available_series": sorted(available),
        "missing_series": [series_id for series_id in TARGET_SERIES if series_id not in available],
        "epu_partial": not complete,
        "policy_uncertainty_proxy": source == "authorized_policy_uncertainty_proxy",
        "official_epu": source in {"epu_authorized_api", "fred"},
    }
    if metadata["policy_uncertainty_proxy"]:
        warnings.append("EPU official source unavailable; built policy uncertainty proxy from authorized historical risk packages.")
    return rows, source, status, warnings, metadata


def _authorized_api_rows(start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet, warnings: list[str]) -> list[dict[str, Any]]:
    base = os.environ.get("EPU_AUTH_BASE_URL")
    endpoint = os.environ.get("EPU_AUTH_EXPORT_ENDPOINT")
    if not base or not endpoint:
        return []
    url = base.rstrip("/") + "/" + endpoint.lstrip("/") + "?" + urlencode({"start_date": start_date, "end_date": end_date})
    try:
        return _parse_epu_payload(_http_get_retry(url, timeout, retries, http_get), source="epu_authorized_api")
    except Exception as exc:  # noqa: BLE001 - fail-soft source fallback.
        warnings.append(f"EPU authorized API unavailable: {exc}")
        return []


def _fred_epu_rows(start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet, warnings: list[str]) -> list[dict[str, Any]]:
    mapping = _fred_series_mapping()
    rows: list[dict[str, Any]] = []
    for fred_id, series_id in mapping.items():
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id": fred_id, "observation_start": start_date, "observation_end": end_date})
        try:
            text = _http_get_retry(url, timeout, retries, http_get)
            rows.extend(_parse_fred_csv(text, fred_id=fred_id, series_id=series_id))
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{fred_id}: {exc}")
    return rows


def _fred_series_mapping() -> dict[str, str]:
    raw = os.environ.get("FRED_EPU_SERIES_IDS")
    if not raw:
        return dict(DEFAULT_FRED_SERIES)
    mapping: dict[str, str] = {}
    for item in raw.split(","):
        if ":" in item:
            series_id, fred_id = [part.strip() for part in item.split(":", 1)]
            if series_id and fred_id:
                mapping[fred_id] = series_id
        elif item.strip():
            mapping[item.strip()] = item.strip().lower()
    return mapping or dict(DEFAULT_FRED_SERIES)


def _parse_epu_payload(payload: bytes, *, source: str) -> list[dict[str, Any]]:
    text = payload.decode("utf-8-sig")
    if text.lstrip().startswith("["):
        rows = json.loads(text)
        return [_normalize_epu_row(row, source=source) for row in rows if isinstance(row, dict)]
    return _parse_epu_csv(text, source=source)


def _parse_epu_csv(text: str, *, source: str) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, Any]] = []
    for row in csv.DictReader(text.splitlines()):
        day = str(row.get("date") or row.get("observation_date") or row.get("DATE") or "").strip()
        if not day:
            continue
        if row.get("series_id") and row.get("value") not in {None, "", "."}:
            rows.append({**row, "date": day, "series_id": str(row["series_id"]), "value": row["value"], "frequency": row.get("frequency") or "daily", "source": source, "downloaded_at": row.get("downloaded_at") or now, "generated_at": row.get("generated_at") or f"{day}T23:59:00Z"})
            continue
        for series_id in TARGET_SERIES:
            if row.get(series_id) not in {None, "", "."}:
                rows.append({"date": day, "series_id": series_id, "value": row[series_id], "frequency": row.get("frequency") or "daily", "source": source, "downloaded_at": now, "generated_at": row.get("generated_at") or f"{day}T23:59:00Z"})
    return rows


def _normalize_epu_row(row: dict[str, Any], *, source: str) -> dict[str, Any]:
    day = str(row.get("date") or row.get("observation_date") or row.get("as_of_date") or "")
    return {
        "date": day,
        "series_id": str(row.get("series_id") or row.get("name") or "global_epu"),
        "value": row.get("value"),
        "frequency": row.get("frequency") or "daily",
        "source": row.get("source") or source,
        "downloaded_at": row.get("downloaded_at") or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "generated_at": row.get("generated_at") or f"{day}T23:59:00Z",
    }


def _parse_fred_csv(payload: bytes, *, fred_id: str, series_id: str) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    rows = []
    for row in csv.DictReader(payload.decode("utf-8-sig").splitlines()):
        day = row.get("observation_date") or row.get("DATE") or row.get("date")
        value = row.get(fred_id) or row.get("VALUE") or row.get("value")
        if day and value not in {None, "", "."}:
            rows.append({"date": day, "series_id": series_id, "value": value, "frequency": "daily", "source": "fred", "downloaded_at": now, "generated_at": f"{day}T23:59:00Z"})
    return rows


def _policy_uncertainty_proxy_rows(paths: ProjectPaths, start_date: str, end_date: str, warnings: list[str]) -> list[dict[str, Any]]:
    vix = _series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-GLOBAL-RISK-VIX-V1.csv", "vix_close")
    fx = _series(paths.data_dir / "global_briefing" / "authorized" / "packages" / "HIST-FX-USDCNY-V1.csv", "usd_cny")
    if not vix and not fx:
        warnings.append("policy uncertainty proxy unavailable because VIX and FX packages are missing")
        return []
    dates = sorted({day for day in set(vix) | set(fx) if start_date <= day <= end_date})
    rows: list[dict[str, Any]] = []
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    for day in dates:
        vix_value = vix.get(day)
        fx_value = fx.get(day)
        stress = _clip(((vix_value or 15.0) - 15.0) / 25.0) if vix_value is not None else 0.0
        fx_pressure = _clip(((fx_value or 6.5) - 6.5) / 1.2) if fx_value is not None else 0.0
        global_value = round(100.0 + 300.0 * _clip((stress * 0.7) + (fx_pressure * 0.3)), 6)
        china_value = round(100.0 + 300.0 * _clip((fx_pressure * 0.6) + (stress * 0.4)), 6)
        for series_id, value in [("global_epu", global_value), ("china_epu", china_value)]:
            rows.append({"date": day, "series_id": series_id, "value": value, "frequency": "daily", "source": "authorized_policy_uncertainty_proxy", "downloaded_at": now, "generated_at": f"{day}T23:59:00Z"})
    return rows


def _series(path, column: str) -> dict[str, float]:
    output = {}
    for row in read_csv_rows(path):
        try:
            output[str(row.get("date"))] = float(row[column])
        except (KeyError, TypeError, ValueError):
            continue
    return output


def _http_get_retry(url: str, timeout: int, retries: int, http_get: HttpGet) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            return http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(min(1.0, 0.2 * attempt))
    raise RuntimeError(last_error) from last_error


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
