"""Coverage and quality audit for authorized historical data packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import (
    AUTHORIZED_GB_PACKAGE_ID,
    PACKAGE_SPECS,
    PROXY_PACKAGE_ID,
    REQUIRED_PACKAGE_IDS,
    TRADING_AUTHORIZATION_NOTICE,
    text_contains_secret,
)
from trading_core.global_briefing.signal_schema import read_signal_package
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


CRITICAL_PACKAGE_IDS = ["HIST-ETF-OHLCV-CN-HK-V1", "HIST-BENCHMARK-INDEX-CN-HK-V1"]


def audit_historical_data_quality(
    *,
    download_manifest_path: str | None = None,
    normalization_path: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    audit_id, created_at = timestamp_id("HIST-DATA-QUALITY-AUDIT")
    manifest_file = _resolve(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    normalization_file = _resolve(normalization_path, paths.data_dir / "system" / "historical_package_normalization_summary.json", paths)
    manifest = read_json(manifest_file, default={})
    normalization = read_json(normalization_file, default={})
    packages = manifest.get("packages", []) if isinstance(manifest, dict) else []
    by_id = {item.get("package_id"): item for item in packages}
    start = start_date or manifest.get("start_date") or "2018-01-01"
    end = end_date or manifest.get("end_date") or start
    package_results: dict[str, Any] = {}
    blocking: list[str] = []
    warnings: list[str] = []

    for package_id in REQUIRED_PACKAGE_IDS:
        item = by_id.get(package_id)
        if not item:
            blocking.append(f"{package_id}: missing package status")
            package_results[package_id] = {"passed": False, "coverage_ratio": 0.0, "warnings": ["missing package status"]}
            continue
        status = item.get("status")
        issues = []
        item_warnings = list(item.get("warnings", []))
        if status in {"downloaded", "loaded_from_local"}:
            if not item.get("sha256"):
                issues.append("checksum missing")
            if not item.get("provenance_path"):
                issues.append("provenance missing")
            path = Path(str(item.get("path", "")))
            if not path.exists():
                issues.append("package path missing")
            elif text_contains_secret(path.read_text(encoding="utf-8", errors="ignore")):
                issues.append("secret leakage detected")
            if not item.get("source"):
                issues.append("source missing")
            if not item.get("row_count"):
                issues.append("row_count missing")
        elif package_id in CRITICAL_PACKAGE_IDS:
            issues.append("critical package unavailable")
        elif package_id in {"HIST-FX-USDCNY-V1", "HIST-GLOBAL-RISK-VIX-V1"} and not _vix_or_fx_available(by_id):
            issues.append("critical VIX/FX package unavailable")
        elif package_id == AUTHORIZED_GB_PACKAGE_ID and status == "not_configured":
            item_warnings.append("authorized global-briefing signal package not configured; production package not validated")
        else:
            item_warnings.append(f"package status explained: {status}")
        if issues:
            blocking.extend(f"{package_id}: {issue}" for issue in issues)
        warnings.extend(f"{package_id}: {warning}" for warning in item_warnings)
        package_results[package_id] = {
            "passed": not issues,
            "status": status,
            "coverage_ratio": item.get("coverage_ratio", 0.0),
            "warnings": item_warnings,
            "issues": issues,
        }

    proxy = normalization.get("proxy_package", {}) if isinstance(normalization, dict) else {}
    proxy_path = proxy.get("normalized_path")
    if not proxy_path or not Path(str(proxy_path)).exists():
        blocking.append("proxy package missing")
    else:
        signal_package = read_signal_package(str(proxy_path), paths)
        if signal_package.blocking_reasons:
            blocking.extend(f"proxy package: {item}" for item in signal_package.blocking_reasons)
    if _artifact_secret_leak(paths):
        blocking.append("secret leakage detected in system artifacts")
    available = [item for item in packages if item.get("status") in {"downloaded", "loaded_from_local"}]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "coverage": {
            "start_date": start,
            "end_date": end,
            "required_packages": len(REQUIRED_PACKAGE_IDS),
            "available_packages": len(available),
            "critical_packages_available": _critical_available(by_id),
        },
        "packages": package_results,
        "proxy_package": {
            "path": proxy_path,
            "validated": bool(proxy.get("validated")),
            "coverage_ratio": _proxy_coverage_ratio(proxy),
        },
        "boundary": {
            "quality_audit_only": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "strategy_effectiveness_proven": False,
            "trading_authorization": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_quality_audit.json"
    md_path = paths.outputs_dir / "audit" / "HISTORICAL_DATA_QUALITY_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_quality_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _vix_or_fx_available(by_id: dict[str, dict[str, Any]]) -> bool:
    return any(by_id.get(package_id, {}).get("status") in {"downloaded", "loaded_from_local"} for package_id in ["HIST-FX-USDCNY-V1", "HIST-GLOBAL-RISK-VIX-V1"])


def _critical_available(by_id: dict[str, dict[str, Any]]) -> bool:
    return all(by_id.get(package_id, {}).get("status") in {"downloaded", "loaded_from_local"} for package_id in CRITICAL_PACKAGE_IDS) and _vix_or_fx_available(by_id)


def _proxy_coverage_ratio(proxy: dict[str, Any]) -> float:
    rows = int(proxy.get("row_count") or 0)
    return 1.0 if rows else 0.0


def _artifact_secret_leak(paths: ProjectPaths) -> bool:
    for path in (paths.data_dir / "system").glob("hist*_*.json"):
        if text_contains_secret(path.read_text(encoding="utf-8", errors="ignore")):
            return True
    return False


def build_quality_audit_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Data Quality Audit",
            "",
            "## Overall Verdict",
            f"- overall_passed={str(payload['overall_passed']).lower()}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Coverage",
            *[f"- {key}: {value}" for key, value in payload["coverage"].items()],
            "",
            "## Packages",
            *[f"- {package_id}: passed={str(item['passed']).lower()} status={item.get('status')} coverage_ratio={item.get('coverage_ratio')}" for package_id, item in payload["packages"].items()],
            "",
            "## Boundary",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "- quality audit only",
            "- no main ledger write",
            "- no run-daily call",
            "- not forward dry-run validation",
            "- not strategy effectiveness proof",
            "",
        ]
    )
