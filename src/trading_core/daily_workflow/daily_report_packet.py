"""Daily research preview report packet."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths

from .common import DEFAULT_AS_OF_DATE, NOTICE, boundary_markdown, daily_order_preview_path, daily_report_packet_markdown_path, daily_report_packet_path, daily_signals_path, data_quality_path, execution_preview_path, freeze_path, paths_or_default, read_json_file, snapshot_path, workflow_boundary, write_artifact
from .daily_isolated_execution_preview import build_daily_isolated_execution_preview


EXPLICIT_NON_CLAIMS = [
    "This is not forward dry-run day 1.",
    "This does not call run-daily.",
    "This is not strategy effectiveness proof.",
    "This is not forward dry-run validation.",
    "This is not live trading readiness.",
    "This does not trigger promotion.",
    "This does not use ML/LLM/RL for trading decisions.",
]


def build_daily_report_packet(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if not execution_preview_path(paths, as_of_date).exists():
        build_daily_isolated_execution_preview(as_of_date=as_of_date, execution_mode="isolated", paths=paths)
    snapshot = read_json_file(snapshot_path(paths, as_of_date))
    quality = read_json_file(data_quality_path(paths, as_of_date))
    signals = read_json_file(daily_signals_path(paths, as_of_date))
    orders = read_json_file(daily_order_preview_path(paths, as_of_date))
    execution = read_json_file(execution_preview_path(paths, as_of_date))
    signal_summary = {item["strategy_id"]: {"cash_weight": item["cash_weight"], "target_count": len(item.get("target_weights", {})), "warnings": item.get("warnings", [])} for item in signals.get("signals", [])}
    order_summary = {}
    for proposal in orders.get("proposals", []):
        item = order_summary.setdefault(proposal["strategy_id"], {"proposal_count": 0, "rejected_count": 0})
        item["proposal_count"] += 1
        if proposal.get("reject_reason"):
            item["rejected_count"] += 1
    payload: dict[str, Any] = {
        "as_of_date": as_of_date,
        "latest_available_trading_date": snapshot.get("latest_available_trading_date"),
        "data_freshness_status": "passed" if quality.get("overall_passed") else "blocked",
        "data_completeness_status": quality.get("summary", {}),
        "freeze_manifest": f"data/daily_workflow/freeze_manifests/daily_input_freeze_manifest-{as_of_date}.json",
        "signals_summary_by_strategy": signal_summary,
        "order_preview_summary_by_strategy": order_summary,
        "execution_preview_summary": {
            "fills": len(execution.get("fills", [])),
            "rejects": len(execution.get("rejects", [])),
            "execution_mode": execution.get("execution_mode"),
            "state_updated": execution.get("state_updated"),
        },
        "reject_summary": execution.get("rejects", []),
        "cost_estimate_summary": execution.get("cost_summary", {}),
        "warning_summary": quality.get("warnings", []) + [warning for item in signals.get("signals", []) for warning in item.get("warnings", [])],
        "operator_checklist": [
            "review data quality audit",
            "review freeze manifest hashes",
            "review daily baseline signals",
            "review order preview proposals",
            "review isolated execution preview estimates",
            "do not start forward dry-run without future authorization pack",
        ],
        "next_allowed_action": "prepare v0.6.2 forward dry-run start authorization pack",
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
        "run_daily_called": False,
        "main_ledger_written": False,
        "boundary": workflow_boundary("daily_report_packet_only"),
    }
    return write_artifact(daily_report_packet_path(paths, as_of_date), payload, daily_report_packet_markdown_path(paths, as_of_date), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Report Packet - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Signals Summary",
    ]
    lines.extend(f"- {strategy_id}: targets={item['target_count']}" for strategy_id, item in payload["signals_summary_by_strategy"].items())
    lines.extend(["", "## Order Preview Summary"])
    lines.extend(f"- {strategy_id}: proposals={item['proposal_count']} rejected={item['rejected_count']}" for strategy_id, item in payload["order_preview_summary_by_strategy"].items())
    lines.extend(["", "## Execution Preview Summary", f"- execution_mode: {payload['execution_preview_summary']['execution_mode']}", f"- state_updated: {payload['execution_preview_summary']['state_updated']}", "", "## Operator Checklist"])
    lines.extend(f"- {item}" for item in payload["operator_checklist"])
    lines.extend(["", "## Explicit Non-Claims"])
    lines.extend(f"- {item}" for item in payload["explicit_non_claims"])
    lines.extend(["", "## Boundary"])
    lines.extend(boundary_markdown("daily report packet only"))
    lines.append("")
    return "\n".join(lines)

