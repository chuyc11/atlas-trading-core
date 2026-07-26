"""Audit the v0.5.8.1 plan alignment and MVP gap package."""

from __future__ import annotations

from typing import Any

from trading_core.planning.common import PLAN_ALIGNMENT_NOTICE, RELEASE_CANDIDATE, paths_or_default, read_dict, rel, standard_boundary
from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import protected_diff, timestamp_id, write_json_markdown


REQUIRED_IDS = {f"R{number:03d}" for number in range(1, 25)}
FORBIDDEN_PHRASES = [
    "forward dry-run started",
    "forward dry-run validated",
    "strategy effectiveness proven",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
    "ml approved for trading",
    "llm approved for trading",
    "rl approved for trading",
]


def audit_plan_alignment(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("PLAN-ALIGNMENT-AUDIT")
    artifacts = _load_artifacts(paths)
    sections = {
        "plan_checklist": _audit_checklist(artifacts["checklist"]),
        "requirement_map": _exists_section(artifacts["requirement_map"], "requirement map missing"),
        "artifact_coverage_scan": _exists_section(artifacts["artifact_scan"], "artifact coverage scan missing"),
        "mvp_gap_classification": _audit_gap_classification(artifacts["classification"]),
        "day1_blocker_classification": _exists_section(artifacts["day1_blockers"], "day1 blocker classification missing"),
        "next_work_register": _audit_next_work(artifacts["next_work"]),
        "boundary": _audit_boundaries(artifacts),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording(paths),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": ["protected path changed", *protected_changes] if protected_changes else [], "modified_paths": [rel(item, paths) for item in protected_changes], "checked_paths": list(PROTECTED_PATHS)}
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    classification = artifacts["classification"]
    summary = {
        "requirements_total": classification.get("summary", {}).get("requirements_total", 0),
        "passed": classification.get("summary", {}).get("passed", 0),
        "partial": classification.get("summary", {}).get("partial", 0),
        "missing": classification.get("summary", {}).get("missing", 0),
        "deferred": classification.get("summary", {}).get("deferred", 0),
        "not_applicable": classification.get("summary", {}).get("not_applicable", 0),
        "day1_blockers": classification.get("summary", {}).get("day1_blockers", 0),
        "recommended_next_version": artifacts["next_work"].get("recommended_next_version"),
    }
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": summary,
        "sections": sections,
        "boundary": standard_boundary("plan_alignment_audit_only"),
    }
    json_path = paths.data_dir / "system" / "plan_alignment_audit.json"
    md_path = paths.outputs_dir / "audit" / "PLAN_ALIGNMENT_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_plan_alignment_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _load_artifacts(paths: ProjectPaths) -> dict[str, dict[str, Any]]:
    names = {
        "checklist": "plan_checklist.json",
        "requirement_map": "mvp_requirement_map.json",
        "artifact_scan": "artifact_coverage_scan.json",
        "classification": "mvp_gap_classification.json",
        "day1_blockers": "day1_blocker_classification.json",
        "next_work": "next_work_register.json",
    }
    return {key: read_dict(paths.data_dir / "system" / name) for key, name in names.items()}


def _exists_section(data: dict[str, Any], message: str) -> dict[str, Any]:
    issues = [] if data else [message]
    return {"passed": not issues, "issues": issues}


def _audit_checklist(data: dict[str, Any]) -> dict[str, Any]:
    issues = [] if data else ["plan checklist missing"]
    ids = {item.get("requirement_id") for item in data.get("requirements", [])}
    missing = sorted(REQUIRED_IDS - ids)
    if missing:
        issues.append(f"missing requirements: {missing}")
    return {"passed": not issues, "issues": issues}


def _audit_gap_classification(data: dict[str, Any]) -> dict[str, Any]:
    issues = [] if data else ["MVP gap classification missing"]
    ids = {item.get("requirement_id") for item in data.get("requirements", []) if item.get("status")}
    missing = sorted(REQUIRED_IDS - ids)
    if missing:
        issues.append(f"requirements not classified: {missing}")
    return {"passed": not issues, "issues": issues}


def _audit_next_work(data: dict[str, Any]) -> dict[str, Any]:
    issues = [] if data else ["next work register missing"]
    if data and not data.get("recommended_next_version"):
        issues.append("recommended_next_version missing")
    return {"passed": not issues, "issues": issues}


def _audit_boundaries(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    issues = []
    for name, artifact in artifacts.items():
        boundary = artifact.get("boundary", {})
        if boundary.get("run_daily_called") is not False:
            issues.append(f"{name} run_daily_called boundary is not false")
        if boundary.get("forward_dry_run_started") is not False:
            issues.append(f"{name} forward_dry_run_started boundary is not false")
        if boundary.get("main_ledger_written") is not False:
            issues.append(f"{name} main_ledger_written boundary is not false")
        if boundary.get("ml_shadow_used_as_authorization") is not False:
            issues.append(f"{name} ml authorization boundary is not false")
        if boundary.get("llm_trading_decision") is not False:
            issues.append(f"{name} llm boundary is not false")
        if boundary.get("rl_used") is not False:
            issues.append(f"{name} rl boundary is not false")
        if boundary.get("promotion_triggered") is not False:
            issues.append(f"{name} promotion boundary is not false")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    files = []
    for root in [paths.outputs_dir / "system", paths.outputs_dir / "audit", paths.project_root / "docs"]:
        if root.exists():
            files.extend(root.glob("*.md"))
    for file in files:
        for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            lowered = line.lower()
            if not lowered or any(token in lowered for token in ["not ", "no ", "false", "does not", "is not", "not used"]):
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def build_plan_alignment_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Plan Alignment Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        PLAN_ALIGNMENT_NOTICE,
        "",
        "## MVP Coverage Summary",
    ]
    lines.extend(f"- {key}: {value}" for key, value in payload["summary"].items())
    lines.extend(["", "## Day-1 Blockers", f"- day1_blockers: {payload['summary']['day1_blockers']}"])
    lines.extend(["", "## Recommended Next Version", f"- {payload['summary'].get('recommended_next_version')}"])
    lines.extend(
        [
            "",
            "## Boundary",
            "- plan alignment audit only",
            "- run-daily not called",
            "- forward dry-run not started",
            "- main ledger not written",
            "- ML shadow not used as day-1 authorization",
            "- LLM not used for trading decision",
            "- RL not used",
            "- promotion not triggered",
            "- historical performance is not strategy effectiveness proof",
            "- this is not live trading readiness",
            "",
            "## Release Recommendation",
        ]
    )
    lines.append(f"Recommended patch tag: {RELEASE_CANDIDATE}" if payload["overall_passed"] else "Patch tag is not recommended until blockers are resolved.")
    lines.append("")
    return "\n".join(lines)

