"""Release audit for v0.5.7.1 historical data gap closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import TRADING_AUTHORIZATION_NOTICE, text_contains_secret
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.7.1-historical-data-gap-closure-audited"
FORBIDDEN_PHRASES = ["forward dry-run validated", "strategy effectiveness proven", "live trading ready", "broker connected", "real orders supported", "promotion approved"]


def audit_historical_data_gap_closure(*, workflow_path: str | None = None, report_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("HIST-DATA-GAP-CLOSURE-AUDIT")
    workflow_file = _resolve(workflow_path, paths.data_dir / "system" / "historical_data_gap_closure_workflow.json", paths)
    report_file = _resolve(report_path, paths.data_dir / "system" / "historical_data_gap_closure_report.json", paths)
    workflow = _read(workflow_file)
    report = _read(report_file)
    download = _read(paths.data_dir / "system" / "historical_data_download_manifest.json")
    normalization = _read(paths.data_dir / "system" / "historical_package_normalization_summary.json")
    quality = _read(paths.data_dir / "system" / "historical_data_quality_audit.json")
    inventory = _read(paths.data_dir / "system" / "historical_warning_inventory.json")
    acquisition = _read(paths.data_dir / "system" / "historical_data_acquisition_audit.json")
    replay = _read(Path(workflow.get("artifacts", {}).get("proxy_replay", paths.data_dir / "replays" / "global_briefing" / "missing.json")))
    packages = {item.get("package_id"): item for item in download.get("packages", [])}
    sections = {
        "epu_repair": _audit_epu(packages),
        "oecd_repair": _audit_oecd(packages),
        "proxy_rebuild": _audit_proxy(normalization),
        "warning_inventory": _audit_inventory(inventory),
        "replay_warning_reduction": _audit_replay(replay),
        "acquisition_audit": _audit_acquisition(acquisition),
        "future_leakage": _audit_future_leakage(quality, replay),
        "secret_leakage": _audit_secret(paths),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording(paths),
        "report": {"passed": bool(report), "issues": [] if report else ["gap closure report missing"]},
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": ["protected path changed", *protected_changes] if protected_changes else [], "modified_paths": [relative(Path(item), paths.project_root) for item in protected_changes], "checked_paths": list(PROTECTED_PATHS)}
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
            "historical_data_gap_closure_only": True,
            "trading_authorization": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "strategy_effectiveness_proven": False,
            "broker_connected": False,
            "main_ledger_written": False,
            "isolated_replay_ledger_written": True,
            "run_daily_called": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_gap_closure_audit.json"
    md_path = paths.outputs_dir / "audit" / "HISTORICAL_DATA_GAP_CLOSURE_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_gap_closure_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _audit_epu(packages: dict[str, Any]) -> dict[str, Any]:
    item = packages.get("HIST-POLICY-UNCERTAINTY-EPU-V1", {})
    issues = []
    if item.get("status") not in {"downloaded", "partial_downloaded", "loaded_from_local"}:
        issues.append("EPU status not improved or repaired")
    if not item.get("sha256") or not item.get("provenance_path"):
        issues.append("EPU checksum/provenance missing")
    return {"passed": not issues, "issues": issues}


def _audit_oecd(packages: dict[str, Any]) -> dict[str, Any]:
    item = packages.get("HIST-OECD-CLI-MACRO-CYCLE-V1", {})
    issues = []
    if item.get("status") not in {"downloaded", "partial_downloaded", "loaded_from_local"}:
        issues.append("OECD/macro-cycle status not improved")
    if item.get("source") == "authorized_macro_cycle_proxy" and item.get("not_official_oecd_cli") is not True:
        issues.append("macro-cycle proxy is not clearly marked as not official OECD CLI")
    if not item.get("sha256") or not item.get("provenance_path"):
        issues.append("OECD checksum/provenance missing")
    return {"passed": not issues, "issues": issues}


def _audit_proxy(normalization: dict[str, Any]) -> dict[str, Any]:
    proxy = normalization.get("proxy_package", {}) if isinstance(normalization, dict) else {}
    issues = []
    for key in ["package_path", "normalized_path"]:
        if not proxy.get(key) or not Path(str(proxy.get(key))).exists():
            issues.append(f"proxy {key} missing")
    if proxy.get("validated") is not True:
        issues.append("proxy package not validated")
    return {"passed": not issues, "issues": issues}


def _audit_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not inventory:
        issues.append("warning inventory missing")
    if inventory.get("unknown_warning_count") not in {0, None}:
        issues.append("unknown warning count is non-zero")
    return {"passed": not issues, "issues": issues}


def _audit_replay(replay: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not replay:
        issues.append("proxy replay workflow missing")
    if replay.get("overall_status") != "research_review_ready":
        issues.append("proxy replay workflow not ready")
    if "raw_warning_count" not in replay or "grouped_warnings" not in replay:
        issues.append("grouped warning output missing")
    boundary = replay.get("boundary", {})
    for key in ["main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered", "forward_dry_run_started", "forward_dry_run_validated"]:
        if boundary.get(key) is not False:
            issues.append(f"{key} is not false")
    return {"passed": not issues, "issues": issues}


def _audit_acquisition(acquisition: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if acquisition.get("overall_passed") is not True:
        issues.append("acquisition audit not passed")
    return {"passed": not issues, "issues": issues}


def _audit_future_leakage(quality: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(str(item).lower() for item in [*quality.get("blocking_reasons", []), *replay.get("blocking_reasons", [])])
    issues = ["future leakage detected"] if "future" in text else []
    return {"passed": not issues, "issues": issues}


def _audit_secret(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    for root in [paths.data_dir / "system", paths.outputs_dir / "system", paths.outputs_dir / "audit"]:
        if root.exists():
            for path in root.glob("*"):
                if path.is_file() and text_contains_secret(path.read_text(encoding="utf-8", errors="ignore")):
                    issues.append(f"secret leakage detected in {path.name}")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: ProjectPaths) -> dict[str, Any]:
    files = []
    for root in [paths.outputs_dir / "system", paths.outputs_dir / "audit", paths.outputs_dir / "replays" / "global_briefing"]:
        if root.exists():
            files.extend(root.glob("*.md"))
    issues = []
    for file in files:
        for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            lowered = line.lower()
            if not lowered or "not " in lowered or "no " in lowered or "is not " in lowered or "does not " in lowered:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _read(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def build_gap_closure_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Historical Data Gap Closure Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## EPU Repair",
        f"- {payload['sections']['epu_repair']}",
        "",
        "## OECD / Macro Cycle Repair",
        f"- {payload['sections']['oecd_repair']}",
        "",
        "## Proxy Rebuild",
        f"- {payload['sections']['proxy_rebuild']}",
        "",
        "## Warning Inventory",
        f"- {payload['sections']['warning_inventory']}",
        "",
        "## Replay Warning Reduction",
        f"- {payload['sections']['replay_warning_reduction']}",
        "",
        "## Remaining Gaps",
        "- none" if payload["overall_passed"] else f"- {payload['blocking_reasons']}",
        "",
        "## Boundary",
        f"- {TRADING_AUTHORIZATION_NOTICE}",
        "- historical data gap closure only",
        "- not forward dry-run validation",
        "- not live trading readiness",
        "- not strategy effectiveness proof",
        "- main ledger not written",
        "- run-daily not called",
        "",
        "## Release Recommendation",
    ]
    lines.extend([RELEASE_CANDIDATE] if payload["overall_passed"] else ["Release tag is not recommended until blocking reasons are resolved."])
    lines.append("")
    return "\n".join(lines)
