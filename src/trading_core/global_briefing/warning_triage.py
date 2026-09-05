"""Warning triage for v0.5.6 real-package-style artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


CATEGORIES = [
    "fixture_expected",
    "coverage_gap",
    "pit_ambiguity",
    "stale_signal_risk",
    "data_quality",
    "adapter_limitation",
    "documentation_only",
    "unknown",
]
PRODUCTION_COVERAGE_THRESHOLD = 0.80


def build_global_briefing_warning_triage(
    *,
    coverage_path: str | None = None,
    workflow_path: str | None = None,
    report_path: str | None = None,
    audit_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    triage_id, created_at = timestamp_id("GB-WARNING-TRIAGE")
    files = {
        "coverage": _resolve_or_default(coverage_path, paths.data_dir / "system" / "global_briefing_package_coverage_audit.json", paths),
        "workflow": _resolve_or_latest(workflow_path, paths.data_dir / "replays" / "global_briefing", "real_package_replay_workflow-*.json", paths),
        "report": _resolve_or_default(report_path, paths.data_dir / "system" / "global_briefing_real_package_integration_report.json", paths),
        "audit": _resolve_or_default(audit_path, paths.data_dir / "system" / "global_briefing_real_package_integration_audit.json", paths),
    }
    artifacts = {name: _read_optional(path) for name, path in files.items()}
    warnings = _collect_warnings(artifacts)
    coverage_ratio = _coverage_ratio(artifacts["coverage"], artifacts["report"])
    current_package = artifacts["report"].get("selected_package") or "GB-REAL-FIXTURE"
    triaged = [_triage_warning(item, coverage_ratio=coverage_ratio, current_package=str(current_package)) for item in warnings]
    production_blockers = _production_blockers(triaged, coverage_ratio)
    by_category = dict.fromkeys(CATEGORIES, 0)
    for item in triaged:
        by_category[item["category"]] += 1

    payload: dict[str, Any] = {
        "triage_id": triage_id,
        "created_at": created_at,
        "source_files": {name: str(path) if path is not None else None for name, path in files.items()},
        "current_package": current_package,
        "coverage_ratio": coverage_ratio,
        "warning_count": len(triaged),
        "by_category": by_category,
        "warnings": triaged,
        "production_blockers": production_blockers,
        "boundary": {
            "triage_only": True,
            "replay_started": False,
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
    json_path = paths.data_dir / "system" / "global_briefing_warning_triage.json"
    md_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_WARNING_TRIAGE.md"
    write_json_markdown(json_path, payload, md_path, build_warning_triage_markdown(payload))
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


def _read_optional(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def _collect_warnings(artifacts: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    workflow_messages = {str(item) for item in artifacts.get("workflow", {}).get("warnings", [])}
    for source in ["coverage", "workflow"]:
        rows.extend({"source": source, "message": str(item)} for item in artifacts.get(source, {}).get("warnings", []))
    # The v0.5.6 integration report carries workflow warnings forward. Keep any report-only warnings,
    # but do not double count the copied workflow list.
    for item in artifacts.get("report", {}).get("warnings", []):
        message = str(item)
        if message not in workflow_messages:
            rows.append({"source": "report", "message": message})
    rows.extend({"source": "audit", "message": str(item)} for item in artifacts.get("audit", {}).get("warnings", []))
    return rows


def _coverage_ratio(coverage: dict[str, Any], report: dict[str, Any]) -> float | None:
    value = coverage.get("coverage", {}).get("coverage_ratio")
    if value is None:
        value = report.get("coverage_ratio")
    return float(value) if isinstance(value, int | float) else None


def _triage_warning(item: dict[str, str], *, coverage_ratio: float | None, current_package: str) -> dict[str, Any]:
    message = item["message"]
    category = categorize_warning(message)
    severity = severity_for_warning(message, category, coverage_ratio=coverage_ratio, current_package=current_package)
    return {
        "source": item["source"],
        "category": category,
        "severity": severity,
        "message": message,
        "blocking": False,
        "recommended_action": recommended_action(category, severity),
    }


def categorize_warning(message: str) -> str:
    lowered = message.lower()
    if "future signal leakage" in lowered or "future_signal" in lowered:
        return "pit_ambiguity"
    if any(token in lowered for token in ["fixture", "test", "synthetic"]):
        return "fixture_expected"
    if any(token in lowered for token in ["coverage", "missing day", "missing signal", "missing signal dates", "duplicate signal", "ratio"]):
        return "coverage_gap"
    if any(token in lowered for token in ["generated_at", "timezone", "timestamp", "decision time", "point-in-time"]):
        return "pit_ambiguity"
    if any(token in lowered for token in ["carry-forward", "carry forward", "stale", "old signal"]):
        return "stale_signal_risk"
    if any(token in lowered for token in ["adapter", "fallback", "skipped trade", "lot size", "missing price", "no order generated", "execution mode"]):
        return "adapter_limitation"
    if any(token in lowered for token in ["malformed", "missing field", "null", "invalid value", "signals empty", "kept as string", "unknown signal fields", "unknown fields"]):
        return "data_quality"
    if any(token in lowered for token in ["docs", "wording", "limitation"]):
        return "documentation_only"
    return "unknown"


def severity_for_warning(message: str, category: str, *, coverage_ratio: float | None, current_package: str) -> str:
    lowered = message.lower()
    if "future signal leakage" in lowered or "future_signal" in lowered:
        return "high"
    if category == "pit_ambiguity":
        return "high"
    if category == "coverage_gap":
        if coverage_ratio is not None and coverage_ratio < PRODUCTION_COVERAGE_THRESHOLD:
            return "medium" if current_package == "GB-REAL-FIXTURE" else "high"
        return "medium"
    if category == "unknown":
        return "medium"
    if category == "documentation_only":
        return "low"
    if category == "fixture_expected":
        return "low"
    return "medium"


def recommended_action(category: str, severity: str) -> str:
    if category == "coverage_gap":
        return "raise_min_coverage_for_production_package"
    if category == "pit_ambiguity":
        return "verify_generated_at_timezone_and_decision_time"
    if category == "stale_signal_risk":
        return "tighten_carry_forward_policy_before_production"
    if category == "adapter_limitation":
        return "inspect_replay_adapter_inputs_and_price_coverage"
    if category == "data_quality":
        return "fix_package_schema_or_field_values"
    if category == "documentation_only":
        return "clarify_report_wording"
    if category == "fixture_expected":
        return "replace_fixture_with_production_historical_package"
    if severity == "high":
        return "block_production_package_until_resolved"
    return "manual_review_required"


def _production_blockers(warnings: list[dict[str, Any]], coverage_ratio: float | None) -> list[str]:
    blockers: list[str] = []
    if coverage_ratio is not None and coverage_ratio < PRODUCTION_COVERAGE_THRESHOLD:
        blockers.append(f"coverage ratio {coverage_ratio} is below production minimum {PRODUCTION_COVERAGE_THRESHOLD}")
    if any("future signal leakage" in item["message"].lower() or "future_signal" in item["message"].lower() for item in warnings):
        blockers.append("future signal leakage warning present")
    if any(item["category"] == "pit_ambiguity" and item["severity"] == "high" for item in warnings):
        blockers.append("high severity point-in-time ambiguity warning present")
    return blockers


def build_warning_triage_markdown(payload: dict[str, Any]) -> str:
    category_lines = [f"- {category}: {count}" for category, count in payload["by_category"].items()]
    action_lines = sorted({f"- {item['recommended_action']}" for item in payload["warnings"]}) or ["- none"]
    return "\n".join(
        [
            "# Global Briefing Warning Triage",
            "",
            "## Scope",
            "This report triages warnings from v0.5.6 real-package-style integration artifacts.",
            "",
            "GB-REAL-FIXTURE is not a production global-briefing package.",
            "",
            "## Warning Summary",
            f"- warning_count={payload['warning_count']}",
            f"- coverage_ratio={payload['coverage_ratio']}",
            "",
            "## Warning Categories",
            *category_lines,
            "",
            "## Production Blockers",
            *([f"- {item}" for item in payload["production_blockers"]] if payload["production_blockers"] else ["- none for fixture validation; production acceptance remains blocked until thresholds are met"]),
            "",
            "## Recommended Actions",
            *action_lines,
            "",
            "## Boundary",
            "- triage only",
            "- no replay started",
            "- no run-daily call",
            "- no main ledger write",
            "- no network access",
            "",
        ]
    )
