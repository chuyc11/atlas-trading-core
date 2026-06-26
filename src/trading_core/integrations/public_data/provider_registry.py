"""Provider registry and fallback orchestration for A-share data ingestion."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import read_json, snapshot_cache_path, utc_now, write_json
from trading_core.integrations.public_data.akshare_provider import probe_akshare
from trading_core.integrations.public_data.baostock_provider import probe_baostock
from trading_core.integrations.public_data.local_file_provider import load_local_snapshot
from trading_core.integrations.public_data.qstock_reference_adapter import fetch_public_snapshot
from trading_core.integrations.public_data.tushare_provider import probe_tushare
from trading_core.storage.file_paths import ProjectPaths


PROVIDER_PRIORITY = [
    "qstock_reference_public_http",
    "akshare_provider",
    "tushare_provider",
    "baostock_provider",
    "local_file_provider",
    "future_ifind_quantapi_reserved",
]


def load_or_fetch_snapshot(paths: ProjectPaths, *, allow_network: bool = True, force_refresh: bool = False) -> dict[str, Any]:
    cache_path = snapshot_cache_path(paths)
    cached = read_json(cache_path)
    if cached.get("rows") and not force_refresh:
        return cached

    attempts: list[dict[str, Any]] = []
    if allow_network:
        attempts.append(fetch_public_snapshot())
    attempts.extend([probe_akshare(), probe_tushare(), probe_baostock()])
    local = load_local_snapshot(paths)
    attempts.append(local)
    selected = next((attempt for attempt in attempts if attempt.get("succeeded") and attempt.get("rows")), None)
    if selected is None:
        payload = {
            "snapshot_id": "A-SHARE-PUBLIC-DATA-SNAPSHOT",
            "provider": "",
            "source_timestamp": utc_now(),
            "rows": [],
            "attempts": attempts,
            "external_api_called": any(item.get("external_api_called") for item in attempts),
            "real_time_market_data_downloaded": False,
            "blocking_reasons": ["all_public_data_providers_unavailable"],
        }
        write_json(cache_path, payload)
        return payload
    payload = {
        "snapshot_id": "A-SHARE-PUBLIC-DATA-SNAPSHOT",
        "provider": selected["provider"],
        "source_timestamp": utc_now(),
        "rows": selected["rows"],
        "attempts": attempts,
        "external_api_called": bool(selected.get("external_api_called")),
        "real_time_market_data_downloaded": False,
        "provider_reason": selected.get("reason", ""),
        "blocking_reasons": [],
    }
    if selected.get("source_path"):
        payload["source_path"] = selected["source_path"]
    if selected.get("raw_total") is not None:
        payload["raw_total"] = selected["raw_total"]
    if selected.get("raw_coverage_ratio") is not None:
        payload["raw_coverage_ratio"] = selected["raw_coverage_ratio"]
    write_json(cache_path, payload)
    return payload


def provider_status(snapshot: dict[str, Any]) -> dict[str, Any]:
    attempts = snapshot.get("attempts", [])
    return {
        "provider_priority": PROVIDER_PRIORITY,
        "providers_attempted": [item.get("provider") for item in attempts],
        "providers_succeeded": [item.get("provider") for item in attempts if item.get("succeeded")],
        "providers_failed": [
            {"provider": item.get("provider"), "reason": item.get("reason", "")}
            for item in attempts
            if not item.get("succeeded")
        ],
    }
