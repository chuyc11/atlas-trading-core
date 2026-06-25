"""Resolve authorized historical data package sources."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import (
    AUTHORIZED_GB_PACKAGE_ID,
    PACKAGE_SPECS,
    REQUIRED_PACKAGE_IDS,
    TRADING_AUTHORIZATION_NOTICE,
    is_forbidden_data_package,
    latest_end_date,
    local_authorized_candidates,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


SOURCE_TYPES = {
    "authorized_macro_cycle_proxy": "derived_authorized_proxy",
    "authorized_policy_uncertainty_proxy": "derived_authorized_proxy",
    "local_authorized_export": "authorized_local_file",
    "GB_AUTH_PACKAGE_PATH": "authorized_local_file",
    "epu_authorized_api": "authorized_api",
    "oecd_authorized_api": "authorized_api",
    "oecd_public_api": "public_api",
    "gb_authorized_api": "authorized_api",
    "fred": "public_api",
    "cboe_vix": "public_file_download",
    "oecd": "public_api",
    "nasdaq_data_link": "public_api",
    "policy_uncertainty_public_file": "public_file_download",
    "yahoo_query_or_equivalent_authorized_market_data_source": "public_api",
    "fixture": "fixture",
}
SOURCE_SECRET_ENV = {
    "epu_authorized_api": "EPU_AUTH_TOKEN",
    "gb_authorized_api": "GB_AUTH_TOKEN",
    "nasdaq_data_link": "NASDAQ_DATA_LINK_API_KEY",
    "oecd_authorized_api": "OECD_AUTH_TOKEN",
}


def resolve_historical_data_sources(
    *,
    packages: list[str] | None = None,
    start_date: str = "2018-01-01",
    end_date: str = "latest",
    preferred_source: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    package_ids = packages or list(REQUIRED_PACKAGE_IDS)
    resolved_end_date = latest_end_date(end_date)
    resolution_id, created_at = timestamp_id("HIST-DATA-SOURCE-RESOLUTION")
    rows = [_resolve_one(package_id, start_date, resolved_end_date, preferred_source, paths) for package_id in package_ids]
    blocking = [f"{row['package_id']}: {row['reason']}" for row in rows if not row["allowed"]]
    payload: dict[str, Any] = {
        "resolution_id": resolution_id,
        "created_at": created_at,
        "start_date": start_date,
        "end_date": resolved_end_date,
        "packages": rows,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "boundary": {
            "source_resolution_only": True,
            "historical_data_authorization": True,
            "trading_authorization": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "network_access": False,
            "broker_connected": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_source_resolution.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_DATA_SOURCE_RESOLUTION.md"
    write_json_markdown(json_path, payload, md_path, build_source_resolution_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve_one(package_id: str, start_date: str, end_date: str, preferred_source: str | None, paths: ProjectPaths) -> dict[str, Any]:
    if is_forbidden_data_package(package_id):
        return {
            "package_id": package_id,
            "selected_source": None,
            "source_type": None,
            "status": "rejected",
            "requires_secret": False,
            "secret_env": None,
            "fallback_sources": [],
            "allowed": False,
            "reason": "broker/account/order/trade/position/margin data source rejected",
        }
    spec = PACKAGE_SPECS.get(package_id)
    if spec is None:
        return {
            "package_id": package_id,
            "selected_source": None,
            "source_type": None,
            "status": "unknown_package",
            "requires_secret": False,
            "secret_env": None,
            "fallback_sources": [],
            "allowed": False,
            "reason": "unknown package",
        }
    if preferred_source:
        priority = [preferred_source, *[source for source in spec.source_priority if source != preferred_source]]
    else:
        priority = list(spec.source_priority)
    local_file = next((path for path in local_authorized_candidates(paths, package_id) if path.exists()), None)
    if local_file is not None:
        return _configured(package_id, "local_authorized_export", priority, f"local authorized export configured: {local_file}", local_file=str(local_file))
    if package_id == AUTHORIZED_GB_PACKAGE_ID:
        package_path = os.environ.get("GB_AUTH_PACKAGE_PATH")
        if package_path and Path(package_path).exists():
            return _configured(package_id, "GB_AUTH_PACKAGE_PATH", priority, "GB_AUTH_PACKAGE_PATH configured", local_file=package_path)
        if _gb_authorized_api_configured(paths):
            return _configured(package_id, "gb_authorized_api", priority, "authorized global-briefing API configured")
        return {
            "package_id": package_id,
            "selected_source": "gb_authorized_api",
            "source_type": SOURCE_TYPES["gb_authorized_api"],
            "status": "not_configured",
            "requires_secret": True,
            "secret_env": "GB_AUTH_TOKEN",
            "fallback_sources": [source for source in priority if source != "gb_authorized_api"],
            "allowed": True,
            "reason": "authorized global-briefing signal package source not configured",
        }
    priority_without_local = [source for source in priority if source != "local_authorized_export"]
    selected = next((source for source in priority_without_local if _source_configured(source, paths)), priority_without_local[0] if priority_without_local else priority[0])
    return _configured(package_id, selected, priority, f"{selected} source configured")


def _configured(package_id: str, source: str, priority: list[str], reason: str, *, local_file: str | None = None) -> dict[str, Any]:
    secret_env = SOURCE_SECRET_ENV.get(source)
    return {
        "package_id": package_id,
        "selected_source": source,
        "source_type": SOURCE_TYPES.get(source, "public_api"),
        "status": "configured",
        "requires_secret": bool(secret_env),
        "secret_env": secret_env,
        "fallback_sources": [item for item in priority if item != source],
        "allowed": True,
        "reason": reason,
        "local_file": local_file,
    }


def _gb_authorized_api_configured(paths: ProjectPaths) -> bool:
    config_paths = [
        paths.project_root / "config" / "global_briefing_authorized_source.json",
        paths.data_dir / "global_briefing" / "authorized" / "source_config.json",
    ]
    env_configured = bool(os.environ.get("GB_AUTH_BASE_URL") and (os.environ.get("GB_AUTH_TOKEN") or os.environ.get("GB_AUTH_EXPORT_ENDPOINT")))
    return env_configured or any(path.exists() for path in config_paths)


def _source_configured(source: str, paths: ProjectPaths) -> bool:
    if source == "epu_authorized_api":
        return bool(os.environ.get("EPU_AUTH_BASE_URL") and os.environ.get("EPU_AUTH_EXPORT_ENDPOINT"))
    if source == "oecd_authorized_api":
        return bool(os.environ.get("OECD_AUTH_BASE_URL") and os.environ.get("OECD_AUTH_EXPORT_ENDPOINT"))
    if source == "oecd_public_api":
        return bool(os.environ.get("OECD_PUBLIC_CLI_URL"))
    if source == "authorized_policy_uncertainty_proxy":
        package_root = paths.data_dir / "global_briefing" / "authorized" / "packages"
        return (package_root / "HIST-GLOBAL-RISK-VIX-V1.csv").exists() or (package_root / "HIST-FX-USDCNY-V1.csv").exists()
    if source == "authorized_macro_cycle_proxy":
        return (paths.data_dir / "market" / "historical" / "authorized" / "HIST-BENCHMARK-INDEX-CN-HK-V1.csv").exists()
    return source in {"fred", "cboe_vix", "fixture", "yahoo_query_or_equivalent_authorized_market_data_source"}


def build_source_resolution_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Data Source Resolution",
            "",
            "## Scope",
            TRADING_AUTHORIZATION_NOTICE,
            "This resolver does not connect to a broker and does not authorize trading.",
            "",
            "## Packages",
            *[
                f"- {row['package_id']}: source={row['selected_source']} type={row['source_type']} status={row['status']} allowed={str(row['allowed']).lower()}"
                for row in payload["packages"]
            ],
            "",
            "## Boundary",
            "- source resolution only",
            "- no historical download started",
            "- no broker/account/order/trade data",
            "- no main ledger write",
            "- no run-daily call",
            "",
        ]
    )
