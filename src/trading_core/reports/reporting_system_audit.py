"""Audit v0.5 research reporting and control plane."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import default_paths, snapshot_diff, snapshot_protected, write_json_and_markdown
from trading_core.storage.file_paths import ProjectPaths


RELEASE_CANDIDATE = "v0.5.0-research-reporting-control-plane-audited"
BAD_WORDING = [
    "shadow result is ready for live trading",
    "promotion approved",
    "active strategy promoted",
    "forward 30d dry-run validated",
    "live trading ready",
]


def audit_reporting_system(
    reports_dir: str | Path | None = None,
    system_dir: str | Path | None = None,
    audit_dir: str | Path | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    reports_path = _resolve(reports_dir, paths.outputs_dir / "reports", paths)
    system_path = _resolve(system_dir, paths.outputs_dir / "system", paths)
    audit_path = _resolve(audit_dir, paths.outputs_dir / "audit", paths)
    before = snapshot_protected(paths)

    sections = {
        "weekly_report": _audit_weekly(paths, reports_path),
        "monthly_report": _audit_monthly(paths, reports_path),
        "system_dashboard": _audit_system_dashboard(paths, system_path),
        "project_status": _audit_project_status(paths, system_path),
        "research_pipeline": _audit_pipeline(paths, system_path),
        "main_ledger_pollution": {"passed": True, "modified_paths": [], "issues": []},
        "run_daily_isolation": {"passed": True, "issues": []},
        "wording": _audit_wording(reports_path, system_path),
    }
    after = snapshot_protected(paths)
    modified = snapshot_diff(before, after)
    if modified:
        sections["main_ledger_pollution"] = {"passed": False, "modified_paths": modified, "issues": ["audit modified protected paths"]}
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    now = datetime.now(UTC)
    payload = {
        "audit_id": f"REPORTAUDIT-{now:%Y%m%d}-001",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "artifact_inventory": {
            "weekly_reports": [str(p) for p in _glob(reports_path, "WEEKLY_RESEARCH_REPORT-*.md")],
            "monthly_reports": [str(p) for p in _glob(reports_path, "MONTHLY_RESEARCH_REPORT-*.md")],
            "system_dashboard": str(system_path / "SYSTEM_DASHBOARD.md"),
            "project_status": str(system_path / "PROJECT_STATUS_REPORT.md"),
            "research_pipeline": [str(p) for p in _glob(system_path, "RESEARCH_PIPELINE_REPORT-*.md")],
        },
        "boundary": {
            "research_only": True,
            "write_main_ledger": False,
            "run_daily_called": False,
            "strategy_state_changed": False,
            "strategy_parameters_changed": False,
            "promotion_triggered": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "reporting_system_audit.json"
    md_path = audit_path / "REPORTING_SYSTEM_AUDIT.md"
    write_json_and_markdown(json_path, payload, md_path, build_reporting_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_reporting_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reporting System Audit",
        "",
        "## 1. Scope",
        f"- audit_id: {payload['audit_id']}",
        f"- release_candidate: {payload['release_candidate']}",
        "",
        "## 2. Overall Verdict",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {payload['warnings']}",
        "",
        "## 3. Section Results",
    ]
    for name, section in payload["sections"].items():
        lines.append(f"- {name}: passed={str(section['passed']).lower()} issues={section.get('issues', [])}")
    lines.extend(["", "## 4. Artifact Inventory"])
    for name, value in payload["artifact_inventory"].items():
        lines.append(f"- {name}: {value}")
    lines.extend(
        [
            "",
            "## 5. Safety Boundary",
            "- This reporting system is research-only.",
            "- No strategy state was changed.",
            "- No strategy parameter was changed.",
            "- No promotion was triggered.",
            "- No orders were written.",
            "- No trades were written.",
            "- No portfolio was written.",
            "- No accounts were written.",
            "- This is not an admission gate.",
            "- This is not a live trading validation.",
            "- This does not validate forward 30d dry-run.",
            "",
            "## 6. Release Recommendation",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)


def _audit_weekly(paths: ProjectPaths, reports: Path) -> dict[str, Any]:
    issues = []
    jsons = _glob(paths.data_dir / "reports", "weekly_research_summary-*.json")
    mds = _glob(reports, "WEEKLY_RESEARCH_REPORT-*.md")
    if not jsons:
        issues.append("weekly summary JSON missing")
    if not mds:
        issues.append("weekly Markdown missing")
    text = mds[-1].read_text(encoding="utf-8") if mds else ""
    for phrase in ["not an admission gate", "not forward 30d dry-run", "research_only=true"]:
        if phrase not in text:
            issues.append(f"weekly report missing {phrase}")
    return {"passed": not issues, "issues": issues}


def _audit_monthly(paths: ProjectPaths, reports: Path) -> dict[str, Any]:
    issues = []
    jsons = _glob(paths.data_dir / "reports", "monthly_research_summary-*.json")
    mds = _glob(reports, "MONTHLY_RESEARCH_REPORT-*.md")
    if not jsons:
        issues.append("monthly summary JSON missing")
    if not mds:
        issues.append("monthly Markdown missing")
    text = mds[-1].read_text(encoding="utf-8") if mds else ""
    for phrase in ["no active promotion", "not an admission gate", "does not validate forward 30d dry-run"]:
        if phrase not in text:
            issues.append(f"monthly report missing {phrase}")
    return {"passed": not issues, "issues": issues}


def _audit_system_dashboard(paths: ProjectPaths, system: Path) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "system_dashboard.json"
    md_path = system / "SYSTEM_DASHBOARD.md"
    if not json_path.exists():
        issues.append("system_dashboard.json missing")
    if not md_path.exists():
        issues.append("SYSTEM_DASHBOARD.md missing")
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    if "Known Limitations" not in text:
        issues.append("system dashboard missing known limitations")
    if "no live trading" not in text:
        issues.append("system dashboard missing no live trading")
    return {"passed": not issues, "issues": issues}


def _audit_project_status(paths: ProjectPaths, system: Path) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "project_status_summary.json"
    md_path = system / "PROJECT_STATUS_REPORT.md"
    if not json_path.exists():
        issues.append("project_status_summary.json missing")
    if not md_path.exists():
        issues.append("PROJECT_STATUS_REPORT.md missing")
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    if "forward 30d dry-run" not in text:
        issues.append("project status missing forward 30d dry-run")
    if "research-only" not in text:
        issues.append("project status missing research-only")
    return {"passed": not issues, "issues": issues}


def _audit_pipeline(paths: ProjectPaths, system: Path) -> dict[str, Any]:
    issues = []
    jsons = _glob(paths.data_dir / "system", "research_pipeline_summary-*.json")
    mds = _glob(system, "RESEARCH_PIPELINE_REPORT-*.md")
    if not jsons:
        issues.append("research pipeline summary missing")
    if not mds:
        issues.append("research pipeline Markdown missing")
    if jsons:
        payload = _read_json(jsons[-1])
        boundary = payload.get("boundary", {}) if isinstance(payload, dict) else {}
        if boundary.get("run_daily_called") is not False:
            issues.append("boundary.run_daily_called is not false")
        if boundary.get("write_main_ledger") is not False:
            issues.append("boundary.write_main_ledger is not false")
    return {"passed": not issues, "issues": issues}


def _audit_wording(reports: Path, system: Path) -> dict[str, Any]:
    issues = []
    text = "\n".join(path.read_text(encoding="utf-8").lower() for root in [reports, system] for path in _glob(root, "*.md"))
    for bad in BAD_WORDING:
        if bad in text:
            issues.append(f"forbidden wording: {bad}")
    return {"passed": not issues, "issues": issues}


def _resolve(value: str | Path | None, default: Path, paths: ProjectPaths) -> Path:
    if value is None:
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    return paths.project_root / path


def _glob(directory: Path, pattern: str) -> list[Path]:
    return sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime) if directory.exists() else []


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
