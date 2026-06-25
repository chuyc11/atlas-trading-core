"""Release audit for v0.5.7 historical data acquisition."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import PACKAGE_SPECS, PROXY_PACKAGE_ID, RELEASE_CANDIDATE, REQUIRED_PACKAGE_IDS, TRADING_AUTHORIZATION_NOTICE, text_contains_secret
from trading_core.global_briefing.signal_schema import read_signal_package
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


FORBIDDEN_PHRASES = [
    "trading authorization",
    "forward dry-run validated",
    "strategy effectiveness proven",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
]


def audit_historical_data_acquisition(
    *,
    source_resolution_path: str | None = None,
    download_manifest_path: str | None = None,
    normalization_path: str | None = None,
    quality_audit_path: str | None = None,
    proxy_workflow_path: str | None = None,
    report_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("HIST-DATA-ACQUISITION-AUDIT")
    source_file = _resolve(source_resolution_path, paths.data_dir / "system" / "historical_data_source_resolution.json", paths)
    download_file = _resolve(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    normalization_file = _resolve(normalization_path, paths.data_dir / "system" / "historical_package_normalization_summary.json", paths)
    quality_file = _resolve(quality_audit_path, paths.data_dir / "system" / "historical_data_quality_audit.json", paths)
    workflow_file = _resolve_latest(proxy_workflow_path, paths.data_dir / "replays" / "global_briefing", "full_historical_proxy_workflow-*.json", paths)
    report_file = _resolve(report_path, paths.data_dir / "system" / "historical_data_acquisition_report.json", paths)
    source = _read(source_file)
    download = _read(download_file)
    normalization = _read(normalization_file)
    quality = _read(quality_file)
    workflow = _read(workflow_file) if workflow_file else {}
    report = _read(report_file)
    sections = {
        "source_resolution": _audit_source(source),
        "download_manifest": _audit_download(download),
        "normalization": _audit_normalization(normalization, paths),
        "quality": _audit_quality(quality),
        "proxy_replay": _audit_workflow(workflow),
        "report": _audit_report(report),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording(_wording_paths(paths)),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {
        "passed": not protected_changes,
        "issues": ["protected path changed", *protected_changes] if protected_changes else [],
        "modified_paths": [relative(Path(item), paths.project_root) for item in protected_changes],
        "checked_paths": list(PROTECTED_PATHS),
    }
    if _secret_leak(paths):
        sections["download_manifest"]["passed"] = False
        sections["download_manifest"]["issues"].append("secret leakage detected")
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "boundary": {
            "historical_data_acquisition_only": True,
            "trading_authorization": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "strategy_effectiveness_proven": False,
            "broker_connected": False,
            "main_ledger_written": False,
            "isolated_replay_ledger_written": bool(workflow.get("boundary", {}).get("isolated_replay_ledger_written")),
            "run_daily_called": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_acquisition_audit.json"
    md_path = paths.outputs_dir / "audit" / "HISTORICAL_DATA_ACQUISITION_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_acquisition_audit_markdown(payload))
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


def _read(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def _audit_source(source: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not source:
        return {"passed": False, "issues": ["source resolution missing"]}
    if len(source.get("packages", [])) < len(REQUIRED_PACKAGE_IDS):
        issues.append("not all required packages resolved")
    return {"passed": not issues, "issues": issues}


def _audit_download(download: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not download:
        return {"passed": False, "issues": ["download manifest missing"]}
    packages = {item.get("package_id"): item for item in download.get("packages", [])}
    for package_id in REQUIRED_PACKAGE_IDS:
        item = packages.get(package_id)
        if not item:
            issues.append(f"{package_id} status missing")
            continue
        if item.get("status") in {"downloaded", "loaded_from_local"}:
            if not item.get("sha256"):
                issues.append(f"{package_id} checksum missing")
            if not item.get("provenance_path"):
                issues.append(f"{package_id} provenance missing")
    for package_id in ["HIST-ETF-OHLCV-CN-HK-V1", "HIST-BENCHMARK-INDEX-CN-HK-V1"]:
        if packages.get(package_id, {}).get("status") not in {"downloaded", "loaded_from_local"}:
            issues.append(f"{package_id} critical package unavailable")
    if not any(packages.get(package_id, {}).get("status") in {"downloaded", "loaded_from_local"} for package_id in ["HIST-FX-USDCNY-V1", "HIST-GLOBAL-RISK-VIX-V1"]):
        issues.append("VIX/FX critical package unavailable")
    return {"passed": not issues, "issues": issues}


def _audit_normalization(normalization: dict[str, Any], paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    if not normalization:
        return {"passed": False, "issues": ["normalization summary missing"]}
    proxy_path = normalization.get("proxy_package", {}).get("normalized_path")
    if not proxy_path or not Path(str(proxy_path)).exists():
        issues.append("proxy package missing")
    else:
        package = read_signal_package(str(proxy_path), paths)
        if package.blocking_reasons:
            issues.extend(f"proxy contract: {item}" for item in package.blocking_reasons)
    return {"passed": not issues, "issues": issues}


def _audit_quality(quality: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not quality:
        return {"passed": False, "issues": ["quality audit missing"]}
    if quality.get("overall_passed") is not True:
        issues.extend(quality.get("blocking_reasons", ["quality audit failed"]))
    return {"passed": not issues, "issues": issues}


def _audit_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not workflow:
        return {"passed": False, "issues": ["proxy replay workflow missing"]}
    if workflow.get("overall_status") != "research_review_ready":
        issues.append("proxy replay workflow not ready")
    boundary = workflow.get("boundary", {})
    for key in ["main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered", "forward_dry_run_started", "forward_dry_run_validated"]:
        if boundary.get(key) is not False:
            issues.append(f"{key} is not false")
    return {"passed": not issues, "issues": issues}


def _audit_report(report: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not report:
        return {"passed": False, "issues": ["acquisition report missing"]}
    limitations = report.get("known_limitations", [])
    for required in [
        "Historical data authorization is not trading authorization.",
        "This does not validate forward dry-run.",
        "This does not prove strategy effectiveness.",
        "This is not live trading readiness.",
    ]:
        if required not in limitations:
            issues.append(f"missing limitation: {required}")
    return {"passed": not issues, "issues": issues}


def _wording_paths(paths: ProjectPaths) -> list[Path]:
    return [
        paths.outputs_dir / "system" / "HISTORICAL_DATA_DOWNLOAD_MANIFEST.md",
        paths.outputs_dir / "system" / "HISTORICAL_PACKAGE_NORMALIZATION_REPORT.md",
        paths.outputs_dir / "audit" / "HISTORICAL_DATA_QUALITY_AUDIT.md",
        paths.outputs_dir / "replays" / "global_briefing",
        paths.outputs_dir / "system" / "HISTORICAL_DATA_ACQUISITION_REPORT.md",
        paths.outputs_dir / "audit" / "HISTORICAL_DATA_ACQUISITION_AUDIT.md",
    ]


def _audit_wording(paths: list[Path]) -> dict[str, Any]:
    issues = []
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.exists():
            files.append(path)
    for file in files:
        for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            lowered = line.strip().lower()
            if not lowered or "not " in lowered or "no " in lowered or "is not " in lowered or "does not " in lowered:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{file.name}:{line_number} contains forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def _secret_leak(paths: ProjectPaths) -> bool:
    for root in [paths.data_dir / "system", paths.outputs_dir / "system", paths.outputs_dir / "audit"]:
        if root.exists():
            for path in root.glob("*"):
                if path.is_file() and text_contains_secret(path.read_text(encoding="utf-8", errors="ignore")):
                    return True
    return False


def build_acquisition_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Historical Data Acquisition Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## Section Results",
    ]
    for name, section in payload["sections"].items():
        lines.append(f"- {name}: passed={str(section['passed']).lower()} issues={section.get('issues', [])}")
    lines.extend(
        [
            "",
            "## Boundary",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "- historical data acquisition only",
            "- no broker connected",
            "- no real orders supported",
            "- main ledger was not written",
            "- run-daily CLI was not called",
            "- forward dry-run was not started or validated",
            "- strategy effectiveness is not proven",
            "- live trading readiness is not certified",
            "",
            "## Release Recommendation",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)
