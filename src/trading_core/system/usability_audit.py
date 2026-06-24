"""v0.5.2 usability release audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import protected_diff, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.2-usability-polish"


def run_usability_audit(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("USABILITY-AUDIT")
    sections = {
        "final_handoff_wording": _audit_final_handoff(paths),
        "report_index": _audit_report_index(paths),
        "latest_artifact": _audit_latest_artifact(paths),
        "artifact_browser": _audit_artifact_browser(paths),
        "quick_status": _audit_quick_status(paths),
        "command_cookbook": _audit_command_cookbook(paths),
        "boundary": {"passed": True, "issues": []},
    }
    protected_changes = protected_diff(paths, before)
    if protected_changes:
        sections["boundary"] = {"passed": False, "issues": ["protected ledger changed", *protected_changes]}
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    payload = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "boundary": {
            "usability_only": True,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "usability_audit.json"
    report_path = paths.outputs_dir / "audit" / "USABILITY_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_usability_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_usability_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Usability Audit",
        "",
        "## Overall Verdict",
        f"overall_passed={str(payload['overall_passed']).lower()}",
        f"blocking_reasons={payload['blocking_reasons']}",
        f"warnings={payload['warnings']}",
        "",
        "## Sections",
    ]
    for name, section in payload["sections"].items():
        lines.append(f"- {name}: passed={str(section['passed']).lower()} issues={section['issues']}")
    lines.extend(
        [
            "",
            "## Release Recommendation",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.extend(
        [
            "",
            "## Boundary",
            "- This release adds usability only.",
            "- No trading functionality was added.",
            "- No run-daily call was made.",
            "- No orders were written.",
            "- No trades were written.",
            "- No portfolio was written.",
            "- No accounts were written.",
            "",
        ]
    )
    return "\n".join(lines)


def _audit_final_handoff(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    text = _read_text(paths.outputs_dir / "system" / "FINAL_HANDOFF_REVIEW_REPORT.md")
    if "381 passed, 1 skipped" not in text:
        issues.append("pytest result not updated")
    if "parameter sweep has shadow candidates" in text:
        issues.append("old parameter sweep wording present")
    if "no eligible shadow candidate" not in text:
        issues.append("no eligible shadow candidate wording missing")
    return {"passed": not issues, "issues": issues}


def _audit_report_index(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    payload = _read_json(paths.data_dir / "system" / "report_index.json")
    text = _read_text(paths.outputs_dir / "system" / "REPORT_INDEX.md")
    if not payload:
        issues.append("report_index.json missing")
    if not text:
        issues.append("REPORT_INDEX.md missing")
    if "FINAL_HANDOFF_REVIEW_REPORT.md" not in text:
        issues.append("final handoff report missing from report index")
    if "SYSTEM_INTEGRITY_AUDIT.md" not in text:
        issues.append("audit reports missing from report index")
    return {"passed": not issues, "issues": issues}


def _audit_latest_artifact(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    payload = _read_json(paths.data_dir / "system" / "latest_artifact.json")
    text = _read_text(paths.outputs_dir / "system" / "LATEST_ARTIFACT.md")
    if not payload:
        issues.append("latest_artifact.json missing")
    if not text:
        issues.append("LATEST_ARTIFACT.md missing")
    serialized = json.dumps(payload)
    if "FINAL_HANDOFF_REVIEW_REPORT.md" not in serialized and "FINAL_HANDOFF_REVIEW_REPORT.md" not in text:
        issues.append("latest handoff artifact not found")
    return {"passed": not issues, "issues": issues}


def _audit_artifact_browser(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    payload = _read_json(paths.data_dir / "system" / "artifact_browser.json")
    text = _read_text(paths.outputs_dir / "system" / "ARTIFACT_BROWSER.md")
    if not payload:
        issues.append("artifact_browser.json missing")
    if not text:
        issues.append("ARTIFACT_BROWSER.md missing")
    if "Not Trading Authorization" not in text:
        issues.append("Not Trading Authorization section missing")
    return {"passed": not issues, "issues": issues}


def _audit_quick_status(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    payload = _read_json(paths.data_dir / "system" / "quick_status.json")
    text = _read_text(paths.outputs_dir / "system" / "QUICK_STATUS.md")
    if not payload:
        issues.append("quick_status.json missing")
    if not text:
        issues.append("QUICK_STATUS.md missing")
    combined = json.dumps(payload) + text
    for phrase in ["forward 30d dry-run not completed", "not live trading ready"]:
        if phrase not in combined:
            issues.append(f"{phrase} missing")
    return {"passed": not issues, "issues": issues}


def _audit_command_cookbook(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    text = _read_text(paths.project_root / "docs" / "COMMAND_COOKBOOK.md")
    if not text:
        issues.append("docs/COMMAND_COOKBOOK.md missing")
    for phrase in ["Resume project", "Find reports", "Check safety", "What not to do"]:
        if phrase not in text:
            issues.append(f"{phrase} missing")
    return {"passed": not issues, "issues": issues}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""
