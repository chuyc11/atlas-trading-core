"""Historical data acquisition summary report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import AUTHORIZED_GB_PACKAGE_ID, PACKAGE_SPECS, TRADING_AUTHORIZATION_NOTICE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


LIMITATIONS = [
    "Historical data authorization is not trading authorization.",
    "Proxy package is not internal global-briefing signal.",
    "This does not validate forward dry-run.",
    "This does not prove strategy effectiveness.",
    "This is not live trading readiness.",
]


def build_historical_data_acquisition_report(
    *,
    download_manifest_path: str | None = None,
    normalization_path: str | None = None,
    quality_audit_path: str | None = None,
    proxy_workflow_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    report_id, created_at = timestamp_id("HIST-DATA-ACQUISITION")
    download_file = _resolve(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    normalization_file = _resolve(normalization_path, paths.data_dir / "system" / "historical_package_normalization_summary.json", paths)
    quality_file = _resolve(quality_audit_path, paths.data_dir / "system" / "historical_data_quality_audit.json", paths)
    workflow_file = _resolve_latest(proxy_workflow_path, paths.data_dir / "replays" / "global_briefing", "full_historical_proxy_workflow-*.json", paths)
    download = _read(download_file)
    normalization = _read(normalization_file)
    quality = _read(quality_file)
    workflow = _read(workflow_file) if workflow_file else {}
    packages = {item.get("package_id"): item for item in download.get("packages", [])}
    critical_gaps = [reason for reason in quality.get("blocking_reasons", []) if "critical" in reason.lower()]
    proxy = normalization.get("proxy_package", {})
    auth_gb = packages.get(AUTHORIZED_GB_PACKAGE_ID, {})
    overall_status = "research_data_ready" if quality.get("overall_passed") and workflow.get("overall_status") == "research_review_ready" else "needs_attention"
    payload: dict[str, Any] = {
        "report_id": report_id,
        "created_at": created_at,
        "overall_status": overall_status,
        "packages": packages,
        "critical_gaps": critical_gaps,
        "production_global_briefing_package": {
            "status": auth_gb.get("status", "missing"),
            "validated": bool(normalization.get("authorized_global_briefing_normalized_path")),
        },
        "proxy_package": {
            "status": "built" if proxy.get("package_path") else "missing",
            "validated": bool(proxy.get("validated")),
            "path": proxy.get("package_path"),
            "normalized_path": proxy.get("normalized_path"),
        },
        "quality_audit": {
            "path": str(quality_file),
            "overall_passed": quality.get("overall_passed"),
        },
        "proxy_replay_workflow": {
            "path": str(workflow_file) if workflow_file else None,
            "overall_status": workflow.get("overall_status"),
        },
        "known_limitations": LIMITATIONS,
        "boundary": {
            "report_only": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_acquisition_report.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_DATA_ACQUISITION_REPORT.md"
    write_json_markdown(json_path, payload, md_path, build_acquisition_report_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _resolve_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _read(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def build_acquisition_report_markdown(payload: dict[str, Any]) -> str:
    package_lines = []
    for package_id in PACKAGE_SPECS:
        item = payload["packages"].get(package_id, {})
        package_lines.append(f"- {package_id}: status={item.get('status')} source={item.get('source')} rows={item.get('row_count')} checksum={item.get('sha256')}")
    return "\n".join(
        [
            "# Historical Data Acquisition Report",
            "",
            "## Overall Status",
            f"- overall_status={payload['overall_status']}",
            "",
            "## Packages",
            *package_lines,
            "",
            "## Critical Gaps",
            *([f"- {item}" for item in payload["critical_gaps"]] if payload["critical_gaps"] else ["- none"]),
            "",
            "## Production Global Briefing Package",
            f"- status={payload['production_global_briefing_package']['status']}",
            f"- validated={str(payload['production_global_briefing_package']['validated']).lower()}",
            "",
            "## Proxy Package",
            f"- status={payload['proxy_package']['status']}",
            f"- validated={str(payload['proxy_package']['validated']).lower()}",
            "",
            "## Known Limitations",
            *[f"- {item}" for item in payload["known_limitations"]],
            "",
            "## Boundary",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "- report only",
            "- no main ledger write",
            "- no run-daily call",
            "- not forward dry-run validation",
            "- not strategy effectiveness proof",
            "- not live trading readiness",
            "",
        ]
    )
