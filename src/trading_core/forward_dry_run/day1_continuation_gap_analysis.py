"""Analyze the day1 continuation artifact gap before day2."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import audit_report, system_json, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import (
    BASELINE_TAG,
    CONTINUATION_ARTIFACTS,
    standard_boundary,
    day1_core_status,
    day2_executed,
    markdown_boundary,
    paths_or_default,
    project_path,
    v064_preflight,
)
from trading_core.storage.file_paths import ProjectPaths


def build_day1_continuation_gap_analysis(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    core = day1_core_status(paths)
    preflight = v064_preflight(paths)
    missing = [relative for relative in CONTINUATION_ARTIFACTS.values() if not project_path(paths, relative).exists()]
    preflight_missing = preflight.get("missing_required_artifacts", [])
    blocking = list(core["blocking_reasons"])
    if not preflight:
        blocking.append("v064_blocking_preflight_missing")
    payload: dict[str, Any] = {
        "analysis_id": "FORWARD-DRY-RUN-DAY1-CONTINUATION-GAP-ANALYSIS",
        "baseline_tag": BASELINE_TAG,
        "day1_core_execution_passed": core["overall_passed"],
        "v064_preflight_blocked": preflight.get("overall_passed") is False if preflight else False,
        "missing_artifacts": missing,
        "v064_preflight_missing_artifacts": preflight_missing,
        "missing_artifacts_derivable": core["overall_passed"] and set(missing).issubset(set(CONTINUATION_ARTIFACTS.values())),
        "day2_should_remain_blocked_until_artifacts_generated": bool(missing),
        "day2_execution_allowed_in_this_stage": False,
        "day2_executed": day2_executed(paths),
        "run_daily_called": False,
        "main_ledger_written": False,
        "overall_passed": not blocking and core["overall_passed"],
        "blocking_reasons": blocking,
        "boundary": standard_boundary("analysis_only"),
    }
    payload["boundary"]["analysis_only"] = True
    return write_artifact(system_json(paths, "forward_dry_run_day1_continuation_gap_analysis.json"), payload, audit_report(paths, "FORWARD_DRY_RUN_DAY1_CONTINUATION_GAP_ANALYSIS.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Continuation Gap Analysis",
        "",
        f"- baseline_tag: {payload['baseline_tag']}",
        f"- day1_core_execution_passed: {str(payload['day1_core_execution_passed']).lower()}",
        f"- v064_preflight_blocked: {str(payload['v064_preflight_blocked']).lower()}",
        f"- missing_artifacts_derivable: {str(payload['missing_artifacts_derivable']).lower()}",
        "- day2_execution_allowed_in_this_stage: false",
        "",
        "## Missing Artifacts",
    ]
    lines.extend(f"- {item}" for item in payload["missing_artifacts"])
    lines.extend(["", "## Boundary", *markdown_boundary(), ""])
    return "\n".join(lines)

