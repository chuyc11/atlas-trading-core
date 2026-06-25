"""Day-0 data freeze manifest for future forward dry-run readiness."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.forward_dry_run.common import (
    AVAILABLE_STATUSES,
    DAY0_NOTICE,
    OPTIONAL_AUTH_GB_PACKAGE,
    PROXY_PACKAGE_ID,
    RELEASE_CANDIDATE,
    REQUIRED_FREEZE_PACKAGES,
    TRADING_AUTHORIZATION_NOTICE,
    file_record,
    package_by_id,
    paths_or_default,
    proxy_package_default,
    read_dict,
    rel,
    resolve_path,
    standard_boundary,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_day0_data_freeze(
    *,
    download_manifest_path: str | None = None,
    quality_audit_path: str | None = None,
    gap_closure_audit_path: str | None = None,
    proxy_package_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    freeze_id, created_at = timestamp_id("DAY0-DATA-FREEZE")
    download_path = resolve_path(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    quality_path = resolve_path(quality_audit_path, paths.data_dir / "system" / "historical_data_quality_audit.json", paths)
    gap_audit_path = resolve_path(gap_closure_audit_path, paths.data_dir / "system" / "historical_data_gap_closure_audit.json", paths)
    proxy_path = resolve_path(proxy_package_path, proxy_package_default(paths), paths)
    download = read_dict(download_path)
    quality = read_dict(quality_path)
    gap_audit = read_dict(gap_audit_path)
    packages = package_by_id(download)
    frozen: dict[str, Any] = {}
    blocking: list[str] = []
    for package_id in REQUIRED_FREEZE_PACKAGES:
        item = packages.get(package_id, {})
        accepted, limitations = _acceptance(package_id, item)
        if not item:
            blocking.append(f"{package_id} missing from download manifest")
        elif item.get("status") not in AVAILABLE_STATUSES:
            blocking.append(f"{package_id} status not accepted: {item.get('status')}")
        if not item.get("sha256") and item.get("status") in AVAILABLE_STATUSES:
            blocking.append(f"{package_id} missing checksum")
        frozen[package_id] = {
            "status": item.get("status"),
            "source": item.get("source"),
            "path": rel(item.get("path"), paths),
            "sha256": item.get("sha256"),
            "provenance_path": rel(item.get("provenance_path"), paths),
            "coverage_ratio": item.get("coverage_ratio"),
            "row_count": item.get("row_count"),
            "accepted_for_day0": accepted,
            "accepted_limitations": limitations,
            "warnings": item.get("warnings", []),
        }
    auth_item = packages.get(OPTIONAL_AUTH_GB_PACKAGE, {})
    frozen[OPTIONAL_AUTH_GB_PACKAGE] = {
        "status": auth_item.get("status", "not_configured"),
        "source": auth_item.get("source", "gb_authorized_api"),
        "path": rel(auth_item.get("path"), paths),
        "accepted_for_day0": True,
        "reason": "internal global-briefing historical package not required for proxy-based day-0 readiness",
        "production_internal_global_briefing_validated": False,
    }
    proxy = {
        **file_record(proxy_path, paths),
        "coverage_ratio": _proxy_coverage(quality),
        "accepted_for_day0": proxy_path.exists(),
        "is_internal_global_briefing_signal": False,
    }
    if not proxy_path.exists():
        blocking.append("proxy package missing")
    if gap_audit.get("overall_passed") is not True:
        blocking.append("gap closure audit not passed")
    payload: dict[str, Any] = {
        "freeze_id": freeze_id,
        "release_candidate": RELEASE_CANDIDATE,
        "created_at": created_at,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "forward_dry_run_started": False,
        "run_daily_called": False,
        "download_manifest": rel(download_path, paths),
        "quality_audit": rel(quality_path, paths),
        "gap_closure_audit": rel(gap_audit_path, paths),
        "packages": frozen,
        "proxy_package": proxy,
        "boundary": standard_boundary("data_freeze_only"),
    }
    json_path = paths.data_dir / "system" / "day0_data_freeze_manifest.json"
    md_path = paths.outputs_dir / "system" / "DAY0_DATA_FREEZE_MANIFEST.md"
    write_json_markdown(json_path, payload, md_path, build_data_freeze_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _acceptance(package_id: str, item: dict[str, Any]) -> tuple[bool, list[str]]:
    status = item.get("status")
    limitations: list[str] = []
    if package_id == "HIST-POLICY-UNCERTAINTY-EPU-V1":
        if item.get("epu_partial") or status == "partial_downloaded":
            limitations.append("missing us_epu/europe_epu")
        if item.get("policy_uncertainty_proxy") or item.get("source") == "authorized_policy_uncertainty_proxy":
            limitations.append("policy uncertainty proxy only")
    if package_id == "HIST-OECD-CLI-MACRO-CYCLE-V1" and (item.get("macro_cycle_proxy") or item.get("source") == "authorized_macro_cycle_proxy"):
        limitations.extend(["not official OECD CLI", "authorized macro-cycle proxy"])
    return status in AVAILABLE_STATUSES, limitations


def _proxy_coverage(quality: dict[str, Any]) -> float | None:
    for key in ["proxy_package_coverage_ratio", "coverage_ratio"]:
        if key in quality:
            return quality.get(key)
    return quality.get("proxy_package", {}).get("coverage_ratio") if isinstance(quality.get("proxy_package"), dict) else None


def build_data_freeze_markdown(payload: dict[str, Any]) -> str:
    limitation_lines = []
    for package_id, item in payload["packages"].items():
        for limitation in item.get("accepted_limitations", []):
            limitation_lines.append(f"- {package_id}: {limitation}")
    return "\n".join(
        [
            "# Day-0 Data Freeze Manifest",
            "",
            "## Scope",
            "This freezes day-0 research data inputs for a future 30 trading-day forward dry-run.",
            DAY0_NOTICE,
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Frozen Packages",
            *[f"- {package_id}: status={item.get('status')} accepted_for_day0={str(item.get('accepted_for_day0')).lower()} path={item.get('path')}" for package_id, item in payload["packages"].items()],
            "",
            "## Accepted Limitations",
            *(limitation_lines or ["- none"]),
            "",
            "## Explicit Non-Claims",
            "- This does not validate forward dry-run.",
            "- This does not prove strategy effectiveness.",
            "- This is not live trading readiness.",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "",
            "## Boundary",
            "- data freeze only",
            "- run-daily not called",
            "- main ledger not written",
            "- forward dry-run not started",
            "",
        ]
    )
