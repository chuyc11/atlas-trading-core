"""Map MVP requirements to candidate evidence in the current repo."""

from __future__ import annotations

from typing import Any

from trading_core.planning.common import VALID_EVIDENCE_TYPES, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.planning.plan_checklist_extractor import build_plan_checklist
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


EVIDENCE_HINTS: dict[str, list[dict[str, str]]] = {
    "R001": [{"type": "module", "path": "src/trading_core/calendar"}, {"type": "test", "path": "tests/test_calendar.py"}, {"type": "cli", "path": "src/trading_core/cli.py"}],
    "R002": [{"type": "module", "path": "src/trading_core/universe"}, {"type": "test", "path": "tests/test_universe.py"}],
    "R003": [{"type": "module", "path": "src/trading_core/data"}, {"type": "test", "path": "tests/test_historical_data_downloaders.py"}, {"type": "artifact", "path": "data/system/historical_data_quality_audit.json"}],
    "R004": [{"type": "module", "path": "src/trading_core/data/price_dataset_merge.py"}, {"type": "test", "path": "tests/test_price_dataset_merge.py"}],
    "R005": [{"type": "module", "path": "src/trading_core/data"}, {"type": "test", "path": "tests/test_point_in_time.py"}],
    "R006": [{"type": "module", "path": "src/trading_core/global_briefing/isolated_replay_execution.py"}, {"type": "test", "path": "tests/test_isolated_replay_execution.py"}],
    "R007": [{"type": "module", "path": "src/trading_core/broker/market_rules.py"}, {"type": "test", "path": "tests/test_market_rules.py"}],
    "R008": [{"type": "module", "path": "src/trading_core/broker/market_rules.py"}, {"type": "test", "path": "tests/test_market_rules.py"}],
    "R009": [{"type": "module", "path": "src/trading_core/universe"}, {"type": "doc", "path": "docs/SAFETY_BOUNDARY.md"}],
    "R010": [{"type": "module", "path": "src/trading_core/broker/market_rules.py"}, {"type": "test", "path": "tests/test_market_rules.py"}, {"type": "artifact", "path": "data/system/day0_accepted_warning_register.json"}],
    "R011": [{"type": "module", "path": "src/trading_core/broker/cost_model.py"}, {"type": "test", "path": "tests/test_cost_model.py"}],
    "R012": [{"type": "module", "path": "src/trading_core/accounting"}, {"type": "test", "path": "tests/test_accounting.py"}, {"type": "test", "path": "tests/test_consistency_checker.py"}],
    "R013": [{"type": "module", "path": "src/trading_core/daily_run.py"}, {"type": "test", "path": "tests/test_end_to_end_daily_run.py"}],
    "R014": [{"type": "module", "path": "src/trading_core/reports"}, {"type": "test", "path": "tests/test_dry_run_validation_report.py"}],
    "R015": [{"type": "module", "path": "src/trading_core/benchmarks"}, {"type": "test", "path": "tests/test_benchmark_engine.py"}],
    "R016": [{"type": "module", "path": "src/trading_core/strategy"}, {"type": "test", "path": "tests/test_strategy_comparison.py"}],
    "R017": [{"type": "module", "path": "src/trading_core/daily_run.py"}, {"type": "test", "path": "tests/test_end_to_end_daily_run.py"}, {"type": "doc", "path": "docs/RUNBOOK.md"}],
    "R018": [{"type": "doc", "path": "VERSION"}, {"type": "release_tag", "path": ".git/refs/tags/v0.5.8-day0-operational-readiness-audited"}],
    "R019": [{"type": "audit", "path": "outputs/audit/DAY0_READINESS_AUDIT.md"}, {"type": "test", "path": "tests/test_day0_readiness_audit.py"}],
    "R020": [{"type": "module", "path": "src/trading_core/global_briefing/isolated_replay_adapter_audit.py"}, {"type": "test", "path": "tests/test_isolated_replay_adapter_audit.py"}],
    "R021": [{"type": "audit", "path": "outputs/audit/DAY0_READINESS_AUDIT.md"}, {"type": "doc", "path": "docs/SAFETY_BOUNDARY.md"}],
    "R022": [{"type": "audit", "path": "outputs/audit/DAY0_READINESS_AUDIT.md"}, {"type": "doc", "path": "docs/FORWARD_DRY_RUN_DAY0_READINESS.md"}],
    "R023": [{"type": "module", "path": "src/trading_core/experiments/promotion_simulation.py"}, {"type": "test", "path": "tests/test_promotion_simulation.py"}],
    "R024": [{"type": "artifact", "path": "data/system/forward_dry_run_operating_calendar.json"}, {"type": "report", "path": "outputs/system/FORWARD_DRY_RUN_OPERATING_CALENDAR.md"}, {"type": "test", "path": "tests/test_forward_dry_run_operating_calendar.py"}],
}


def build_mvp_requirement_map(*, checklist_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    map_id, created_at = timestamp_id("MVP-REQUIREMENT-MAP")
    checklist_file = resolve_path(checklist_path, paths.data_dir / "system" / "plan_checklist.json", paths)
    checklist = read_dict(checklist_file)
    if not checklist:
        checklist = build_plan_checklist(paths=paths)
    entries = []
    for requirement in checklist.get("requirements", []):
        requirement_id = requirement["requirement_id"]
        hints = EVIDENCE_HINTS.get(requirement_id, [])
        candidate_evidence = [_evidence_record(hint, paths) for hint in hints]
        entries.append(
            {
                "requirement_id": requirement_id,
                "name": requirement["name"],
                "expected_evidence": requirement.get("evidence_expected", []),
                "candidate_evidence": candidate_evidence,
                "missing_evidence": [item["path"] for item in candidate_evidence if not item["exists"]],
                "manual_review_required": any(not item["exists"] or item["confidence"] != "high" for item in candidate_evidence),
            }
        )
    payload: dict[str, Any] = {
        "map_id": map_id,
        "created_at": created_at,
        "checklist_path": rel(checklist_file, paths),
        "valid_evidence_types": sorted(VALID_EVIDENCE_TYPES),
        "requirements": entries,
        "boundary": standard_boundary("requirement_map_only"),
    }
    json_path = paths.data_dir / "system" / "mvp_requirement_map.json"
    md_path = paths.outputs_dir / "system" / "MVP_REQUIREMENT_MAP.md"
    write_json_markdown(json_path, payload, md_path, build_mvp_requirement_map_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _evidence_record(hint: dict[str, str], paths: ProjectPaths) -> dict[str, Any]:
    path = paths.project_root / hint["path"]
    exists = path.exists()
    confidence = "high" if exists and hint["type"] in {"test", "audit", "artifact", "report"} else "medium" if exists else "missing"
    return {"type": hint["type"], "path": rel(path, paths), "exists": exists, "confidence": confidence}


def build_mvp_requirement_map_markdown(payload: dict[str, Any]) -> str:
    lines = ["# MVP Requirement Map", "", "## Scope", "This map links checklist requirements to candidate repo evidence.", "It does not start forward dry-run.", "", "## Requirements"]
    for item in payload["requirements"]:
        lines.append(f"- {item['requirement_id']} {item['name']}: evidence={len(item['candidate_evidence'])} missing={len(item['missing_evidence'])} manual_review_required={str(item['manual_review_required']).lower()}")
    lines.extend(["", "## Boundary", "- requirement map only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

