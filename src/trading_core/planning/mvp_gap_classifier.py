"""Classify MVP gaps from checklist, requirement map, and artifact scan."""

from __future__ import annotations

from typing import Any

from trading_core.planning.artifact_coverage_scanner import build_artifact_coverage_scan
from trading_core.planning.common import VALID_GAP_STATUSES, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.planning.mvp_requirement_map import build_mvp_requirement_map
from trading_core.planning.plan_checklist_extractor import build_plan_checklist
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


CRITICAL_DAY1_IDS = {
    "R001",
    "R003",
    "R004",
    "R005",
    "R006",
    "R007",
    "R008",
    "R010",
    "R011",
    "R012",
    "R013",
    "R014",
    "R015",
    "R017",
    "R019",
    "R020",
    "R021",
    "R024",
}
CURRENT_ACCEPTED_PARTIAL = {"R004", "R014", "R018"}
CURRENT_FORCE_PARTIAL = {"R004", "R006", "R007", "R008", "R009", "R014", "R016", "R018"}
CURRENT_FORCE_PASSED = {"R001", "R003", "R005", "R010", "R011", "R012", "R013", "R015", "R017", "R019", "R020", "R021", "R022", "R023", "R024"}
DEFERRED_IDS = set()


def classify_mvp_gaps(
    *,
    checklist_path: str | None = None,
    requirement_map_path: str | None = None,
    artifact_scan_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    classification_id, created_at = timestamp_id("MVP-GAP-CLASSIFICATION")
    checklist_file = resolve_path(checklist_path, paths.data_dir / "system" / "plan_checklist.json", paths)
    map_file = resolve_path(requirement_map_path, paths.data_dir / "system" / "mvp_requirement_map.json", paths)
    scan_file = resolve_path(artifact_scan_path, paths.data_dir / "system" / "artifact_coverage_scan.json", paths)
    checklist = read_dict(checklist_file) or build_plan_checklist(paths=paths)
    requirement_map = read_dict(map_file) or build_mvp_requirement_map(paths=paths)
    artifact_scan = read_dict(scan_file) or build_artifact_coverage_scan(paths=paths)
    map_by_id = {item["requirement_id"]: item for item in requirement_map.get("requirements", [])}
    requirements = []
    for requirement in checklist.get("requirements", []):
        mapped = map_by_id.get(requirement["requirement_id"], {})
        classified = _classify_requirement(requirement, mapped)
        requirements.append(classified)
    summary = {status: sum(1 for item in requirements if item["status"] == status) for status in VALID_GAP_STATUSES}
    summary["day1_blockers"] = sum(1 for item in requirements if item["day1_blocker"])
    summary["requirements_total"] = len(requirements)
    payload: dict[str, Any] = {
        "classification_id": classification_id,
        "created_at": created_at,
        "checklist_path": rel(checklist_file, paths),
        "requirement_map_path": rel(map_file, paths),
        "artifact_scan_path": rel(scan_file, paths),
        "artifact_counts": artifact_scan.get("counts", {}),
        "summary": summary,
        "requirements": requirements,
        "boundary": standard_boundary("classification_only"),
    }
    json_path = paths.data_dir / "system" / "mvp_gap_classification.json"
    md_path = paths.outputs_dir / "system" / "MVP_GAP_CLASSIFICATION.md"
    write_json_markdown(json_path, payload, md_path, build_mvp_gap_classification_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _classify_requirement(requirement: dict[str, Any], mapped: dict[str, Any]) -> dict[str, Any]:
    requirement_id = requirement["requirement_id"]
    evidence = mapped.get("candidate_evidence", [])
    evidence_types = {item.get("type") for item in evidence if item.get("exists")}
    if requirement_id in DEFERRED_IDS:
        status = "deferred"
        rationale = "Explicitly deferred from current MVP day-1 authorization path."
    elif requirement_id in CURRENT_FORCE_PASSED and evidence_types:
        status = "passed"
        rationale = "Detected current implementation, tests, artifacts, or boundary audit evidence."
    elif requirement_id in CURRENT_FORCE_PARTIAL:
        status = "partial"
        rationale = _partial_rationale(requirement_id)
    elif {"module", "test"} <= evidence_types and evidence_types & {"artifact", "audit", "report", "doc", "release_tag"}:
        status = "passed"
        rationale = "Detected module, tests, and artifact/report evidence."
    elif evidence_types:
        status = "partial"
        rationale = "Detected partial repo evidence but not a complete module/test/artifact chain."
    else:
        status = "missing"
        rationale = "No clear repo evidence detected."
    accepted_partial = requirement_id in CURRENT_ACCEPTED_PARTIAL
    day1_blocker = requirement_id in CRITICAL_DAY1_IDS and status not in {"passed", "deferred", "not_applicable"} and not accepted_partial
    return {
        "requirement_id": requirement_id,
        "name": requirement["name"],
        "category": requirement["category"],
        "status": status,
        "accepted_partial": accepted_partial,
        "day1_blocker": day1_blocker,
        "rationale": rationale,
        "evidence_count": len(evidence),
        "manual_review_required": mapped.get("manual_review_required", True),
    }


def _partial_rationale(requirement_id: str) -> str:
    return {
        "R004": "Adjusted price handling exists in data tooling but needs explicit day-1 acceptance wording.",
        "R006": "Replay/execution adapter evidence exists, but explicit future day-1 T/T+1 acceptance remains incomplete.",
        "R007": "Market rule evidence exists, but suspension handling is not yet a dedicated day-1 hardening artifact.",
        "R008": "Market rule evidence exists, but A-share limit up/down handling needs explicit day-1 hardening.",
        "R009": "ST/new listing handling remains a scoped limitation rather than a complete MVP gate.",
        "R014": "Equity curve/reporting evidence exists, but forward dry-run use remains unvalidated.",
        "R016": "Baseline strategy modules exist, but a dedicated baseline strategy pack is not complete.",
        "R018": "Versioning exists through release tags and docs, but parameter/data/code binding can be strengthened.",
    }.get(requirement_id, "Partial evidence detected.")


def build_mvp_gap_classification_markdown(payload: dict[str, Any]) -> str:
    lines = ["# MVP Gap Classification", "", "## Summary"]
    lines.extend(f"- {key}: {value}" for key, value in payload["summary"].items())
    for status in ["passed", "partial", "missing", "deferred", "not_applicable"]:
        lines.extend(["", f"## {status.replace('_', ' ').title()}"])
        lines.extend(f"- {item['requirement_id']} {item['name']}" for item in payload["requirements"] if item["status"] == status)
    lines.extend(["", "## Day-1 Blockers"])
    blockers = [item for item in payload["requirements"] if item["day1_blocker"]]
    lines.extend(f"- {item['requirement_id']} {item['name']}: {item['rationale']}" for item in blockers)
    if not blockers:
        lines.append("- none")
    lines.extend(["", "## Boundary", "- classification only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)
