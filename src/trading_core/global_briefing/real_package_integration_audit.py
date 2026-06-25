"""Release audit for local real global-briefing package integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.real_package_integration_report import LIMITATIONS
from trading_core.global_briefing.signal_schema import read_signal_package
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.6-real-global-briefing-signal-integration-audited"
FORBIDDEN_PHRASES = [
    "forward dry-run validated",
    "strategy effectiveness proven",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
]


def audit_global_briefing_real_package_integration(
    *,
    manifest_path: str | None = None,
    workflow_path: str | None = None,
    report_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("GB-REAL-INTEGRATION-AUDIT")
    manifest_file = _resolve_or_default(manifest_path, paths.data_dir / "system" / "global_briefing_package_manifest.json", paths)
    workflow_file = _resolve_or_latest(workflow_path, paths.data_dir / "replays" / "global_briefing", "real_package_replay_workflow-*.json", paths)
    report_file = _resolve_or_default(report_path, paths.data_dir / "system" / "global_briefing_real_package_integration_report.json", paths)
    manifest = read_json(manifest_file, default=None)
    workflow = read_json(workflow_file, default=None) if workflow_file else None
    report = read_json(report_file, default=None)
    normalization = read_json(Path(workflow.get("normalization")), default=None) if isinstance(workflow, dict) and workflow.get("normalization") else None
    validation = read_json(Path(workflow.get("validation")), default=None) if isinstance(workflow, dict) and workflow.get("validation") else None
    coverage = read_json(Path(workflow.get("coverage_audit")), default=None) if isinstance(workflow, dict) and workflow.get("coverage_audit") else None

    sections = {
        "manifest": _audit_manifest(manifest),
        "normalization": _audit_normalization(normalization),
        "validation": _audit_validation(validation),
        "coverage": _audit_coverage(coverage),
        "workflow": _audit_workflow(workflow),
        "integration_report": _audit_report(report),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording([_report_md(workflow_file), paths.outputs_dir / "replays" / "global_briefing" / "GLOBAL_BRIEFING_REAL_PACKAGE_INTEGRATION_REPORT.md"]),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {
        "passed": not protected_changes,
        "issues": ["protected path changed", *protected_changes] if protected_changes else [],
        "modified_paths": [relative(Path(item), paths.project_root) for item in protected_changes],
        "checked_paths": list(PROTECTED_PATHS),
    }
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "inputs": {
            "manifest": str(manifest_file),
            "workflow": str(workflow_file) if workflow_file else None,
            "report": str(report_file),
        },
        "boundary": {
            "real_package_integration_only": True,
            "local_files_only": True,
            "network_access": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "strategy_effectiveness_proven": False,
            "broker_connected": False,
            "main_ledger_written": False,
            "isolated_replay_ledger_written": bool(isinstance(workflow, dict) and workflow.get("boundary", {}).get("isolated_replay_ledger_written")),
            "run_daily_called": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_real_package_integration_audit.json"
    md_path = paths.outputs_dir / "audit" / "GLOBAL_BRIEFING_REAL_PACKAGE_INTEGRATION_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_real_integration_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve_or_default(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _resolve_or_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _audit_manifest(manifest: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(manifest, dict):
        return {"passed": False, "issues": ["manifest missing"]}
    if manifest.get("boundary", {}).get("local_files_only") is not True:
        issues.append("local_files_only is not true")
    if manifest.get("boundary", {}).get("network_access") is not False:
        issues.append("network_access is not false")
    if not manifest.get("packages") and not manifest.get("warnings"):
        issues.append("no packages found and no warning recorded")
    return {"passed": not issues, "issues": issues}


def _audit_normalization(normalization: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(normalization, dict):
        return {"passed": False, "issues": ["normalization missing"]}
    if normalization.get("rows_out", 0) <= 0:
        issues.append("rows_out is not positive")
    output = normalization.get("output")
    if not output or not Path(output).exists():
        issues.append("normalized output missing")
    elif read_signal_package(output, default_project_paths()).blocking_reasons:
        issues.append("normalized output does not conform to signal package reader")
    return {"passed": not issues, "issues": issues}


def default_project_paths() -> ProjectPaths:
    return default_paths(None)


def _audit_validation(validation: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(validation, dict):
        return {"passed": False, "issues": ["validation missing"]}
    if validation.get("overall_passed") is not True:
        issues.append("validation overall_passed is not true")
    return {"passed": not issues, "issues": issues}


def _audit_coverage(coverage: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(coverage, dict):
        return {"passed": False, "issues": ["coverage missing"]}
    if coverage.get("coverage", {}).get("coverage_ratio") is None:
        issues.append("coverage ratio missing")
    if coverage.get("point_in_time", {}).get("future_signal_rows", 1) != 0:
        issues.append("future signal leakage detected")
    return {"passed": not issues, "issues": issues}


def _audit_workflow(workflow: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(workflow, dict):
        return {"passed": False, "issues": ["workflow missing"]}
    boundary = workflow.get("boundary", {}) if isinstance(workflow.get("boundary"), dict) else {}
    if workflow.get("overall_status") != "research_review_ready":
        issues.append("workflow is not research_review_ready")
    for key in ["network_access", "main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered", "forward_dry_run_started", "forward_dry_run_validated"]:
        if boundary.get(key) is not False:
            issues.append(f"{key} is not false")
    if boundary.get("isolated_replay_ledger_written") is not True:
        issues.append("isolated replay ledger not written")
    return {"passed": not issues, "issues": issues}


def _audit_report(report: dict[str, Any] | None) -> dict[str, Any]:
    issues = []
    if not isinstance(report, dict):
        return {"passed": False, "issues": ["integration report missing"]}
    limitations = report.get("known_limitations", [])
    for item in LIMITATIONS:
        if item not in limitations:
            issues.append(f"missing limitation: {item}")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: list[Path | None]) -> dict[str, Any]:
    issues = []
    for path in paths:
        if path is None or not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lowered = line.strip().lower()
            if not lowered or "not " in lowered or "no " in lowered or "does not " in lowered:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{path.name}:{line_number} contains forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def _report_md(workflow_json: Path | None) -> Path | None:
    if workflow_json is None:
        return None
    project_root = _project_root_from_data_path(workflow_json)
    if project_root is None:
        return None
    suffix = workflow_json.name.removeprefix("real_package_replay_workflow-").removesuffix(".json")
    return project_root / "outputs" / "replays" / "global_briefing" / f"REAL_PACKAGE_REPLAY_WORKFLOW-{suffix}.md"


def _project_root_from_data_path(path: Path) -> Path | None:
    parts = list(path.parts)
    for index, part in enumerate(parts):
        if part.lower() == "data":
            return Path(*parts[:index])
    return None


def build_real_integration_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Global Briefing Real Package Integration Audit",
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
            "## Protected Path Snapshot",
            f"- modified_paths={payload['sections']['protected_paths']['modified_paths']}",
            "",
            "## Boundary",
            "- This audit checks local historical global-briefing package integration only.",
            "- This is not forward dry-run validation.",
            "- This is not live trading readiness.",
            "- This does not prove strategy effectiveness.",
            "- No network access was used.",
            "- No broker is connected.",
            "- No real orders are supported.",
            "- Main ledger was not written.",
            "- Isolated replay ledger only.",
            "- run-daily CLI was not called.",
            "- Labels were not used.",
            "- ML shadow outputs were not used.",
            "- Experiment or promotion outputs were not used.",
            "- Promotion was not triggered.",
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
