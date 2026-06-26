"""Preview the structural gate for a future day2 continuation."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import day_json, day_report, read_json_file, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import NEXT_VERSION, day2_executed, markdown_boundary, paths_or_default
from trading_core.forward_dry_run.day2_readiness_packet import build_day2_readiness_packet
from trading_core.storage.file_paths import ProjectPaths


def build_day2_continuation_gate_preview(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    packet_path = day_json(paths, "day2_readiness_packet.json")
    if not packet_path.exists():
        build_day2_readiness_packet(paths=paths)
    packet = read_json_file(packet_path)
    blocking: list[str] = []
    if packet.get("overall_passed") is not True:
        blocking.append("day2_readiness_packet_not_passed")
    if day2_executed(paths):
        blocking.append("day2_already_executed")
    payload: dict[str, Any] = {
        "preview_id": "FORWARD-DRY-RUN-DAY2-CONTINUATION-GATE-PREVIEW",
        "source_day_index": 1,
        "next_day_index": 2,
        "day2_continuation_structurally_eligible": not blocking,
        "operator_review_required": True,
        "day2_execution_authorized_in_this_artifact": False,
        "day2_executed": day2_executed(paths),
        "recommended_next_version": NEXT_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "boundary": {
            "gate_preview_only": True,
            "run_daily_called_for_day2": False,
            "forward_dry_run_day2_started": False,
            "main_ledger_written": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    return write_artifact(day_json(paths, "day2_continuation_gate_preview.json"), payload, day_report(paths, "DAY2_CONTINUATION_GATE_PREVIEW.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day2 Continuation Gate Preview",
        "",
        f"- day2_continuation_structurally_eligible: {str(payload['day2_continuation_structurally_eligible']).lower()}",
        "- operator_review_required: true",
        "- day2_execution_authorized_in_this_artifact: false",
        "- day2_executed: false",
        f"- recommended_next_version: {payload['recommended_next_version']}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return "\n".join(lines)

