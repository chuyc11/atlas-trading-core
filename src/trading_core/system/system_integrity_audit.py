"""v0.5.1 system integrity release audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, protected_diff, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.1-system-integrity-and-documentation"
DOCS = [
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/SAFETY_BOUNDARY.md",
    "docs/RELEASE_MATRIX.md",
    "docs/CLI_REFERENCE.md",
    "docs/ARTIFACT_MAP.md",
    "docs/RUNBOOK.md",
    "docs/FORWARD_DRY_RUN_RUNBOOK.md",
]
FORBIDDEN_WORDING = [
    "live trading ready",
    "forward 30d dry-run validated",
    "strategy effectiveness proven",
    "broker connected",
    "rl active trading enabled",
    "llm trading decision enabled",
]


def run_system_integrity_audit(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("SYSINTEGRITY")
    sections = {
        "documentation": _audit_documentation(paths),
        "cli_inventory": _audit_cli_inventory(paths),
        "artifact_inventory": _audit_artifact_inventory(paths),
        "smoke_test": _audit_smoke(paths),
        "boundary_regression": _audit_boundary(paths),
        "release_wording": _audit_wording(paths),
    }
    protected_changes = protected_diff(paths, before)
    if protected_changes:
        sections["protected_ledger"] = {"passed": False, "issues": ["audit modified protected paths", *protected_changes]}
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
            "research_only": True,
            "live_trading_ready": False,
            "broker_connected": False,
            "forward_30d_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
        },
    }
    json_path = paths.data_dir / "system" / "system_integrity_audit.json"
    report_path = paths.outputs_dir / "audit" / "SYSTEM_INTEGRITY_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_integrity_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_integrity_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# System Integrity Audit",
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
            "- This project remains research-only.",
            "- This is not live trading ready.",
            "- This does not validate forward 30d dry-run.",
            "- Strategy effectiveness is not proven.",
            "",
        ]
    )
    return "\n".join(lines)


def _audit_documentation(paths: ProjectPaths) -> dict[str, Any]:
    issues = [f"missing {doc}" for doc in DOCS if not (paths.project_root / doc).exists()]
    return {"passed": not issues, "issues": issues}


def _audit_cli_inventory(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "cli_inventory.json"
    md_path = paths.outputs_dir / "system" / "CLI_INVENTORY.md"
    payload = _read_json(json_path)
    commands = payload.get("commands", []) if isinstance(payload, dict) else []
    command_names = {item.get("command") for item in commands if isinstance(item, dict)}
    if not json_path.exists():
        issues.append("cli_inventory.json missing")
    if not md_path.exists():
        issues.append("CLI_INVENTORY.md missing")
    for command in ["run-daily", "run-research-pipeline"]:
        if command not in command_names:
            issues.append(f"missing command {command}")
    if any(not item.get("safety") for item in commands if isinstance(item, dict)):
        issues.append("one or more commands missing safety notes")
    return {"passed": not issues, "issues": issues}


def _audit_artifact_inventory(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "artifact_inventory.json"
    md_path = paths.outputs_dir / "system" / "ARTIFACT_INVENTORY.md"
    payload = _read_json(json_path)
    artifacts = payload.get("artifacts", []) if isinstance(payload, dict) else []
    names = {item.get("path") for item in artifacts if isinstance(item, dict)}
    if not json_path.exists():
        issues.append("artifact_inventory.json missing")
    if not md_path.exists():
        issues.append("ARTIFACT_INVENTORY.md missing")
    for key in ["data/experiments", "data/system", "outputs/audit"]:
        if key not in names:
            issues.append(f"key artifact directory not listed: {key}")
    return {"passed": not issues, "issues": issues}


def _audit_smoke(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "system_smoke_test.json"
    md_path = paths.outputs_dir / "system" / "SYSTEM_SMOKE_TEST.md"
    payload = _read_json(json_path)
    if not json_path.exists():
        issues.append("system_smoke_test.json missing")
    if not md_path.exists():
        issues.append("SYSTEM_SMOKE_TEST.md missing")
    if payload.get("passed") is not True:
        issues.append("system smoke test did not pass")
    return {"passed": not issues, "issues": issues}


def _audit_boundary(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    json_path = paths.data_dir / "system" / "boundary_regression_audit.json"
    md_path = paths.outputs_dir / "audit" / "BOUNDARY_REGRESSION_AUDIT.md"
    payload = _read_json(json_path)
    if not json_path.exists():
        issues.append("boundary_regression_audit.json missing")
    if not md_path.exists():
        issues.append("BOUNDARY_REGRESSION_AUDIT.md missing")
    if payload.get("passed") is not True:
        issues.append("boundary regression audit did not pass")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    texts = []
    for doc in DOCS:
        path = paths.project_root / doc
        if path.exists():
            texts.append(path.read_text(encoding="utf-8").lower())
    text = "\n".join(texts)
    for phrase in FORBIDDEN_WORDING:
        if phrase in text:
            issues.append(f"forbidden wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
