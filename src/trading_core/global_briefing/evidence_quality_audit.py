"""Patch audit for v0.5.6.1 evidence-quality artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.6.1-warning-triage-evidence-quality"
FORBIDDEN_PHRASES = [
    "production global-briefing package validated",
    "production global briefing package validated",
    "strategy effectiveness proven",
    "forward dry-run validated",
    "live trading ready",
    "promotion approved",
]


def audit_global_briefing_evidence_quality(
    *,
    triage_path: str | None = None,
    evidence_path: str | None = None,
    criteria_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("GB-EVIDENCE-QUALITY-AUDIT")
    triage_file = _resolve_or_default(triage_path, paths.data_dir / "system" / "global_briefing_warning_triage.json", paths)
    evidence_file = _resolve_or_default(evidence_path, paths.data_dir / "system" / "global_briefing_evidence_quality.json", paths)
    criteria_file = _resolve_or_default(criteria_path, paths.data_dir / "system" / "global_briefing_production_acceptance_criteria.json", paths)
    triage = _read_optional(triage_file)
    evidence = _read_optional(evidence_file)
    criteria = _read_optional(criteria_file)
    sections = {
        "warning_triage": _audit_triage(triage),
        "evidence_quality": _audit_evidence(evidence),
        "production_acceptance_criteria": _audit_criteria(criteria),
        "wording": _audit_wording(_wording_paths(paths)),
        "boundary": _audit_boundary([triage, evidence, criteria]),
    }
    protected_changes = protected_diff(paths, before)
    if protected_changes:
        sections["boundary"]["passed"] = False
        sections["boundary"]["issues"].extend(["protected path changed", *[relative(Path(item), paths.project_root) for item in protected_changes]])
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    production_ready = evidence.get("production_readiness", {}).get("ready") if isinstance(evidence, dict) else None
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "sections": sections,
        "evidence_status": evidence.get("overall_evidence_status") if isinstance(evidence, dict) else None,
        "production_readiness": {"ready": production_ready},
        "inputs": {
            "triage": str(triage_file),
            "evidence": str(evidence_file),
            "criteria": str(criteria_file),
        },
        "boundary": {
            "evidence_quality_only": True,
            "production_package_validated": False,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "network_access": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_evidence_quality_audit.json"
    md_path = paths.outputs_dir / "audit" / "GLOBAL_BRIEFING_EVIDENCE_QUALITY_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_evidence_quality_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _resolve_or_default(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _read_optional(path: Path) -> dict[str, Any]:
    payload = read_json(path, default=None)
    return payload if isinstance(payload, dict) else {}


def _audit_triage(triage: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not triage:
        return {"passed": False, "issues": ["warning triage missing"]}
    if "warning_count" not in triage:
        issues.append("warning_count missing")
    categories = triage.get("by_category")
    if not isinstance(categories, dict):
        issues.append("categories missing")
    elif "coverage_gap" not in categories:
        issues.append("coverage warning category missing")
    if "unknown" not in (categories or {}):
        issues.append("unknown warning category missing")
    return {"passed": not issues, "issues": issues}


def _audit_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not evidence:
        return {"passed": False, "issues": ["evidence quality missing"]}
    if not evidence.get("overall_evidence_status"):
        issues.append("overall_evidence_status missing")
    if evidence.get("production_readiness", {}).get("ready") is not False:
        issues.append("production_readiness.ready is not false")
    insufficient = evidence.get("evidence_levels", {}).get("insufficient_for_production", [])
    not_validated = evidence.get("evidence_levels", {}).get("not_validated", [])
    if not insufficient:
        issues.append("production limitations missing")
    if not not_validated:
        issues.append("not_validated limitations missing")
    return {"passed": not issues, "issues": issues}


def _audit_criteria(criteria: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not criteria:
        return {"passed": False, "issues": ["production acceptance criteria missing"]}
    required = criteria.get("required", {})
    if required.get("min_coverage", 0) < 0.8:
        issues.append("min_coverage below 0.8")
    if required.get("target_coverage", 0) < 0.9:
        issues.append("target_coverage below 0.9")
    if required.get("future_signal_leakage_rows") != 0:
        issues.append("future_signal_leakage_rows is not zero")
    must_not_claim = set(criteria.get("must_not_claim", []))
    for item in ["strategy_effectiveness_proven", "forward_dry_run_validated", "live_trading_ready"]:
        if item not in must_not_claim:
            issues.append(f"missing non-claim: {item}")
    return {"passed": not issues, "issues": issues}


def _audit_boundary(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[str] = []
    for payload in payloads:
        boundary = payload.get("boundary", {}) if isinstance(payload.get("boundary"), dict) else {}
        for key in ["main_ledger_written", "run_daily_called", "network_access", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered", "forward_dry_run_started"]:
            if key in boundary and boundary.get(key) is not False:
                issues.append(f"{key} is not false")
    return {"passed": not issues, "issues": issues, "checked_paths": list(PROTECTED_PATHS)}


def _wording_paths(paths: ProjectPaths) -> list[Path]:
    return [
        paths.outputs_dir / "system" / "GLOBAL_BRIEFING_WARNING_TRIAGE.md",
        paths.outputs_dir / "system" / "GLOBAL_BRIEFING_EVIDENCE_QUALITY_REPORT.md",
        paths.outputs_dir / "system" / "GLOBAL_BRIEFING_PRODUCTION_ACCEPTANCE_CRITERIA.md",
        paths.project_root / "docs" / "GLOBAL_BRIEFING_PRODUCTION_ACCEPTANCE.md",
    ]


def _audit_wording(paths: list[Path]) -> dict[str, Any]:
    issues = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lowered = line.strip().lower()
            if not lowered or "not " in lowered or "does not " in lowered or "no " in lowered:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{path.name}:{line_number} contains forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def build_evidence_quality_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Global Briefing Evidence Quality Audit",
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
            "## Evidence Status",
            f"- {payload['evidence_status']}",
            "",
            "## Production Readiness",
            f"Production readiness: {str(payload['production_readiness']['ready']).lower()}",
            "",
            "## Boundary",
            "- This audit is evidence-quality only.",
            "- Production global-briefing historical package is not validated.",
            "- Strategy effectiveness is not proven.",
            "- Forward dry-run is not validated.",
            "- Live trading readiness is not certified.",
            "- Main ledger was not written.",
            "- run-daily CLI was not called.",
            "- No network access was used.",
            "",
            "## Release Recommendation",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended patch tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Patch tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)
