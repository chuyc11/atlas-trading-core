"""Build a day2 readiness packet from completed day1 artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import day_json, day_report, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest
from trading_core.forward_dry_run.day1_continuation_common import day1_core_status, day2_executed, markdown_boundary, paths_or_default
from trading_core.forward_dry_run.day1_continuation_gap_analysis import build_day1_continuation_gap_analysis
from trading_core.forward_dry_run.day1_reproducibility_manifest import build_day1_reproducibility_manifest
from trading_core.storage.file_paths import ProjectPaths


def build_day2_readiness_packet(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if not day_json(paths, "day1_artifact_manifest.json").exists():
        build_day1_artifact_manifest(paths=paths)
    if not day_json(paths, "day1_reproducibility_manifest.json").exists():
        build_day1_reproducibility_manifest(paths=paths)
    gap_path = paths.data_dir / "system" / "forward_dry_run_day1_continuation_gap_analysis.json"
    if not gap_path.exists():
        build_day1_continuation_gap_analysis(paths=paths)
    core = day1_core_status(paths)
    audit = read_json_file(day_json(paths, "day1_post_execution_audit.json"))
    status = read_json_file(paths.data_dir / "system" / "forward_dry_run_status.json")
    manifest = read_json_file(day_json(paths, "day1_artifact_manifest.json"))
    reproducibility = read_json_file(day_json(paths, "day1_reproducibility_manifest.json"))
    blocking = list(core["blocking_reasons"])
    if manifest.get("overall_passed") is not True:
        blocking.append("day1_artifact_manifest_not_passed")
    if not reproducibility:
        blocking.append("day1_reproducibility_manifest_missing")
    payload: dict[str, Any] = {
        "packet_id": "FORWARD-DRY-RUN-DAY2-READINESS-PACKET",
        "source_day_index": 1,
        "next_day_index": 2,
        "day1_passed": audit.get("overall_passed") is True,
        "day1_artifacts_complete": manifest.get("overall_passed") is True,
        "day1_reproducibility_manifest_exists": bool(reproducibility),
        "forward_dry_run_started": status.get("forward_dry_run_started") is True,
        "forward_dry_run_days_completed": status.get("forward_dry_run_days_completed"),
        "day2_prompt_eligible_after_operator_review": not blocking and not day2_executed(paths),
        "operator_review_required": True,
        "day2_executed": day2_executed(paths),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "boundary": {
            "readiness_packet_only": True,
            "run_daily_called_for_day2": False,
            "forward_dry_run_day2_started": False,
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    return write_artifact(day_json(paths, "day2_readiness_packet.json"), payload, day_report(paths, "DAY2_READINESS_PACKET.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day2 Readiness Packet",
        "",
        f"- day1_passed: {str(payload['day1_passed']).lower()}",
        f"- day1_artifacts_complete: {str(payload['day1_artifacts_complete']).lower()}",
        "- operator_review_required: true",
        "- day2_executed: false",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

