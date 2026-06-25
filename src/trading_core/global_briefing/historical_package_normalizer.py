"""Normalize authorized historical packages and build the proxy package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.global_briefing.full_historical_proxy_builder import build_full_historical_proxy_package
from trading_core.global_briefing.historical_data_packages import (
    AUTHORIZED_GB_PACKAGE_ID,
    PACKAGE_SPECS,
    PROXY_PACKAGE_ID,
    TRADING_AUTHORIZATION_NOTICE,
    latest_end_date,
)
from trading_core.global_briefing.real_package_normalizer import normalize_global_briefing_package
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


def normalize_historical_data_packages(
    *,
    download_manifest_path: str | None = None,
    start_date: str = "2018-01-01",
    end_date: str = "latest",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    resolved_end_date = latest_end_date(end_date)
    normalization_id, created_at = timestamp_id("HIST-PACKAGE-NORMALIZATION")
    manifest_file = _resolve(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    manifest = read_json(manifest_file, default={})
    packages = manifest.get("packages", []) if isinstance(manifest, dict) else []
    package_paths = {item["package_id"]: item.get("path") for item in packages if item.get("path")}
    normalized: dict[str, Any] = {}
    warnings: list[str] = []
    for item in packages:
        package_id = item.get("package_id")
        status = item.get("status")
        if status in {"downloaded", "partial_downloaded", "loaded_from_local"}:
            normalized[package_id] = {"status": "normalized", "path": item.get("path"), "row_count": item.get("row_count")}
        elif package_id == AUTHORIZED_GB_PACKAGE_ID and status == "not_configured":
            normalized[package_id] = {"status": "not_configured", "production_global_briefing_package_validated": False}
        else:
            normalized[package_id] = {"status": status or "missing", "warnings": item.get("warnings", [])}
            warnings.extend(item.get("warnings", []))

    auth_gb = next((item for item in packages if item.get("package_id") == AUTHORIZED_GB_PACKAGE_ID and item.get("status") in {"downloaded", "partial_downloaded", "loaded_from_local"}), None)
    auth_normalized = None
    if auth_gb and auth_gb.get("path"):
        auth_result = normalize_global_briefing_package(
            str(auth_gb["path"]),
            package_id=AUTHORIZED_GB_PACKAGE_ID,
            source="authorized_global_briefing",
            version="v1",
            strict=False,
            paths=paths,
        )
        auth_normalized = auth_result["output"]
        normalized[AUTHORIZED_GB_PACKAGE_ID] = {"status": "normalized", "path": auth_normalized, "overall_passed": auth_result["overall_passed"]}

    proxy = build_full_historical_proxy_package(package_paths=package_paths, start_date=start_date, end_date=resolved_end_date, paths=paths)
    normalized[PROXY_PACKAGE_ID] = {"status": "normalized", "path": proxy["normalized_path"], "validated": proxy["validated"], "row_count": proxy["row_count"]}
    warnings.extend(proxy["warnings"])
    payload: dict[str, Any] = {
        "normalization_id": normalization_id,
        "created_at": created_at,
        "download_manifest": str(manifest_file),
        "start_date": start_date,
        "end_date": resolved_end_date,
        "packages": normalized,
        "proxy_package": proxy,
        "authorized_global_briefing_normalized_path": auth_normalized,
        "warnings": warnings,
        "boundary": {
            "normalization_only": True,
            "proxy_signals_not_internal_global_briefing": True,
            "trading_authorization": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_package_normalization_summary.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_PACKAGE_NORMALIZATION_REPORT.md"
    write_json_markdown(json_path, payload, md_path, build_normalization_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def build_normalization_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Package Normalization Report",
            "",
            "## Scope",
            TRADING_AUTHORIZATION_NOTICE,
            "This report normalizes historical research data and builds a proxy signal package.",
            "",
            "## Packages",
            *[f"- {package_id}: status={item.get('status')} path={item.get('path')}" for package_id, item in payload["packages"].items() if package_id in PACKAGE_SPECS or package_id == PROXY_PACKAGE_ID],
            "",
            "## Proxy Package",
            f"- package_path={payload['proxy_package']['package_path']}",
            f"- normalized_path={payload['proxy_package']['normalized_path']}",
            f"- validated={str(payload['proxy_package']['validated']).lower()}",
            "",
            "## Boundary",
            "- normalization only",
            "- proxy package is not internal global-briefing signal",
            "- no main ledger write",
            "- no run-daily call",
            "- not forward dry-run validation",
            "",
        ]
    )
