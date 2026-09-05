"""Repair the OECD CLI / macro-cycle historical package."""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import UTC, datetime
from typing import Any
from collections.abc import Callable
from urllib.parse import urlencode

from trading_core.global_briefing.macro_cycle_proxy_builder import REGIONS, build_macro_cycle_proxy_rows
from trading_core.storage.file_paths import ProjectPaths


HttpGet = Callable[[str, int], bytes]


def build_oecd_cli_rows(
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
    source = "oecd_authorized_api"
    if not rows:
        rows = _public_api_rows(start_date, end_date, timeout, retries, http_get, warnings)
        source = "oecd_public_api"
    metadata = {"official_oecd_cli": True, "macro_cycle_proxy": False, "not_official_oecd_cli": False, "required_regions": REGIONS}
    if not rows:
        rows, proxy_warnings = build_macro_cycle_proxy_rows(paths, start_date, end_date)
        warnings.extend(proxy_warnings)
        source = "authorized_macro_cycle_proxy"
        metadata.update({"official_oecd_cli": False, "macro_cycle_proxy": True, "not_official_oecd_cli": True})
    if not rows:
        return [], source, "failed_soft", warnings or ["OECD CLI and macro-cycle proxy unavailable"], metadata
    regions = sorted({str(row.get("region")) for row in rows})
    metadata["available_regions"] = regions
    metadata["missing_regions"] = [region for region in REGIONS if region not in regions]
    status = "downloaded" if not metadata["missing_regions"] else "partial_downloaded"
    return rows, source, status, warnings, metadata


def _authorized_api_rows(start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet, warnings: list[str]) -> list[dict[str, Any]]:
    base = os.environ.get("OECD_AUTH_BASE_URL")
    endpoint = os.environ.get("OECD_AUTH_EXPORT_ENDPOINT")
    if not base or not endpoint:
        return []
    url = base.rstrip("/") + "/" + endpoint.lstrip("/") + "?" + urlencode({"start_date": start_date, "end_date": end_date})
    try:
        return _parse_rows(_http_get_retry(url, timeout, retries, http_get), source="oecd_authorized_api")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"OECD authorized API unavailable: {exc}")
        return []


def _public_api_rows(start_date: str, end_date: str, timeout: int, retries: int, http_get: HttpGet, warnings: list[str]) -> list[dict[str, Any]]:
    url = os.environ.get("OECD_PUBLIC_CLI_URL")
    if not url:
        return []
    separator = "&" if "?" in url else "?"
    full_url = url + separator + urlencode({"start_date": start_date, "end_date": end_date})
    try:
        return _parse_rows(_http_get_retry(full_url, timeout, retries, http_get), source="oecd_public_api")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"OECD public API unavailable: {exc}")
        return []


def _parse_rows(payload: bytes, *, source: str) -> list[dict[str, Any]]:
    text = payload.decode("utf-8-sig")
    if text.lstrip().startswith("["):
        return [_normalize_row(row, source=source) for row in json.loads(text) if isinstance(row, dict)]
    return [_normalize_row(row, source=source) for row in csv.DictReader(text.splitlines())]


def _normalize_row(row: dict[str, Any], *, source: str) -> dict[str, Any]:
    day = str(row.get("date") or row.get("TIME_PERIOD") or row.get("observation_date") or "")
    region = str(row.get("region") or row.get("LOCATION") or row.get("country") or "").upper()
    value = row.get("cli_value") or row.get("value") or row.get("OBS_VALUE")
    return {
        "date": day,
        "region": region,
        "cli_value": value,
        "macro_cycle_pressure": row.get("macro_cycle_pressure") or "",
        "source": row.get("source") or source,
        "official_oecd_cli": str(row.get("official_oecd_cli", "true")).lower(),
        "macro_cycle_proxy": str(row.get("macro_cycle_proxy", "false")).lower(),
        "downloaded_at": row.get("downloaded_at") or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


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
