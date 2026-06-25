"""Reclassify day-1 blockers after the baseline strategy pack audit."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import read_dict, rel
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown
from trading_core.strategies.common import NEXT_VERSION, RESEARCH_NOTICE, paths_or_default, research_boundary


def reclassify_day1_blockers_after_baseline_strategies(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    reclassification_id, created_at = timestamp_id("DAY1-BLOCKER-RECLASSIFICATION-V060")
    mvp_gap_path = paths.data_dir / "system" / "mvp_gap_classification.json"
    v059_path = paths.data_dir / "system" / "day1_blocker_reclassification_v059.json"
    audit_path = paths.data_dir / "system" / "baseline_strategy_pack_audit.json"
    mvp_gap = read_dict(mvp_gap_path)
    v059 = read_dict(v059_path)
    audit = read_dict(audit_path)
    baseline_closed = (
        audit.get("overall_passed") is True
        and audit.get("summary", {}).get("all_strategies_complete") is True
        and not audit.get("blocking_reasons")
    )
    previous_count = int(v059.get("updated_day1_blocker_count", v059.get("baseline_day1_blocker_count", 0)) or 0)
    updated_count = 0 if baseline_closed and previous_count == 0 else max(previous_count, 1)
    payload: dict[str, Any] = {
        "reclassification_id": reclassification_id,
        "created_at": created_at,
        "input_artifacts": {
            "mvp_gap_classification": rel(mvp_gap_path, paths) if mvp_gap_path.exists() else None,
            "day1_blocker_reclassification_v059": rel(v059_path, paths) if v059_path.exists() else None,
            "baseline_strategy_pack_audit": rel(audit_path, paths) if audit_path.exists() else None,
        },
        "mvp_gap_classification_loaded": bool(mvp_gap),
        "baseline_day1_blocker_count": int(v059.get("baseline_day1_blocker_count", 0) or 0),
        "v059_updated_day1_blocker_count": previous_count,
        "baseline_strategy_blocker_closed": baseline_closed,
        "updated_day1_blocker_count": updated_count,
        "recommended_next_version": NEXT_VERSION,
        "day1_start_allowed": False,
        "day1_start_denied_reason": "future start authorization pack and daily workflow binding are still required",
        "forward_dry_run_started": False,
        "run_daily_called": False,
        "main_ledger_written": False,
        "boundary": research_boundary("reclassification_only"),
    }
    json_path = paths.data_dir / "system" / "day1_blocker_reclassification_v060.json"
    md_path = paths.outputs_dir / "system" / "DAY1_BLOCKER_RECLASSIFICATION_V060.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Blocker Reclassification V060",
        "",
        RESEARCH_NOTICE,
        "",
        "## Summary",
        f"- baseline_strategy_blocker_closed: {str(payload['baseline_strategy_blocker_closed']).lower()}",
        f"- updated_day1_blocker_count: {payload['updated_day1_blocker_count']}",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "- day1_start_allowed=false",
        "",
        "## Boundary",
        "- reclassification only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "",
    ]
    return "\n".join(lines)

