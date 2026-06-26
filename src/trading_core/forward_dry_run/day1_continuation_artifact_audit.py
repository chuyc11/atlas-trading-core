"""Audit the v0.6.3.1 day1 continuation artifact package."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import audit_report, read_json_file, system_json, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import (
    NEXT_VERSION,
    TARGET_VERSION,
    day_json,
    day2_executed,
    day3_executed,
    forbidden_wording_issues,
    markdown_boundary,
    paths_or_default,
    standard_boundary,
    v064_preflight,
)
from trading_core.storage.file_paths import ProjectPaths


def audit_day1_continuation_artifacts(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    artifacts = {
        "gap_analysis": system_json(paths, "forward_dry_run_day1_continuation_gap_analysis.json"),
        "day1_artifact_manifest": day_json(paths, "day1_artifact_manifest.json"),
        "day1_reproducibility_manifest": day_json(paths, "day1_reproducibility_manifest.json"),
        "day2_readiness_packet": day_json(paths, "day2_readiness_packet.json"),
        "day2_continuation_gate_preview": day_json(paths, "day2_continuation_gate_preview.json"),
    }
    payloads = {name: read_json_file(path) for name, path in artifacts.items()}
    blocking: list[str] = []
    for name, path in artifacts.items():
        if not path.exists() or not payloads[name]:
            blocking.append(f"{name}_missing")
    if payloads["gap_analysis"].get("overall_passed") is not True:
        blocking.append("gap_analysis_not_passed")
    if payloads["day1_artifact_manifest"].get("overall_passed") is not True:
        blocking.append("day1_artifact_manifest_not_passed")
    if payloads["day2_readiness_packet"].get("overall_passed") is not True:
        blocking.append("day2_readiness_packet_not_passed")
    if payloads["day2_continuation_gate_preview"].get("day2_continuation_structurally_eligible") is not True:
        blocking.append("day2_continuation_gate_preview_not_structurally_eligible")
    if not v064_preflight(paths):
        blocking.append("v064_blocking_preflight_missing")
    if day2_executed(paths):
        blocking.append("day2_executed=true")
    if day3_executed(paths):
        blocking.append("day3_executed=true")
    boundary = standard_boundary("continuation_artifacts_only")
    for key in ["main_ledger_written", "broker_connected", "real_orders_placed", "strategy_effectiveness_proven", "forward_dry_run_fully_validated", "live_trading_ready", "promotion_triggered"]:
        if any(payload.get("boundary", {}).get(key) is True for payload in payloads.values()):
            blocking.append(f"{key}=true")
    blocking.extend(forbidden_wording_issues(paths))
    payload: dict[str, Any] = {
        "audit_id": "FORWARD-DRY-RUN-DAY1-CONTINUATION-ARTIFACT-AUDIT",
        "release_candidate": TARGET_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "missing_continuation_artifacts_resolved": not blocking,
            "day2_readiness_packet_exists": artifacts["day2_readiness_packet"].exists(),
            "day2_continuation_gate_preview_exists": artifacts["day2_continuation_gate_preview"].exists(),
            "v064_blocking_preflight_absorbed": bool(v064_preflight(paths)),
            "recommended_next_version": NEXT_VERSION,
        },
        "boundary": {
            **boundary,
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
        },
    }
    return write_artifact(system_json(paths, "forward_dry_run_day1_continuation_artifact_audit.json"), payload, audit_report(paths, "FORWARD_DRY_RUN_DAY1_CONTINUATION_ARTIFACT_AUDIT.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Continuation Artifact Audit",
        "",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- recommended_next_version: {payload['summary']['recommended_next_version']}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

