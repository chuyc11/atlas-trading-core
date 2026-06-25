"""Reclassify day-1 blockers after v0.5.9 execution hardening."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, read_dict, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


EXECUTION_ARTIFACTS = {
    "ashare_trading_calendar_audit": "ashare_trading_calendar_audit.json",
    "execution_timeline_contract": "execution_timeline_contract.json",
    "ashare_price_status_contract": "ashare_price_status_contract.json",
    "ashare_lot_position_contract": "ashare_lot_position_contract.json",
    "ashare_execution_cost_contract": "ashare_execution_cost_contract.json",
    "virtual_execution_contract": "virtual_execution_contract.json",
    "isolated_ledger_invariant_audit": "isolated_ledger_invariant_audit.json",
    "execution_aware_replay_smoke": "execution_aware_replay_smoke.json",
}


def reclassify_day1_blockers_after_execution_hardening(*, baseline_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    reclassification_id, created_at = timestamp_id("DAY1-BLOCKER-RECLASSIFICATION-V059")
    baseline_file = resolve_path(baseline_path, paths.data_dir / "system" / "day1_blocker_classification.json", paths)
    baseline = read_dict(baseline_file)
    artifacts = {key: read_dict(paths.data_dir / "system" / name) for key, name in EXECUTION_ARTIFACTS.items()}
    evidence_passed = _evidence_passed(artifacts)
    closed = []
    still_open = []
    for blocker in baseline.get("blockers", []):
        record = {**blocker, "reclassification": "closed" if evidence_passed else "still_open"}
        if evidence_passed:
            closed.append(record)
        else:
            still_open.append(record)
    updated_count = len(still_open)
    payload: dict[str, Any] = {
        "reclassification_id": reclassification_id,
        "created_at": created_at,
        "baseline_path": rel(baseline_file, paths),
        "baseline_day1_blocker_count": int(baseline.get("blocking_count", len(baseline.get("blockers", []))) or 0),
        "updated_day1_blocker_count": updated_count,
        "closed_blockers": closed,
        "still_open_blockers": still_open,
        "accepted_manual_review": baseline.get("requires_manual_acceptance", []),
        "replaced_by_new_blocker": [],
        "recommended_next_version": "v0.6.0-baseline-strategy-pack" if updated_count == 0 else "v0.5.9-ashare-execution-rules-hardening",
        "day1_start_allowed": False,
        "day1_start_denied_reason": "baseline strategy pack and daily workflow binding still not completed",
        "execution_artifacts": {key: bool(value) for key, value in artifacts.items()},
        "boundary": standard_boundary("reclassification_only"),
    }
    json_path = paths.data_dir / "system" / "day1_blocker_reclassification_v059.json"
    md_path = paths.outputs_dir / "system" / "DAY1_BLOCKER_RECLASSIFICATION_V059.md"
    write_json_markdown(json_path, payload, md_path, build_reclassification_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _evidence_passed(artifacts: dict[str, dict[str, Any]]) -> bool:
    required_present = all(bool(value) for value in artifacts.values())
    if not required_present:
        return False
    return (
        artifacts["ashare_trading_calendar_audit"].get("overall_passed") is True
        and artifacts["isolated_ledger_invariant_audit"].get("overall_passed") is True
        and artifacts["execution_aware_replay_smoke"].get("overall_passed") is True
        and artifacts["execution_timeline_contract"].get("same_day_close_signal_execution_rejected") is True
        and artifacts["ashare_price_status_contract"].get("suspension_missing_limit_handled") is True
    )


def build_reclassification_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Day-1 Blocker Reclassification V059", "", "## Scope", "This reclassifies v0.5.8.1 day-1 execution blockers after v0.5.9 hardening.", HARDENING_NOTICE, "", "## Summary", f"- baseline_day1_blocker_count: {payload['baseline_day1_blocker_count']}", f"- updated_day1_blocker_count: {payload['updated_day1_blocker_count']}", f"- recommended_next_version: {payload['recommended_next_version']}", "", "## Closed Blockers"]
    if payload["closed_blockers"]:
        lines.extend(f"- {item.get('requirement_id')} {item.get('blocker_id')}" for item in payload["closed_blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Boundary", "- reclassification only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)
