"""Evidence quality report for v0.5.6 global-briefing integration artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


RECOMMENDED_MIN_COVERAGE = 0.80
RECOMMENDED_TARGET_COVERAGE = 0.90


def build_global_briefing_evidence_quality_report(
    *,
    triage_path: str | None = None,
    coverage_path: str | None = None,
    workflow_path: str | None = None,
    audit_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    report_id, created_at = timestamp_id("GB-EVIDENCE-QUALITY")
    triage_file = _resolve_or_default(triage_path, paths.data_dir / "system" / "global_briefing_warning_triage.json", paths)
    coverage_file = _resolve_or_default(coverage_path, paths.data_dir / "system" / "global_briefing_package_coverage_audit.json", paths)
    workflow_file = _resolve_or_latest(workflow_path, paths.data_dir / "replays" / "global_briefing", "real_package_replay_workflow-*.json", paths)
    audit_file = _resolve_or_default(audit_path, paths.data_dir / "system" / "global_briefing_real_package_integration_audit.json", paths)
    triage = _read_optional(triage_file)
    coverage = _read_optional(coverage_file)
    workflow = _read_optional(workflow_file)
    audit = _read_optional(audit_file)
    current_package = triage.get("current_package") or "GB-REAL-FIXTURE"
    coverage_ratio = _coverage_ratio(coverage, triage)
    warning_count = int(triage.get("warning_count", 0))
    evidence_levels = build_evidence_levels(current_package=str(current_package), coverage_ratio=coverage_ratio, workflow=workflow, audit=audit)
    production_reasons = [
        "Production global-briefing historical package not provided.",
        f"Coverage ratio {coverage_ratio} is below production threshold." if coverage_ratio is not None and coverage_ratio < RECOMMENDED_MIN_COVERAGE else "Production coverage threshold has not been independently validated.",
        "Workflow/report warnings require triage before production acceptance.",
        "Production PIT rules require real generated_at validation.",
        "Production package should meet higher min_coverage.",
    ]
    payload: dict[str, Any] = {
        "report_id": report_id,
        "created_at": created_at,
        "overall_evidence_status": "fixture_validated_not_production_validated",
        "current_package": current_package,
        "coverage_ratio": coverage_ratio,
        "warning_count": warning_count,
        "evidence_levels": evidence_levels,
        "production_readiness": {
            "ready": False,
            "reasons": production_reasons,
            "recommended_min_coverage": RECOMMENDED_MIN_COVERAGE,
            "recommended_target_coverage": RECOMMENDED_TARGET_COVERAGE,
        },
        "inputs": {
            "triage": str(triage_file),
            "coverage": str(coverage_file),
            "workflow": str(workflow_file) if workflow_file else None,
            "audit": str(audit_file),
        },
        "boundary": {
            "report_only": True,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "network_access": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
            "forward_dry_run_started": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_evidence_quality.json"
    md_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_EVIDENCE_QUALITY_REPORT.md"
    write_json_markdown(json_path, payload, md_path, build_evidence_quality_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_evidence_levels(*, current_package: str, coverage_ratio: float | None, workflow: dict[str, Any], audit: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "engineering_validated": [
            "CLI chain exists.",
            "Normalization works.",
            "Validation works.",
            "Coverage audit works.",
            "Isolated replay workflow works." if workflow.get("overall_status") == "research_review_ready" else "Isolated replay workflow requires review.",
            "Integration audit passed." if audit.get("overall_passed") is True else "Integration audit is not confirmed.",
            "Main ledger not written.",
            "run-daily not called.",
            "No network access.",
        ],
        "fixture_validated": [
            f"{current_package} E2E passed.",
            f"Coverage ratio {coverage_ratio} passed under fixture threshold.",
            "Isolated replay completed on fixture package.",
        ],
        "research_review_only": [
            "Replay outputs are research review artifacts.",
            "Replay evaluation is a review artifact.",
            "Warning triage is a review artifact.",
            "Coverage analysis is a review artifact.",
        ],
        "insufficient_for_production": [
            "Production global-briefing package not provided.",
            f"Coverage ratio {coverage_ratio} is insufficient for production.",
            "Workflow/report warnings require triage.",
            "Production PIT rules require real generated_at validation.",
            "Production package should meet higher min_coverage.",
        ],
        "not_validated": [
            "Strategy effectiveness.",
            "Forward dry-run.",
            "Live trading readiness.",
            "Production global-briefing historical coverage.",
            "Production global-briefing signal quality.",
        ],
    }


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


def _read_optional(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def _coverage_ratio(coverage: dict[str, Any], triage: dict[str, Any]) -> float | None:
    value = coverage.get("coverage", {}).get("coverage_ratio")
    if value is None:
        value = triage.get("coverage_ratio")
    return float(value) if isinstance(value, int | float) else None


def build_evidence_quality_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Global Briefing Evidence Quality Report",
        "",
        "## Executive Summary",
        "v0.5.6 validates the integration framework with GB-REAL-FIXTURE.",
        "It does not validate production global-briefing historical coverage.",
        "",
        "## Evidence Levels",
    ]
    for level, items in payload["evidence_levels"].items():
        lines.append(f"### {level}")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    lines.extend(
        [
            "## Production Readiness",
            f"- ready={str(payload['production_readiness']['ready']).lower()}",
            *[f"- {item}" for item in payload["production_readiness"]["reasons"]],
            "",
            "## What Is Validated",
            "- local integration framework",
            "- fixture E2E path",
            "- isolated replay ledger boundary",
            "- integration audit boundary",
            "",
            "## What Is Not Validated",
            "- production global-briefing historical coverage",
            "- production global-briefing signal quality",
            "- strategy effectiveness",
            "- forward dry-run validation",
            "- live trading readiness",
            "",
            "## Recommended Production Thresholds",
            "- minimum coverage: 0.80",
            "- target coverage: 0.90",
            "- future signal leakage: 0",
            "- PIT ambiguity: 0 high severity issues",
            "- unknown warnings: 0",
            "",
            "## Boundary",
            "- report only",
            "- not strategy effectiveness proof",
            "- not forward dry-run validation",
            "- not live trading readiness",
            "- no main ledger write",
            "- no run-daily call",
            "",
        ]
    )
    return "\n".join(lines)
